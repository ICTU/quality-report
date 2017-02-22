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

import datetime
import logging
import os
import urllib

from ..abstract.version_control_system import VersionControlSystem
from ... import utils


class Git(VersionControlSystem):
    """ Class representing a Git repository. """

    metric_source_name = 'Git'

    def __init__(self, *args, **kwargs):
        self.__branch_to_checkout = kwargs.pop('branch', None)
        self.__chdir = kwargs.pop('chdir', os.chdir)
        super(Git, self).__init__(*args, **kwargs)
        self.__repo_folder = None

    def _run_shell_command(self, *args, **kwargs):
        if not self.__repo_folder:
            self.__get_repo()
        folder = self.__repo_folder if os.path.exists(self.__repo_folder) else None
        return super(Git, self)._run_shell_command(folder=folder, *args, **kwargs)

    @utils.memoized
    def last_changed_date(self, path):
        """ Return the date when the url was last changed in Git. """
        timestamp = self._run_shell_command(['git', 'log', '--format="%ct"', '-n', '1', '--', path])
        if timestamp:
            return datetime.datetime.fromtimestamp(float(timestamp.strip('"\n')))
        else:
            return datetime.datetime.min

    def branches(self, path):  # pylint: disable=unused-argument
        """ Return a list of branch names for the master branch. """
        return self.__get_branches()

    def tags(self, path):  # pylint: disable=unused-argument
        """ Return a list of tags for the repo. """
        return self.__valid_names(self._run_shell_command(['git', 'tag']))

    @utils.memoized
    def unmerged_branches(self, path, list_of_branches_to_ignore=None, re_of_branches_to_ignore='',
                          list_of_branches_to_include=None):
        """ Return a dictionary of branch names and number of unmerged commits for each branch that has
            any unmerged commits. """
        unmerged_branches = [branch for branch in self.__get_branches(unmerged_only=True) if not
                             self._ignore_branch(branch, list_of_branches_to_ignore, re_of_branches_to_ignore,
                                                 list_of_branches_to_include)]
        branches_and_commits = [(branch, self.__nr_unmerged_commits(branch)) for branch in unmerged_branches]
        return dict(branches_and_commits)

    @classmethod
    def branch_folder_for_branch(cls, trunk_url, branch):
        """ Return the branch folder for the specified branch. """
        return trunk_url + '/' + branch

    def __get_branches(self, unmerged_only=False):
        """ Get the (remote) branches for the repository. """
        command = ['git', 'branch', '--list', '--remote', '--no-color']
        if unmerged_only:
            command.append('--no-merged')
        return self.__valid_names(self._run_shell_command(command),
                                  lambda name: name and ' -> ' not in name and 'origin/master' not in name)

    def __nr_unmerged_commits(self, branch_name):
        """ Return whether the branch has unmerged commits. """
        logging.info('Checking for unmerged commits in branch %s.', branch_name)
        command = ['git', 'cherry', 'origin/master', branch_name]
        commits = self._run_shell_command(command)
        nr_commits = commits.count('\n')
        logging.info('Branch %s has %d unmerged commits.', branch_name, nr_commits)
        return nr_commits

    def __get_repo(self):
        """ Clone the repository if necessary, else pull it. """
        self.__repo_folder = self.__determine_repo_folder_name()
        if os.path.exists(self.__repo_folder):
            logging.info('Updating Git repo %s in %s', self.url(), self.__repo_folder)
            command = ['git', 'pull', '--prune']
            self._run_shell_command(command)
        else:
            branch_string = self.__branch_to_checkout or 'master'
            logging.info('Cloning Git repo %s (branch: %s) in %s', self.url(), branch_string, self.__repo_folder)
            command = ['git', 'clone', self.__full_url(), self.__repo_folder]
            if self.__branch_to_checkout:
                command.insert(2, '--branch')
                command.insert(3, self.__branch_to_checkout)
            self._run_shell_command(command)

    def __full_url(self):
        """ Return the Git repository url with username and password. """
        if self._username and self._password:
            sep = '://'
            prefix, postfix = self.url().split(sep)
            url = prefix + sep + '{username}:{password}@' + postfix
            return url.format(username=self._username, password=urllib.pathname2url(self._password))
        else:
            return self.url()

    def __determine_repo_folder_name(self):
        url_parts = [part for part in self.url().split('/') if part]
        folder = url_parts[-1]
        if self.__branch_to_checkout:
            folder += '-{0!s}'.format(self.__branch_to_checkout)
        return os.path.join(os.getcwd(), 'repos', folder)

    @staticmethod
    def __valid_names(text, is_valid=bool):
        """ Return the names in the text that are valid. """
        names = [name.strip() for name in text.strip().split('\n')]
        return [name for name in names if is_valid(name)]
