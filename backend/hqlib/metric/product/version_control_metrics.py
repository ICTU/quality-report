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
from typing import Dict, List, Optional

from hqlib import utils
from hqlib.typing import MetricParameters
from ...domain import LowerIsBetterMetric, ExtraInfo
from ...metric_source import VersionControlSystem, Branch


class UnmergedBranches(LowerIsBetterMetric):
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
    metric_source_class = VersionControlSystem

    def value(self):
        unmerged_branches = self.__unmerged_branches()
        return -1 if unmerged_branches is None else len(unmerged_branches)

    def comment_urls(self) -> Dict[str, str]:
        return self.__branch_urls(self.__list_of_branches_to_ignore())

    def comment(self) -> str:
        comment = super().comment()
        branches_to_include = self.__list_of_branches_to_include()
        if branches_to_include:
            branches = ', '.join(branches_to_include)
            branch_comment = 'Alleen deze branches worden bewaakt: {0}.'.format(branches)
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

    def extra_info(self) -> ExtraInfo:
        """ Returns a list with unmerged branches as an extra info object. """
        extra_info = None
        unmerged_branches = self.__unmerged_branches()
        if unmerged_branches:
            extra_info = ExtraInfo(link="Branch", comment="Aantal ongemergde revisies__detail-column-number",
                                   date_last_change="Datum laatste wijziging__detail-column-number")
            extra_info.title = self.url_label_text
            for branch in unmerged_branches:
                extra_info += ({"href": self.__branch_folder_for_branch(self.__vcs_path(), branch.name),
                                "text": branch.name}, branch.nr_revisions, branch.date_last_change.strftime("%d-%m-%Y"))

        return extra_info if extra_info is not None and extra_info.data else None

    def format_text_with_links(self, text: str) -> str:
        """ Format a text paragraph with additional url. """
        if self._metric_source:
            text = '{0} [{1}]'.format(utils.html_escape(text).replace('\n', ' '),
                                      "<a href='{href}' target='_blank'>{anchor}</a>"
                                      .format(href=self._metric_source.url(), anchor=utils
                                              .html_escape(self._metric_source.metric_source_name)))
        return json.dumps(text)[1:-1]  # Strip quotation marks

    @staticmethod
    def format_comment_with_links(text: str, url_dict: Dict[str, str], url_label: str) -> str:
        """ Format a text paragraph with optional urls and label for the urls. """
        comment_text = LowerIsBetterMetric._format_links_in_comment_text(text)
        links = [anchor for (anchor, href) in list(url_dict.items())]
        if links:
            if url_label:
                url_label += ': '
            comment_text = '{0} [{1}{2}]'.format(comment_text, url_label, ', '.join(sorted(links)))
        return json.dumps(comment_text)[1:-1]  # Strip quotation marks

    def _parameters(self) -> MetricParameters:
        parameters = super()._parameters()
        branches = self.__branches()
        parameters['nr_branches'] = 'onbekend aantal' if branches is None else str(len(branches))
        return parameters

    def __branch_urls(self, branches: List[str]) -> Dict[str, str]:
        """ Return a list of branch urls. """
        urls = dict()
        for branch in branches:
            urls[branch] = self.__branch_folder_for_branch(self.__vcs_path(), branch)
        return urls

    def __branches(self) -> List[str]:
        """ Return a list of branches for the product. """
        return self._metric_source.branches(self.__vcs_path()) if self._metric_source else None

    def __unmerged_branches(self) -> Optional[List[Branch]]:
        """ Return a list of unmerged branches. """
        return self._metric_source.unmerged_branches(
            self.__vcs_path(), self.__list_of_branches_to_ignore(), self.__re_of_branches_to_ignore(),
            self.__list_of_branches_to_include()) if self._metric_source else None

    def __list_of_branches_to_ignore(self) -> List[str]:
        """ Return the list of branches to ignore for the measured product. """
        return self.__get_metric_option('branches_to_ignore') or []

    def __re_of_branches_to_ignore(self) -> str:
        """ Return the regular expression of branches to ignore for the measured product. """
        return self.__get_metric_option('branches_to_ignore_re') or ''

    def __list_of_branches_to_include(self) -> List[str]:
        """ Return the list of branches to include for the measured product. """
        return self.__get_metric_option('branches_to_include') or []

    def __get_metric_option(self, option):
        """ Get the specified option from the subject. """
        return self._subject.metric_options(self.__class__).get(option)

    def __vcs_path(self) -> str:
        """ Return the version control system path of the product. """
        if not self._metric_source:
            return ''
        return self._metric_source.normalize_path(self._metric_source_id) if self._metric_source_id else ''

    def __branch_folder_for_branch(self, path: str, branch: str) -> str:
        """ Return the folder for the branch. """
        return self._metric_source.branch_folder_for_branch(path, branch) if self._metric_source else ''
