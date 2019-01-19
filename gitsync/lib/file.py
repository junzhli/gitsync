#!/usr/bin/env python3
"""File Operations

"""
from shutil import copyfile, ignore_patterns
from os import remove

__all__ = ['copy_file', 'delete_file']


def copy_file(src_path, dst_path):
    """Copy a file from source path to specific destination

    Arguments:
        src_path {str} -- Source path
        dst_path {str} -- Destination path

    Raises:
        error -- raises if any error occurred in this operation.
    """
    try:
        copyfile(src_path, dst_path, follow_symlinks=True)
    except Exception as error:
        raise error


def delete_file(file_path):
    """Delete a file with given path

    Arguments:
        file_path {str} -- File path

    Warnings:
        It won't throw FileNotFoundError exception if this file doesn't exist

    Raises:
        error -- raises if any error occurred in this operation.
    """
    try:
        remove(file_path)
    except FileNotFoundError as error:
        # just bypass it
        pass
    except Exception as error:
        raise error
