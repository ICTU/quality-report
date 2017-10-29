"""
Copyright 2012-2017 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import base64
import functools
import http.client
import logging
import signal
import socket
import urllib.error
import urllib.request
import sys
from typing import cast, Callable, IO
import types


class Timeout(object):
    """ Time out class using the alarm signal. """
    def __init__(self, duration_in_seconds: int, signal: types.ModuleType=signal) -> None:
        self.__duration = duration_in_seconds
        self.__signal_module = signal

    def __enter__(self) -> None:
        if not sys.platform.startswith("win"):
            self.__signal_module.signal(self.__signal_module.SIGALRM, self.__raise_timeout)
            self.__signal_module.alarm(self.__duration)

    def __exit__(self, *args) -> None:
        if not sys.platform.startswith("win"):
            self.__signal_module.alarm(0)  # Disable the alarm

    def __raise_timeout(self, *args) -> None:
        """ Raise the TimeoutError exception. """
        raise TimeoutError("Operation timed out after {0} seconds.".format(self.__duration))


class UrlOpener(object):
    """ Class for opening urls with or without authentication. """

    url_open_exceptions = (urllib.error.HTTPError, urllib.error.URLError, socket.error, socket.gaierror,
                           http.client.BadStatusLine, TimeoutError)

    def __init__(self, uri: str=None, username: str=None, password: str=None,
                 build_opener=urllib.request.build_opener, url_open=urllib.request.urlopen) -> None:
        self.__username = username
        self.__password = password
        self.__opener = self.__create_url_opener(uri, build_opener, url_open)

    def username(self) -> str:
        """ Return the username, if any. """
        return self.__username

    def password(self) -> str:
        """ Return the password, if any. """
        return self.__password

    def __create_url_opener(self, uri: str, build_opener, url_open) -> Callable[[str], IO]:
        """ Return a url opener method. If credentials are supplied, create an opener with authentication handler. """
        if uri and self.__username and self.__password:
            password_manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            password_manager.add_password(realm=None, uri=uri, user=self.__username, passwd=self.__password)
            auth_handler = urllib.request.HTTPBasicAuthHandler(cast(urllib.request.HTTPPasswordMgr, password_manager))
            return build_opener(auth_handler).open
        elif self.__username and self.__password:
            credentials = base64.b64encode(bytes(':'.join([self.__username, self.__password]), 'utf-8')).decode('ascii')

            def url_open_with_basic_auth(url: str):
                """ Open the url with basic authentication. """
                request = urllib.request.Request(url)
                request.add_header('Authorization', 'Basic ' + credentials)
                return url_open(request)

            return url_open_with_basic_auth
        else:
            return url_open

    def url_open(self, url: str) -> IO:
        """ Return an opened url, using the opener created earlier. """
        try:
            with Timeout(15):
                return self.__opener(url)
        except self.url_open_exceptions as reason:
            logging.warning("Couldn't open %s: %s", url, reason)
            raise  # Let caller decide whether to ignore the exception

    @functools.lru_cache(maxsize=4096)
    def url_read(self, url: str, encoding: str='utf-8') -> str:
        """ Open and read a url, and transform the bytes to a string. """
        data = self.url_open(url).read()
        return data.decode(encoding) if isinstance(data, bytes) else data
