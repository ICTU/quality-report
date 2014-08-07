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

from qualitylib.metric_source import Subversion, SubversionFolder
import datetime
import logging
import unittest
import StringIO
import subprocess


class SubversionTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the Subversion class. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__run_shell_command_results = ['r123']
        self.__system_args = ()
        self.__stream = None
        self.__subversion = Subversion( \
                                run_shell_command=self.__shell_command)

    def __shell_command(self, args):  # pylint: disable=unused-argument
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

    def test_latest_tagged_product_version(self):
        ''' Test that the latest tagged product version is correct. '''
        self.__run_shell_command_results = ['<name>product-1.2.3</name>' \
                                            '<name>product-1.2.4-emma</name']
        self.assertEqual('1.2.3', 
            self.__subversion.latest_tagged_product_version('product url'))

    def test_latest_tagged_product_version_with_error(self):
        ''' Test that the version is None when Subversion can't be reached. '''
        self.assertEqual(None, 
            self.__subversion.latest_tagged_product_version('raise HTTPError'))

    def test_branches(self):
        ''' Test that Subversion returns a list of branches for a product. '''
        self.__run_shell_command_results = ['<name>product-1.2.3</name>' \
                                            '<name>product-1.2.3-emma</name>']
        self.assertEqual(['product-1.2.3', 'product-1.2.3-emma'], 
                         self.__subversion.branches('product_url/trunk/'))

    def test_tags(self):
        ''' Test that Subversion returns a list of tags for a product. '''
        self.__run_shell_command_results = ['<name>product-1.2.3</name>']
        self.assertEqual(['product-1.2.3'],
                         self.__subversion.tags('product_url/trunk/'))

    def test_tags_folder_for_version(self):
        ''' Test that Subversion returns the tags folder for a specific
            product version. '''
        self.__run_shell_command_results = ['<name>product-1.2.3</name>']
        self.assertEqual('product_url/tags/product-1.2.3/',
            self.__subversion.tags_folder_for_version('product_url/trunk/',
                                                      '1.2.3'))

    def test_no_tags_folder_for_version(self):
        ''' Test that Subversion returns nothing when the tags folder for a 
            specific product version doesn't exist. '''
        self.__run_shell_command_results = ['<name>product-2.1</name>']
        self.assertEqual('',
            self.__subversion.tags_folder_for_version('product_url/trunk/',
                                                      '1.2.3'))

    def test_unmerged_branches(self):
        ''' Test that Subversion returns a list of branches for a product. '''
        self.__run_shell_command_results = ['<name>product-1.2.3</name>' \
                                            '<name>product-1.2.3-emma</name>',
                                            'r123\nr124\n', 
                                            '<url>bla</url>', 
                                            '<url>bla</url>', '\n']
        self.assertEqual({'product-1.2.3': 2}, 
            self.__subversion.unmerged_branches('product_url/trunk/'))

    def test_unmerged_branches_with_tag_revision(self):
        ''' Test that Subversion ignores revisions made on tags (Maven
            release plugin does this). '''
        self.__run_shell_command_results = ['<name>product-1.2.3</name>' \
                                            '<name>product-1.2.3-emma</name>',
                                            'r123\nr124\n', 
                                            '<url>http://tags/rev123</url>', 
                                            '<url>http://branch/rev124/url>',
                                            '\n']
        self.assertEqual({'product-1.2.3': 1}, 
            self.__subversion.unmerged_branches('product_url/trunk/'))

    def test_check_out(self):
        ''' Test that Subversion can check out. '''    
        self.__subversion.check_out('svn_path', 'folder')
        self.assertEqual('svn co svn_path folder', 
                         ' '.join(self.__system_args))

    def test_check_out_with_credentials(self):
        ''' Test that Subversion can check out. '''
        subversion = Subversion(username='username', password='password',
                                run_shell_command=self.__shell_command)
        subversion.check_out('svn_path', 'folder')
        self.assertEqual('svn co svn_path folder --no-auth-cache ' \
                         '--username username --password password', 
                         ' '.join(self.__system_args))

    def test_last_changed_date(self):
        ''' Test that Subversion correctly reports the date a url was last
            changed. '''
        self.__run_shell_command_results = [
'''<?xml version="1.0" encoding="UTF-8"?>
<info>
    <entry kind="dir" path="lrk" revision="22537">
        <url>http://svn.lrk.org/lrk</url>
        <repository>
            <root>http://svn.lrk.org/lrk</root>
            <uuid>628f2182-6271-4ebc-b737-691fb6c682ec</uuid>
        </repository>
        <commit revision="22537">
            <author>jenkins</author>
            <date>2014-01-27T09:33:09.907516Z</date>
        </commit>
    </entry>
</info>
''']
        self.assertEqual(datetime.datetime(2014, 1, 27, 9, 33, 9, 907516), 
                         self.__subversion.last_changed_date('svn_path'))

    def test_log_exception(self):
        ''' Test that a failure is logged when svn info fails. '''
        self.__run_shell_command_results = ['raise']
        self.assertRaises(IndexError,
                          self.__subversion.last_changed_date, 'svn_path')
        self.__assert_logged('Shell command failed: Command ' \
                         "'command' returned non-zero exit status -1\n")

    def test_log_and_raise_exception(self):
        ''' Test that a failure is logged and raised when svn co fails. '''
        self.__run_shell_command_results = ['raise']
        self.assertRaises(subprocess.CalledProcessError, 
                          self.__subversion.check_out, 'svn_path', 'folder')
        self.__assert_logged('Shell command failed: Command ' \
                         "'command' returned non-zero exit status -1\n")


class SubversionFolderTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the SubversionFolder class. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__subversion = SubversionFolder('name', 'http://svn', 
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
