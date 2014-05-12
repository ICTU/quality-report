'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from qualitylib.metric_source import url_opener
import unittest


class FakeBuildOpener(object):  # pylint: disable=too-few-public-methods
    ''' Fake a url opener build method. '''
    def __init__(self, *args):
        pass

    @staticmethod  # pylint: disable=unused-argument
    def open(*args):
        ''' Fake opening a url and returning its contents. '''
        return 'url contents'


class UrlOpenerTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the URL opener class. '''

    def test_username_password(self):
        ''' Test that the username and password can be set. '''
        opener = url_opener.UrlOpener(username='user', password='pass')
        self.assertEqual('user', opener.username())
        self.assertEqual('pass', opener.password())

    def test_opener_with_password_mgr(self):
        ''' Test that the opener can create a basic auth handler with password
            manager. '''
        opener = url_opener.UrlOpener('http://uri', username='user',
                                      password='pass',
                                      build_opener=FakeBuildOpener)
        self.assertEqual('url contents', opener.url_open('http://bla'))

    def test_basic_auth_handler(self):
        ''' Test that the opener can create a basic auth handler. '''
        opener = url_opener.UrlOpener(username='user', password='pass', 
                                      url_open=FakeBuildOpener.open)
        self.assertEqual('url contents', opener.url_open('http://bla'))

    def test_opener_without_auth(self):
        ''' Test that the opener can open urls without authentication. '''
        opener = url_opener.UrlOpener(url_open=FakeBuildOpener.open)
        self.assertEqual('url contents', opener.url_open('http://bla'))

    def test_delete(self):
        ''' Test that a url can be deleted. '''
        opener = url_opener.UrlOpener(url_open=FakeBuildOpener.open)
        self.assertEqual('url contents', opener.url_delete('http://bla'))
