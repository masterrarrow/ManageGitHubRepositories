#!/usr/bin/python
# -*- coding: utf-8 -*-

from subprocess import call, check_output
from os import path, chdir, mkdir
from click import command, argument, option
from decouple import config
from git import Git


def open_in_vscode(folder: str):
    """
        Open a local repository in VS Code.

        :param folder: path to folder.

        :return: bool.
    """
    call(['bash', '-c', f"code '{folder}'"])

    return True


def local_repository(user: str, repository: str, folder: str):
    """
        Get data from the GitHub repository to a local folder.
        Folder name is a repository name.

        :param user: GitHub user name.

        :param repository: repository name.

        :param folder: folder path.

        :return: bool.
    """
    if path.exists(path.join(folder, repository)):
        return False

    mkdir(path.join(folder, repository))
    chdir(path.join(folder, repository))

    commands = list()
    commands.append('git init')
    commands.append(
        f'git remote add origin git@github.com:{user}/{repository}.git')
    commands.append('git pull origin master')
    commands.append('git branch -u origin/master')

    for cmd in commands:
        call(['bash', '-c', cmd])

    return True


@command()
@argument('repository')
@option(
    '--description', '-d',
    type=str,
    default='',
    help='repository description',
)
@option(
    '--private', '-p',
    type=bool,
    default=False,
    help='private repository or not (True/False)',
)
def main(repository: str, description='', private=False):
    # Get username and password from environment
    username = config('USERNAME')
    password = config('PASSWORD')

    # Get the absolute path to the folder -
    # the path where the script is executed via bash
    folder = check_output(['bash', '-c', 'pwd']).decode('utf-8').strip()

    # Try to connecting to GitHub and create a new repository
    # with a standard README.md file in it
    try:
        git = Git(username, password)
        git.create_repository(repository, description, private, init=True)
    except Exception as e:
        print(e)
        return

    print(f'\nRepository "{repository}" has been created.')

    print('\nInitializing repository:')

    # Get data from GitHub repository to local
    if not local_repository(username, repository, folder):
        print('\nUnable to initialize local repository!')
        return

    # Open the local repository in vs code
    if not open_in_vscode(path.join(folder, repository)):
        print('\nUnable to open folder with local repository!')
        return

    print('Done!')


if __name__ == "__main__":
    main()
