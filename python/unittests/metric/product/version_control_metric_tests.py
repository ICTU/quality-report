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

import unittest

from qualitylib import metric, domain, metric_source


class FakeSubversion(object):
    """ Provide for a fake Subversion metric source. """

    metric_source_name = 'FakeSubversion'

    @staticmethod
    def unmerged_branches(*args):  # pylint: disable=unused-argument
        """ Return the branches that have not been merged to the trunk. """
        return {'branch2': 1}

    @staticmethod
    def branches(*args):  # pylint: disable=unused-argument
        """ Return the branches for a product. """
        return ['branch1', 'branch2']

    @staticmethod
    def branch_folder_for_branch(*args):  # pylint: disable=unused-argument
        """ Return the branch folder for the branch. """
        return 'http://branch/'

    @staticmethod
    def normalize_path(svn_path):
        """ Return a normalized version of the path. """
        return svn_path


class UnmergedBranchesTest(unittest.TestCase):
    """ Unit tests for the unmerged branches metric. """

    def setUp(self):
        self.__subversion = FakeSubversion()
        self.__project = domain.Project(metric_sources={metric_source.VersionControlSystem: self.__subversion})
        self.__subject = domain.Product(
            self.__project, name='Product',
            short_name='PR',
            metric_source_ids={self.__subversion: 'http://svn/trunk/foo/'},
            metric_options={
                metric.UnmergedBranches: dict(
                    branches_to_include=['branch', 'ignored branch'],
                    branches_to_ignore=['ignored branch'],
                    branches_to_ignore_re='feature.*')})
        self.__metric = metric.UnmergedBranches(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that the value of the metric equals the number of unmerged branches reported by Subversion. """
        expected_value = len(self.__subversion.unmerged_branches())
        self.assertEqual(expected_value, self.__metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertEqual('1 van de 2 branches van Product hebben revisies die niet met de trunk zijn gemerged.',
                         self.__metric.report())

    def test_url(self):
        """ Test that the unmerged branches are listed. """
        self.assertEqual({'branch2: 1 ongemergde revisie(s)': 'http://branch/'}, self.__metric.url())

    def test_url_label(self):
        """ Test that the label for the urls is correct. """
        self.assertEqual('Niet gemergde branches', self.__metric.url_label())

    def test_comment_ignored_branches(self):
        """ Test that the comment includes the regular expression for unmerged branches to ignore. """
        self.assertEqual('Alleen deze branches worden bewaakt: branch, ignored branch. '
                         'Branches die voldoen aan de reguliere expressie feature.* zijn genegeerd.',
                         self.__metric.comment())

    def test_comment_urls(self):
        """ Test that the comment urls include a link to ignored branches. """
        self.assertEqual({'ignored branch': 'http://branch/'}, self.__metric.comment_urls())

    def test_comment_urls_no_ignored_branches(self):
        """ Test the comment urls when there are no ignored branches. """
        product = domain.Product(self.__project, short_name='Product',
                                 metric_source_ids={self.__subversion: 'http://svn/trunk/foo/'})
        unmerged_branches = metric.UnmergedBranches(subject=product, project=self.__project)
        self.assertEqual({}, unmerged_branches.comment_urls())

    def test_comment_url_label(self):
        """ Test the label for the comment urls. """
        self.assertEqual('Genegeerde branches', self.__metric.comment_url_label())

    def test_is_applicable(self):
        """ Test that the metric is applicable if the product is the trunk version. """
        self.assertTrue(metric.UnmergedBranches.is_applicable(self.__subject))

    def test_is_not_applicable_if_release(self):
        """ Test that the metric isn't applicable for released versions. """
        self.__subject.set_product_version('1.1')
        self.assertFalse(metric.UnmergedBranches.is_applicable(self.__subject))

    def test_is_not_applicable_if_branch(self):
        """ Test that the metric isn't applicable for released versions. """
        self.__subject.set_product_branch('branch')
        self.assertFalse(metric.UnmergedBranches.is_applicable(self.__subject))
