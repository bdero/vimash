#!/usr/bin/env python2
"""vimash.

Usage:
  vimash.py <keyword>... [options]
  vimash.py --help
  vimash.py --version

Options:
  -n --num-clips=<clips>     Number of clips to string together [default: 100].
  -v --num-videos=<videos>   Sample size of unique videos to use [default: 20].
  -m --max-search=<results>  Max YouTube results per term [default: 50].
  -c --config=<config>       Path to config file [default: ./config.yml].
  -a --cache=<cache>         Location to store search cache [default: ./cache].
  -f --fps=<fps>             The output video framerate [default: 25].
  -w --width=<pixels>        The output video width [default: 1920].
  -h --height=<pixels>       The output video height [default: 1080].
  -o --output=<file>         The path to the output file [default: ].
  --min-clip-len=<seconds>   Minimum length of video segments [default: 0.04].
  --clip-len-var=<seconds>   Length variation of each segment [default: 0.4].
  --codec=<codec>            The output video's codec [default: libx264].
  --bitrate=<bps>            The output video's bitrate [default: 8000k].
  --audio-bitrate=<bps>      The output audio's bitrate [default: 384k].
  --help                     Show this help message.
  --version                  Show the version.
"""
from __future__ import unicode_literals

import md5
import os
import sys
import yaml

from random import random, sample

from docopt import docopt
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from moviepy import editor
from youtube_dl import YoutubeDL


def youtube_search(keywords, developer_key,
                   max_results='50', cache='./cache'):
    def read_cache(location):
        try:
            with open(location) as f:
                contents = yaml.load(f)
        except IOError:
            contents = None
        return contents

    def write_cache(location, contents):
        cache_dir = os.path.dirname(location)
        if not os.path.exists(cache_dir):
            os.mkdir(cache_dir)
        with open(location, 'w') as f:
            f.write(yaml.dump(contents))

    search_results = {}
    youtube = None
    for keyword in keywords:
        cache_path = os.path.join(cache, '{}.yml'.format(keyword))
        # Try reading from the cache
        keyword_results = read_cache(cache_path)

        if keyword_results is None:
            # If there's no cache for this term, do the search
            print keyword, ': fetching results from YouTube.'
            if youtube is None:
                youtube = build('youtube', 'v3', developerKey=developer_key)
            try:
                keyword_results = youtube.search().list(
                    q=keyword,
                    type='video',
                    part='id',
                    maxResults=max_results
                ).execute()
            except HttpError, e:
                print 'Unable to fetch results; HttpError from Google:',
                print e._get_reason().strip()
                continue
            print ' '*len(keyword), ':',
            print len(keyword_results['items']), 'results fetched.'
            write_cache(cache_path, keyword_results)
        else:
            print keyword, ': fetched', len(keyword_results['items']),
            print 'results from cache.'
        search_results[keyword] = keyword_results

    return search_results


def youtube_download(videos, cache='./cache'):
    print 'Fetching', len(videos), 'videos.'
    options = {
        'outtmpl': os.path.join(cache, 'videos', '%(id)s.%(ext)s'),
        'format': 'mp4',
        'download_archive': os.path.join(cache, 'videos', 'download_archive')
    }
    with YoutubeDL(options) as ydl:
        result = ydl.download(videos)

    return result


def generate_video(video_ids, options=None, cache='./cache'):
    # Define default options and override anything explicitly set
    opts = {
        'num_clips': 20,
        'min_clip_len': 0.04,
        'clip_len_var': 0.4,
        'width': 1920,
        'height': 1080,
        'fps': 30,
        'codec': 'libx264',
        'bitrate': '8000k',
        'audio_bitrate': '384k',
        'output': '',
    }
    if options is not None:
        opts.update(options)

    # Load the videos
    paths = [
        os.path.join(cache, 'videos', '{}.mp4'.format(video_id))
        for video_id in video_ids
    ]
    videos = [editor.VideoFileClip(path) for path in paths]

    # Segment the videos into random clips
    clips = []
    for iteration in xrange(opts['num_clips']):
        clip = sample(videos, 1)[0]
        length = (
            random()*opts['clip_len_var'] + opts['min_clip_len']
        )
        start_time = random()*(clip.duration - length)

        print 'Clip', iteration, ':',
        print 'Slicing video', video_ids[videos.index(clip)],
        print '(', start_time, 'to', start_time + length, ')'
        clips += [
            clip
            .subclip(start_time, start_time + length)
            .set_fps(opts['fps'])
            .resize((opts['width'], opts['height']))
        ]

    # Combine the clips
    result = editor.concatenate_videoclips(clips)

    # Output result to a file
    title = (
        'output/generated_{}.mp4'.format(
            md5.new(''.join(video_ids)).hexdigest()
        )
        if not len(opts['output']) else opts['output']
    )

    # Create the output dir if it doesn't exist
    output_dir = os.path.dirname(title)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    print 'Saving result:', title
    result.write_videofile(
        title,
        fps=opts['fps'],
        codec=opts['codec'],
        bitrate=opts['bitrate'],
        audio_bitrate=opts['audio_bitrate']
    )


if __name__ == '__main__':
    arguments = docopt(__doc__, version='vimash 0.1.0')

    def optional_args(*args):
        return {
            arg[0]: arg[1](arguments['--{}'.format(arg[0].replace('_', '-'))])
            for arg in args
        }
    config = {
        'keywords': arguments['<keyword>'],
        'video': optional_args(
            ('num_clips', int),
            ('min_clip_len', float),
            ('clip_len_var', float),
            ('width', int),
            ('height', int),
            ('fps', int),
            ('codec', str),
            ('bitrate', str),
            ('audio_bitrate', str),
            ('output', str),
        ),
        'num_videos': int(arguments['--num-videos']),
        'max_search': int(arguments['--max-search']),
        'cache': arguments['--cache'],
    }

    # Override config dict with config file
    config_file = arguments['--config']
    try:
        with open(config_file) as f:
            config.update(yaml.load(f))
    except IOError:
        print 'Unable to read configuration file; aborting.'
        sys.exit(1)

    # Fetch YouTube search results
    query_results = youtube_search(
        config['keywords'],
        config['DEVELOPER_KEY'],
        max_results=config['max_search'],
        cache=config['cache']
    )
    # Collect all of the video IDs
    videos = []
    for result in query_results.values():
        videos += [
            video['id']['videoId']
            for video in result.get('items', [])
        ]

    # Select a random sample of the videos
    sample_videos = sample(videos, min(config['num_videos'], len(videos)))

    # Download selected videos from YouTube
    youtube_download(sample_videos, cache=config['cache'])

    # Generate random video
    generate_video(
        sample_videos,
        options=config['video'],
        cache=config['cache']
    )
