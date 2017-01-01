"""
Copyright 2012-2017 Ministerie van Sociale Zaken en Werkgelegenheid

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
from ... import utils
from ...domain import LowerIsBetterMetric


class UnmergedBranches(VersionControlSystemMetricMixin, LowerIsBetterMetric):
    """ Metric for measuring the number of unmerged branches. """

    name = 'Hoeveelheid ongemergde branches'
    unit = 'branches'
    norm_template = 'Maximaal {target} {unit} met ongemergde code. Meer dan {low_target} {unit} is rood.'
    perfect_template = 'Geen van de {nr_branches} {unit} van {name} heeft revisies die niet met de trunk zijn ' \
        'gemerged.'
    template = '{value} van de {nr_branches} {unit} van {name} hebben revisies die niet met de trunk zijn gemerged.'
    url_label_text = 'Niet gemergde branches'
    comment_url_label_text = 'Genegeerde branches'
    target_value = 0
    low_target_value = 1

    def value(self):
        unmerged_branches = self.__unmerged_branches()
        return -1 if unmerged_branches is None else len(unmerged_branches)

    def url(self):
        unmerged_branches = self.__unmerged_branches()
        return dict() if unmerged_branches is None else self.__branch_and_nr_revs_urls(unmerged_branches)

    def comment_urls(self):
        return self.__branch_urls(self.__list_of_branches_to_ignore())

    def comment(self):
        comment = super(UnmergedBranches, self).comment()
        branches_to_include = self.__list_of_branches_to_include()
        if branches_to_include:
            branches = ', '.join(branches_to_include)
            branch_comment = 'Alleen deze branches worden bewaakt: {}.'.format(branches)
            if comment:
                comment += ' ' + branch_comment
            else:
                comment = branch_comment
        branch_re = self.__re_of_branches_to_ignore()
        if branch_re:
            branch_comment = 'Branches die voldoen aan de reguliere expressie {re} zijn genegeerd.'.format(re=branch_re)
            if comment:
                comment += ' ' + branch_comment
            else:
                comment = branch_comment
        return comment

    def _parameters(self):
        parameters = super(UnmergedBranches, self)._parameters()
        branches = self.__branches()
        parameters['nr_branches'] = -1 if branches is None else len(branches)
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
        return self._vcs_product_info.unmerged_branches(self._vcs_path(), self.__list_of_branches_to_ignore(),
                                                        self.__re_of_branches_to_ignore(),
                                                        self.__list_of_branches_to_include())

    def __list_of_branches_to_ignore(self):
        """ Return the list of branches to ignore for the measured product. """
        metric_options = self._subject.metric_options(self.__class__)
        return metric_options.get('branches_to_ignore', []) if metric_options else []

    def __re_of_branches_to_ignore(self):
        """ Return the regular expression of branches to ignore for the measured product. """
        metric_options = self._subject.metric_options(self.__class__)
        return metric_options.get('branches_to_ignore_re', '') if metric_options else ''

    def __list_of_branches_to_include(self):
        """ Return the list of branches to include for the measured product. """
        metric_options = self._subject.metric_options(self.__class__)
        return metric_options.get('branches_to_include', []) if metric_options else []
