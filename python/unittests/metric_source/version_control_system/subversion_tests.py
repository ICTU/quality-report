"""
Copyright 2012-2016 Ministerie van Sociale Zaken en Werkgelegenheid

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

from qualitylib.metric_source import Subversion


class SubversionUnderTest(Subversion):
    """ Override the Subversion class to prevent it from running shell commands. """
    mergeinfo = ''

    def _run_shell_command(self, command, *args, **kwargs):
        self.last_command = command
        if command[1] == 'mergeinfo':
            return self.mergeinfo
        elif command[1] == 'list' and 'path' not in command[3]:
            return '<name>folder</name>'


class SubversionTests(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """ Unit tests for the Subversion class. """
    def setUp(self):
        self.__svn = SubversionUnderTest(url='http://svn/')

    def test_last_changed_date(self):
        """ Test that there is no last changed date for a missing repo. """
        self.assertEqual(datetime.datetime.min, self.__svn.last_changed_date('path'))

    def test_tags(self):
        """ Test that there are no tags by default. """
        self.failIf(self.__svn.tags('path'))

    def test_no_tags_folder_for_version(self):
        """ Test that there is no tags folder by default. """
        self.assertEqual('', self.__svn.tags_folder_for_version('http://svn/trunk', '1.1'))

    def test_branches(self):
        """ Test that there are no branches by default. """
        self.failIf(self.__svn.branches('path'))

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
        self.assertEqual({}, self.__svn.unmerged_branches('http://svn/', list_of_branches_to_ignore=['folder']))

    def test_one_unmerged_branch_that_is_ignored_with_re(self):
        """ Test one unmerged branch that is ignored. """
        self.__svn.mergeinfo = 'rev1\nrev2\nrev3\nrev4\nrev5'
        self.assertEqual({}, self.__svn.unmerged_branches('http://svn/', re_of_branches_to_ignore='f.*'))

    def test_normalize_path(self):
        """ Test path that needs no changes. """
        self.assertEqual('http://svn/trunk/', self.__svn.normalize_path('http://svn/trunk/'))

    def test_normalize_path_adds_trailing_slash(self):
        """ Test that the normalized path has a trailing slash. """
        self.assertEqual('http://svn/trunk/', self.__svn.normalize_path('http://svn/trunk'))

    def test_normalize_path_adds_trunk(self):
        """ Test that the normalized path has a trunk folder at the end. """
        self.assertEqual('http://svn/trunk/', self.__svn.normalize_path('http://svn'))

    def test_checkout(self):
        """ Test the check out command. """
        self.__svn.check_out('http://svn/trunk/', 'folder')
        self.assertEqual(['svn', 'co', 'http://svn/trunk/', 'folder'], self.__svn.last_command)

    def test_checkout_with_credentials(self):
        """ Test the check out command with credentials. """
        svn = SubversionUnderTest(url='http://svn/', username='john', password='doe')
        svn.check_out('http://svn/trunk/', 'folder')
        self.assertEqual(['svn', 'co', 'http://svn/trunk/', 'folder','--no-auth-cache',
                          '--username', 'john', '--password', 'doe'], svn.last_command)
