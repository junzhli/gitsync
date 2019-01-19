#!/usr/bin/env python3
from shutil import copyfile, ignore_patterns
from os import remove

__all__ = ['copy_file', 'delete_file']


def copy_file(src_path, dst_path):
    try:
        copyfile(src_path, dst_path, follow_symlinks=True)
    except Exception as error:
        raise error

def delete_file(file_path):
    try:
        remove(file_path)
    except FileNotFoundError as error:
        # just bypass it
        pass
    except Exception as error:
        raise error
