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

from qualitylib.domain import LowerIsBetterMetric, \
    HigherPercentageIsBetterMetric
from qualitylib.metric.metric_source_mixin import BirtMetricMixin, \
    BirtTestDesignMetricMixin
from qualitylib.metric.quality_attributes import TEST_COVERAGE, DOC_QUALITY
import datetime


class ReviewedAndApprovedLogicalTestCases(BirtTestDesignMetricMixin,
                                          HigherPercentageIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the percentage of logical test cases that has
        been reviewed and approved. '''

    name = 'Goedkeuring van logische testgevallen'
    norm_template = 'Minimaal %(target)d%% van de logische testgevallen is ' \
        'gereviewd en goedgekeurd. Lager dan %(low_target)d%% is rood.'
    template = '%(name)s heeft %(value)d%% (%(numerator)d van ' \
        '%(denominator)d) goedgekeurde logische testgevallen.'
    target_value = 95
    low_target_value = 75
    quality_attribute = DOC_QUALITY

    @classmethod
    def can_be_measured(cls, product, project):
        return super(ReviewedAndApprovedLogicalTestCases, cls).\
            can_be_measured(product, project) and not product.product_version()

    def _numerator(self):
        return self._birt.approved_ltcs(self._birt_id())

    def _denominator(self):
        return self._birt.nr_ltcs(self._birt_id())


class AutomatedLogicalTestCases(BirtTestDesignMetricMixin, 
                                HigherPercentageIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the percentage of logical test cases that should
        be automated that has actually been automated. '''

    name = 'Automatisering van logische testgevallen'
    norm_template = 'Minimaal %(target)d%% van de te automatiseren logische ' \
        'testgevallen is opgenomen in de ART. ' \
        'Lager dan %(low_target)d%% is rood.'
    template = '%(name)s heeft %(value)d%% (%(numerator)d van ' \
        '%(denominator)d) geautomatiseerde logische testgevallen.'
    target_value = 95
    low_target_value = 75
    quality_attribute = TEST_COVERAGE

    @classmethod
    def can_be_measured(cls, product, project):
        return super(AutomatedLogicalTestCases, cls).can_be_measured(product,
                                                                     project) \
            and not product.product_version()

    def _numerator(self):
        return self._birt.nr_automated_ltcs(self._birt_id())

    def _denominator(self):
        return self._birt.nr_ltcs_to_be_automated(self._birt_id())


class ManualLogicalTestCases(BirtMetricMixin, LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the how long ago the manual logical test cases
        have been tested. '''

    name = 'Uitvoering van handmatige logische testgevallen'
    norm_template = 'Alle handmatige logische testgevallen zijn minstens ' \
        'eenmaal uitgevoerd. In geval van trunk versies geldt bovendien dat ' \
        'ze minder dan %(target)d dagen geleden moeten zijn uitgevoerd. ' \
        'Langer dan %(low_target)d dagen geleden is rood.'
    template = '%(nr_manual_ltcs_too_old)d van de %(nr_manual_ltcs)d ' \
        'handmatige logische testgevallen van %(name)s zijn te lang geleden '\
        '(%(value)d dag(en), op %(date)s) uitgevoerd.'
    target_value = 21
    low_target_value = 28
    quality_attribute = TEST_COVERAGE

    @classmethod
    def can_be_measured(cls, product, project):
        return super(ManualLogicalTestCases, cls).can_be_measured(product,
                                                                  project) and \
            product.responsible_teams() 

    def target(self):
        teams = self._subject.responsible_teams()
        sprint_length = min([team.days_per_sprint() for team in teams])
        return sprint_length

    def low_target(self):
        return self.target() + 7

    def value(self):
        date = self._date()  # Make sure date is older than datetime.now() in
        # the next line so that the time delta is always positive
        return (datetime.datetime.now() - date).days

    def url(self):
        return dict(Birt=self._birt.manual_test_execution_url(self._birt_id(),
                                                              self.__version()))

    def _date(self):
        date = self._birt.date_of_last_manual_test(self._birt_id(),
                                                   self.__version())
        # If this product/version never has been tested and it is not the 
        # trunk version, return the date the version was created so we don't 
        # start complaining about not executed manual  tests right after 
        # creation of the version.
        if date == datetime.datetime.min and self._subject.product_version():
            date = self._subject.last_changed_date()
        return date

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(ManualLogicalTestCases, self)._parameters()
        parameters['nr_manual_ltcs'] = \
            self._birt.nr_manual_ltcs(self._birt_id(), self.__version())
        parameters['nr_manual_ltcs_too_old'] = \
            self._birt.nr_manual_ltcs_too_old(self._birt_id(), self.__version(),
                                              self.target())
        return parameters

    def __version(self):
        ''' Return the version number for the product this metric is reporting 
            on. '''
        return self._subject.product_version() or 'trunk'
