'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import unittest
import datetime
import logging

from qualitylib.metric_source import Git


class GitUnderTest(Git):
    ''' Override to adapt the run shell command method. '''
    def __init__(self, shell_command_results=None, *args, **kwargs):
        self.shell_commands = []  # List to collect executed commands
        self.__shell_command_results = shell_command_results
        super(GitUnderTest, self).__init__(*args, **kwargs)

    def _run_shell_command(self, shell_command, folder=None,
                           log_level=logging.WARNING):
        self.shell_commands.append(shell_command)
        return self.__shell_command_results.pop(0)


class GitTests(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the Git class. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__shell_command_results = ['fake result for initial clone']
        self.__stream = None
        self.__git = GitUnderTest(
            shell_command_results=self.__shell_command_results)

    def test_normalize_path(self):
        ''' Test that git paths don't change when normalized. '''
        self.assertEqual('path', self.__git.normalize_path('path'))

    def test_last_changed_date(self):
        ''' Test that Git correctly reports the date a path was last
            changed. '''
        self.__shell_command_results.append('''1416471398\n''')
        self.assertEqual(datetime.datetime(2014, 11, 20, 9, 16, 38),
                         self.__git.last_changed_date('path'))

    def test_latest_tagged_product_version(self):
        ''' Test that the product has no latest tagged version by default. '''
        self.assertFalse(self.__git.latest_tagged_product_version('path'))

    def test_no_unmerged_branches(self):
        ''' Test that the product has no unmerged branches by default. '''
        self.__shell_command_results.append('''* master\n''')
        self.assertFalse(self.__git.unmerged_branches('path'))

    def test_one_unmerged_branch(self):
        ''' Test that the product has no unmerged branches by default. '''
        self.__shell_command_results.extend(
            ['* master\n  branch\n',
             '+ 18b4d7d2ef98fc5efc226c41502fabc99f478478\n'])
        self.assertEqual(dict(branch=1), self.__git.unmerged_branches('path'))

    def test_no_branches(self):
        ''' Test that the product has no branches by default. '''
        self.__shell_command_results.append('''* master\n''')
        self.assertFalse(self.__git.branches('path'))

    def test_one_branch(self):
        ''' Test branches when the product has a branch. '''
        self.__shell_command_results.append('''* master\n  branch\n''')
        self.assertEqual(['branch'], self.__git.branches('path'))

    def test_username_password(self):
        ''' Test that a correct url is constructed when a username and password
            is provided to git. '''
        self.__shell_command_results.append('')
        git = GitUnderTest(username='user', password='pass', url='http://repo/',
                           shell_command_results=self.__shell_command_results)
        self.assertEqual('http://user:pass@repo/', git.shell_commands[0][2])