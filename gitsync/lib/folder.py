#!/usr/bin/env python3
from shutil import copyfile, copytree, rmtree, move, ignore_patterns, Error
from os import remove

__all__ = ['copy_dir', 'delete_dir']


def copy_dir(src_path, dst_path, ignore=[]):
    """Copy a folder recursively from source path to specific destination
    
    Arguments:
        src_path {str} -- Source path
        dst_path {str} -- Destination path
    
    Keyword Arguments:
        ignore {list} -- Ignore patterns used in the operation where any directory or file named with one of patterns is ignored (default: {[]})
    
    Raises:
        error -- raises if any error occurred in this operation.
    """
    try:
        copytree(src_path, dst_path, symlinks=True,
                 ignore=ignore_patterns(*ignore))
    except Exception as error:
        raise error


def delete_dir(dir_path):
    """Delete a folder recursively with given path
    
    Arguments:
        dir_path {str} -- Dir path

    Warnings:
        It won't throw FileNotFoundError exception if this folder doesn't exist
    
    Raises:
        error -- raises if any error occurred in this operation.
    """
    try:
        rmtree(dir_path)
    except FileNotFoundError as error:
        # just bypass it
        pass
    except Exception as error:
        raise error
