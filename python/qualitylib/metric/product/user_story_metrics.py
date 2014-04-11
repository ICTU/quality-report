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

from qualitylib.domain import HigherPercentageIsBetterMetric
from qualitylib.metric.metric_source_mixin import BirtTestDesignMetricMixin
from qualitylib.metric.quality_attributes import TEST_COVERAGE, DOC_QUALITY 


class ReviewedAndApprovedUserStories(BirtTestDesignMetricMixin,
                                     HigherPercentageIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the percentage of user stories that have been
        reviewed and approved. '''

    name = 'Goedkeuring user stories'
    norm_template = 'Minimaal %(target)d%% van de user stories is gereviewd ' \
        'en goedgekeurd. Lager dan %(low_target)d%% is rood.'
    template = '%(name)s heeft %(value)d%% (%(numerator)d van ' \
        '%(denominator)d) goedgekeurde user stories.'
    target_value = 95
    low_target_value = 75
    quality_attribute = DOC_QUALITY

    @classmethod
    def can_be_measured(cls, product, project):
        return super(ReviewedAndApprovedUserStories, cls).\
            can_be_measured(product, project) and not product.product_version()

    def _numerator(self):
        return self._birt.approved_user_stories(self._birt_id())

    def _denominator(self):
        return self._birt.nr_user_stories(self._birt_id())


class UserStoriesWithEnoughLogicalTestCases(BirtTestDesignMetricMixin,
                                            HigherPercentageIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the percentage of user stories that has sufficient
        logical test cases. '''

    name = 'Voldoende logische testgevallen per user story'
    norm_template = 'Minimaal %(target)d%% van de user stories heeft ' \
        'voldoende logische testgevallen. Lager dan %(low_target)d%% is rood.'
    template = '%(name)s heeft %(value)d%% (%(numerator)d van ' \
        '%(denominator)d) user stories met voldoende logische testgevallen.'
    target_value = 95
    low_target_value = 75
    quality_attribute = TEST_COVERAGE

    @classmethod
    def can_be_measured(cls, product, project):
        return super(UserStoriesWithEnoughLogicalTestCases, cls).\
            can_be_measured(product, project) and not product.product_version()

    def _numerator(self):
        return self._birt.nr_user_stories_with_sufficient_ltcs(self._birt_id())

    def _denominator(self):
        return self._birt.nr_user_stories(self._birt_id())
