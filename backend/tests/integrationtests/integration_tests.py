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

import json
import os
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
        cls.report_folder = tempfile.mkdtemp(dir='build')
        os.system('coverage{0} run --parallel-mode --branch quality_report.py --project {1} --report {2} '
                  '--log ERROR'.format(sys.version_info[0], cls.project_folder, cls.report_folder))


class AllRequirementsNoSourcesTests(IntegrationTestCase):
    """ Integration tests using a report with all requirements, but no sources defined. """
    project_folder = 'tests/integrationtests/test_all_requirements_no_sources'
    expected_number_of_metrics = 204

    def report(self):
        """ Read the report and return as beautiful soup. """
        with open('{0}/index.html'.format(self.report_folder)) as contents:
            return bs4.BeautifulSoup(contents.read(), "lxml")

    def assert_file_exists(self, filename):
        """ Assert that the specified file exists. """
        self.assertTrue(os.path.exists('{0}/{1}'.format(self.report_folder, filename)))

    def test_files_exists(self):
        """ Test that the copied/generated files exists. """
        self.assert_file_exists('index.html')
        for filename in 'metrics', 'meta_history', 'meta_data':
            self.assert_file_exists('json/{0}.json'.format(filename))

    def test_report_title(self):
        """ Test the report title. """
        title = self.report()('head')[0]('title')[0].string
        self.assertEqual('Kwaliteitsrapportage ...', title)

    def test_number_of_metrics(self):
        """ Test the number of metrics in the report. """
        with open('{0}/json/metrics.json'.format(self.report_folder)) as metrics_json:
            metrics = json.load(metrics_json)["metrics"]
        self.assertEqual(self.expected_number_of_metrics, len(metrics))


class AllRequirementsNoSourceIdsTests(AllRequirementsNoSourcesTests):
    """ Integration tests using a report with all requirements and all sources, but no source ids defined. """
    project_folder = 'tests/integrationtests/test_no_source_ids'


class AllRequirementsNoSourceIdsSecondProject(AllRequirementsNoSourceIdsTests):
    """ Integration tests using a second project definition from the same folder. """
    project_folder = AllRequirementsNoSourceIdsTests.project_folder + '/second_project_definition.py'
