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
import tempfile
import bs4


class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Create the report. """
        cls.report_folder = tempfile.mkdtemp()
        os.system('python python/quality_report.py --project python/integrationtests/test_all_requirements_no_sources '
                  '--report {} --log ERROR'.format(cls.report_folder))

    def test_report_exists(self):
        """ Test that the report exists. """
        self.failUnless(os.path.exists('{}/index.html'.format(self.report_folder)))

    def test_report_title(self):
        """ Test the report title. """
        with open('{}/index.html'.format(self.report_folder)) as contents:
            soup = bs4.BeautifulSoup(contents.read(), "html.parser")
            self.assertEqual('Kwaliteitsrapportage ICTU/Quality report with all requirements but no sources',
                             soup('head')[0]('title')[0].string)
