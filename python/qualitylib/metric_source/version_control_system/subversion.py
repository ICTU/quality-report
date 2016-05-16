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


import datetime
import logging

from BeautifulSoup import BeautifulSoup


from ..abstract import version_control_system
from ... import utils


class Subversion(version_control_system.VersionControlSystem):
    """ Class representing the Subversion repository. """

    metric_source_name = 'Subversion'

    def check_out(self, svn_path, folder):
        """ Check out the subversion path into the folder. """
        shell_command = ['svn', 'co', svn_path, folder]
        if self._username and self._password:
            shell_command.extend(['--no-auth-cache', '--username', self._username, '--password', self._password])
        self._run_shell_command(shell_command, log_level=logging.ERROR)

    @utils.memoized
    def tags_folder_for_version(self, trunk_url, version):
        """ Return the tags folder for the specified version. """
        tags = self.tags(trunk_url)
        # Mapping from version numbers to tags:
        folders = dict([(self._parse_version(tag)[1], tag) for tag in tags])
        # Look up the tag by its version number and return the tag folder
        tags_folder = self.__tags_folder(trunk_url)
        if version in folders:
            return tags_folder + folders[version] + '/' + trunk_url.split('/trunk/')[1]
        else:
            logging.warn('No tag folder for %s version %s in %s', trunk_url, version, tags_folder)
            return ''

    @classmethod
    def branch_folder_for_branch(cls, trunk_url, branch):
        """ Return the branch folder for the specified branch. """
        return cls.__branches_folder(trunk_url) + branch + '/' + trunk_url.split('/trunk/')[1]

    @staticmethod
    def normalize_path(svn_path):
        """ Return a normalized version of the path. """
        if not svn_path.endswith('/'):
            svn_path += '/'
        if '/trunk/' not in svn_path:
            svn_path += 'trunk/'
        return svn_path

    @utils.memoized
    def last_changed_date(self, url):
        """ Return the date when the url was last changed in Subversion. """
        svn_info_xml = str(self._run_shell_command(['svn', 'info', '--xml', url]))
        try:
            date = BeautifulSoup(svn_info_xml)('date')[0].string
        except IndexError:
            return datetime.datetime.min
        return datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')

    @utils.memoized
    def unmerged_branches(self, product_url, branches_to_ignore=None):
        """ Return a dictionary of branch names and number of unmerged
            revisions for each branch that has any unmerged revisions. """
        branches_to_ignore = branches_to_ignore or []
        branches = [branch for branch in self.branches(product_url) if branch not in branches_to_ignore]
        branches = [(branch, self.__nr_unmerged_revisions(product_url, branch)) for branch in branches]
        unmerged_branches = [(branch, nr_revisions) for (branch, nr_revisions) in branches if nr_revisions > 0]
        return dict(unmerged_branches)

    def __nr_unmerged_revisions(self, product_url, branch_name):
        """ Return whether the branch has unmerged revisions. """
        branch_url = self.__branches_folder(product_url) + branch_name
        trunk_url = product_url
        revisions = str(self._run_shell_command(['svn', 'mergeinfo', '--show-revs', 'eligible',
                                                 branch_url, trunk_url])).strip()
        logging.debug('Unmerged revisions from %s to %s: "%s"', branch_url, trunk_url, revisions)
        # Number of revisions is one more than the number of line breaks, if there is any output:
        nr_revisions = revisions.count('\n') + 1 if revisions else 0
        # If there is a small number of revisions, it may be caused by the Maven release plugin committing to a tag
        # before creating the branch. Check for that and ignore those revisions if that's the case.
        if 1 <= nr_revisions <= 3:
            # Create a list of revision numbers and remove the initial 'r'
            revisions = [revision[1:].strip() for revision in revisions.split('\n')]
            for revision in revisions:
                if '/tags/' in self.__revision_url(branch_url, revision):
                    nr_revisions -= 1
        return nr_revisions

    def __revision_url(self, branch_url, revision_number):
        """ Return the url for a specific revision number. """
        svn_info_xml = str(self._run_shell_command(['svn', 'info', branch_url, '--xml', '-r', revision_number]))
        return BeautifulSoup(svn_info_xml)('url')[0].string

    @utils.memoized
    def branches(self, trunk_url):
        """ Return a list of branch names for the specified trunk url. """
        return self.__svn_list(self.__branches_folder(trunk_url))

    @utils.memoized
    def tags(self, trunk_url):
        """ Return a list of tags for the specified trunk url. """
        return self.__svn_list(self.__tags_folder(trunk_url))

    @staticmethod
    def __tags_folder(trunk_url):
        """ Return the tags folder for the trunk url. """
        return trunk_url.split('/trunk/')[0] + '/tags/'

    @staticmethod
    def __branches_folder(trunk_url):
        """ Return the branches folder for the trunk url. """
        return trunk_url.split('/trunk/')[0] + '/branches/'

    def __svn_list(self, url):
        """ Return a list of sub folder names. """
        shell_command = ['svn', 'list', '--xml', url]
        svn_info_xml = str(self._run_shell_command(shell_command))
        return [name.string for name in BeautifulSoup(svn_info_xml)('name')]
