"""Random video generator.

Usage:
  generator.py <keyword>... [-n clips -v videos -m results -c config -a cache]
  generator.py (-h | --help)
  generator.py --version

Options:
  -h --help                  Show this help message.
  --version                  Show the version.
  -n --num-clips=<clips>     Number of clips to string together [default: 100].
  -v --num-videos=<videos>   Number of unique videos to use [default: 20].
  -m --max-search=<results>  Max YouTube results per term [default: 200].
  -c --config=<config>       Path to config file [default: ./config.yml].
  -a --cache=<cache>         Location to store search cache [default: ./cache].
"""
import os
import sys
import yaml

from docopt import docopt
from googleapiclient.discovery import build


def youtube_search(keywords, developer_key,
                   max_results='200', cache='./cache.yml'):
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
    for keyword in keywords:
        cache_path = os.path.join(cache, '{}.yml'.format(keyword))
        # Try reading from the cache
        keyword_results = read_cache(cache_path)

        if keyword_results is None:
            # If there's no cache for this term, do the search
            print keyword, ': fetching results from YouTube.'
            youtube = build('youtube', 'v3', developerKey=developer_key)
            keyword_results = youtube.search().list(
                q=keyword,
                type='video',
                part='id',
                maxResults=max_results
            ).execute()
            write_cache(cache_path, keyword_results)
        else:
            print keyword, ': fetched results from cache.'
        search_results[keyword] = keyword_results


if __name__ == '__main__':
    args = docopt(__doc__, version='Random video generator 0.0.1')
    config = {
        'keywords': args['<keyword>'],
        'num_clips': args['--num-clips'],
        'num_videos': args['--num-videos'],
        'max_search': args['--max-search'],
        'cache': args['--cache'],
    }

    # Override config dict with config file
    config_file = args['--config']
    try:
        with open(config_file) as f:
            config.update(yaml.load(f))
    except IOError:
        print('Unable to read configuration file; aborting.')
        sys.exit(1)

    query_results = youtube_search(
        config['keywords'],
        config['DEVELOPER_KEY'],
        max_results=config['max_search'],
        cache=config['cache']
    )
