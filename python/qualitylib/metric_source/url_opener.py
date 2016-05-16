"""
Copyright 2012-2016 Ministerie van Sociale Zaken en Werkgelegenheid

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
from __future__ import absolute_import

import base64
import logging
import socket
import urllib2


class UrlOpener(object):
    """ Class for opening urls with or without authentication. """

    def __init__(self, uri=None, username=None, password=None,
                 build_opener=urllib2.build_opener, url_open=urllib2.urlopen):
        self.__username = username
        self.__password = password
        self.__opener = self.__create_url_opener(uri, build_opener, url_open)

    def username(self):
        """ Return the username, if any. """
        return self.__username

    def password(self):
        """ Return the password, if any. """
        return self.__password

    def __create_url_opener(self, uri, build_opener, url_open):
        """ Return a url opener method. If credentials are supplied, create an opener with authentication handler. """
        if uri and self.__username and self.__password:
            password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
            password_manager.add_password(realm=None, uri=uri, user=self.__username, passwd=self.__password)
            auth_handler = urllib2.HTTPBasicAuthHandler(password_manager)
            return build_opener(auth_handler).open
        elif self.__username and self.__password:
            credentials = base64.encodestring(':'.join([self.__username, self.__password]))[:-1]

            def url_open_with_basic_auth(url):
                """ Open the url with basic authentication. """
                if isinstance(url, urllib2.Request):
                    request = url
                else:
                    request = urllib2.Request(url)
                request.add_header('Authorization', 'Basic ' + credentials)
                return url_open(request)

            return url_open_with_basic_auth
        else:
            return url_open

    def url_open(self, url):
        """ Return an opened url, using the opener created earlier. """
        try:
            return self.__opener(url)
        except (urllib2.HTTPError, urllib2.URLError, socket.error) as reason:
            logging.warning("Couldn't open %s: %s", url, reason)
            raise  # Let caller decide whether to ignore the exception

    def url_delete(self, url):
        """ Delete the given url. """
        request = urllib2.Request(url)
        request.get_method = lambda: 'DELETE'  # pragma: no branch
        return self.__opener(request)
