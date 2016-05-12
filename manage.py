#!/usr/bin/python3

import os
import argparse
import configparser

from dotfiles import Dotfiles


def get_args():
    """ Parse and validate command line options.

    :returns: Namespace with provided options.

    """
    # TODO(@b0nd0 2015-05-09) Add subparsers. just for practice purposes.
    parser = argparse.ArgumentParser(
            description='bondo dotfiles management utility')

    parser.add_argument('--install', '-i', help='install configs',
                        action='store_true')

    parser.add_argument('--remove', '-r', help='restore old configs',
                        action='store_true')

    parser.add_argument('--config', '-c', help='path to configuration file',
                        action='store', default='./config.ini')

    return parser.parse_args()


def get_config(path):
    """ read config from ini file

    :path: config file path
    :returns: configParser object??

    """
    config = configparser.ConfigParser()
    config.read(path)

    # realpath directories
    config.set('main',
               'source_dir',
               os.path.realpath(config['main']['source_dir']))

    config.set('main',
               'backup_dir',
               os.path.realpath(config['main']['backup_dir']))

    if config['main']['destination_dir'] == '~':
        config.set('main',
                   'destination_dir',
                   os.path.expanduser(config['main']['destination_dir']))
    else:
        config.set('main',
                   'destination_dir',
                   os.path.realpath(config['main']['destination_dir']))

    return config


def manage():
    """ This is an entry point function

    :returns: None

    """
    args = get_args()
    config = get_config(args.config)
    d = Dotfiles(config['main']['source_dir'],
                 config['main']['destination_dir'],
                 config['main']['backup_dir'])

    if args.install:
        d.install()
    elif args.remove:
        d.remove()
    else:
        print('Error: Unsupported action. Use -h for help.')


if __name__ == '__main__':
    manage()
