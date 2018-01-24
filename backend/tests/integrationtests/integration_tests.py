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

import json
import os
import sys
import tempfile
import unittest

import bs4

from hqlib import domain, requirement


def requirement_metric_classes(*requirements):
    """ Return the metric classes of the requirements. """
    metrics = []
    for req in requirements:
        metrics.extend(req.metric_classes())
    return metrics


def metric_classes(domain_classes):
    """ Return the metric classes for the domain objects. """
    metrics = []
    for domain_class in domain_classes:
        metrics.extend(requirement_metric_classes(*(domain_class.default_requirements() +
                                                    domain_class.optional_requirements())))
    return metrics


class IntegrationTestCase(unittest.TestCase):
    """ Base class for integration test cases that examine a generated report. """
    project_folder = 'Subclass responsibility'

    @classmethod
    def setUpClass(cls):
        """ Create the report and read it. """
        cls.report_folder = tempfile.mkdtemp(dir='build')
        os.system('coverage{0} run --parallel-mode --branch quality_report.py --project {1} --report {2} '
                  '--log ERROR'.format(sys.version_info[0], cls.project_folder, cls.report_folder))
        with open('{0}/json/metrics.json'.format(cls.report_folder)) as metrics_json:
            cls.metrics = json.load(metrics_json)["metrics"]


class AllRequirementsNoSourcesTests(IntegrationTestCase):
    """ Integration tests using a report with all requirements, but no sources defined. """
    project_folder = 'tests/integrationtests/test_all_requirements_no_sources'
    nr_metrics = len(metric_classes([domain.Project, domain.Process, domain.Product, domain.Application,
                                     domain.Component, domain.Environment, domain.Document, domain.Team]))
    nr_meta_metrics = 5
    nr_art_metrics = len(requirement_metric_classes(requirement.CodeQuality, requirement.TrackBranches))
    expected_number_of_metrics = nr_metrics + nr_art_metrics + nr_meta_metrics

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
        self.assertEqual(self.expected_number_of_metrics, len(self.metrics))


class AllRequirementsNoSourceIdsTests(AllRequirementsNoSourcesTests):
    """ Integration tests using a report with all requirements and all sources, but no source ids defined. """
    project_folder = 'tests/integrationtests/test_no_source_ids'


class AllRequirementsNoSourceIdsSecondProject(AllRequirementsNoSourceIdsTests):
    """ Integration tests using a second project definition from the same folder. """
    project_folder = AllRequirementsNoSourceIdsTests.project_folder + '/second_project_definition.py'


class MetricOptionsTests(IntegrationTestCase):
    """ Integration tests for metric options. """
    project_folder = 'tests/integrationtests/test_metric_options'

    def test_technical_debt_does_not_change_norm(self):
        """ Test that the norm is not changed when there is technical debt. """
        for metric in self.metrics:
            if metric['measurement'] == 'De automatic regression test statement coverage van Application FOO kon ' \
                                        'niet gemeten worden omdat de bron CoverageReport niet is geconfigureerd.':
                self.assertTrue(metric["norm"].startswith("Minimaal 80% van de statements wordt gedekt door "
                                                          "geautomatiseerde functionele tests."))
                break

    def test_technical_debt_adds_commment(self):
        """ Test that the comment shows the technical debt. """
        for metric in self.metrics:
            if metric['measurement'] == 'De automatic regression test statement coverage van Application FOO kon ' \
                                        'niet gemeten worden omdat de bron CoverageReport niet is geconfigureerd.':
                self.assertEqual("De op dit moment geaccepteerde technische schuld is 42%. How do we explain this?",
                                 metric["comment"])
                break

    def test_adapted_target_does_change_norm(self):
        """ Test that the norm is not changed when there is technical debt. """
        for metric in self.metrics:
            if metric['measurement'] == 'De automatic regression test branch coverage van Application FOO kon ' \
                                        'niet gemeten worden omdat de bron CoverageReport niet is geconfigureerd.':
                self.assertEqual("Minimaal 35% van de branches wordt gedekt door geautomatiseerde functionele tests. "
                                 "Minder dan 30% is rood.", metric["norm"])
                break

    def test_adapted_target_adds_comment(self):
        """ Test that the comment shows the adapted target. """
        for metric in self.metrics:
            if metric['measurement'] == 'De automatic regression test branch coverage van Application FOO kon ' \
                                        'niet gemeten worden omdat de bron CoverageReport niet is geconfigureerd.':
                self.assertEqual("De norm is aangepast van 60% (default) naar 30%.", metric["comment"])
                break
