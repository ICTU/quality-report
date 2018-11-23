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

import os
import datetime
import unittest
from unittest.mock import patch
from pathlib import Path
import subprocess
from subprocess import CalledProcessError

from hqlib.metric_source import Git, VersionControlSystem, Branch


@patch.object(Path, 'exists')
class GitTests(unittest.TestCase):
    """ Unit tests for the Git class. """
    def setUp(self):
        # pylint: disable=protected-access
        VersionControlSystem._run_shell_command.cache_clear()
        Git._run_shell_command.cache_clear()
        Git._get_branches.cache_clear()
        self.__git = Git(url='http://git/')
        self.__git_branch = Git(url=self.__git.url(), branch='branch')

    def test_is_equal(self, mock_exists):
        """ Test that the branch is taken into account for equality. """
        mock_exists.return_value = True
        self.assertNotEqual(self.__git_branch, self.__git)

    def test_hash(self, mock_exists):
        """ Test that the branch is taken into account for the hash. """
        mock_exists.return_value = True
        self.assertNotEqual(hash(self.__git_branch), hash(self.__git))

    @patch.object(os, 'chdir')
    def test_last_changed_date(self, mock_chdir, mock_exists):
        """ Test that there is no last changed date for a missing repo. """
        mock_exists.return_value = True
        with patch.object(subprocess, "check_output", return_value=''):
            self.assertEqual(datetime.datetime.min, self.__git.last_changed_date('path'))
        mock_chdir.assert_called()

    @patch.object(os, 'chdir')
    def test_last_changed_date_with_repo(self, mock_chdir, mock_exists):
        """ Test the date with a (faked) repo. """
        mock_exists.return_value = True
        with patch.object(subprocess, "check_output", return_value='1490445344.0'):
            self.assertEqual(datetime.datetime.fromtimestamp(1490445344.0), self.__git_branch.last_changed_date('path'))
        mock_chdir.assert_called()

    @patch.object(os, 'chdir')
    def test_branches(self, mock_chdir, mock_exists):
        """ Test that there are no branches by default. """
        mock_exists.return_value = True
        with patch.object(subprocess, "check_output", return_valie=''):
            self.assertFalse(self.__git.branches('path'))
        mock_chdir.assert_called()

    @patch.object(os, 'chdir')
    def test_unmerged_branches(self, mock_chdir, mock_exists):
        """ Test that there are no unmerged branches by default. """
        mock_exists.return_value = True
        with patch.object(subprocess, "check_output", return_valie=''):
            self.assertEqual([], self.__git.unmerged_branches('http://git/'))
        mock_chdir.assert_called()

    @patch.object(os, 'chdir')
    def test_unmerged_branches_with_repo(self, mock_chdir, mock_exists):
        """ Test the unmerged branches with a (faked) repo. """
        mock_exists.return_value = True
        expected_datetime = datetime.datetime.fromtimestamp(1490445344.0)
        with patch.object(subprocess, "check_output",
                          side_effect=["pull output", "branch\n", "commit_id\n", "1490445344.0\n"]):
            branches = self.__git.unmerged_branches('path')
        self.assertEqual([Branch("branch", 1, expected_datetime)], branches)
        mock_chdir.assert_called()

    @patch.object(os, 'chdir')
    def test_unmerged_branches_invalid_date(self, mock_chdir, mock_exists):
        """ Test that the last change date of a branch is the minimum date if parsing fails. """
        mock_exists.return_value = True
        with patch.object(subprocess, "check_output",
                          side_effect=["pull output", "branch\n", "commit_id\n", "invalid_date\n"]):
            self.assertEqual([Branch("branch", 1, datetime.datetime.min)], self.__git.unmerged_branches('path'))
        mock_chdir.assert_called()

    def test_normalize_path(self, mock_exists):
        """ Test path that needs no changes. """
        mock_exists.return_value = True
        self.assertEqual('http://git/master/', self.__git.normalize_path('http://git/master/'))

    def test_normalize_path_does_not_add_trailing_slash(self, mock_exists):
        """ Test that the normalized path doesn't have a trailing slash. """
        mock_exists.return_value = True
        self.assertEqual('http://git/master', self.__git.normalize_path('http://git/master'))

    def test_branch_folder_for_branch(self, mock_exists):
        """ Test that a branch folder can be created from a trunk folder and a branch name. """
        mock_exists.return_value = True
        self.assertEqual('http://git/master/branch',
                         self.__git.branch_folder_for_branch('http://git/master', 'branch'))


class GitTestsWhenCloningFails(unittest.TestCase):
    """ Unit tests for the Git class, when there is no repo and cloning fails. """
    def setUp(self):
        # pylint: disable=protected-access
        VersionControlSystem._run_shell_command.cache_clear()
        Git._run_shell_command.cache_clear()
        Git._get_branches.cache_clear()
        self.__git = Git(url='http://git/')

    def test_last_changed_date_when_cloning_fails(self):
        """ Test that there is no last changed date for a missing repo. """
        with patch.object(subprocess, "check_output", side_effect=[CalledProcessError(128, [])]) as mock_check_output:
            self.assertEqual(datetime.datetime.min, self.__git.last_changed_date('path'))
            self.assertEqual(("git", "clone", "http://git/"), mock_check_output.call_args[0][0][:3])

    def test_branches(self):
        """ Test that the branches of a missing repo are None. """
        with patch.object(subprocess, "check_output", side_effect=[CalledProcessError(128, [])]) as mock_check_output:
            self.assertEqual(None, self.__git.branches('path'))
            self.assertEqual(("git", "clone", "http://git/"), mock_check_output.call_args[0][0][:3])

    def test_branches_for_non_master(self):
        """ Test that the branches of a missing repo of a non-master branch are None. """
        git = Git(url='http://git/', branch='another', username='un', password='pwd')
        with patch.object(subprocess, "check_output", side_effect=[CalledProcessError(128, [])]) as mock_check_output:
            self.assertEqual(None, git.branches('path'))
            self.assertEqual(("git", "clone", "--branch", "another", "http://un:pwd@git/"),
                             mock_check_output.call_args[0][0][:5])

    def test_unmerged_branches(self):
        """ Test that the unmerged branches of a missing repo are None. """
        with patch.object(subprocess, "check_output", side_effect=[CalledProcessError(128, [])]) as mock_check_output:
            self.assertEqual(None, self.__git.unmerged_branches('path'))
            self.assertEqual(("git", "clone", "http://git/"), mock_check_output.call_args[0][0][:3])
