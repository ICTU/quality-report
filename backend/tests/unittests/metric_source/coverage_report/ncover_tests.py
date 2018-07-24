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

from hqlib.metric_source import NCover, url_opener

HTML = """ <script type="text/javascript">
     Other javascript
    </script>
    <script type="text/javascript">
      ncover.execution.stats = {
        "sequencePointCoverage": {
          "coveragePercent": 0.7707082833133253
        },
        "branchCoverage": {
            "coveragePercent": 0.74105490438001242
        }
      };
    </script>
    <script type="text/javascript">
        ncover.serverRoot = 'http://127.0.0.1:11235';
        ncover.createDateTime = '1440425155042';
    </script>"""


@patch.object(url_opener.UrlOpener, 'url_read')
class NCoverTest(unittest.TestCase):
    """ Unit tests for the NCover class. """

    def setUp(self):
        NCover._HTMLCoverageReport__get_soup.cache_clear()
        NCover.datetime.cache_clear()
        self.__ncover = NCover()

    def test_statement_coverage(self, mock_url_read):
        """ Test the statement coverage for a specific product. """
        mock_url_read.return_value = HTML
        self.assertAlmostEqual(77.07082, self.__ncover.statement_coverage('http://ncover'), places=4)

    def test_statement_coverage_onerror(self, mock_url_read):
        """ Test that the reported statement coverage is -1 when NCover can't be reached. """
        mock_url_read.side_effect = urllib.error.HTTPError('', None, None, None, None)
        self.assertEqual(-1, self.__ncover.statement_coverage('raise'))

    def test_missing_statement_coverage(self, mock_url_read):
        """ Test that the statement coverage is -1 when it can't be found in the report. """
        mock_url_read.return_value = ''
        self.assertEqual(-1, self.__ncover.statement_coverage('http://ncover'))

    def test_branch_coverage(self, mock_url_read):
        """ Test the branch coverage for a specific product. """
        mock_url_read.return_value = HTML
        self.assertAlmostEqual(74.10549, self.__ncover.branch_coverage('http://ncover'), places=4)

    def test_branch_coverage_on_error(self, mock_url_read):
        """ Test that the reported branch coverage is -1 when NCover can't be reached. """
        mock_url_read.side_effect = urllib.error.HTTPError('', None, None, None, None)
        self.assertEqual(-1, self.__ncover.branch_coverage('raise'))

    def test_missing_branch_coverage(self, mock_url_read):
        """ Test that the branch coverage is -1 when it can't be found in the report. """
        mock_url_read.return_value = ''
        self.assertEqual(-1, self.__ncover.branch_coverage('http://ncover'))

    def test_coverage_date(self, mock_url_read):
        """ Test the date of the coverage report. """
        mock_url_read.return_value = HTML
        expected = datetime.datetime.fromtimestamp(1440425155042 / 1000.)
        self.assertEqual(expected, self.__ncover.datetime('http://ncover'))

    def test_coverage_date_on_error(self, mock_url_read):
        """ Test that the date is now when NCover can't be reached. """
        mock_url_read.side_effect = urllib.error.HTTPError('', None, None, None, None)
        self.assertEqual(datetime.datetime.min, self.__ncover.datetime('raise'))

    def test_missing_coverage_date(self, mock_url_read):
        """ Test that the date is now when the date is missing in the report. """
        mock_url_read.return_value = ''
        coverage_date = self.__ncover.datetime('http://ncover')
        age = datetime.datetime.now() - coverage_date
        self.assertTrue(age < datetime.timedelta(seconds=1))
