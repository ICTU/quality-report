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

from qualitylib.domain import HigherIsBetterMetric, \
   LowerPercentageIsBetterMetric
from qualitylib.metric.metric_source_mixin import BirtMetricMixin
from qualitylib.metric.quality_attributes import TEST_COVERAGE, PERFORMANCE
import datetime


class ARTCoverage(HigherIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the coverage of automated regression tests (ART)
        for a product. '''

    name = 'Automatic regression test coverage'
    norm_template = 'Minimaal %(target)d%% van de regels code wordt gedekt ' \
           'door geautomatiseerde functionele tests. ' \
           'Minder dan %(low_target)d%% is rood.'
    template = '%(name)s ART coverage is %(coverage)d%% ' \
               '(%(date)s, %(age)s geleden).'
    perfect_value = 100
    target_value = 80
    low_target_value = 70
    quality_attribute = TEST_COVERAGE

    def __init__(self, *args, **kwargs):
        super(ARTCoverage, self).__init__(*args, **kwargs)
        self.__emma = self._project.emma()
        self.__jacoco = self._project.jacoco()
        if not self._subject.product_version():
            # Trunk version, ART coverage measurement should not be too old.
            self.old_age = datetime.timedelta(hours=3 * 24)
            self.max_old_age = datetime.timedelta(hours=5 * 24)
            self.norm_template = 'Minimaal %(target)d%% van de regels code ' \
                'wordt gedekt door geautomatiseerde functionele tests en de ' \
                'coverage meting is niet ouder dan %(old_age)s. Minder dan ' \
                '%(low_target)d%% of meting ouder dan %(max_old_age)s is rood.'

    @classmethod
    def can_be_measured(cls, subject, project):
        return super(ARTCoverage, cls).can_be_measured(subject, project) and \
            (project.jacoco() and subject.art_coverage_jacoco()) or \
            (project.emma() and subject.art_coverage_emma())

    def value(self):
        return self.__coverage()

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(ARTCoverage, self)._parameters()
        parameters['coverage'] = self.__coverage()
        return parameters

    def url(self):
        urls = dict()
        emma_id = self._subject.art_coverage_emma()
        if emma_id:
            urls['Emma'] = self.__emma.get_coverage_url(emma_id)
        jacoco_id = self._subject.art_coverage_jacoco()
        if jacoco_id:
            urls['JaCoCo'] = self.__jacoco.get_coverage_url(jacoco_id)
        return urls

    def __coverage(self):
        ''' Return the coverage from Emma or Jacoco. '''
        emma_id = self._subject.art_coverage_emma()
        if emma_id:
            return self.__emma.coverage(emma_id)
        else:
            jacoco_id = self._subject.art_coverage_jacoco()
            return self.__jacoco.coverage(jacoco_id)

    def _date(self):
        ''' Return the date of the last coverage measurement from Emma or 
            Jacoco. '''
        emma_id = self._subject.art_coverage_emma()
        if emma_id:
            return self.__emma.coverage_date(emma_id)
        else:
            jacoco_id = self._subject.art_coverage_jacoco()
            return self.__jacoco.coverage_date(jacoco_id)


class ARTPerformance(BirtMetricMixin, LowerPercentageIsBetterMetric):
    ''' Metric for measuring the percentage of pages that loads too slow 
        during running an automated regression test. '''

    name = 'Automatic regression test performance'
    norm_template = 'Maximaal %(target)d%% van de paginas heeft een ' \
        'gemiddelde laadtijd hoger dan het maximum. ' \
        'Meer dan %(low_target)d%% is rood.'
    template = '%(value)d%% (%(numerator)d van de %(denominator)d) van de ' \
        'paginas van %(name)s laadt te langzaam bij het uitvoeren van de ART.' 
    target_value = 25
    low_target_value = 50
    quality_attribute = PERFORMANCE

    @classmethod
    def can_be_measured(cls, product, project):
        return super(ARTPerformance, cls).can_be_measured(product, project) \
            and product.product_version() and product.art() and project.birt()

    def _denominator(self):
        return self._birt.nr_performance_pages(self._birt_id(), 
                                               self.__version())

    def _numerator(self):
        return self._birt.nr_slow_performance_pages(self._birt_id(), 
                                                    self.__version())

    def url(self):
        return dict(Birt=self._birt.page_performance_url(self._birt_id(),
                                                         self.__version()))

    def __version(self):
        ''' Return the version number for the product this metric is reporting 
            on. '''
        return self._subject.product_version() or 'trunk'
