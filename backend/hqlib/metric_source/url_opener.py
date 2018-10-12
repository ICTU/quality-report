"""
Copyright 2012-2018 Ministerie van Sociale Zaken en Werkgelegenheid

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
import urllib.parse
import urllib.request
import sys
from typing import cast, Callable, IO, Set


class Timeout(object):
    """ Time out class using the alarm signal. """
    def __init__(self, duration_in_seconds: int) -> None:
        self.__duration = duration_in_seconds

    def __enter__(self) -> None:
        if not sys.platform.startswith("win"):
            signal.signal(signal.SIGALRM, self.__raise_timeout)
            signal.alarm(self.__duration)

    def __exit__(self, *args) -> None:
        if not sys.platform.startswith("win"):
            signal.alarm(0)  # Disable the alarm

    def __raise_timeout(self, *args) -> None:  # pylint: disable=unused-argument
        """ Raise the TimeoutError exception. """
        raise TimeoutError("Operation timed out after {0} seconds.".format(self.__duration))


class TimeoutTracker(object):
    """ Class to keep track of urls that have timed out. """

    timed_out_netlocs: Set[str] = set()  # Keep track of the network locations (host/port) that have timed out

    def raise_timeout_if_url_timed_out_before(self, url) -> None:
        """ Raise a time out error if the netloc of the url has timed out before. """
        netloc = self.__netloc(url)
        if netloc in self.timed_out_netlocs:
            reason = "Skipped because {0} timed out before.".format(netloc)
            logging.warning("Not opening %s: %s", url, reason)
            raise TimeoutError(reason)

    def register_url(self, url) -> None:
        """ Register the url as timed out. """
        self.timed_out_netlocs.add(self.__netloc(url))

    @staticmethod
    def __netloc(url) -> str:
        """ Return the netloc for the url. """
        return urllib.parse.urlparse(url).netloc


class UrlOpener(object):
    """ Class for opening urls with or without authentication. """

    url_open_exceptions = (urllib.error.HTTPError, urllib.error.URLError, socket.error, socket.gaierror,
                           http.client.BadStatusLine, TimeoutError)

    def __init__(self, uri: str = None,
                 username: str = None, password: str = None, authorization_token: str = None) -> None:
        self.__username = username
        self.__password = password
        self.__basic_auth_credentials = \
            base64.b64encode(bytes(':'.join([username, password]), 'utf-8')).decode('ascii')\
            if username or password else ''
        self.__bearer_token = authorization_token
        self.__opener = self.__create_url_opener(uri)
        self.__time_out_tracker = TimeoutTracker()

    def __url_open_with_basic_auth(self, url: str, data: object = None):
        """ Open the url with basic authentication. """
        request = urllib.request.Request(url)
        request.add_header('Authorization', 'Basic ' + self.__basic_auth_credentials)
        return urllib.request.urlopen(request, data)

    def __url_open_with_token_auth(self, url: str, data: object = None):
        """ Open the url with bearer token authentication. """
        request = urllib.request.Request(url)
        request.add_header('Authorization', 'Bearer ' + self.__bearer_token)
        return urllib.request.urlopen(request, data)

    def __create_url_opener(self, uri: str) -> Callable[[str, object], IO]:
        """ Return a url opener method. If credentials are supplied, create an opener with authentication handler. """
        if uri and self.__username:
            password_manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            password_manager.add_password(realm=None, uri=uri, user=self.__username, passwd=self.__password)
            auth_handler = urllib.request.HTTPBasicAuthHandler(cast(urllib.request.HTTPPasswordMgr, password_manager))
            return urllib.request.build_opener(auth_handler).open
        elif (self.__username or self.__password):
            return self.__url_open_with_basic_auth
        elif self.__bearer_token:
            return self.__url_open_with_token_auth

        return urllib.request.urlopen

    def url_open(self, url: str, log_error: bool = True, post_body: object = None) -> IO:
        """ Return an opened url, using the opener created earlier. """
        self.__time_out_tracker.raise_timeout_if_url_timed_out_before(url)
        try:
            with Timeout(15):
                return self.__opener(url, post_body)
        except self.url_open_exceptions as reason:
            if "Operation timed out after" in str(reason):
                self.__time_out_tracker.register_url(url)
            if log_error:
                logging.warning("Couldn't open %s: %s", url, reason)
            raise  # Let caller decide whether to ignore the exception

    @functools.lru_cache(maxsize=4096)
    def url_read(self, url: str, *args, encoding: str = 'utf-8', **kwargs) -> str:
        """ Open and read a url, and transform the bytes to a string. """
        data = self.url_open(url, *args, **kwargs).read()
        return data.decode(encoding) if isinstance(data, bytes) else data
