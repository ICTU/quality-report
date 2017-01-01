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

import os
import re
import shutil
import sys
import tempfile
import unittest

import bs4


class IntegrationTestCase(unittest.TestCase):
    """ Base class for integration test cases that examine a generated report. """
    project_folder = 'Subclass responsibility'

    @classmethod
    def setUpClass(cls):
        """ Create the report. """
        cls.report_folder = tempfile.mkdtemp()
        os.system('coverage{0} run --parallel-mode --branch quality_report.py --project {1} --report {2} '
                  '--log ERROR'.format(sys.version_info[0], cls.project_folder, cls.report_folder))

    @classmethod
    def tearDownClass(cls):
        """ Remove the report. """
        shutil.rmtree(cls.report_folder)


class AllRequirementsNoSourcesTests(IntegrationTestCase):
    """ Integration tests using a report with all requirements, but no sources defined. """
    project_folder = 'tests/integrationtests/test_all_requirements_no_sources'
    expected_title = 'all requirements but no sources'
    expected_number_of_metrics = 133

    def report(self):
        """ Read the report and return as beautiful soup. """
        with open('{}/index.html'.format(self.report_folder)) as contents:
            return bs4.BeautifulSoup(contents.read(), "html.parser")

    def test_report_exists(self):
        """ Test that the report exists. """
        self.assertTrue(os.path.exists('{}/index.html'.format(self.report_folder)))

    def test_report_title(self):
        """ Test the report title. """
        title = self.report()('head')[0]('title')[0].string
        self.assertEqual('Kwaliteitsrapportage Integrationtest/{}'.format(self.expected_title), title)

    def test_number_of_metrics(self):
        """ Test the number of metrics in the report. """
        metrics_js = self.report()('script')[-1].string
        match = re.search(r'\(\d+ van de (\d+)\)', metrics_js)
        self.assertEqual(self.expected_number_of_metrics, int(match.group(1)))


class AllRequirementsNoSourceIdsTests(AllRequirementsNoSourcesTests):
    """ Integration tests using a report with all requirements and all sources, but no source ids defined. """
    project_folder = 'tests/integrationtests/test_no_source_ids'
    expected_title = 'all requirements and sources, but no source ids'
