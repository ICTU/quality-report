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

import logging
import subprocess
import unittest
from unittest.mock import patch

from hqlib.metric_source import VersionControlSystem


class VersionControlSystemTests(unittest.TestCase):
    """ Unit tests for the version control system class. """

    def test_ignore_branch_not_in_includes(self):
        """ Test that branches not in the list of branches to include are ignored. """
        self.assertTrue(VersionControlSystem._ignore_branch('foo', list_of_branches_to_include=['bar']))

    def test_ignore_branch_in_ignore_list(self):
        """ Test that branches in the list of branches to ignore are ignored. """
        self.assertTrue(VersionControlSystem._ignore_branch('foo', list_of_branches_to_ignore=['foo']))

    def test_ignore_branch_that_matches(self):
        """ Test that branches that match the regular expression of branches to ignore are ignored. """
        self.assertTrue(VersionControlSystem._ignore_branch('foobar', re_of_branches_to_ignore='foo.*'))

    def test_do_not_ignore_branches_by_default(self):
        """ Test that branches are not ignored by default. """
        self.assertFalse(VersionControlSystem._ignore_branch('foo'))

    # pylint: disable=protected-access

    def test_run_shell_command(self):
        """ Test that the result of the shell command is returned. """
        mock_shell_command = unittest.mock.Mock(return_value="success")
        vcs = VersionControlSystem(run_shell_command=mock_shell_command)
        self.assertEqual("success", vcs._run_shell_command(shell_command=("ls",)))

    @patch("os.chdir")
    def test_run_shell_command_chdir(self, mock_chdir):  # pylint: disable=no-self-use
        """ Test that shell command is run in the correct folder. """
        vcs = VersionControlSystem(run_shell_command=unittest.mock.Mock())
        vcs._run_shell_command(shell_command=("ls",), folder="test")
        mock_chdir.assert_any_call("test")

    def test_run_shell_command_exception(self):
        """ Test that the result is the empty string if an exception occurs. """
        mock_shell_command = unittest.mock.Mock(side_effect=subprocess.CalledProcessError(1, "ls"))
        vcs = VersionControlSystem(run_shell_command=mock_shell_command)
        self.assertEqual("", vcs._run_shell_command(shell_command=("ls",)))

    def test_run_shell_command_exception_reraise(self):
        """ Test that any exception is reraised if the log level is higher than warning. """
        mock_shell_command = unittest.mock.Mock(side_effect=subprocess.CalledProcessError(1, "ls"))
        vcs = VersionControlSystem(run_shell_command=mock_shell_command)
        self.assertRaises(subprocess.CalledProcessError, vcs._run_shell_command, shell_command=("ls",),
                          log_level=logging.ERROR)
