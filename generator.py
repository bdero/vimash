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
import yaml
import sys

from docopt import docopt
from googleapiclient.discovery import build


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

    print config
