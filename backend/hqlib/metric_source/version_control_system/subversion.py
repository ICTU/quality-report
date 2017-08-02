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


from datetime import datetime
import logging
from typing import List, Dict

import bs4

from ..abstract import version_control_system


class Subversion(version_control_system.VersionControlSystem):
    """ Class representing the Subversion repository. """

    metric_source_name = 'Subversion'

    @classmethod
    def branch_folder_for_branch(cls, trunk_url: str, branch: str) -> str:
        """ Return the branch folder for the specified branch. """
        return cls.__branches_folder(trunk_url) + branch + '/' + trunk_url.split('/trunk/')[1]

    @staticmethod
    def normalize_path(svn_path: str) -> str:
        """ Return a normalized version of the path. """
        if not svn_path.endswith('/'):
            svn_path += '/'
        if '/trunk/' not in svn_path:
            svn_path += 'trunk/'
        return svn_path

    def last_changed_date(self, url: str) -> datetime:
        """ Return the date when the url was last changed in Subversion. """
        svn_info_xml = str(self._run_shell_command(('svn', 'info', '--xml', url)))
        try:
            date = bs4.BeautifulSoup(svn_info_xml, "lxml")('date')[0].string
        except IndexError:
            return datetime.min
        return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')

    def unmerged_branches(self, product_url: str, list_of_branches_to_ignore: List[str]=None,
                          re_of_branches_to_ignore: str='',
                          list_of_branches_to_include: List[str]=None) -> Dict[str, int]:
        """ Return a dictionary of branch names and number of unmerged revisions for each branch that has any
            unmerged revisions. """
        branches = [branch for branch in self.branches(product_url) if not
                    self._ignore_branch(branch, list_of_branches_to_ignore, re_of_branches_to_ignore,
                                        list_of_branches_to_include)]
        branches_and_revs = [(branch, self.__nr_unmerged_revisions(product_url, branch)) for branch in branches]
        unmerged_branches = [(branch, nr_revisions) for (branch, nr_revisions) in branches_and_revs if nr_revisions > 0]
        return dict(unmerged_branches)

    def __nr_unmerged_revisions(self, product_url: str, branch_name: str) -> int:
        """ Return whether the branch has unmerged revisions. """
        branch_url = self.__branches_folder(product_url) + branch_name
        trunk_url = product_url
        revisions = str(self._run_shell_command(('svn', 'mergeinfo', '--show-revs', 'eligible',
                                                 branch_url, trunk_url))).strip()
        logging.debug('Unmerged revisions from %s to %s: "%s"', branch_url, trunk_url, revisions)
        # Number of revisions is one more than the number of line breaks, if there is any output:
        nr_revisions = revisions.count('\n') + 1 if revisions else 0
        # If there is a small number of revisions, it may be caused by the Maven release plugin committing to a tag
        # before creating the branch. Check for that and ignore those revisions if that's the case.
        if 1 <= nr_revisions <= 3:
            # Create a list of revision numbers and remove the initial 'r'
            revision_numbers = [revision[1:].strip() for revision in revisions.split('\n')]
            for revision in revision_numbers:
                if '/tags/' in self.__revision_url(branch_url, revision):
                    nr_revisions -= 1
        return nr_revisions

    def __revision_url(self, branch_url: str, revision_number: str) -> str:
        """ Return the url for a specific revision number. """
        svn_info_xml = str(self._run_shell_command(('svn', 'info', branch_url, '--xml', '-r', revision_number)))
        return bs4.BeautifulSoup(svn_info_xml, "lxml")('url')[0].string

    def branches(self, trunk_url: str) -> List[str]:
        """ Return a list of branch names for the specified trunk url. """
        return self.__svn_list(self.__branches_folder(trunk_url))

    @staticmethod
    def __branches_folder(trunk_url: str) -> str:
        """ Return the branches folder for the trunk url. """
        return trunk_url.split('/trunk/')[0] + '/branches/'

    def __svn_list(self, url: str) -> List[str]:
        """ Return a list of sub folder names. """
        shell_command = ('svn', 'list', '--xml', url)
        svn_info_xml = str(self._run_shell_command(shell_command))
        return [name.string for name in bs4.BeautifulSoup(svn_info_xml, "lxml")('name')]
