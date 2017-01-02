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

from hqlib.metric_source import Git


class GitUnderTest(Git):  # pylint: disable=too-few-public-methods
    """ Override the Git class to prevent it from running shell commands. """
    def _run_shell_command(self, command, *args, **kwargs):  # pylint: disable=unused-argument
        self.last_command = command  # pylint: disable=attribute-defined-outside-init
        return ''


class GitTests(unittest.TestCase):
    """ Unit tests for the Git class. """
    def setUp(self):
        self.__git = GitUnderTest(url='http://git/')

    def test_last_changed_date(self):
        """ Test that there is no last changed date for a missing repo. """
        self.assertEqual(datetime.datetime.min, self.__git.last_changed_date('path'))

    def test_tags(self):
        """ Test that there are no tags by default. """
        self.assertFalse(self.__git.tags('path'))

    def test_no_tags_folder_for_version(self):
        """ Test that there is no tags folder by default. """
        self.assertEqual('', self.__git.tags_folder_for_version('http://git/master', '1.1'))

    def test_branches(self):
        """ Test that there are no branches by default. """
        self.assertFalse(self.__git.branches('path'))

    def test_unmerged_branches(self):
        """ Test that there are no unmerged branches by default. """
        self.assertEqual({}, self.__git.unmerged_branches('http://git/'))

    def test_normalize_path(self):
        """ Test path that needs no changes. """
        self.assertEqual('http://git/master/', self.__git.normalize_path('http://git/master/'))

    def test_normalize_path_does_not_add_trailing_slash(self):
        """ Test that the normalized path has a trailing slash. """
        self.assertEqual('http://git/master', self.__git.normalize_path('http://git/master'))

    def test_encode_password(self):
        """ Test that the password is encoded. """
        git = GitUnderTest(url='http://git/', username='user', password='foo@bar')
        self.assertEqual('http://user:foo%40bar@git/', git.last_command[2])
