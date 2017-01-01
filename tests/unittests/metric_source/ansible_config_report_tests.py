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

from hqlib.metric_source import AnsibleConfigReport


class FakeUrlOpener(object):  # pylint: disable=too-few-public-methods
    """ Fake the url opener class to return a fixed json object. """

    json = u"""
[
  {
    "na-bd-dev.lrk.org": {
      "appserver version": "Sun GlassFish Enterprise Server v2.1.1 Patch24",
      "java version": "1.7.0_79",
      "timestamp": "2015-10-06T15:00:01Z"
    }
  },
  {
    "na-bd-test1.lrk.org": {
      "appserver version": "Sun GlassFish Enterprise Server v2.1.1 Patch23",
      "java version": "1.7.0_79",
      "timestamp": "2015-10-06T15:00:05Z"
    }
  },
  {
    "na-lrk-dev.lrk.org": {
      "appserver version": "Sun GlassFish Enterprise Server v2.1.1 Patch22",
      "java version": "1.7.0_79",
      "timestamp": "2015-10-06T15:00:08Z"
    }
  },
  {
    "oa-bd-test1.lrk.org": {
      "appserver version": "Sun GlassFish Enterprise Server v2.1.1 Patch22",
      "java version": "1.7.0_67",
      "timestamp": "2015-10-06T15:00:02Z"
    }
  }
]"""

    def url_open(self, url):
        """ Fake opening a url, or failing in different ways. """
        if 'raise' in url:
            raise urllib2.HTTPError(url, None, None, None, None)
        else:
            return io.StringIO(u"invalid.json" if 'invalid' in url else self.json)


class AnsibleConfigReportTest(unittest.TestCase):
    """ Unit tests for the Ansible config report class. """

    def setUp(self):
        self.__config = AnsibleConfigReport(url_open=FakeUrlOpener().url_open)

    def test_java_versions(self):
        """ Test the java versions. """
        self.assertEqual(2, self.__config.java_versions('http://ansible_report'))

    def test_java_versions_on_error(self):
        """ Test that the amount of java versions is -1 on failure. """
        self.assertEqual(-1, self.__config.java_versions('raise'))

    def test_app_server_versions(self):
        """ Test the app server versions. """
        self.assertEqual(3, self.__config.app_server_versions('http://ansible_report'))

    def test_app_server_versions_on_error(self):
        """ Test that the amount of app server versions is -1 on failure. """
        self.assertEqual(-1, self.__config.app_server_versions('raise'))

    def test_date(self):
        """ Test that the date of the report is the oldest timestamp in the json. """
        self.assertEqual(datetime.datetime(2015, 10, 6, 15, 0, 1),
                         self.__config.date('http://ansible_report'))

    def test_date_on_error(self):
        """ Test that the date of the report is the minimal date on error. """
        self.assertEqual(datetime.datetime.min, self.__config.date('raise'))

    def test_date_on_invalid_json(self):
        """ Test that the date of the report is the minimal date on invalid json. """
        self.assertEqual(datetime.datetime.min, self.__config.date('invalid'))
