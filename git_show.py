#!/home/masterarrow/anaconda3/bin/python
# -*- coding: utf-8 -*-

from decouple import config
from git import Git


def main():
    # Get username and password from environment
    username = config('USERNAME')
    password = config('PASSWORD')

    # Try to connecting to GitHub and get the list of repositories
    try:
        git = Git(username, password)
        resp = git.list_repositories()
    except Exception as e:
        print(e)
        return

    print(f'\nList of {username} repositories:\n')

    for item in resp:
        print('Name: ', item['name'])
        print('Language: ', item['language'])
        print('Size: {:.1f} KB'.format(item['size']/1024))
        print('Type: ', 'private' if item['private'] else 'public')
        print('Description: ', item['description'])
        print('Url: ', item['url'], '\n')


if __name__ == "__main__":
    main()
