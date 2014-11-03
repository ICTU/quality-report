'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from qualitylib.domain import HigherIsBetterMetric, LowerIsBetterMetric
from qualitylib.metric.metric_source_mixin import BirtMetricMixin
from qualitylib.metric.quality_attributes import TEST_COVERAGE, PERFORMANCE, \
   TEST_QUALITY
from qualitylib import metric_source
import datetime


class FailingRegressionTests(LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the number of regression tests that fail. '''

    name = 'Falende regressietesten'
    norm_template = 'Alle regressietesten slagen.'
    perfect_template = 'Alle %(tests)d regressietesten van %(name)s slagen.'
    template = '%(value)d van de %(tests)d regressietesten van %(name)s ' \
        'slagen niet.'
    target_value = 0
    low_target_value = 0
    quality_attribute = TEST_QUALITY
    metric_source_classes = (metric_source.JenkinsTestReport,)

    def __init__(self, *args, **kwargs):
        super(FailingRegressionTests, self).__init__(*args, **kwargs)
        self.__jenkins_test_report = \
            self._project.metric_source(metric_source.JenkinsTestReport)

    def value(self):
        return self.__jenkins_test_report.failed_tests(self.__jenkins_ids()) + \
               self.__jenkins_test_report.skipped_tests(self.__jenkins_ids())

    def _get_template(self):
        # pylint: disable=protected-access
        return self.perfect_template if self._is_perfect() else \
            super(FailingRegressionTests, self)._get_template()

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(FailingRegressionTests, self)._parameters()
        parameters['tests'] = self.value() + \
            self.__jenkins_test_report.passed_tests(self.__jenkins_ids())
        return parameters

    def __jenkins_ids(self):
        ''' Return the Jenkins test report ids (job names). '''
        test_report = self._subject.metric_source_id(self.__jenkins_test_report)
        return [test_report] if type(test_report) == type('') else test_report

    def url(self):
        jenkins_ids = self.__jenkins_ids()
        if len(jenkins_ids) == 1:
            return {'Jenkins test report': 
                    self.__jenkins_test_report.test_report_url(jenkins_ids[0])}
        else:
            urls = {}
            for jenkins_id in jenkins_ids:
                urls['Jenkins test report %s' % jenkins_id] = \
                    self.__jenkins_test_report.test_report_url(jenkins_id)
            return urls


class ARTCoverage(HigherIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the coverage of automated regression tests (ART)
        for a product. '''

    name = 'Automatic regression test coverage'
    norm_template = 'Minimaal %(target)d%% van de regels code wordt gedekt ' \
           'door geautomatiseerde functionele tests. ' \
           'Minder dan %(low_target)d%% is rood.'
    template = '%(name)s ART coverage is %(value)d%% ' \
               '(%(date)s, %(age)s geleden).'
    perfect_value = 100
    target_value = 80
    low_target_value = 70
    quality_attribute = TEST_COVERAGE
    metric_source_classes = []  # subclass responsibility

    def __init__(self, *args, **kwargs):
        super(ARTCoverage, self).__init__(*args, **kwargs)
        self.__coverage_report = \
            self._project.metric_source(self.__coverage_class())
        if not self._subject.product_version():
            # Trunk version, ART coverage measurement should not be too old.
            self.old_age = datetime.timedelta(hours=3 * 24)
            self.max_old_age = datetime.timedelta(hours=5 * 24)
            self.norm_template = 'Minimaal %(target)d%% van de regels code ' \
                'wordt gedekt door geautomatiseerde functionele tests en de ' \
                'coverage meting is niet ouder dan %(old_age)s. Minder dan ' \
                '%(low_target)d%% of meting ouder dan %(max_old_age)s is rood.'

    def value(self):
        coverage_id = self._subject.metric_source_id(self.__coverage_report)
        return self.__coverage_report.coverage(coverage_id)

    def url(self):
        urls = dict()
        coverage_id = self._subject.metric_source_id(self.__coverage_report)
        urls[self.__coverage_class().__name__] = \
            self.__coverage_report.get_coverage_url(coverage_id)
        return urls

    def _date(self):
        ''' Return the date of the last coverage measurement from the coverage
            report. '''
        coverage_id = self._subject.metric_source_id(self.__coverage_report)
        return self.__coverage_report.coverage_date(coverage_id)

    def __coverage_class(self):
        ''' Return the coverage class we're using. '''
        return self.metric_source_classes[0]


class EmmaARTCoverage(ARTCoverage):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the coverage of automated regression tests (ART)
        for a product with Emma. '''
    metric_source_classes = [metric_source.Emma]


class JaCoCoARTCoverage(ARTCoverage):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the coverage of automated regression tests (ART)
        for a product with JacCoCo. '''
    metric_source_classes = [metric_source.JaCoCo]


class RelativeARTPerformance(BirtMetricMixin, LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the number of pages that loads slower during
        running of an automated regression test than during a previous ART. '''

    name = 'Automatic regression test relative performance'
    norm_template = 'Maximaal %(target)d van de paginas laadt langzamer dan ' \
        'tijdens de vorige automatische regressie test. ' \
        'Meer dan %(low_target)d is rood.'
    template = '%(value)d van de paginas van %(name)s laadt langzamer ' \
        'bij het uitvoeren van de laatste test dan bij de voorlaatste test.'
    target_value = 0
    low_target_value = 5
    quality_attribute = PERFORMANCE
    metric_source_classes = (metric_source.Birt,)

    @classmethod
    def can_be_measured(cls, product, project):
        birt = project.metric_source(metric_source.Birt)
        birt_id = product.metric_source_id(birt)
        return super(RelativeARTPerformance, cls).can_be_measured(product, 
                                                                  project) \
            and birt.has_art_performance(birt_id, product.product_version())

    def value(self):
        return self._birt.nr_slower_pages_art(self._birt_id(),
                                              self._subject.product_version())

    def url(self):
        return dict(
            Birt=self._birt.relative_art_performance_url(self._birt_id()))
