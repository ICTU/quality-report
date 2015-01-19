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
from __future__ import absolute_import


import datetime
import os
import logging

from ..abstract.version_control_system import \
    VersionControlSystem
from ... import utils


class Git(VersionControlSystem):
    ''' Class representing a Git repository. '''

    metric_source_name = 'Git'

    def __init__(self, *args, **kwargs):
        self.__chdir = kwargs.pop('chdir', os.chdir)
        super(Git, self).__init__(*args, **kwargs)
        self.__repo_folder = None
        self.__get_repo()

    @utils.memoized
    def last_changed_date(self, path):
        ''' Return the date when the url was last changed in Git. '''
        timestamp = self._run_shell_command(['git', 'log', '--format="%ct"',
                                             '-n', '1', path],
                                            folder=self.__repo_folder)
        return datetime.datetime.fromtimestamp(float(timestamp.strip('"\n')))

    def branches(self, path):
        ''' Return a list of branch names for the master branch. '''
        branches = self._run_shell_command(['git', 'branch', '--list',
                                            '--no-color'],
                                           folder=self.__repo_folder)
        return [branch.strip() for branch in branches.strip().split('\n')[1:]]

    def unmerged_branches(self, path):
        ''' Return a dictionary of branch names and number of unmerged
            commits for each branch that has any unmerged commits. '''
        branches = [(branch, self.__nr_unmerged_commits(path, branch)) \
                    for branch in self.branches(path)]
        unmerged_branches = [(branch, nr_commits) for (branch, nr_commits) \
                             in branches if nr_commits > 0]
        return dict(unmerged_branches)

    def __nr_unmerged_commits(self, path, branch_name):
        ''' Return whether the branch has unmerged commits. '''
        commits = self._run_shell_command(['git', 'cherry', 'master',
                                           branch_name],
                                          folder=self.__repo_folder)
        return commits.count('\n')

    def __get_repo(self):
        ''' Clone the repository if not necessary, else pull it. '''
        self.__repo_folder = os.path.join(os.getcwd(), 'repo')
        if os.path.exists(self.__repo_folder):
            logging.info('Updating Git repo %s in %s', self.url(),
                         os.getcwd())
            self._run_shell_command(['git', 'pull'], folder=self.__repo_folder)
        else:
            logging.info('Cloning Git repo %s in %s', self.url(),
                         self.__repo_folder)
            # TODO: Add --no-checkout? --quiet? --depth 1?
            self._run_shell_command(['git', 'clone', self.__full_url(), 'repo'])

    def __full_url(self):
        ''' Return the Git repository url with username and password. '''
        if self._username and self._password:
            sep = '://'
            prefix, postfix = self.url().split(sep)
            url = prefix + sep + '{username}:{password}@' + postfix
            return url.format(username=self._username,
                              password=self._password)
        else:
            return self.url()
