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
from qualitylib import metric, domain


class FakeSubversion(object):
    ''' Provide for a fake Subversion metric source. '''
    @staticmethod  # pylint: disable=unused-argument
    def unmerged_branches(*args):
        ''' Return the branches that have not been merged to the trunk. '''
        return {'branch2': 1, 'ignored branch': 2}

    @staticmethod  # pylint: disable=unused-argument
    def branches(*args):
        ''' Return the branches for a product. '''
        return ['branch1', 'branch2', 'ignored branch']


class FakeSubject(object):
    ''' Provide for a fake subject. '''

    def __init__(self, version=None):
        self.__version = version

    def __repr__(self):
        return 'FakeSubject'

    def product_version(self):
        ''' Return the fake version. '''
        return self.__version

    @staticmethod
    def svn_path():
        ''' Return the Subversion path of the subject. '''
        return 'http://svn/trunk'

    @staticmethod
    def branches_to_ignore():
        ''' Return the branches to ignore when checking for unmerged 
            branches. '''
        return ['ignored branch']


class UnmergedBranchesTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the unmerged branches metric. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__subversion = FakeSubversion()
        self.__project = domain.Project(subversion=self.__subversion)
        self.__subject = FakeSubject()
        self.__metric = metric.UnmergedBranches(subject=self.__subject,
                                                project=self.__project)

    def test_value(self):
        ''' Test that the value of the metric equals the number of unmerged 
            branches reported by Subversion. '''
        self.assertEqual(len(self.__subversion.unmerged_branches()) - 
                         len(self.__subject.branches_to_ignore()), 
                         self.__metric.value())

    def test_report(self):
        ''' Test that the report is correct. '''
        self.assertEqual('1 van de 3 branches van FakeSubject hebben ' \
                         'revisies die niet met de trunk zijn gemerged.', 
                         self.__metric.report())

    def test_url(self):
        ''' Test that the unmerged branches are listed. '''
        self.assertEqual({'branch2: 1 ongemergde revisie(s)': 
                          'http://svn/branches/branch2'}, self.__metric.url())

    def test_url_label(self):
        ''' Test that the label for the urls is correct. '''
        self.assertEqual('Niet gemergde branches', self.__metric.url_label())

    def test_comment_urls(self):
        ''' Test that the comment urls include a link to ignored branches. '''
        self.assertEqual({'ignored branch': 
                          'http://svn/branches/ignored branch'}, 
                         self.__metric.comment_urls())

    def test_comment_url_label(self):
        ''' Test the label for the comment urls. '''
        self.assertEqual('Genegeerde branches', 
                         self.__metric.comment_url_label())

    def test_can_be_measured(self):
        ''' Test that the metric can only be measured if the product is under
            version control and is the trunk version. '''
        self.failUnless(metric.UnmergedBranches.can_be_measured(self.__subject,
                                                                self.__project))

    def test_cant_be_measured(self):
        ''' Test that the metric can not be measured if the product is 
            a trunk version. '''
        self.failIf(metric.UnmergedBranches.can_be_measured(FakeSubject('1.1'),
                                                            self.__project))

    def test_cant_be_measured_without_subversion(self):
        ''' Test that the metric can not be measured if the project has 
            no Subversion. '''
        project = domain.Project()
        self.failIf(metric.UnmergedBranches.can_be_measured(self.__subject,
                                                            project))
