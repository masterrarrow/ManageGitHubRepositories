from json import dumps
from base64 import b64encode, b64decode
from requests import request


class Git:
    """
        Class provides access to GitHub.
        --------------------------------

        :param username: GitHub user name.

        :param password: GitHub password.

        :error: ConnectionError - Cannot connect to server.

        :error: Exception(message): Incorrect request or authentication failure.
    """

    def __init__(self, username: str, password: str):
        self.__username = username
        self.__password = password

        # Try to connect to Github
        self.__send_request('GET', 'https://api.github.com/user')

    def __send_request(self, method: str, url: str, data=dict()) -> dict:
        """
            Send get request to server.

            :param method: GET, POST, PUT, DELETE.

            :param url: request url.

            :param data: request data.

            :return: Response object.

            :error: ConnectionError - Cannot connect to server.

            :error: Exception(message): Incorrect request or authentication failure.
        """
        try:
            resp = request(method, url, data=dumps(data),
                           auth=(self.__username, self.__password))
        except:
            raise ConnectionError("Cannot connect to server!")

        try:
            if not resp.raise_for_status():
                return resp.json()
        except:
            # Incorrect request has been sent
            raise Exception(resp.json()['message'])

    def list_repository(self, repository: str) -> list:
        """
            Get list of all items inside a repository.

            :param repository: repository name.

            :return: empty list or

            [
                {
                    'name': 'file name',
                    'type': file/dir,
                    'size': 0 bytes for dir,
                    'url': 'object url',
                    'sha': 'sha'
                }
                ...
            ]
        """
        url = 'https://api.github.com/repos/{}/{}/contents'

        resp = self.__send_request(
            'GET', url.format(self.__username, repository))

        result = list()

        # Return list of all existing repositories
        for item in resp:
            result.append({
                'name': item['name'],
                'type': item['type'],
                'size': item['size'],
                'url': item['html_url'],
                'sha': item['sha']
            })

        return result

    def list_repositories(self) -> list:
        """
            Get all user repositories.

            :return: empty list or

            [
                {
                    'name': 'repository name,
                    'description': 'repository description',
                    'url': 'repository url',
                    'private': bool,
                    'size': int (size in bytes),
                    'language': str
                }
                ...
            ]
        """
        repos = self.__send_request('GET', 'https://api.github.com/user/repos')

        result = list()

        # Return list of all existing repositories
        for repo in repos:
            result.append({
                'name': repo['name'],
                'description': repo['description'],
                'url': repo['html_url'],
                'private': repo['private'],
                'size': repo['size'],
                'language': repo['language'],
            })

        return result

    def get_file_content(self, repository: str, file: str) -> str:
        """
            Get file content.

            :param repository: repository name.

            :param file: file path inside a repository.

            :return: file content.
        """
        url = 'https://api.github.com/repos/{}/{}/contents/{}'

        content = self.__send_request(
            'GET', url.format(self.__username, repository, file))

        # Decode file content
        file_bytes = b64decode(content['content'])

        return file_bytes.decode('utf-8')

    def create_repository(self, name: str, description: str, private=False, init=False) -> bool:
        """
            Create a new repository in GitHub.

            :param name: repository name.

            :param description: repository description.

            :param private: repository type (private=True / public=False).

            :param init: init repository with standard README.md file.

            :return: True, if succeeded.
        """
        url = 'https://api.github.com/user/repos'

        data = {
            'name': name,
            'description': description,
            'homepage': 'https://github.com',
            'private': private,
            'has_issues': True,
            'has_projects': True,
            'has_wiki': True,
            'auto_init': init
        }

        self.__send_request('POST', url, data)

        # Created
        return True

    def create_update_file(self, repository: str, file: str, file_content: str,
                           commit='', sha='') -> str:
        """
            Update or create a new file inside a repository.

            :param repository: repository name.

            :param file: file name (example README.md).

            :param sha: for updating existing file.

            :return: file 'sha'.
        """
        # Encode file content
        b_content = file_content.encode('utf-8')
        base64_content = b64encode(b_content)
        base64_content_str = base64_content.decode('utf-8')

        # Create a new file inside the repository
        url = 'https://api.github.com/repos/{}/{}/contents/{}'
        data = {
            'path': '',
            'message': commit,
            'content': base64_content_str,
            'committer': {
                'name': self.__username,
                'email': self.__username
            },
            "sha": sha
        }

        resp = self.__send_request('PUT', url.format(
            self.__username, repository, file), data)

        # Created
        return resp['content']['sha']

    def del_file(self, repository: str, file: str, commit: str, sha: str) -> bool:
        """
            Delete a file.

            :param repository: repository name.

            :param file: file path inside a repository.

            :return: True.
        """
        # https://api.github.com/repos/:owner/:repo/contents/:path
        url = 'https://api.github.com/repos/{}/{}/contents/{}'

        data = {
            'path': '',
            'message': commit,
            'committer': {
                'name': self.__username,
                'email': self.__username
            },
            "sha": sha
        }

        self.__send_request('DELETE', url.format(
            self.__username, repository, file), data=dumps(data))

        # Deleted
        return True

    def del_repository(self, repository: str) -> bool:
        """
            Delete a repository.

            :param repository: repository name.

            :return: True.
        """
        # https://api.github.com/repos/:owner/:repo
        url = 'https://api.github.com/repos/{}/{}'

        self.__send_request('DELETE', url.format(self.__username, repository))

        # Deleted
        return True
