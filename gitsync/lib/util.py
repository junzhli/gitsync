import json
from os import path
from filecmp import dircmp, cmp

__all__ = ['load_config', 'check_last_sync', 'load_last_sync', 'save_current_sync', 'check_sync_state', 'NO_LAST_SYNC_STATE']

# private constant
STATE_FILE = '.state'
CONFIG = {
    'FILES': 'files',
    'DIRS': 'dirs'
}

# exposed constant
NO_LAST_SYNC_STATE = 'no-last-sync-state'


def load_config(config_file_path):
    with open(config_file_path, encoding='utf-8') as reader:
        data = reader.read()
        config = json.loads(data)
        return config


def check_last_sync(repo_dir):
    return path.exists(path.join(repo_dir, STATE_FILE))


def load_last_sync(repo_dir):
    data = dict()
    with open(path.join(repo_dir, STATE_FILE)) as f:
        data = json.load(f)
    return data

def save_current_sync(repo_dir, config):
    """save the location of files defined in settings"""
    with open(path.join(repo_dir, STATE_FILE), 'w') as f:
        f.write(json.dumps(config))

def check_sync_state(prev_config, config, repo_dir):
    if not CONFIG['FILES'] in config:
        raise AttributeError('Invalid config file. \'{0}\' key not found'.format(CONFIG['FILES']))
    if not CONFIG['DIRS'] in config:
        raise AttributeError('Invalid config file. \'{0}\' key not found'.format(CONFIG['DIRS']))

    if prev_config != NO_LAST_SYNC_STATE:
        if not CONFIG['FILES'] in prev_config:
            raise AttributeError('Invalid .state file. \'{0}\' key not found'.format(CONFIG['FILES']))
        if not CONFIG['DIRS'] in prev_config:
            raise AttributeError('Invalid .state file. \'{0}\' key not found'.format(CONFIG['DIRS']))

    prev_files_mapping = prev_config[CONFIG['FILES']] if prev_config != NO_LAST_SYNC_STATE else dict()
    prev_dirs_mapping = prev_config[CONFIG['DIRS']] if prev_config != NO_LAST_SYNC_STATE else dict()
    files_mapping = config[CONFIG['FILES']]
    dirs_mapping = config[CONFIG['DIRS']]
    dst_files_to_be_deleted = []
    dst_dirs_to_be_deleted = []
    src_files_to_be_copied = {}
    src_dirs_to_be_copied = {}
    
    # check items listed in previous state doesn't no longer exist in current items
    ### files
    for prev_src_item, prev_dst_item in prev_files_mapping.items():
        src_items = files_mapping.keys()
        prev_dst_path = path.join(repo_dir, prev_dst_item)

        if prev_src_item not in src_items:
            dst_files_to_be_deleted.append(prev_dst_path)

    ### dirs
    for prev_src_item, prev_dst_item in prev_dirs_mapping.items():
        src_items = dirs_mapping.keys()
        prev_dst_path = path.join(repo_dir, prev_dst_item)

        if prev_src_item not in src_items:
            dst_dirs_to_be_deleted.append(prev_dst_path)

    # TODO: check items listed in current state whether its destination is changed

    
    # recursively look into folders and items to check distinctions from previous state
    ## for folder item: overwrite/add files in that folder if files can't be found or is modified
    ## for file item: compare both and overwrite in that folder if file is modified or doesn't exist
    # files, dirs = _categorize_file_mapping(file_mapping)

    ### files
    for src_path, dst_item in files_mapping.items():
        dst_path = path.join(repo_dir, dst_item)

        if not path.exists(src_path):
            raise FileNotFoundError('Source location {0}: No such file to check sync state'.format(src_path))

        to_sync = False
        if not path.exists(dst_path):
            to_sync = True
        if not to_sync:
            is_identical = cmp(src_path, dst_path)
            to_sync = False if is_identical else True
        if to_sync:
            src_files_to_be_copied.update({src_path: dst_path})

    ### dirs
    dir_mapping = {src_path: path.join(repo_dir, dst_item) for src_path, dst_item in dirs_mapping.items()}
    dir_src_files_to_be_copied, dir_src_dirs_to_be_copied, dir_dst_files_to_be_deleted, dir_dst_dirs_to_be_deleted = _find_diff_folders(dir_mapping)

    src_files_to_be_copied.update(dir_src_files_to_be_copied)
    src_dirs_to_be_copied.update(dir_src_dirs_to_be_copied)
    dst_files_to_be_deleted.extend(dir_dst_files_to_be_deleted)
    dst_dirs_to_be_deleted.extend(dir_dst_dirs_to_be_deleted)

    return src_files_to_be_copied, src_dirs_to_be_copied, dst_files_to_be_deleted, dst_dirs_to_be_deleted
        
def _categorize_file_mapping(file_mapping):
    files = []
    dirs = []
    for src_item in file_mapping.keys():
        dirs.append(src_item) if path.isdir(src_item) else files.append(src_item)
    return files, dirs

def _find_diff_folders(dir_mapping):
    src_dirs_to_be_copied = {}
    src_files_to_be_copied = {}
    dst_dirs_to_be_deleted = []
    dst_files_to_be_deleted = []
    common_dirs_to_be_looked_into = {}
    for src_path, dst_path in dir_mapping.items():
        if not path.exists(src_path):
            raise FileNotFoundError('Source location {0}: No such dir to check sync state'.format(src_path))

        copy_entire_dir = False
        if not path.exists(dst_path):
            copy_entire_dir = True
            src_dirs_to_be_copied.update({src_path: dst_path})
        if not copy_entire_dir:
            dircmp_report = dircmp(src_path, dst_path)
            src_only = dircmp_report.left_only
            src_files_only = [item for item in {item : item_path for item, item_path in {item: path.join(src_path, item) for item in src_only}.items() if path.isfile(item_path)}.keys()]
            src_dirs_only = [item for item in {item : item_path for item, item_path in {item: path.join(src_path, item) for item in src_only}.items() if path.isdir(item_path)}.keys()]
            src_files_only_with_path = list(map(lambda item: path.join(src_path, item), src_files_only))
            src_files_only_with_path_mapping = {src_file_only_with_path: path.join(dst_path, src_files_only[index]) for index, src_file_only_with_path in enumerate(src_files_only_with_path)}
            src_dirs_only_with_path = list(map(lambda item: path.join(src_path, item), src_dirs_only))
            src_dirs_only_with_path_mapping = {src_dir_only_with_path: path.join(dst_path, src_dirs_only[index]) for index, src_dir_only_with_path in enumerate(src_dirs_only_with_path)}
            dst_only = dircmp_report.right_only
            dst_only_with_path = list(map(lambda item: path.join(dst_path, item), dst_only))
            dst_files_only_with_path = list(filter(lambda item: path.isfile(item), dst_only_with_path))
            dst_dirs_only_with_path = list(filter(lambda item: path.isdir(item), dst_only_with_path))
            diff_files = dircmp_report.diff_files
            diff_files_with_path = list(map(lambda item: path.join(src_path, item), diff_files))
            diff_files_with_path_mapping = {src_file_with_path: path.join(dst_path, diff_files[index]) for index, src_file_with_path in enumerate(diff_files_with_path)}
            common_dirs = dircmp_report.common_dirs
            common_dirs_with_path = list(map(lambda item: path.join(src_path, item), dircmp_report.common_dirs))
            common_dirs_mapping = {common_dir_with_path: path.join(dst_path, common_dirs[index]) for index, common_dir_with_path in enumerate(common_dirs_with_path)}

            src_files_to_be_copied.update(src_files_only_with_path_mapping)
            src_files_to_be_copied.update(diff_files_with_path_mapping)
            src_dirs_to_be_copied.update(src_dirs_only_with_path_mapping)
            dst_files_to_be_deleted.extend(dst_files_only_with_path)
            dst_dirs_to_be_deleted.extend(dst_dirs_only_with_path)
            common_dirs_to_be_looked_into.update(common_dirs_mapping)

    if common_dirs_to_be_looked_into:
        src_files_to_be_copied_from_common_dirs, src_dirs_to_be_copied_from_common_dirs, dst_files_to_be_deleted_from_common_dirs, dst_dirs_to_be_deleted_from_common_dirs = _find_diff_folders(common_dirs_to_be_looked_into)
        src_files_to_be_copied.update(src_files_to_be_copied_from_common_dirs)
        src_dirs_to_be_copied.update(src_dirs_to_be_copied_from_common_dirs)
        dst_files_to_be_deleted.extend(dst_files_to_be_deleted_from_common_dirs)
        dst_dirs_to_be_deleted.extend(dst_dirs_to_be_deleted_from_common_dirs)

    return src_files_to_be_copied, src_dirs_to_be_copied, dst_files_to_be_deleted, dst_dirs_to_be_deleted
