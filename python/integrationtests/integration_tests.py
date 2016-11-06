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

import unittest
import os
import shutil
import tempfile
import bs4


class IntegrationTestCase(unittest.TestCase):
    """ Base class for integration test cases that examine a generated report. """
    project_folder = 'Subclass responsibility'

    @classmethod
    def setUpClass(cls):
        """ Create the report. """
        cls.report_folder = tempfile.mkdtemp()
        os.system('coverage run --parallel-mode --branch python/quality_report.py --project {0} --report {1} '
                  '--log ERROR'.format(cls.project_folder, cls.report_folder))

    @classmethod
    def tearDownClass(cls):
        """ Remove the report. """
        shutil.rmtree(cls.report_folder)


class AllRequirementsNoSourcesTests(IntegrationTestCase):
    """ Integration tests using a report with all requirements, but no sources defined. """
    project_folder = 'python/integrationtests/test_all_requirements_no_sources'
    expected_title = 'all requirements but no sources'

    def test_report_exists(self):
        """ Test that the report exists. """
        self.failUnless(os.path.exists('{}/index.html'.format(self.report_folder)))

    def test_report_title(self):
        """ Test the report title. """
        with open('{}/index.html'.format(self.report_folder)) as contents:
            soup = bs4.BeautifulSoup(contents.read(), "html.parser")
            self.assertEqual('Kwaliteitsrapportage Integrationtest/{}'.format(self.expected_title),
                             soup('head')[0]('title')[0].string)


class AllRequirementsNoSourceIdsTests(AllRequirementsNoSourcesTests):
    """ Integration tests using a report with all requirements and all sources, but no source ids defined. """
    project_folder = 'python/integrationtests/test_no_source_ids'
    expected_title = 'all requirements and sources, but no source ids'
