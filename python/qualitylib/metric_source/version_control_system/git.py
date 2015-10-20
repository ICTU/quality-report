'''
Copyright 2012-2015 Ministerie van Sociale Zaken en Werkgelegenheid

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
        if timestamp:
            return datetime.datetime.fromtimestamp(float(timestamp.strip('"\n')))
        else:
            return datetime.datetime.min

    def branches(self, path):
        ''' Return a list of branch names for the master branch. '''
        return self.__get_branches()

    @utils.memoized
    def unmerged_branches(self, path, branches_to_ignore=None):
        ''' Return a dictionary of branch names and number of unmerged
            commits for each branch that has any unmerged commits. '''
        branches_to_ignore = branches_to_ignore or []
        unmerged_branches = [branch for branch in
                             self.__get_branches(unmerged_only=True)
                             if branch not in branches_to_ignore]
        branches_and_commits = [(branch, self.__nr_unmerged_commits(branch))
                                for branch in unmerged_branches]
        return dict(branches_and_commits)

    @classmethod
    def branch_folder_for_branch(cls, trunk_url, branch):
        ''' Return the branch folder for the specified branch. '''
        return trunk_url + '/' + branch

    def __get_branches(self, unmerged_only=False):
        ''' Get the (remote) branches for the repository. '''
        def valid_branch_name(name):
            ''' Return whether name is a valid branch name. '''
            return name and not ' -> ' in name and not 'origin/master' in name

        command = ['git', 'branch', '--list', '--remote', '--no-color']
        if unmerged_only:
            command.append('--no-merged')
        logging.debug( ">>> VCS:Git::__get_branches" )
        logging.debug( "running '%s'", " ".join(command) )
        branches = self._run_shell_command(command, folder=self.__repo_folder)
        logging.debug( "--- output:" )
        logging.debug( branches )
        logging.debug( "<<< VCS:Git::__get_branches" )
        return [branch.strip() for branch in branches.strip().split('\n')
                if valid_branch_name(branch.strip())]

    def __nr_unmerged_commits(self, branch_name):
        ''' Return whether the branch has unmerged commits. '''
        logging.info('Checking for unmerged commits in branch %s.', branch_name)
        command = ['git', 'cherry', 'origin/master', branch_name]
        logging.debug( ">>> VCS:Git::__nr_unmerged_commits" )
        logging.debug( "running '%s'", " ".join(command) )
        commits = self._run_shell_command(command, folder=self.__repo_folder)
        nr_commits = commits.count('\n')
        logging.debug( "--- output:" )
        logging.debug( commits )
        logging.debug( "<<< VCS:Git::__nr_unmerged_commits" )
        logging.info('Branch %s has %d unmerged commits.', branch_name,
                     nr_commits)
        return nr_commits

    def __get_repo(self):
        ''' Clone the repository if necessary, else pull it. '''
        self.__repo_folder = self.__determine_repo_folder_name()
        if os.path.exists(self.__repo_folder):
            logging.info('Updating Git repo %s in %s', self.url(),
                         self.__repo_folder)
            command = ['git', 'pull']
            logging.debug( ">>> VCS:Git::__get_repo" )
            logging.debug( "running '%s'", " ".join(command) )
            self._run_shell_command( command, folder=self.__repo_folder )
            logging.debug( "<<< VCS:Git::__get_repo" )
        else:
            logging.info('Cloning Git repo %s in %s', self.url(),
                         self.__repo_folder)
            # TODO: Add --no-checkout? --quiet? --depth 1?
            command = ['git', 'clone', self.__full_url(), self.__repo_folder]
            logging.debug( ">>> VCS:Git::__get_repo" )
            logging.debug( "running '%s'", " ".join(command) )
            self._run_shell_command( command )
            logging.debug( "<<< VCS:Git::__get_repo" )

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

    def __determine_repo_folder_name(self):
        url_parts = [part for part in self.url().split('/') if part]
        return os.path.join(os.getcwd(), 'repos', url_parts[-1])
