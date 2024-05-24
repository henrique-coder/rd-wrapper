# Local example: from rd_wrapper import RDW (PyPi example: pip install rd-wrapper)

import httpx
from langcodes import Language, LanguageTagError
from datetime import datetime
from urllib.parse import unquote
from threading import Thread
from queue import Queue
from time import sleep
from typing import *


class RDW:
    """
    Real-Debrid API wrapper. This class is used to interact with the Real-Debrid API.
    """

    # Exceptions
    class Exception:
        """
        Real-Debrid API wrapper exceptions.
        """

        class NonPremiumAccount(Exception):
            def __init__(self, message: AnyStr) -> None:
                super().__init__(message)
                self.message = message

            def __str__(self) -> AnyStr:
                return self.message

        class UnknownError(Exception):
            def __init__(self, message: AnyStr) -> None:
                super().__init__(message)
                self.message = message

            def __str__(self) -> AnyStr:
                return self.message

        class InvalidAPIToken(Exception):
            def __init__(self, message: AnyStr) -> None:
                super().__init__(message)
                self.message = message

            def __str__(self) -> AnyStr:
                return self.message

        class APITokenDisabledSuccessfully(Exception):
            def __init__(self, message: AnyStr) -> None:
                super().__init__(message)
                self.message = message

            def __str__(self) -> AnyStr:
                return self.message

        class GetServerTimeError(Exception):
            def __init__(self, message: AnyStr) -> None:
                super().__init__(message)
                self.message = message

            def __str__(self) -> AnyStr:
                return self.message

        class GetServerISOTimeError(Exception):
            def __init__(self, message: AnyStr) -> None:
                super().__init__(message)
                self.message = message

            def __str__(self) -> AnyStr:
                return self.message

        class UnsupportedHosterError(Exception):
            def __init__(self, message: AnyStr) -> None:
                super().__init__(message)
                self.message = message

            def __str__(self) -> AnyStr:
                return self.message

        class EmptyFolderOrNotSupportedError(Exception):
            def __init__(self, message: AnyStr) -> None:
                super().__init__(message)
                self.message = message

            def __str__(self) -> AnyStr:
                return self.message

    # Internal methods
    def __init__(self, api_token: AnyStr) -> None:
        """
        Constructor to initialize the Real-Debrid API wrapper and fetch user data from the API.
        :param api_token: To get your API token, visit: https://real-debrid.com/apitoken
        """

        self._base_api_url = 'https://api.real-debrid.com/rest/1.0'
        self._api_token = api_token
        self._http_client = httpx.Client(params={'auth_token': self._api_token}, headers={'Accept': 'application/json', 'Content-Type': 'application/json'}, follow_redirects=False, timeout=10)

        try: res = self._http_client.get(self._base_api_url + '/user')
        except Exception as e: raise e

        if res.status_code == 200: self._raw_user_data = dict(res.json())
        else: raise RDW.Exception.InvalidAPIToken('Invalid Real-Debrid API token. Please provide a valid one to interact with the API.')

        self.account_id = int(self._raw_user_data.get('id'))
        self.account_username = str(self._raw_user_data.get('username'))
        self.account_email = str(self._raw_user_data.get('email'))
        self.account_avatar_url = unquote(self._raw_user_data.get('avatar'))
        self.account_language_code = str(self._raw_user_data.get('locale'))
        try: self.account_language_name = str(Language.get(self.account_language_code).display_name('en-us'))
        except LanguageTagError: self.account_language_name = 'Unknown'
        self.is_premium_account = True if str(self._raw_user_data.get('type')).strip() == 'premium' else False
        self.premium_expiration_time = int(datetime.strptime(self._raw_user_data.get('expiration'), '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())
        self.account_fidelity_points = int(self._raw_user_data.get('points'))

    def __del__(self) -> None:
        """
        Destructor to close the HTTP client.
        """

        self._http_client.close()

    # Hidden methods
    def _premium_account_is_required(self) -> None:
        """
        Check if the account is a premium account. If not, raise an exception.
        :return: A raise statement if the account is not a premium account. Otherwise, return None.
        """

        if not self.is_premium_account: raise RDW.Exception.NonPremiumAccount('Only premium users can use this function. Please upgrade your account to premium at: https://real-debrid.com/premium')
        return None

    # Public methods (internal)
    def stop_http_session(self) -> None:
        """
        Stop the current HTTP session.
        """

        self.__del__()

    # Public methods (endpoints)
    def disable_current_api_token(self) -> None:
        """
        Disable the current API token. To generate a new one, visit: https://real-debrid.com/apitoken
        :return: A raise statement if the API token is disabled successfully or not.
        """

        def replace_middle_with_asterisks(string: AnyStr) -> str:
            if len(string) <= 2: return '*' * len(string)
            elif len(string) <= 6: return string[0] + '*' * (len(string) - 2) + string[-1]
            return str(string[:3] + '*' * (len(string) - 6) + string[-3:])

        try: res = self._http_client.get(self._base_api_url + '/disable_access_token')
        except Exception as e: raise e
        finally: self.stop_http_session()

        if res.status_code == 204: raise RDW.Exception.APITokenDisabledSuccessfully(f'Your current API token ({replace_middle_with_asterisks(self._api_token)}) has been disabled. To see your new API token, please visit: https://real-debrid.com/apitoken')
        elif res.status_code == 401: raise RDW.Exception.InvalidAPIToken('Invalid Real-Debrid API token. Please provide a valid one so that it can be disabled.')
        raise RDW.Exception.UnknownError('An unknown error occurred while disabling your current API token.')

    def get_server_time(self, unix_timestamp: bool = False) -> Union[str, int]:
        """
        Fetch server time. This is useful for debugging purposes.
        :param unix_timestamp: Whether to return the raw server time in Unix timestamp format.
        :return: The server time in string or Unix timestamp format.
        """

        try: res = self._http_client.get(self._base_api_url + '/time')
        except Exception as e: raise e

        if res.status_code == 200:
            if unix_timestamp: return int(datetime.strptime(res.text, '%Y-%m-%d %H:%M:%S').timestamp())
            else: return str(res.text)

        raise RDW.Exception.GetServerTimeError('An error occurred while fetching the server time.')

    def get_server_iso_time(self, unix_timestamp: bool = False) -> Union[str, int]:
        """
        Fetch server time in ISO format. This is useful for debugging purposes.
        :return: The server time in ISO format.
        """

        try: res = self._http_client.get(self._base_api_url + '/time/iso')
        except Exception as e: raise e

        if res.status_code == 200:
            if unix_timestamp: return int(datetime.strptime(res.text, '%Y-%m-%dT%H:%M:%S%z').timestamp())
            else: return str(res.text)

        raise RDW.Exception.GetServerISOTimeError('An error occurred while fetching the server time in ISO format.')

    def is_url_supported(self, url: AnyStr, password: AnyStr = None) -> bool:
        """
        Check if the given url is supported by Real-Debrid.
        :param url: The original url to check.
        :param password: The password to access the url. Default is None.
        :return: True if the url is supported. Otherwise, return False.
        """

        try: res = self._http_client.post(self._base_api_url + '/unrestrict/check', data={'link': url, 'password': password})
        except Exception as e: raise e

        if res.status_code == 200: return True
        return False

    def get_unlimited_url_data(self, file_url: AnyStr, password: AnyStr = None, remote_traffic: bool = False) -> dict:
        """
        Generate an unrestricted url for the given URL.
        :param file_url: The original url to generate an unrestricted url.
        :param password: The password to access the url. Default is None.
        :param remote_traffic: Whether to generate a remote traffic url. Default is False.
        :return: The unrestricted url if successful. Otherwise, return the original url.
        """

        RDW._premium_account_is_required(self)

        try: res = self._http_client.post(self._base_api_url + '/unrestrict/link', data={'link': file_url, 'password': password, 'remote': 1 if remote_traffic else 0})
        except Exception as e: raise e

        if res.status_code != 200: raise RDW.Exception.UnsupportedHosterError('The given url is not supported by Real-Debrid.')
        json_data = dict(res.json())

        output_data = {
            'id': str(json_data.get('id')),
            'originalUrl': str(json_data.get('link')),
            'unrestrictedUrl': str(json_data.get('download')),
            'filename': str(json_data.get('filename')),
            'size': int(json_data.get('filesize')),
            'hoster': str(json_data.get('host')),
            'mimetype': str(json_data.get('mimeType')),
            'isStreamable': bool(int(json_data.get('streamable', 0))),
            'hasMultipleUrls': False,
            'collectedUrls': list(),
        }

        if 'alternative' not in json_data: output_data.pop('collectedUrls')
        else:
            output_data['hasMultipleUrls'] = True
            output_data['quality'] = str(json_data.get('quality'))

            for item in json_data.get('alternative', list()):
                output_data['collectedUrls'].append({
                    'id': str(item.get('id')),
                    'unrestrictedUrl': unquote(item.get('download', str())) if item.get('download') else None,
                    'filename': str(item.get('filename')),
                    'mimetype': str(item.get('mimeType')),
                    'quality': str(item.get('quality')),
                })

        return output_data

    def get_individual_urls_from_folder_url(self, folder_url: AnyStr, return_unlimited_urls: bool = False) -> list:
        """
        Generate individual original urls from the given folder URL.
        :param folder_url: The original folder url to generate an unrestricted url.
        :param return_unlimited_urls: Whether to return the unrestricted urls. Default is False. (This may take a while depending on the number of urls in your folder)
        :return: The unrestricted url if successful. Otherwise, return the original url.
        """

        RDW._premium_account_is_required(self)

        try: res = self._http_client.post(self._base_api_url + '/unrestrict/folder', data={'link': folder_url})
        except Exception as e: raise e

        if res.status_code != 200: raise RDW.Exception.UnsupportedHosterError('The given folder url is not supported by Real-Debrid.')
        json_data = list(res.json())

        if folder_url in json_data: json_data.remove(folder_url)
        if not json_data: raise RDW.Exception.EmptyFolderOrNotSupportedError('The given folder url is empty or not supported by Real-Debrid.')

        if return_unlimited_urls:
            def _get_unlimited_url_data_threading(_q: Queue, _url: str) -> None:
                data = self.get_unlimited_url_data(_url)
                _q.put(data['unrestrictedUrl'])

            q = Queue()
            threads = list()

            for url in json_data:
                t = Thread(target=_get_unlimited_url_data_threading, args=(q, url))
                t.start()
                threads.append(t)
                sleep(0.1)

            for t in threads:
                t.join()

            return [q.get() for _ in range(q.qsize())]

        return json_data
