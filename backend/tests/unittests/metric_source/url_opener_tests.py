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

import logging
import unittest
import unittest.mock
import urllib.request
import urllib.error
import io
import sys

from hqlib.metric_source import url_opener


class UrlOpenerTest(unittest.TestCase):
    """ Unit tests for the URL opener class. """

    def setUp(self):
        url_opener.TimeoutTracker.timed_out_netlocs = set()

    def test_username_password(self):
        """ Test that the username and password can be set. """
        opener = url_opener.UrlOpener(username='user', password='pass')
        self.assertEqual('user', opener.username())
        self.assertEqual('pass', opener.password())

    def test_opener_with_password_mgr(self):
        """ Test that the opener can create a basic auth handler with password manager. """
        urlopener = unittest.mock.MagicMock()
        urlopener.open = unittest.mock.MagicMock(return_value='url contents')
        urllib.request.build_opener = unittest.mock.MagicMock(return_value=urlopener)
        opener = url_opener.UrlOpener('http://uri', username='user', password='pass')
        self.assertEqual('url contents', opener.url_open('url'))

    def test_basic_auth_handler(self):
        """ Test that the opener can create a basic auth handler.  """
        urllib.request._opener = unittest.mock.Mock()
        urllib.request._opener.open = unittest.mock.Mock(return_value='url contents')
        opener = url_opener.UrlOpener(username='user', password='pass')
        self.assertEqual('url contents', opener.url_open('http://bla'))

    def test_opener_without_auth(self):
        """ Test that the opener can open urls without authentication. """
        opener = url_opener.UrlOpener()
        opener._UrlOpener__opener = unittest.mock.Mock(return_value='url contents')
        self.assertEqual('url contents', opener.url_open('http://bla'))

    def test_exception_while_opening(self):
        """ Test an exception during opening. """
        logging.warning = unittest.mock.MagicMock()
        opener = url_opener.UrlOpener()
        opener._UrlOpener__opener = unittest.mock.Mock(side_effect=urllib.error.HTTPError(None, None, None, None, None))
        self.assertRaises(urllib.error.HTTPError, opener.url_open, 'http://bla')
        logging.warning.assert_called_once()

    def test_exception_while_opening_without_logging(self):
        """ Test an exception during opening without logging. """
        logging.error = unittest.mock.MagicMock()
        logging.warning = unittest.mock.MagicMock()
        opener = url_opener.UrlOpener()
        opener._UrlOpener__opener = unittest.mock.Mock(side_effect=urllib.error.HTTPError(None, None, None, None, None))
        self.assertRaises(urllib.error.HTTPError, opener.url_open, 'http://bla', log_error=False)
        logging.error.assert_not_called()
        logging.warning.assert_not_called()

    @unittest.mock.patch('signal.signal', side_effect=lambda _, handler: handler())
    def test_timeout(self, mock_signal):  # pylint: disable=unused-argument
        """ Test the timeout exception. """
        self.assertRaises(TimeoutError, url_opener.UrlOpener().url_open, 'http://bla')

    @unittest.mock.patch('signal.signal', side_effect=lambda _, handler: handler())
    def test_multiple_timeouts(self, mock_signal):  # pylint: disable=unused-argument
        """ Test that a timed out host isn't contacted again. """
        opener = url_opener.UrlOpener()
        self.assertRaises(TimeoutError, opener.url_open, 'http://bla:9000/url1')
        try:
            opener.url_open('http://bla:9000/url2')
            self.fail("Expected TimeoutError")  # pragma: no cover
        except TimeoutError as reason:
            self.assertEqual('Skipped because bla:9000 timed out before.', str(reason))

    def test_url_read(self):
        """ Test reading an url. """
        opener = url_opener.UrlOpener()
        opener._UrlOpener__opener = unittest.mock.Mock(return_value=io.StringIO('contents'))
        self.assertEqual('contents', opener.url_read('http://bla'))


class TimeoutTest(unittest.TestCase):
    """ Unit tests for the Timeout class. """

    @unittest.skipIf(sys.platform.startswith("win"), "Timeout only works on Posix platforms.")
    @unittest.mock.patch('signal.signal', side_effect=lambda _, handler: handler())  # Throw time out immediately
    def test_with(self, mock_signal):  # pylint: disable=unused-argument
        """ Test the with statement. """
        try:
            with url_opener.Timeout(4):
                self.fail("Expected TimeoutError")  # pragma: no cover
        except TimeoutError as reason:
            self.assertEqual("Operation timed out after 4 seconds.", str(reason))


class TimeoutTrackerTest(unittest.TestCase):
    """ Unit tests for the TimeoutTracker class. """
    def setUp(self):
        url_opener.TimeoutTracker.timed_out_netlocs = set()
        self.__time_out_tracker = url_opener.TimeoutTracker()
        self.__url = "http://timed.out/path"

    def test_registered_url_raises_timeout(self):
        """ Test that a url that is registered triggers a time out exception. """
        self.__time_out_tracker.register_url(self.__url)
        self.assertRaises(TimeoutError, self.__time_out_tracker.raise_timeout_if_url_timed_out_before, self.__url)

    def test_unregistered_url_does_not_raise_timeout(self):
        """ Test that a url that hasn't been registered before does not trigger a time out exception. """
        try:
            self.__time_out_tracker.raise_timeout_if_url_timed_out_before(self.__url)
        except TimeoutError:  # pragma: no cover
            self.fail("No Timeout exception should have been raised.")
