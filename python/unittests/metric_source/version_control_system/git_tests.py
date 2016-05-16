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

from qualitylib.metric_source import Git


class GitUnderTest(Git):
    """ Override the Git class to prevent it from running shell commands. """
    def _run_shell_command(self, command, *args, **kwargs):
        self.last_command = command
        return ''


class GitTests(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """ Unit tests for the Git class. """
    def setUp(self):
        self.__git = GitUnderTest(url='http://git/')

    def test_last_changed_date(self):
        """ Test that there is no last changed date for a missing repo. """
        self.assertEqual(datetime.datetime.min, self.__git.last_changed_date('path'))

    def test_tags(self):
        """ Test that there are no tags by default. """
        self.failIf(self.__git.tags('path'))

    def test_no_tags_folder_for_version(self):
        """ Test that there is no tags folder by default. """
        self.assertEqual('', self.__git.tags_folder_for_version('http://git/master', '1.1'))

    def test_branches(self):
        """ Test that there are no branches by default. """
        self.failIf(self.__git.branches('path'))

    def test_unmerged_branches(self):
        """ Test that there are no unmerged branches by default. """
        self.assertEqual({}, self.__git.unmerged_branches('http://git/'))

    def test_normalize_path(self):
        """ Test path that needs no changes. """
        self.assertEqual('http://git/master/', self.__git.normalize_path('http://git/master/'))

    def test_normalize_path_does_not_add_trailing_slash(self):
        """ Test that the normalized path has a trailing slash. """
        self.assertEqual('http://git/master', self.__git.normalize_path('http://git/master'))

    def test_checkout(self):
        """ Test the check out command. """
        self.__git.check_out('http://git/master/', 'folder')
        self.assertEqual(['git', 'clone', 'http://git/'], self.__git.last_command[:3])
