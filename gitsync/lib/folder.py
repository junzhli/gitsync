#!/usr/bin/env python3
from shutil import copyfile, copytree, rmtree, move, ignore_patterns, Error
from os import remove

__all__ = ['copy_dir', 'delete_dir']


def copy_dir(src_path, dst_path, ignore=[]):
    try:
        copytree(src_path, dst_path, symlinks=True, ignore=ignore_patterns(*ignore))
    except Exception as error:
        raise error

def delete_dir(dir_path):
    try:
        rmtree(dir_path)
    except FileNotFoundError as error:
        # just bypass it
        pass
    except Exception as error:
        raise error
