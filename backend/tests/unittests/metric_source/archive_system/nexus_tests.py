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

import datetime
import unittest
from unittest.mock import patch
import urllib.error

from hqlib.metric_source import Nexus, url_opener


@patch.object(url_opener.UrlOpener, '__init__')
class NexusConstructorTests(unittest.TestCase):
    """ Unit tests of the constructor of the Nexus class. """

    def test_url_opener_constructor(self, init_mock):
        """" Test that by Nexus initialisation, UrlOpener is initialised with user name and password as parameters. """
        init_mock.return_value = None

        self._nexus = Nexus(username='Nexus_username', password='Nexus_wchtwd')

        init_mock.assert_called_with(username='Nexus_username', password='Nexus_wchtwd')


@patch.object(url_opener.UrlOpener, 'url_read')
class NexusTestCase(unittest.TestCase):
    """ Unit tests for the Nexus metric source. """

    def test_last_changed_date(self, mock_url_read):
        """ Test that Nexus returns the last changed date of an artifact. """
        mock_url_read.return_value = '''
        <content>
            <data>
                <content-item>
                    <lastModified>2016-07-04 15:20:35.0 UTC</lastModified>
                </content-item>
                <content-item>
                    <lastModified>2016-06-03 10:30:22.0 UTC</lastModified>
                </content-item>
            </data>
        </content>'''
        nexus = Nexus(username='', password='')
        path = 'http://does/not/matter'
        self.assertEqual(datetime.datetime(2016, 7, 4, 15, 20, 35), nexus.last_changed_date(path))

    def test_exception(self, mock_url_read):
        """ Test that the last changed date is the minumum date when an exception occurs. """
        mock_url_read.side_effect = [urllib.error.HTTPError(None, None, None, None, None)]
        nexus = Nexus(username='', password='')
        path = 'http://does/not/matter'
        self.assertEqual(datetime.datetime.min, nexus.last_changed_date(path))
