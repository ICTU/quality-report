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

import datetime
import unittest
import urllib2

from qualitylib.metric_source import NCover


class FakeUrlOpener(object):  # pylint: disable=too-few-public-methods
    """ Fake the urlopener to return fixed html. """
    html = """
<script type="text/javascript">
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

    def url_open(self, url):
        """ Open a url. """
        if 'raise' in url:
            raise urllib2.HTTPError(url, None, None, None, None)
        else:
            return self.html


class NCoverTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the NCover class. """

    def setUp(self):  # pylint: disable=invalid-name
        self.__opener = FakeUrlOpener()
        self.__ncover = NCover(url_open=self.__opener.url_open)

    def test_statement_coverage(self):
        """ Test the statement coverage for a specific product. """
        self.assertAlmostEqual(77.07082, self.__ncover.statement_coverage('http://ncover'), places=4)

    def test_statement_coverage_on_error(self):
        """ Test that the reported statement coverage is -1 when NCover can't be reached. """
        self.assertEqual(-1, self.__ncover.statement_coverage('raise'))

    def test_missing_statement_coverage(self):
        """ Test that the statement coverage is -1 when it can't be found in the report. """
        self.__opener.html = ''
        self.assertEqual(-1, self.__ncover.statement_coverage('http://ncover'))

    def test_branch_coverage(self):
        """ Test the branch coverage for a specific product. """
        self.assertAlmostEqual(74.10549, self.__ncover.branch_coverage('http://ncover'), places=4)

    def test_branch_coverage_on_error(self):
        """ Test that the reported branch coverage is -1 when NCover can't be reached. """
        self.assertEqual(-1, self.__ncover.branch_coverage('raise'))

    def test_missing_branch_coverage(self):
        """ Test that the branch coverage is -1 when it can't be found in the report. """
        self.__opener.html = ''
        self.assertEqual(-1, self.__ncover.branch_coverage('http://ncover'))

    def test_coverage_date(self):
        """ Test the date of the coverage report. """
        expected = datetime.datetime(2015, 8, 24, 16, 5, 55, 42000)
        self.assertEqual(expected, self.__ncover.coverage_date('http://ncover'))

    def test_coverage_date_on_error(self):
        """ Test that the date is now when NCover can't be reached. """
        coverage_date = self.__ncover.coverage_date('raise')
        age = datetime.datetime.now() - coverage_date
        self.assertTrue(age < datetime.timedelta(seconds=1))

    def test_missing_coverage_date(self):
        """ Test that the date is now when the date is missing in the report. """
        self.__opener.html = ''
        coverage_date = self.__ncover.coverage_date('http://ncover')
        age = datetime.datetime.now() - coverage_date
        self.assertTrue(age < datetime.timedelta(seconds=1))
