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
from qualitylib.metric.metric_source_mixin import BirtTestDesignMetricMixin
from qualitylib.metric.quality_attributes import TEST_COVERAGE, DOC_QUALITY 


class UserStoryMetric(BirtTestDesignMetricMixin, LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Base class for metrics measuring the quality of user stories. '''
    @classmethod
    def can_be_measured(cls, product, project):
        return super(UserStoryMetric, cls).can_be_measured(product, project) \
            and not product.product_version()

    def value(self):
        return self._nr_user_stories() - self._nr_user_stories_ok()

    def _nr_user_stories_ok(self):
        ''' Return the number of user stories whose quality is good. '''
        raise NotImplementedError  # pragma: no cover

    def _nr_user_stories(self):
        ''' Return the total number of user stories. '''
        return self._birt.nr_user_stories(self._birt_id())

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(UserStoryMetric, self)._parameters()
        parameters['total'] = self._nr_user_stories()
        return parameters


class UserStoriesNotReviewedAndApproved(UserStoryMetric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the percentage of user stories that have been
        reviewed and approved. '''

    name = 'Goedkeuring user stories'
    norm_template = 'Maximaal %(target)d van de user stories is niet ' \
        'gereviewd en/of niet goedgekeurd. Meer dan %(low_target)d is rood.'
    template = '%(name)s heeft %(value)d niet gereviewde en/of niet ' \
        'goedgekeurde user stories van in totaal %(total)d user stories.'
    target_value = 3
    low_target_value = 5
    quality_attribute = DOC_QUALITY

    def _nr_user_stories_ok(self):
        return self._birt.approved_user_stories(self._birt_id())


class UserStoriesWithTooFewLogicalTestCases(UserStoryMetric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the number of user stories that has too few
        logical test cases. '''

    name = 'Voldoende logische testgevallen per user story'
    norm_template = 'Maximaal %(target)d van de user stories heeft ' \
        'onvoldoende logische testgevallen. Meer dan %(low_target)d is rood.'
    template = '%(name)s heeft %(value)d user stories met een onvoldoende ' \
        'aantal logische testgevallen van in totaal %(total)d user stories.'
    target_value = 3
    low_target_value = 5
    quality_attribute = TEST_COVERAGE

    def _nr_user_stories_ok(self):
        return self._birt.nr_user_stories_with_sufficient_ltcs(self._birt_id())
