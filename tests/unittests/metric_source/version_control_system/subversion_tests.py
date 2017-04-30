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

import datetime
import unittest

from hqlib.metric_source import Subversion


class SubversionUnderTest(Subversion):
    """ Override the Subversion class to prevent it from running shell commands. """
    mergeinfo = ''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_command = None

    def _run_shell_command(self, command, *args, **kwargs):  # pylint: disable=unused-argument
        self.last_command = command
        if command[1] == 'mergeinfo':
            return self.mergeinfo
        elif command[1] == 'list' and 'path' not in command[3]:
            return '<name>folder</name>'


class SubversionTests(unittest.TestCase):
    """ Unit tests for the Subversion class. """
    def setUp(self):
        self.__svn = SubversionUnderTest(url='http://svn/')

    def test_last_changed_date(self):
        """ Test that there is no last changed date for a missing repo. """
        self.assertEqual(datetime.datetime.min, self.__svn.last_changed_date('path'))

    def test_branches(self):
        """ Test that there are no branches by default. """
        self.assertFalse(self.__svn.branches('path'))

    def test_unmerged_branches(self):
        """ Test that there are no unmerged branches by default. """
        self.assertEqual({}, self.__svn.unmerged_branches('http://svn/'))

    def test_one_unmerged_branch(self):
        """ Test one unmerged branch. """
        self.__svn.mergeinfo = 'rev1\nrev2\nrev3\nrev4\nrev5'
        self.assertEqual(dict(folder=5), self.__svn.unmerged_branches('http://svn/'))

    def test_one_unmerged_branch_that_is_ignored(self):
        """ Test one unmerged branch that is ignored. """
        self.__svn.mergeinfo = 'rev1\nrev2\nrev3\nrev4\nrev5'
        self.assertEqual(dict(), self.__svn.unmerged_branches('http://svn/', list_of_branches_to_ignore=['folder']))

    def test_one_unmerged_branch_that_is_ignored_with_re(self):
        """ Test one unmerged branch that is ignored. """
        self.__svn.mergeinfo = 'rev1\nrev2\nrev3\nrev4\nrev5'
        self.assertEqual(dict(), self.__svn.unmerged_branches('http://svn/', re_of_branches_to_ignore='f.*'))

    def test_one_unmerged_branch_that_is_included(self):
        """ Test that the unmerged branch is returned when it is explicitly included. """
        self.__svn.mergeinfo = 'rev1\nrev2\nrev3\nrev4\nrev5'
        self.assertEqual(dict(folder=5), self.__svn.unmerged_branches('http://svn/',
                                                                      list_of_branches_to_include=['folder']))

    def test_one_unmerged_branch_that_is_not_included(self):
        """ Test that the unmerged branch is returned when it is explicitly included. """
        self.__svn.mergeinfo = 'rev1\nrev2\nrev3\nrev4\nrev5'
        self.assertEqual(dict(), self.__svn.unmerged_branches('http://svn/', list_of_branches_to_include=['other']))

    def test_normalize_path(self):
        """ Test path that needs no changes. """
        self.assertEqual('http://svn/trunk/', self.__svn.normalize_path('http://svn/trunk/'))

    def test_normalize_path_adds_trailing_slash(self):
        """ Test that the normalized path has a trailing slash. """
        self.assertEqual('http://svn/trunk/', self.__svn.normalize_path('http://svn/trunk'))

    def test_normalize_path_adds_trunk(self):
        """ Test that the normalized path has a trunk folder at the end. """
        self.assertEqual('http://svn/trunk/', self.__svn.normalize_path('http://svn'))

    def test_branch_folder_for_branch(self):
        """ Test that a branch folder can be created from a trunk folder and a branch name. """
        self.assertEqual('http://svn/branches/branch/',
                         self.__svn.branch_folder_for_branch('http://svn/trunk/', 'branch'))
