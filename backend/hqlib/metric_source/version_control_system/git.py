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

import datetime
import functools
import logging
import os
import pathlib
import urllib.request
from typing import Callable, List, Tuple

from hqlib.typing import DateTime
from ..abstract.version_control_system import VersionControlSystem, Branch


class Git(VersionControlSystem):
    """ Class representing a Git repository. """

    metric_source_name = 'Git'

    def __init__(self, *args, **kwargs) -> None:
        self.__branch_to_checkout: str = kwargs.pop('branch', '')
        self.__chdir = kwargs.pop('chdir', os.chdir)
        super().__init__(*args, **kwargs)
        self.__repo_folder: str = None

    def __hash__(self) -> int:
        return hash(self.name() + self.short_name() + self.url() + self.__branch_to_checkout)

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.branch() == other.branch()

    @functools.lru_cache(maxsize=1024)
    def _run_shell_command(self, shell_command: Tuple[str, ...], folder: str = '',
                           log_level: int = logging.WARNING) -> str:
        """ Invoke a shell and run the command. If a folder is specified, run the command in that folder. """
        if not self.__repo_folder:
            self.__get_repo()
        folder = self.__repo_folder if self.__repo_folder.exists() else folder
        return super()._run_shell_command(shell_command, folder=folder, log_level=log_level)

    def last_changed_date(self, path: str) -> DateTime:
        """ Return the date when the url was last changed in Git. """
        timestamp = self._run_shell_command(('git', 'log', '--format="%ct"', '-n', '1', path))
        if timestamp:
            try:
                return datetime.datetime.fromtimestamp(float(timestamp.strip('"\n')))
            except ValueError as reason:
                logging.error("Couldn't convert timestamp %s to datetime for path %s: %s", timestamp, path, reason)
        return datetime.datetime.min

    def branch(self) -> str:
        """ Return the checked out branch. """
        return self.__branch_to_checkout

    def branches(self, path: str) -> List[str]:  # pylint: disable=unused-argument
        """ Return a list of branch names for the master branch. """
        return self.__get_branches()

    def unmerged_branches(self, path: str, list_of_branches_to_ignore: List[str] = None,
                          re_of_branches_to_ignore: str = '',
                          list_of_branches_to_include: List[str] = None) -> List[Branch]:
        """ Return a dictionary of branch names and number of unmerged commits for each branch that has
            any unmerged commits. """
        unmerged_branches = [branch for branch in self.__get_branches(unmerged_only=True) if not
                             self._ignore_branch(branch, list_of_branches_to_ignore, re_of_branches_to_ignore,
                                                 list_of_branches_to_include)]
        return [Branch(name, self.__nr_unmerged_commits(name), self.last_changed_date(name))
                for name in unmerged_branches]

    @classmethod
    def branch_folder_for_branch(cls, trunk_url: str, branch: str) -> str:
        """ Return the branch folder for the specified branch. """
        return trunk_url + '/' + branch

    def __get_branches(self, unmerged_only: bool = False) -> List[str]:
        """ Get the (remote) branches for the repository. """
        command = ['git', 'branch', '--list', '--remote', '--no-color']
        if unmerged_only:
            command.append('--no-merged')
        return self.__valid_names(self._run_shell_command(tuple(command)),
                                  lambda name: bool(name and ' -> ' not in name and 'origin/master' not in name))

    def __nr_unmerged_commits(self, branch_name: str) -> int:
        """ Return whether the branch has unmerged commits. """
        logging.info('Checking for unmerged commits in branch %s.', branch_name)
        command = ('git', 'cherry', 'origin/master', branch_name)
        commits = self._run_shell_command(command)
        nr_commits = commits.count('\n')
        logging.info('Branch %s has %d unmerged commits.', branch_name, nr_commits)
        return nr_commits

    def __get_repo(self) -> None:
        """ Clone the repository if necessary, else pull it. """
        self.__repo_folder = self.__determine_repo_folder_name()
        command = ['git']
        if self.__repo_folder.exists():
            logging.info('Updating Git repo %s in %s', self.url(), self.__repo_folder)
            command.extend(['pull', '--prune'])
        else:
            branch_string = self.__branch_to_checkout or 'master'
            logging.info('Cloning Git repo %s (branch: %s) in %s', self.url(), branch_string, self.__repo_folder)
            command.extend(['clone', self.__full_url(), str(self.__repo_folder)])
            if self.__branch_to_checkout:
                command.insert(2, '--branch')
                command.insert(3, self.__branch_to_checkout)
        self._run_shell_command(tuple(command))

    def __full_url(self) -> str:
        """ Return the Git repository url with username and password. """
        if self._username and self._password:
            sep = '://'
            prefix, postfix = self.url().split(sep)
            url = prefix + sep + '{username}:{password}@' + postfix
            return url.format(username=self._username, password=urllib.request.pathname2url(self._password))
        return self.url()

    def __determine_repo_folder_name(self) -> pathlib.Path:
        url_parts = [part for part in self.url().split('/') if part]
        folder = url_parts[-1]
        if self.__branch_to_checkout:
            folder += '-{0!s}'.format(self.__branch_to_checkout)
        return pathlib.Path.cwd() / 'repos' / folder

    @staticmethod
    def __valid_names(text: str, is_valid: Callable[[str], bool] = bool) -> List[str]:
        """ Return the names in the text that are valid. """
        names = [name.strip() for name in text.strip().split('\n')]
        return [name for name in names if is_valid(name)]
