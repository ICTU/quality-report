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

import datetime
import io
import unittest
import urllib2

from hqlib.metric_source import Nexus


class FakeUrlOpener(object):  # pylint: disable=too-few-public-methods
    """ Fake URL opener. """
    contents = u'''<content>
  <data>
    <content-item>
      <lastModified>2016-07-04 15:20:35.0 UTC</lastModified>
    </content-item>
    <content-item>
      <lastModified>2016-06-03 10:30:22.0 UTC</lastModified>
    </content-item>
  </data>
</content>'''

    def url_open(self, url):
        """ Return the html or raise an exception. """
        if 'raise' in url:
            raise urllib2.HTTPError(None, None, None, None, None)
        else:
            return io.StringIO(self.contents)


class NexusTestCase(unittest.TestCase):
    """ Unit tests for the Nexus metric source. """
    def setUp(self):
        self.__nexus = Nexus(url_open=FakeUrlOpener().url_open)

    def test_last_changed_date(self):
        """ Test that Nexus returns the last changed date of an artifact. """
        self.assertEqual(datetime.datetime(2016, 7, 4, 15, 20, 35), self.__nexus.last_changed_date('http://url'))

    def test_exception(self):
        """ Test that the last changed date is the minumum date when an exception occurs. """
        self.assertEqual(datetime.datetime.min, self.__nexus.last_changed_date('raise'))
