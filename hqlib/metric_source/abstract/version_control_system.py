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

import logging
import os
import re
import subprocess

from . import archive_system


class VersionControlSystem(archive_system.ArchiveSystem):
    """ Abstract base class for version control systems such as Subversion and Git. """

    metric_source_name = 'Version control system'
    needs_values_as_list = True
    needs_metric_source_id = True

    def __init__(self, username=None, password=None, url=None, run_shell_command=subprocess.check_output):
        self._username = username
        self._password = password
        self._shell_command = run_shell_command
        super(VersionControlSystem, self).__init__(url=url)

    def last_changed_date(self, url):
        """ Return the date when the url was last changed. """
        raise NotImplementedError  # pragma: no cover

    def branches(self, path):  # pylint: disable=unused-argument
        """ Return a list of branch names for the specified path. """
        raise NotImplementedError  # pragma: no cover

    def tags(self, path):  # pylint: disable=unused-argument
        """ Return a list of tag names for the specified path. """
        raise NotImplementedError  # pragma: no cover

    def unmerged_branches(self, path, list_of_branches_to_ignore=None, re_of_branches_to_ignore='',
                          list_of_branches_to_include=None):
        # pylint: disable=unused-argument
        """ Return a dictionary of branch names and number of unmerged revisions for each branch that has any
            unmerged revisions. Branches listed in the list of branches to ignore or that match the regular
            expression of branches to ignore are, obviously, ignored. """
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def branch_folder_for_branch(cls, trunk_url, branch):  # pylint: disable=unused-argument
        """ Return the branch folder for the specified branch. """
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def tags_folder_for_version(cls, trunk_url, version):  # pylint: disable=unused-argument
        """ Return the tags folder for the specified version. """
        return ''  # pragma: no cover

    def _run_shell_command(self, shell_command, folder=None, log_level=logging.WARNING):
        """ Invoke a shell and run the command. If a folder is specified, run the command in that folder. """
        original_working_dir = os.getcwd()
        if folder:
            os.chdir(folder)
        try:
            return self._shell_command(shell_command)
        except subprocess.CalledProcessError as reason:
            # No need to include the shell command in the log, because the reason contains the shell command.
            logging.log(log_level, 'Shell command failed: %s', reason)
            if log_level > logging.WARNING:
                raise
        finally:
            os.chdir(original_working_dir)

    @staticmethod
    def _parse_version(tag):
        """ Parse and return the version number from the tag. Returns the version as a two-tuple. The first
            element of the tuple is the version number as tuple of integers (for sorting). The second element
            of the tuple is the version number as text, including any postfix elements (e.g. 1.2.3-beta). """
        versions_in_tag = re.findall(r'[0-9]+(?:\.[0-9]+)+', tag)
        if versions_in_tag and 'emma' not in tag.lower():
            numbers = versions_in_tag[0].split('.')
            version_integer_tuple = tuple(int(number) for number in numbers)
            version_text = re.findall(r'[0-9].*', tag)[0]
        else:
            version_integer_tuple = (0, 0, 0)
            version_text = ''
        return version_integer_tuple, version_text
