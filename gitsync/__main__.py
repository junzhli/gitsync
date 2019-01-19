#!/usr/bin/env python3
from git import Repo, Remote, InvalidGitRepositoryError, NoSuchPathError
from .lib import *
import os
import sys
import logging
import argparse
import json

# DEFAULT_SETTING exported as setting_default.json with argument '--init'
DEFAULT_SETTING = {
    'repo_dir': '<Place valid repo directory path with well-prepared remote branch>',
    'files': {
        '<Source Path>': '<Relative Path of Destination in Repo Dir>',
        '/tmp/file.txt': 'file.txt',
        '/tmp/file2.txt': 'folder/fileA.txt'
    },
    "dirs": {
        "<Source Path>": "<Relative Path of Destination in Repo Dir>",
        "/home/user/your_dir": "target_name",
        "/home/user/your_dir2": "folder/sub_folder"
    },
    "ignore": {
        "patterns": [
            "target",
            ".ivy",
            ".DS_Store"
        ]
    },
    '_ver': 1
}

# Ignore anything would break this system as belows
IGNORE_PATTERNS = [
    '.state',
    '.gitignore',
    '.git'
]

# Logging
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger('gitsync')


def init_files(repo_dir, ignore=[]):
    """[summary]
    
    Arguments:
        repo_dir {[type]} -- [description]
    
    Keyword Arguments:
        ignore {list} -- [description] (default: {[]})
    """
    # create ignore list
    ignore_list = ['.state']
    ignore_list.extend(ignore)
    ignore_list = list(set(ignore_list))
    with open(os.path.join(repo_dir, '.gitignore'), 'w') as f:
        for item in ignore_list:
            f.write(item+'\n')

def precheck(files, dirs):
    for f in files:
        if not os.path.isfile(f):
            raise Exception('Item declared in files: {0} is not a file'.format(f))

    for d in dirs:
        if not os.path.isdir(d):
            raise Exception('Item declared in dirs {0} is not a directory'.format(d))

def clean_up_repo(files, dirs, repo_dir, ignore=IGNORE_PATTERNS):
    # files_in_items = list(filter(lambda item: os.path.isfile(os.path.join(repo_dir, item)), files))
    # dirs_in_items = list(filter(lambda item: os.path.isdir(os.path.join(repo_dir, item)), dirs))
    # print(files_in_items, dirs_in_items)
    items_in_repo_root = os.listdir(repo_dir)
    files_in_repo_root = list(filter(lambda item: os.path.isfile(os.path.join(repo_dir, item)), items_in_repo_root))
    dirs_in_repo_root = list(filter(lambda item: os.path.isdir(os.path.join(repo_dir, item)), items_in_repo_root))
    # print(files_in_repo_root, dirs_in_repo_root)

    be_cleaned_files = [item for item in files_in_repo_root if item not in files]
    be_cleaned_dirs = [item for item in dirs_in_repo_root if item not in dirs]
    be_cleaned_files = [item for item in be_cleaned_files if item not in ignore]
    be_cleaned_dirs = [item for item in be_cleaned_dirs if item not in ignore]

    logger.debug('Cleanup checks result:\n\t\tbe_cleaned_files {0}\n\t\tbe_cleaned_dirs {1}'.format(be_cleaned_files, be_cleaned_dirs))
    for f in be_cleaned_files:
        if f not in ignore:
            delete_file(os.path.join(repo_dir, f))

    for d in be_cleaned_dirs:
        if d not in ignore:
            delete_dir(os.path.join(repo_dir, d))

def main():
    parser = argparse.ArgumentParser(
        description='File-sync integrated with Git system solution tool')
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        default=False,
                        help='show more message for debugging')
    parser.add_argument('--config_file', help='Specify the location of the settings (Default value: settings.json)',
                        type=str, default=os.path.join(os.getcwd(), 'settings.json'))
    parser.add_argument('--init', help='Create a default of settings',
                        action='store_true', default=False)

    # Read a set of arguments
    args = parser.parse_args()
    DEBUG = args.debug
    CONFIG_FILE = args.config_file
    INIT = args.init

    # Set Logging Level
    if DEBUG:
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)

    # DEBUG
    logger.debug('Config file: {0}'.format(CONFIG_FILE))
    logger.debug('Generate default setting.json: {0}'.format(INIT))

    if INIT:
        with open('settings_default.json', 'w') as f:
            f.writelines(json.dumps(DEFAULT_SETTING, indent=4))
        sys.exit()

    # Load config
    try:
        logger.debug('Load config...')
        config = load_config(CONFIG_FILE)
        repo_dir = config['repo_dir']
        files_mapping = config['files']
        dirs_mapping = config['dirs']
        ignore_files = config['ignore']['patterns']
        ignore_files.extend(IGNORE_PATTERNS)
        ignore_files = list(set(ignore_files))
    except Exception as error:
        logger.error('Can\'t load config: {0}'.format(error))
        sys.exit(1)

    # Read and check repo has been initialized
    logger.debug('Trying to read repo...')
    try:
        repo = Repo(repo_dir)
        remote = Remote(repo, 'origin')
        if not remote.exists():
            logger.error('Can\'t find \'origin\' remote url. Please set a \'origin\' remote and upstream branch at first to proceed!')
            sys.exit(1)
        logger.debug('Repo has been loaded successfully')
        logger.info('Pulling from repo...')
        remote.pull()
    except InvalidGitRepositoryError as error:
        logger.error('Invalid repo. Please check it again!')
        sys.exit(1)
    except NoSuchPathError as error:
        logger.error('No directory \'.git\' found. Did you initialize git project?!')
        sys.exit(1)
    
    if repo.bare:
        logger.error('Repo can\'t be a bare!')
        sys.exit(1)

    # initialize runtime files/variables
    init_files(repo_dir, ignore_files)
    changed = False
    logger.info('Repo Initialization completed')

    logger.debug('Performing prechecks...')
    try:
        precheck(files_mapping.keys(), dirs_mapping.keys())
    except Exception as error:
        logger.error('Prechecks failed!')
        logger.error(error)
        sys.exit(1)
    

    logger.debug('Perform cleanup task on repo...')
    clean_up_repo(files_mapping.values(), dirs_mapping.values(), repo_dir, ignore=ignore_files)

    logger.debug('Proceed to check file changes')
    logger.debug('Detect if the sync list changes...')
    prev_config = NO_LAST_SYNC_STATE
    if check_last_sync(repo_dir):
        logger.debug('Last sync record found!')
        prev_config = load_last_sync(repo_dir)
        print(prev_config)
    
    # Check whether folder states are identical
    logger.info('Check files whether if updated')
    src_files_to_be_copied, src_dirs_to_be_copied, dst_files_to_be_deleted, dst_dirs_to_be_deleted = check_sync_state(prev_config, config, repo_dir)
    logger.debug('Sync state: \n\t\tFiles be copied {0}\n\t\tDirs be copied {1}\n\t\tFiles be deleted {2}\n\t\tDirs be deleted {3}'.format(src_files_to_be_copied, src_dirs_to_be_copied, dst_files_to_be_deleted, dst_dirs_to_be_deleted)) 

    # Start to perform sync task (overwrite dst-file / delete dst-file / copy entire src-folder(src-file) to dst-folder(dst-file))
    change_indicator = 0
    if (dst_files_to_be_deleted):
        for file_path in dst_files_to_be_deleted:
            try:
                logger.debug('Deleting file {0}'.format(file_path))
                delete_file(file_path)
                logger.debug(' ... Successfully')
            except Exception as error:
                raise error
                logger.debug(' ... Failed')
        logger.debug('Files deletion finished')
        change_indicator += 1

    if (dst_dirs_to_be_deleted):
        for dir_path in dst_dirs_to_be_deleted:
            try:
                logger.debug('Deleting directory {0}'.format(dir_path))
                delete_dir(dir_path)
                logger.debug(' ... Successfully')
            except Exception as error:
                raise error
                logger.debug(' ... Failed')
        logger.debug('Dirs deletion finished')
        change_indicator += 1

    if (src_files_to_be_copied):
        for src_path, dst_path in src_files_to_be_copied.items():
            try:
                logger.debug('Copying file {0} to {1}'.format(src_path, dst_path))
                copy_file(src_path, dst_path)
                logger.debug(' ... Successfully')
            except Exception as error:
                raise error
                logger.debug(' ... Failed')
        logger.debug('Files addition finished')
        change_indicator += 1

    if (src_dirs_to_be_copied):
        for src_path, dst_path in src_dirs_to_be_copied.items():
            try:
                logger.debug('Copying directory {0} to {1}'.format(src_path, dst_path))
                copy_dir(src_path, dst_path, ignore=ignore_files)
                logger.debug(' ... Successfully')
            except Exception as error:
                raise error
                logger.debug(' ... Failed')
        logger.debug('Dirs addition finished')
        change_indicator += 1

    if change_indicator == 0:
        logger.info('All is up to date')
        sys.exit(0)

    logger.debug('Staging files...')
    logger.debug('Reset current staging')
    repo.index.reset()

    logger.info('Stage modified files into repo...')
    repo.git.add(A=True)
    
    logger.info('Commit to repo...')
    repo.index.commit('[(auto-git) leave it here for later editing]')

    logger.info('Push to remote origin server...')
    remote.push()

    logger.debug('Saving current sync state...')
    try:
        save_current_sync(repo_dir, config)
    except Exception as error:
        logger.error('Failed to save current sync state! {0}'.format(error))
        sys.exit(1)
    logger.info('Finished')

if __name__ == '__main__':
    main()