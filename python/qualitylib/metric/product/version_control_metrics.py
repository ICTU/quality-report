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

from ..metric_source_mixin import VersionControlSystemMetricMixin
from ..quality_attributes import CODE_QUALITY
from ... import utils
from ...domain import LowerIsBetterMetric


class UnmergedBranches(VersionControlSystemMetricMixin, LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring the number of unmerged branches. """

    name = 'Ongemergde branches'
    norm_template = 'Maximaal {target} branches met ongemergde code. Meer dan {low_target} is rood.'
    perfect_template = 'Geen van de {nr_branches} branches van {name} heeft revisies die niet met de trunk zijn ' \
        'gemerged.'
    template = '{value} van de {nr_branches} branches van {name} hebben revisies die niet met de trunk zijn gemerged.'
    url_label_text = 'Niet gemergde branches'
    comment_url_label_text = 'Genegeerde branches'
    quality_attribute = CODE_QUALITY
    target_value = 0
    low_target_value = 1

    @classmethod
    def can_be_measured(cls, product, project):
        """ Unmerged branches can only be measured for trunk versions of products that are under version control. """
        return super(UnmergedBranches, cls).can_be_measured(product, project) \
            and not product.product_version() and not product.product_branch()

    def value(self):
        return len(self.__unmerged_branches())

    def url(self):
        return self.__branch_and_nr_revs_urls(self.__unmerged_branches())

    def comment_urls(self):
        return self.__branch_urls(self.__branches_to_ignore())

    def _get_template(self):
        # pylint: disable=protected-access
        return self.perfect_template if self._is_perfect() else super(UnmergedBranches, self)._get_template()

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(UnmergedBranches, self)._parameters()
        parameters['nr_branches'] = len(self.__branches())
        return parameters

    def __branch_and_nr_revs_urls(self, branches_and_revisions):
        """ Return a list of branch urls. """
        urls = dict()
        for branch, nr_revisions in branches_and_revisions.items():
            label = '{branch}: {nr} ongemergde revisie(s)'.format(branch=branch, nr=nr_revisions)
            urls[label] = self._vcs_product_info.branch_folder_for_branch(self._vcs_path(), branch)
        return urls

    def __branch_urls(self, branches):
        """ Return a list of branch urls. """
        urls = dict()
        for branch in branches:
            urls[branch] = self._vcs_product_info.branch_folder_for_branch(self._vcs_path(), branch)
        return urls

    def __branches(self):
        """ Return a list of branches for the product. """
        return self._vcs_product_info.branches(self._vcs_path())

    @utils.memoized
    def __unmerged_branches(self):
        """ Return a dictionary of unmerged branch names and the number of unmerged revisions for each branch. """
        return self._vcs_product_info.unmerged_branches(self._vcs_path(), self.__branches_to_ignore())

    def __branches_to_ignore(self):
        """ Return the branches to ignore for the measured product. """
        metric_options = self._subject.metric_options(self.__class__)
        if metric_options:
            return metric_options.get('branches_to_ignore', [])
        else:
            return []
