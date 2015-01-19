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

from qualitylib.metric_source import VersionControlSystem
import unittest
import logging
import StringIO
import subprocess


class VersionControlSystemTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the abstract version control system class. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__stream = None
        self.__run_shell_command_results = []
        self.__vcs = VersionControlSystem(
            run_shell_command=self.__run_shell_command)

    def __run_shell_command(self, *args):  # pylint: disable=unused-argument
        ''' Fake shell commands, by returning results one by one. '''
        self.__system_args = args
        result = self.__run_shell_command_results.pop(0)
        if result == 'raise':
            self.__stream = StringIO.StringIO()
            logging.getLogger().addHandler(logging.StreamHandler(self.__stream))
            raise subprocess.CalledProcessError(-1, 'command', '')
        else:
            return result

    def __assert_logged(self, log_message):
        ''' Check that the log message has actually been logged. '''
        self.__stream.seek(0)
        self.assertEqual(log_message, self.__stream.getvalue())

    def test_run_shell_command(self):
        ''' Test that a shell command can be run. '''
        self.__run_shell_command_results = ['expected result']
        self.assertEqual('expected result',
                         self.__vcs._run_shell_command(['dummy command']))

    def test_run_shell_command_non_existing_folder(self):
        ''' Test that running a shell command in a non-existing folder raises
            an exception. '''
        self.assertRaises(OSError, self.__vcs._run_shell_command, ['ls'],
                          'Non-existing folder')

    def test_log_exception(self):
        ''' Test that a failure is logged when a shell command fails. '''
        self.__run_shell_command_results = ['raise']
        self.__vcs._run_shell_command(['dummy command'])
        self.__assert_logged('Shell command failed: Command ' \
                         "'command' returned non-zero exit status -1\n")

    def test_re_raise(self):
        ''' Test that the run shell command method re raises the exception when
            the log level is higher than warning. '''
        self.__run_shell_command_results = ['raise']
        self.assertRaises(subprocess.CalledProcessError,
                          self.__vcs._run_shell_command, 'dummy command',
                          log_level=logging.ERROR)
