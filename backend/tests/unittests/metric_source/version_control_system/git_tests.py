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
import unittest

from hqlib.metric_source import Git, VersionControlSystem


class GitTests(unittest.TestCase):
    """ Unit tests for the Git class. """
    def setUp(self):
        self.__git = Git(url='http://git/', run_shell_command=lambda *args, **kwargs: '')
        self.__git_branch = Git(url=self.__git.url(), branch='branch')

    def test_is_equal(self):
        """ Test that the branch is taken into account for equality. """
        self.assertNotEqual(self.__git_branch, self.__git)

    def test_hash(self):
        """ Test that the branch is taken into account for the hash. """
        self.assertNotEqual(hash(self.__git_branch), hash(self.__git))

    def test_last_changed_date(self):
        """ Test that there is no last changed date for a missing repo. """
        self.assertEqual(datetime.datetime.min, self.__git.last_changed_date('path'))

    def test_last_changed_date_with_repo(self):
        """ Test the date with a (faked) repo. """
        VersionControlSystem._run_shell_command.cache_clear()
        Git._run_shell_command.cache_clear()
        git = Git(url=self.__git.url(), run_shell_command=lambda *args, **kwargs: '1490445344.0', branch='branch')
        self.assertEqual(datetime.datetime.fromtimestamp(1490445344.0), git.last_changed_date('path'))

    def test_branches(self):
        """ Test that there are no branches by default. """
        self.assertFalse(self.__git.branches('path'))

    def test_unmerged_branches(self):
        """ Test that there are no unmerged branches by default. """
        self.assertEqual({}, self.__git.unmerged_branches('http://git/'))

    def test_unmerged_branches_with_repo(self):
        """ Test the unmerged branches with a (faked) repo. """
        VersionControlSystem._run_shell_command.cache_clear()
        Git._run_shell_command.cache_clear()
        git = Git(url=self.__git.url(), username='u', password='p',
                  run_shell_command=lambda *args, **kwargs: 'branch\n')
        self.assertEqual(dict(branch=1), git.unmerged_branches('path'))

    def test_normalize_path(self):
        """ Test path that needs no changes. """
        self.assertEqual('http://git/master/', self.__git.normalize_path('http://git/master/'))

    def test_normalize_path_does_not_add_trailing_slash(self):
        """ Test that the normalized path doesn't have a trailing slash. """
        self.assertEqual('http://git/master', self.__git.normalize_path('http://git/master'))

    def test_branch_folder_for_branch(self):
        """ Test that a branch folder can be created from a trunk folder and a branch name. """
        self.assertEqual('http://git/master/branch',
                         self.__git.branch_folder_for_branch('http://git/master', 'branch'))
