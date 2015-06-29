"""Random video generator.

Usage:
  generator.py <keyword>... [-n <clips> -v <videos> -m <results> -c <dir>]
  generator.py (-h | --help)
  generator.py --version

Options:
  -h --help                  Show this help message.
  --version                  Show the version.
  -n --num-clips=<clips>     Number of clips to string together [default: 100].
  -v --num-videos=<videos>   Number of unique videos to use [default: 20].
  -m --max-search=<results>  Max YouTube results per term [default: 200].
  -c --cache=<dir>           Location to store search cache [default: ./cache].
"""
import yaml

from docopt import docopt
from googleapiclient.discovery import build


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Random video generator 0.0.1')
    print arguments
