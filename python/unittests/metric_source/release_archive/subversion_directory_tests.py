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

from qualitylib.metric_source import SubversionDirectory
import datetime
import unittest


class SubversionFolderTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the SubversionFolder class. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__subversion = SubversionDirectory('name', 'http://svn',
                                run_shell_command=self.__run_shell_command)

    @staticmethod
    def __run_shell_command(url):  # pylint: disable=unused-argument
        ''' Fake running svn info. '''
        return '''Path: releases
URL: http://svn.asv.org/asv/releases
Repository Root: http://svn.asv.org/asv
Repository UUID: 4c6f906b-359e-4d83-a601-e16127607476
Revision: 264
Node Kind: directory
Last Changed Author: gakoj
Last Changed Rev: 255
Last Changed Date: 2013-02-08 10:01:43 +0100 (vr, 08 feb 2013)

'''

    def test_name(self):
        ''' Test that the name is correct. '''
        self.assertEqual('name', self.__subversion.name())

    def test_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual('http://svn', self.__subversion.url())

    def test_date_of_most_recent_file(self):
        ''' Test that the date is correctly parsed. '''
        self.assertEqual(datetime.datetime(2013, 2, 8, 10, 1, 43),
                         self.__subversion.date_of_most_recent_file())
