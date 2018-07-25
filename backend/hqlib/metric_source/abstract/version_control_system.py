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
import re
import subprocess
from typing import Tuple, List

from hqlib.typing import DateTime
from hqlib import domain


class Branch:
    """ A branch in a version control system. """

    def __init__(self, name: str, nr_revisions: int = None, date_last_change: DateTime = datetime.datetime.min) -> None:
        self.name = name
        self.nr_revisions = nr_revisions
        self.date_last_change = date_last_change

    def __repr__(self):
        return "{0}({1}. {2}, {3})".format(self.__class__.__name__, self.name, self.nr_revisions, self.date_last_change)

    def __eq__(self, other: "Branch") -> bool:
        return self.name == other.name and self.nr_revisions == other.nr_revisions and \
            self.date_last_change == other.date_last_change


class VersionControlSystem(domain.MetricSource):
    """ Abstract base class for version control systems such as Subversion and Git. """

    metric_source_name = 'Version control system'

    def __init__(self, username: str = '', password: str = '', url: str = '',
                 run_shell_command=subprocess.check_output) -> None:
        self._username = username
        self._password = password
        self._shell_command = run_shell_command
        super().__init__(url=url)

    def last_changed_date(self, path: str) -> DateTime:
        """ Return the date when the url was last changed. """
        raise NotImplementedError

    @staticmethod
    def normalize_path(path: str) -> str:
        """ Return a normalized version of the path. """
        return path

    def branches(self, path: str) -> List[str]:  # pylint: disable=unused-argument
        """ Return a list of branch names for the specified path. """
        raise NotImplementedError

    def unmerged_branches(self, path: str, list_of_branches_to_ignore: List[str] = None,
                          re_of_branches_to_ignore: str = '',
                          list_of_branches_to_include: List[str] = None) -> List[Branch]:
        # pylint: disable=unused-argument
        """ Return a list of branches that have unmerged revisions. Branches listed in the list of branches to ignore
            or that match the regular expression of branches to ignore are, obviously, ignored. """
        raise NotImplementedError

    @staticmethod
    def _ignore_branch(branch_name: str, list_of_branches_to_ignore: List[str] = None,
                       re_of_branches_to_ignore: str = '',
                       list_of_branches_to_include: List[str] = None) -> bool:
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
        raise NotImplementedError

    @functools.lru_cache(maxsize=1024)
    def _run_shell_command(self, shell_command: Tuple[str, ...], folder: str = '',
                           log_level: int = logging.WARNING) -> str:
        """ Invoke a shell and run the command. If a folder is specified, run the command in that folder. """
        original_working_dir = os.getcwd()
        if folder:
            os.chdir(folder)
        try:
            return self._shell_command(shell_command, timeout=120, universal_newlines=True)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as reason:
            # No need to include the shell command in the log, because the reason contains the shell command.
            logging.log(log_level, 'Shell command in folder %s failed: %s', folder, reason)
            if log_level > logging.WARNING:
                raise
            else:
                return ''
        finally:
            os.chdir(original_working_dir)
