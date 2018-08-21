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
from unittest.mock import patch, MagicMock
from pathlib import Path
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
        self.__git = Git(url='http://git/', run_shell_command=lambda *args, **kwargs: '')
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
        self.assertEqual(datetime.datetime.min, self.__git.last_changed_date('path'))
        mock_chdir.assert_called()

    @patch.object(os, 'chdir')
    def test_last_changed_date_with_repo(self, mock_chdir, mock_exists):
        """ Test the date with a (faked) repo. """
        mock_exists.return_value = True
        git = Git(url=self.__git.url(), run_shell_command=lambda *args, **kwargs: '1490445344.0', branch='branch')
        self.assertEqual(datetime.datetime.fromtimestamp(1490445344.0), git.last_changed_date('path'))
        mock_chdir.assert_called()

    @patch.object(os, 'chdir')
    def test_branches(self, mock_chdir, mock_exists):
        """ Test that there are no branches by default. """
        mock_exists.return_value = True
        self.assertFalse(self.__git.branches('path'))
        mock_chdir.assert_called()

    @patch.object(os, 'chdir')
    def test_unmerged_branches(self, mock_chdir, mock_exists):
        """ Test that there are no unmerged branches by default. """
        mock_exists.return_value = True
        self.assertEqual([], self.__git.unmerged_branches('http://git/'))
        mock_chdir.assert_called()

    @patch.object(os, 'chdir')
    def test_unmerged_branches_with_repo(self, mock_chdir, mock_exists):
        """ Test the unmerged branches with a (faked) repo. """
        mock_exists.return_value = True
        git = Git(
            url=self.__git.url(),
            username='u', password='p',
            run_shell_command=lambda *args, **kwargs: "1490445344.0\n" if "log" in args[0] else "branch\n"
        )
        expected_datetime = datetime.datetime.fromtimestamp(1490445344.0)
        result = git.unmerged_branches('path')
        self.assertEqual([Branch("branch", 1, expected_datetime)], result)
        mock_chdir.assert_called()

    @patch.object(os, 'chdir')
    def test_unmerged_branches_invalid_date(self, mock_chdir, mock_exists):
        """ Test that the last change date of a branch is the minimum date if parsing fails. """
        mock_exists.return_value = True
        git = Git(
            url=self.__git.url(),
            username='u', password='p',
            run_shell_command=lambda *args, **kwargs: "invalid date\n" if "show" in args[0] else "branch\n"
        )
        self.assertEqual([Branch("branch", 1, datetime.datetime.min)], git.unmerged_branches('path'))
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
        self.__shell_exec_mock = MagicMock(side_effect=CalledProcessError(128, []))
        self.__git = Git(url='http://git/', run_shell_command=self.__shell_exec_mock)

    def tearDown(self):
        self.__shell_exec_mock.assert_called_once()
        self.assertEqual('git', self.__shell_exec_mock.call_args[0][0][0])
        self.assertEqual('clone', self.__shell_exec_mock.call_args[0][0][1])

    def test_last_changed_date_when_cloning_fails(self):
        """ Test that there is no last changed date for a missing repo. """
        self.assertEqual(datetime.datetime.min, self.__git.last_changed_date('path'))
        self.assertEqual('http://git/', self.__shell_exec_mock.call_args[0][0][2])

    def test_branches(self):
        """ Test that the branches of a missing repo are None. """
        self.assertEqual(None, self.__git.branches('path'))
        self.assertEqual('http://git/', self.__shell_exec_mock.call_args[0][0][2])

    def test_branches_for_non_master(self):
        """ Test that the branches of a missing repo of a non-master branch are None. """
        self.__git = Git(url='http://git/', run_shell_command=self.__shell_exec_mock,
                         branch='another', username='un', password='pwd')
        self.assertEqual(None, self.__git.branches('path'))
        self.assertEqual('--branch', self.__shell_exec_mock.call_args[0][0][2])
        self.assertEqual('another', self.__shell_exec_mock.call_args[0][0][3])
        self.assertEqual('http://un:pwd@git/', self.__shell_exec_mock.call_args[0][0][4])

    def test_unmerged_branches(self):
        """ Test that the unmerged branches of a missing repo are None. """
        self.assertEqual(None, self.__git.unmerged_branches('path'))
        self.assertEqual('http://git/', self.__shell_exec_mock.call_args[0][0][2])
