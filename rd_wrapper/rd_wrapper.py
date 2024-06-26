# Official repository and documentation at https://github.com/Henrique-Coder/rd-wrapper

from datetime import datetime
from os import path
from queue import Queue
from re import search
from sqlite3 import connect as sqlite3_connect
from tempfile import gettempdir
from threading import Thread
from time import sleep
from typing import Optional, Union, List
from urllib.parse import unquote

from bs4 import BeautifulSoup
from fake_useragent import FakeUserAgent
from httpx import _exceptions as httpx_exceptions, Client, get, post
from langcodes import Language, LanguageTagError


fake_useragent = FakeUserAgent()

class RDW:
    """
    A class to interact with the Real-Debrid API.
    """

    def __init__(self, api_token: str = None, username: str = None, password: str = None, anonymous_access: bool = False) -> None:
        """
        Initialize the Real-Debrid API wrapper.
        :param api_token: Real-Debrid API token.
        :param username: Real-Debrid account username.
        :param password: Real-Debrid account password.
        :param anonymous_access: Whether to enable anonymous access mode. (Anonymous access mode does not require an API token, username, or password to send requests, only work with free endpoints)
        :raises Exceptions.MissingCredentials: If the username or password is missing.
        :raises Exceptions.InvalidCredentials: If the username or password is invalid.
        :raises Exceptions.InvalidAPIToken: If the API token is invalid.
        :raises Exceptions.NetworkError: If an error occurs while retrieving the API token.
        """

        self._base_api_url = 'https://api.real-debrid.com/rest/1.0'
        self._http_client: Optional[Client] = None
        self.cache = APIToken()

        if not anonymous_access:
            if not api_token and (not username or not password):
                raise Exceptions.MissingCredentials('Username and password are required if no API token is provided.')

            self._api_token = api_token or self._get_api_token_from_credentials(username, password)
            self._http_client = Client(headers={'Authorization': f'Bearer {self._api_token}', 'Accept': 'application/json', 'Content-Type': 'application/json'}, follow_redirects=False, timeout=10)

            try: response = self._http_client.get(self._base_api_url + '/user')
            except httpx_exceptions.HTTPError as e: raise Exceptions.NetworkError('An error occurred while trying to retrieve the user data. - Error: ' + str(e))

            if response.status_code == 200: self._raw_user_data = dict(response.json())
            else: raise Exceptions.InvalidAPIToken('Invalid Real-Debrid API token. Please provide a valid one.')

            self.is_anonymous_access = False
            self.account_email = str(self._raw_user_data.get('email'))
            self.account_type = 'Premium' if str(self._raw_user_data.get('type')).strip() == 'premium' else 'Free'
            self.is_premium_account = bool(self.account_type == 'Premium')
            self.premium_plan_expiration_timestamp = int(datetime.strptime(self._raw_user_data.get('expiration'), '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())
            self.account_fidelity_points = int(self._raw_user_data.get('points'))
            self.account_id = int(self._raw_user_data.get('id'))
            self.account_username = str(self._raw_user_data.get('username'))
            self.account_avatar_url = unquote(self._raw_user_data.get('avatar'))
            self.account_language_code = str(self._raw_user_data.get('locale'))
            try: self.account_language_name = str(Language.get(self.account_language_code).display_name('en-us'))
            except LanguageTagError: self.account_language_name = 'Unknown'
        else:
            self._http_client = Client(headers={'Accept': 'application/json', 'Content-Type': 'application/json'}, follow_redirects=False, timeout=10)
            self.is_anonymous_access = True
            self.account_email = self.account_type = self.account_username = self.account_avatar_url = self.account_language_code = self.account_language_name = None
            self.is_premium_account = False
            self.premium_plan_expiration_timestamp = self.account_fidelity_points = self.account_id = 0

    def __del__(self) -> None:
        """
        Ensure the HTTP client is closed when the object is deleted.
        """

        if self._http_client:
            self._http_client.close()

    # Hidden methods
    def _premium_account_is_required(self) -> None:
        """
        Check if the account is a premium account. If not, raise an exception.
        :raises Exceptions.NonPremiumAccount: If the account is not a premium account.
        """

        if not self.is_premium_account:
            raise Exceptions.NonPremiumAccount('Only premium users can use this function. Please upgrade your account to premium at: https://real-debrid.com/premium')

    def _is_token_valid(self, token: str) -> bool:
        """
        Check if the given token is valid.
        :param token: Real-Debrid API token.
        :return: True if the token is valid. Otherwise, return False.
        :raises Exceptions.NetworkError: If an error occurs while checking if the token is valid.
        """

        try: response = get(url=self._base_api_url + '/user', headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json', 'Content-Type': 'application/json'}, follow_redirects=False, timeout=10)
        except httpx_exceptions.HTTPError: raise Exceptions.NetworkError('An error occurred while checking if the token is valid.')

        return bool(response.status_code == 200)

    def _get_api_token_from_credentials(self, username: str, password: str) -> str:
        """
        Get the API token from the cache or generate a new one.
        :param username: Real-Debrid account username.
        :param password: Real-Debrid account password.
        :return: The API token.
        :raises Exceptions.InvalidCredentials: If the username or password is invalid.
        :raises Exceptions.NetworkError: If an error occurs while retrieving the API token.
        """

        token = self.cache._get_token(username, password)

        if token and self._is_token_valid(token):
            return token

        auth_token = APIToken.get_auth_token(username, password)
        token = APIToken.get_api_token(auth_token)
        self.cache._set_token(token, username, password)

        return token

    # Public methods (internal)
    def stop_http_session(self) -> None:
        """
        Stop the current HTTP session.
        """

        self.__del__()

    # Public methods (endpoints)
    def disable_current_api_token(self) -> None:
        """
        Disable the current API token and/or raise an exception. Please visit https://real-debrid.com/apitoken to see your new API token.
        :raises Exceptions.NetworkError: If an error occurs while disabling the current API token.
        """

        def replace_middle_with_asterisks(string: str) -> str:
            """
            Replace the middle characters of the string with asterisks. (e.g.: "123456789" -> "123****789")
            :param string: The string to replace the middle characters.
            :return: The string with the middle characters replaced with asterisks.
            """

            if len(string) <= 2: return '*' * len(string)
            elif len(string) <= 6: return string[0] + '*' * (len(string) - 2) + string[-1]

            return str(string[:3] + '*' * (len(string) - 6) + string[-3:])

        try: response = self._http_client.get(self._base_api_url + '/disable_access_token')
        except httpx_exceptions.HTTPError as e: raise Exceptions.NetworkError(f'An error occurred while trying to disable the current API token. - Error: {str(e)}')
        finally: self.stop_http_session()

        if response.status_code == 204: raise Exceptions.APITokenDisabledSuccessfully(f'Your current API token ({replace_middle_with_asterisks(self._api_token)}) has been disabled. To see your new API token, please visit: https://real-debrid.com/apitoken')
        elif response.status_code == 401: raise Exceptions.InvalidAPIToken('Invalid Real-Debrid API token. Please provide a valid one so that it can be disabled.')
        raise Exceptions.NetworkError('An error occurred while trying to disable the current API token.')

    def get_server_time(self, unix_timestamp: bool = False) -> Union[str, int]:
        """
        Fetch server time. This is useful for debugging purposes.
        :param unix_timestamp: Whether to return the raw server time in Unix timestamp format.
        :return: The server time in string or Unix timestamp format.
        :raises Exceptions.GetServerTimeError: If an error occurs while fetching the server time.
        """

        try: response = self._http_client.get(self._base_api_url + '/time')
        except httpx_exceptions.HTTPError as e: raise Exceptions.GetServerTimeError(f'An error occurred while fetching the server time. - Error: {str(e)}')

        if response.status_code == 200:
            if unix_timestamp: return int(datetime.strptime(response.text, '%Y-%m-%d %H:%M:%S').timestamp())
            else: return str(response.text)

        raise Exceptions.GetServerTimeError('An error occurred while receiving the response from the server.')

    def get_server_iso_time(self, unix_timestamp: bool = False) -> Union[str, int]:
        """
        Fetch server time in ISO format. This is useful for debugging purposes.
        :param unix_timestamp: Whether to return the raw server time in Unix timestamp format.
        :return: The server time in ISO format.
        :raises Exceptions.GetServerISOTimeError: If an error occurs while fetching the server time in ISO format.
        """

        try: response = self._http_client.get(self._base_api_url + '/time/iso')
        except httpx_exceptions.HTTPError as e: raise Exceptions.GetServerISOTimeError(f'An error occurred while fetching the server time in ISO format. - Error: {str(e)}')

        if response.status_code == 200:
            if unix_timestamp: return int(datetime.strptime(response.text, '%Y-%m-%dT%H:%M:%S%z').timestamp())
            else: return str(response.text)

        raise Exceptions.GetServerISOTimeError('An error occurred while receiving the response from the server.')

    def is_url_supported(self, url: str, password: str = None) -> bool:
        """
        Check if the given url is supported by Real-Debrid.
        :param url: The url to check
        :param password: The password to access the url.
        :return: True if the url is supported. Otherwise, return False.
        :raises Exceptions.IsURLSupportedError: If an error occurs while checking if the given url is supported by Real-Debrid.
        """

        RDW._premium_account_is_required(self)

        try: response = self._http_client.post(self._base_api_url + '/unrestrict/check', data={'link': url, 'password': password})
        except httpx_exceptions.HTTPError: raise Exceptions.IsURLSupportedError('An error occurred while checking if the given url is supported by Real-Debrid.')

        if response.status_code == 200: return True

        return False

    def get_unlimited_url_data(self, url: str, password: str = None, remote_traffic: bool = False) -> dict:
        """
        Generate an unrestricted url data from the given url.
        :param url: The original url to generate an unrestricted url.
        :param password: The password to access the url.
        :param remote_traffic: Whether to generate a remote traffic url.
        :return: The unrestricted url data.
        :raises Exceptions.GetUnlimitedURLDataError: If an error occurs while generating an unrestricted url.
        :raises Exceptions.UnsupportedHosterError: If the given url is not supported by Real-Debrid.
        :raises Exceptions.RemoteTrafficExhaustedError: If the remote traffic is exhausted.
        """

        RDW._premium_account_is_required(self)

        try: response = self._http_client.post(self._base_api_url + '/unrestrict/link', data={'link': url, 'password': password, 'remote': 1 if remote_traffic else 0})
        except httpx_exceptions.HTTPError: raise Exceptions.GetUnlimitedURLDataError('An error occurred while generating an unrestricted url.')

        if response.status_code != 200:
            if response.status_code == 503 and response.json().get('error') == 'traffic_exhausted': raise Exceptions.RemoteTrafficExhaustedError('Your account\'s remote traffic has ended. Please visit https://real-debrid.com/trafficshare to get more remote traffic.')
            else: raise Exceptions.UnsupportedHosterError('The given url is not supported by Real-Debrid.')

        json_data = dict(response.json())

        output_data = {
            'id': str(json_data.get('id')),
            'originalUrl': unquote(json_data.get('link')),
            'unrestrictedUrl': unquote(json_data.get('download')),
            'filename': str(json_data.get('filename')).strip(),
            'size': int(json_data.get('filesize')),
            'hoster': unquote(json_data.get('host')),
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
                    'filename': str(item.get('filename')).strip(),
                    'mimetype': str(item.get('mimeType')),
                    'quality': str(item.get('quality')),
                })

        return output_data

    def get_unlimited_folder_url_list(self, url: str, unrestrict_urls: bool = True) -> Union[List[str], List[dict]]:
        """
        Generate individual original (or unrestricted) urls from the given folder url.
        :param url: The original folder url to generate individual urls.
        :param unrestrict_urls: Whether to return the unrestricted urls. (This may take a while depending on the number of items in your folder)
        :return: The individual urls or unrestricted urls.
        :raises Exceptions.GetUnlimitedFolderURLListError: If an error occurs while generating individual urls from the given folder url.
        :raises Exceptions.EmptyFolderOrNotSupportedFolderURLError: If the folder is empty or not supported by Real-Debrid.
        :raises Exceptions.UnsupportedHosterError: If the given folder url is not supported by Real-Debrid.
        """

        RDW._premium_account_is_required(self)

        try: response = self._http_client.post(self._base_api_url + '/unrestrict/folder', data={'link': url})
        except httpx_exceptions.HTTPError: raise Exceptions.GetUnlimitedFolderURLListError('An error occurred while generating individual urls from the given folder url.')

        json_data = response.json()
        if url in json_data: json_data.remove(url)

        if response.status_code != 200: raise Exceptions.UnsupportedHosterError('The given folder url is not supported by Real-Debrid.')
        if not json_data: raise Exceptions.EmptyFolderOrNotSupportedFolderURLError('The folder is empty or not supported by Real-Debrid.')

        json_data = [unquote(item) for item in json_data]

        if unrestrict_urls:
            def _get_unlimited_url_data_threading(_q: Queue, _url: str) -> None:
                data = self.get_unlimited_url_data(_url)
                _q.put(data.get('unrestrictedUrl', None) if data else None)

            q = Queue()
            threads = list()

            for url in json_data:
                t = Thread(target=_get_unlimited_url_data_threading, args=(q, url))
                t.start()
                threads.append(t)
                sleep(0.1)

            for t in threads:
                t.join()

            return [unquote(q.get()) for _ in range(q.qsize())]

        return json_data

class APIToken:
    """
    A class to cache Real-Debrid API tokens using SQLite.
    """

    def __init__(self, db_filename: str = 'api-token_cache_real-debrid.com.db') -> None:
        """
        Initialize the SQLite database for caching tokens.
        :param db_filename: The filename for the SQLite database.
        """

        temp_dir = gettempdir()
        self.db_path = path.join(temp_dir, db_filename) if path.isdir(temp_dir) else db_filename
        self._initialize_db()

    def _initialize_db(self) -> None:
        """
        Initialize the SQLite database.
        """

        with sqlite3_connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS tokens (
                                username TEXT,
                                password TEXT,
                                token TEXT,
                                PRIMARY KEY (username, password))''')
            conn.commit()

    def _get_token(self, username: str, password: str) -> Optional[str]:
        """
        Get the token from the cache.
        :param username: Real-Debrid account username.
        :param password: Real-Debrid account password.
        :return: The token if it exists. Otherwise, return None.
        """

        with sqlite3_connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT token FROM tokens WHERE username=? AND password=?''', (username, password))
            result = cursor.fetchone()

            return result[0] if result else None

    def _set_token(self, token: str, username: str, password: str) -> None:
        """
        Set a new token in the cache.
        :param token: Real-Debrid API token.
        :param username: Real-Debrid account username.
        :param password: Real-Debrid account password.
        """

        with sqlite3_connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''REPLACE INTO tokens (username, password, token) VALUES (?, ?, ?)''', (username, password, token))
            conn.commit()

    def _clear_cache(self, username: str, password: str) -> None:
        """
        Clear the token cache for the given username and password.
        :param username: Real-Debrid account username.
        :param password: Real-Debrid account password.
        """

        with sqlite3_connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''DELETE FROM tokens WHERE username=? AND password=?''', (username, password))
            conn.commit()

    @staticmethod
    def get_auth_token(username: str, password: str) -> str:
        """
        Obtain an authentication token using the provided username and password.
        :param username: Real-Debrid account username.
        :param password: Real-Debrid account password.
        :return: The authentication token.
        :raises Exceptions.InvalidCredentials: If the username or password is invalid.
        """

        params = {'user': username, 'pass': password, 'pin_challenge': '', 'pin_answer': 'PIN: 000000', 'time': datetime.now().timestamp()}
        headers = {'User-Agent': fake_useragent.random, 'X-Requested-With': 'XMLHttpRequest'}
        response = get('https://real-debrid.com/ajax/login.php', params=params, headers=headers, timeout=10)

        if response.status_code != 200 or response.json().get('error') != 0:
            raise Exceptions.InvalidCredentials('Invalid Real-Debrid account username or password.')

        return response.json()['cookie'].replace('auth=', str()).replace(';', str()).strip()

    @staticmethod
    def get_api_token(auth_token: str) -> str:
        """
        Retrieve the current API token using the provided authentication token.
        :param auth_token: The authentication token.
        :return: Current API token.
        :raises Exceptions.NetworkError: If an error occurs while generating the API token.
        """

        headers = {'User-Agent': fake_useragent.random}
        cookies = {'auth': auth_token}
        response = get('https://real-debrid.com/apitoken', headers=headers, cookies=cookies, timeout=10)

        if response.status_code != 200 or not response.text.strip():
            raise Exceptions.NetworkError('An error occurred while trying to generate the API token.')

        soup = BeautifulSoup(response.text, 'html.parser')
        script_tag = soup.find('script', string=lambda text: text and 'document.querySelectorAll' in text)
        token_value = search(r'value\s*=\s*\'([^\']+)\'', script_tag.string).group(1)

        return token_value

    @staticmethod
    def generate_new_api_token(auth_token: str) -> str:
        """
        Generate a new API token using the provided authentication token.
        :param auth_token: The authentication token.
        :return: New API token.
        :raises Exceptions.NetworkError: If an error occurs while refreshing the API token.
        """

        headers = {'User-Agent': fake_useragent.random}
        data = {'refresh': '1'}
        cookies = {'auth': auth_token}
        response = post('https://real-debrid.com/apitoken', headers=headers, data=data, cookies=cookies, timeout=10)

        if response.status_code != 200 or not response.text.strip():
            raise Exceptions.NetworkError('An error occurred while trying to refresh the API token.')

        soup = BeautifulSoup(response.text, 'html.parser')
        script_tag = soup.find('script', string=lambda text: text and 'document.querySelectorAll' in text)
        token_value = search(r'value\s*=\s*\'([^\']+)\'', script_tag.string).group(1)

        return token_value

class Exceptions:
    class InvalidAPIToken(Exception): pass
    class MissingCredentials(Exception): pass
    class InvalidCredentials(Exception): pass
    class NetworkError(Exception): pass
    class NonPremiumAccount(Exception): pass
    class APITokenDisabledSuccessfully(Exception): pass
    class GetServerTimeError(Exception): pass
    class GetServerISOTimeError(Exception): pass
    class GetUnlimitedURLDataError(Exception): pass
    class GetUnlimitedFolderURLListError(Exception): pass
    class EmptyFolderOrNotSupportedFolderURLError(Exception): pass
    class IsURLSupportedError(Exception): pass
    class RemoteTrafficExhaustedError(Exception): pass
    class UnsupportedHosterError(Exception): pass
