# GitSync
Sync tool integrated with Git system. It is meant to help developers to back up everything about portable settings and codebase like 
* Dotfile (`.vimrc`, `.zshrc`, `.bashrc`, `.eslint`)
* Workplace config (`.vscode`)
* Source code

## Feature
* Auto comment for every commit
* Command-line utility
* Folder/File synchronization support
* Exclude folders/files with pattern rule

## Installing
### Requirements
Python 3.x or higher is required
### From remote repository
```shell
$ pip3 install git+git://github.com/junzhli/gitsync.git
```
### From local machine
```shell
$ git clone https://github.com/junzhli/gitsync.git
$ cd gitsync
$ python3 setup.py install
```

## Usage
##### Create a template configuration file
```shell
$ gitsync --init
Generate a template settings.json
```

#### Set up `settings.json`
* `repo_dir`
  * Full path of repository
* `files` and `dirs`
  * Files and folders `src: dst`
    * Source path `src`
      * Absolute path
    * Destination key `dst`
      * Relative path in repository folder
* `ignore`
  * `patterns`
    * File/folder being ignored

#### Sync files/folders
```shell
$ gitsync --config_file /folder/settings.json
```

## Known issues

## Contribution

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE) file for details