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


import functools
import logging
import os
import re
import subprocess

from typing import Tuple, List

from . import archive_system


class VersionControlSystem(archive_system.ArchiveSystem):
    """ Abstract base class for version control systems such as Subversion and Git. """

    metric_source_name = 'Version control system'
    needs_metric_source_id = True

    def __init__(self, username: str='', password: str='', url: str=None,
                 run_shell_command=subprocess.check_output) -> None:
        self._username = username
        self._password = password
        self._shell_command = run_shell_command
        super().__init__(url=url)

    def last_changed_date(self, url: str):
        """ Return the date when the url was last changed. """
        raise NotImplementedError  # pragma: no cover

    def branches(self, path: str) -> List[str]:  # pylint: disable=unused-argument
        """ Return a list of branch names for the specified path. """
        raise NotImplementedError  # pragma: no cover

    def unmerged_branches(self, path, list_of_branches_to_ignore=None, re_of_branches_to_ignore='',
                          list_of_branches_to_include=None):
        # pylint: disable=unused-argument
        """ Return a dictionary of branch names and number of unmerged revisions for each branch that has any
            unmerged revisions. Branches listed in the list of branches to ignore or that match the regular
            expression of branches to ignore are, obviously, ignored. """
        raise NotImplementedError  # pragma: no cover

    @staticmethod
    def _ignore_branch(branch_name, list_of_branches_to_ignore=None, re_of_branches_to_ignore='',
                       list_of_branches_to_include=None) -> bool:
        """ Return whether the branch should be ignored. """
        if list_of_branches_to_include and branch_name not in list_of_branches_to_include:
            return True
        if list_of_branches_to_ignore and branch_name in list_of_branches_to_ignore:
            return True
        if re_of_branches_to_ignore and re.match(re_of_branches_to_ignore, branch_name):
            return True
        return False

    @classmethod
    def branch_folder_for_branch(cls, trunk_url: str, branch: str) -> str:  # pylint: disable=unused-argument
        """ Return the branch folder for the specified branch. """
        raise NotImplementedError  # pragma: no cover

    @functools.lru_cache(maxsize=1024)
    def _run_shell_command(self, shell_command: Tuple[str, ...], folder: str='', log_level: int=logging.WARNING) -> str:
        """ Invoke a shell and run the command. If a folder is specified, run the command in that folder. """
        original_working_dir = os.getcwd()
        if folder:
            os.chdir(folder)
        try:
            return self._shell_command(shell_command, universal_newlines=True)
        except subprocess.CalledProcessError as reason:
            # No need to include the shell command in the log, because the reason contains the shell command.
            logging.log(log_level, 'Shell command in folder %s failed: %s', folder, reason)
            if log_level > logging.WARNING:
                raise
            else:
                return ''
        finally:
            os.chdir(original_working_dir)
