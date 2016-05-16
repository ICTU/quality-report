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
from __future__ import absolute_import

import datetime

from ..quality_attributes import TEST_COVERAGE, TEST_QUALITY
from ... import metric_source
from ...domain import HigherIsBetterMetric, LowerIsBetterMetric


class FailingRegressionTests(LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring the number of regression tests that fail. """

    name = 'Falende regressietesten'
    norm_template = 'Alle regressietesten slagen.'
    perfect_template = 'Alle {tests} regressietesten van {name} slagen.'
    template = '{value} van de {tests} regressietesten van {name} slagen niet.'
    target_value = 0
    low_target_value = 0
    quality_attribute = TEST_QUALITY
    metric_source_classes = (metric_source.TestReport,)

    def __init__(self, *args, **kwargs):
        super(FailingRegressionTests, self).__init__(*args, **kwargs)
        self.__test_report = self._project.metric_source(metric_source.TestReport)

    def value(self):
        if self._missing():
            return -1
        else:
            urls = self.__report_urls()
            return self.__test_report.failed_tests(*urls) + self.__test_report.skipped_tests(*urls)

    def _missing(self):
        urls = self.__report_urls()
        return self.__test_report.passed_tests(*urls) < 0 or self.__test_report.failed_tests(*urls) < 0 or \
            self.__test_report.skipped_tests(*urls) < 0

    def _get_template(self):
        # pylint: disable=protected-access
        return self.perfect_template if self._is_perfect() else super(FailingRegressionTests, self)._get_template()

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(FailingRegressionTests, self)._parameters()
        parameters['tests'] = self.value() + self.__test_report.passed_tests(*self.__report_urls())
        return parameters

    def __report_urls(self):
        """ Return the test report urls. """
        report_urls = self._subject.metric_source_id(self.__test_report)
        return report_urls if isinstance(report_urls, list) else [report_urls]

    def url(self):
        report_urls = self.__report_urls()
        urls = {}
        count = len(report_urls)
        for index, report_url in enumerate(report_urls, start=1):
            urls['Test report ({index}/{count})'.format(index=index, count=count)] = report_url
        return urls


class _ARTCoverage(HigherIsBetterMetric):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring the coverage of automated regression tests (ART) for a product. """
    perfect_value = 100
    quality_attribute = TEST_COVERAGE
    metric_source_classes = [metric_source.CoverageReport]
    covered_items = 'Subclass responsibility'

    def __init__(self, *args, **kwargs):
        super(_ARTCoverage, self).__init__(*args, **kwargs)
        self._coverage_report = self._project.metric_source(self.__coverage_class())
        if not self._subject.product_version():
            # Trunk version, ART coverage measurement should not be too old.
            self.old_age = datetime.timedelta(hours=3 * 24)
            self.max_old_age = datetime.timedelta(hours=5 * 24)
            self.norm_template = 'Minimaal {target}% van de {covered_items} wordt gedekt door geautomatiseerde ' \
                'functionele tests en de coverage meting is niet ouder dan {old_age}. Minder dan ' \
                '{low_target}% of meting ouder dan {max_old_age} is rood.'

    def value(self):
        raise NotImplementedError  # pragma: nocover

    def _date(self):
        """ Return the date of the last coverage measurement from the coverage report. """
        return self._coverage_report.coverage_date(self._coverage_url())

    def url(self):
        urls = dict()
        urls[self.__coverage_class().__name__] = self._coverage_url()
        return urls

    def __coverage_class(self):
        """ Return the coverage class we're using. """
        return self.metric_source_classes[0]

    def _coverage_url(self):
        """ Return the url of the coverage report. """
        return self._subject.metric_source_id(self._coverage_report)

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(_ARTCoverage, self)._parameters()
        parameters['covered_items'] = self.covered_items
        return parameters


class ARTStatementCoverage(_ARTCoverage):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring the statement coverage of automated regression tests (ART) for a product. """

    name = 'Automatic regression test statement coverage'
    norm_template = 'Minimaal {target}% van de statements wordt gedekt door geautomatiseerde functionele tests. ' \
           'Minder dan {low_target}% is rood.'
    template = '{name} ART statement coverage is {value}% ({date}, {age} geleden).'
    target_value = 80
    low_target_value = 70
    covered_items = 'statements'

    def value(self):
        return int(round(self._coverage_report.statement_coverage(self._coverage_url())))


class ARTBranchCoverage(_ARTCoverage):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring the branch coverage of automated regression tests (ART) for a product. """

    name = 'Automatic regression test branch coverage'
    norm_template = 'Minimaal {target}% van de branches wordt gedekt door geautomatiseerde functionele tests. ' \
           'Minder dan {low_target}% is rood.'
    template = '{name} ART branch coverage is {value}% ({date}, {age} geleden).'
    target_value = 75
    low_target_value = 60
    covered_items = 'branches'

    def value(self):
        return int(round(self._coverage_report.branch_coverage(self._coverage_url())))

