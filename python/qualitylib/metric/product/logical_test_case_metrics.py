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

from qualitylib.domain import LowerIsBetterMetric
from qualitylib.metric.metric_source_mixin import BirtMetricMixin, \
    BirtTestDesignMetricMixin
from qualitylib.metric.quality_attributes import TEST_COVERAGE, DOC_QUALITY
import datetime


class LogicalTestCaseMetric(BirtTestDesignMetricMixin, LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Base class for metrics measuring the quality of logical test cases. '''
    @classmethod
    def can_be_measured(cls, product, project):
        return super(LogicalTestCaseMetric, cls).can_be_measured(product, 
                                                                 project) and \
            not product.product_version()

    def value(self):
        return self._nr_ltcs() - self._nr_ltcs_ok()

    def _nr_ltcs_ok(self):
        ''' Return the number of logical test cases whose quality is good. '''
        raise NotImplementedError  # pragma: no cover

    def _nr_ltcs(self):
        ''' Return the total number of logical test cases. '''
        raise NotImplementedError  # pragma: no cover

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(LogicalTestCaseMetric, self)._parameters()
        parameters['total'] = self._nr_ltcs()
        return parameters


class LogicalTestCasesNotReviewedAndApproved(LogicalTestCaseMetric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the number of logical test cases that has
        not been reviewed and/or approved. '''

    name = 'Goedkeuring van logische testgevallen'
    norm_template = 'Maximaal %(target)d van de logische testgevallen is ' \
        'niet gereviewd en/of goedgekeurd. Meer dan %(low_target)d is rood.'
    template = '%(name)s heeft %(value)d niet gereviewde en/of niet ' \
        'goedgekeurde logische testgevallen van in totaal %(total)d ' \
        'logische testgevallen.'
    target_value = 9
    low_target_value = 15
    quality_attribute = DOC_QUALITY

    def _nr_ltcs_ok(self):
        return self._birt.approved_ltcs(self._birt_id())

    def _nr_ltcs(self):
        return self._birt.nr_ltcs(self._birt_id())


class LogicalTestCasesNotAutomated(LogicalTestCaseMetric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the number of logical test cases that should
        be automated that has actually been automated. '''

    name = 'Automatisering van logische testgevallen'
    norm_template = 'Maximaal %(target)d van de te automatiseren logische ' \
        'testgevallen is niet geautomatiseerd. ' \
        'Meer dan %(low_target)d is rood.'
    template = '%(name)s heeft %(value)d nog te automatiseren logische ' \
        'testgevallen, van in totaal %(total)d geautomatiseerde logische ' \
        'testgevallen.'
    target_value = 9
    low_target_value = 15
    quality_attribute = TEST_COVERAGE

    def _nr_ltcs_ok(self):
        return self._birt.nr_automated_ltcs(self._birt_id())

    def _nr_ltcs(self):
        return self._birt.nr_ltcs_to_be_automated(self._birt_id())


class ManualLogicalTestCases(BirtMetricMixin, LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring how long ago the manual logical test cases
        have been tested. '''

    name = 'Tijdige uitvoering van handmatige logische testgevallen'
    norm_template = 'Alle handmatige logische testgevallen zijn minder dan ' \
        '%(target)d dagen geleden uitgevoerd. Langer dan %(low_target)d ' \
        'dagen geleden is rood.'
    template = '%(nr_manual_ltcs_too_old)d van de %(nr_manual_ltcs)d ' \
        'handmatige logische testgevallen van %(name)s zijn te lang geleden '\
        '(meest recente %(value)d dag(en), op %(date)s) uitgevoerd.'
    never_template = 'De %(nr_manual_ltcs)d handmatige logische testgevallen ' \
        'van %(name)s zijn nog nooit uitgevoerd.'
    target_value = 21
    low_target_value = 28
    quality_attribute = TEST_COVERAGE

    @classmethod
    def can_be_measured(cls, product, project):
        return super(ManualLogicalTestCases, cls).can_be_measured(product,
                                                                  project) and \
            product.responsible_teams() 

    def target(self):
        if self._subject.product_version_type() == 'release':
            return 0  # Release candidates should already be tested
        else:
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
        return self._birt.date_of_last_manual_test(self._birt_id(),
                                                   self.__version())

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(ManualLogicalTestCases, self)._parameters()
        parameters['nr_manual_ltcs'] = \
            self._birt.nr_manual_ltcs(self._birt_id(), self.__version())
        parameters['nr_manual_ltcs_too_old'] = \
            self._birt.nr_manual_ltcs_too_old(self._birt_id(), self.__version(),
                                              self.target())
        return parameters

    def _get_template(self):
        # pylint: disable=protected-access
        return self.never_template if self._date() == datetime.datetime.min \
            else super(ManualLogicalTestCases, self)._get_template()

    def __version(self):
        ''' Return the version number for the product this metric is reporting 
            on. '''
        return self._subject.product_version() or 'trunk'
