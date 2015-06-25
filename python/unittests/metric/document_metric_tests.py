'''
Copyright 2012-2015 Ministerie van Sociale Zaken en Werkgelegenheid

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

from qualitylib import metric, domain, metric_source
import unittest
import datetime


class FakeSubversion(object):  # pylint: disable=too-few-public-methods
    ''' Fake Subversion for unit tests. '''
    metric_source_name = 'Subversion'

    @staticmethod
    def last_changed_date(url):  # pylint: disable=unused-argument
        ''' Return the date the url was last changed. '''
        return datetime.datetime.now() - datetime.timedelta(days=2.1)

    @staticmethod
    def normalize_path(svn_path):
        ''' Return a normalized version of the path. '''
        return svn_path


class DocumentAgeTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the document age metric. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__subversion = FakeSubversion()
        self.__project = domain.Project(
            metric_sources={
                metric_source.VersionControlSystem: self.__subversion})
        self.__document = domain.Document(name='Title', url='http://doc',
            metric_source_ids={self.__subversion: 'http://doc/'})
        self.__metric = metric.DocumentAge(subject=self.__document,
                                           project=self.__project)

    def test_value(self):
        ''' Test that the value of the metric equals the document age in 
            days. '''
        self.assertEqual(2, self.__metric.value())

    def test_report(self):
        ''' Test that the report is correct. '''
        self.assertEqual('Het document "Title" is 2 dag(en) geleden ' \
                         'bijgewerkt.', self.__metric.report())

    def test_url(self):
        ''' Test that the url of the metric is the url of the document. '''
        self.assertEqual(dict(Subversion='http://doc'), self.__metric.url())

    def test_can_be_measured(self):
        ''' Test that the metric can be measured if the project has Subversion
            and the document has an url. '''
        self.assertTrue(metric.DocumentAge.can_be_measured(self.__document,
                                                           self.__project))

    def test_cant_be_measured_without_url(self):
        ''' Test that the metric cannot be measured if the document has no 
            url. '''
        document = domain.Document(name='Title')
        self.assertFalse(metric.DocumentAge.can_be_measured(document, 
                                                       self.__project))

    def test_cant_be_measured_without_subversion(self):
        ''' Test that the metric cannot be measured without Subversion. '''
        project = domain.Project()
        self.assertFalse(metric.DocumentAge.can_be_measured(self.__document,
                                                       project))

    def test_norm_template_default_values(self):
        ''' Test that the right values are returned to fill in the norm 
            template. '''
        self.assertTrue(metric.DocumentAge.norm_template % \
                        metric.DocumentAge.norm_template_default_values())

    def test_document_overrides_target(self):
        ''' Test that the document can override the default target value. '''
        document = domain.Document(name='Title',
                                   targets={metric.DocumentAge: 20})
        age = metric.DocumentAge(subject=document, project=self.__project)
        self.assertEqual(document.target(metric.DocumentAge), age.target())


class MissingDocumentAgeTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the document age metric when the document is missing. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__document = domain.Document(name='Title', url='http://doc')
        self.__project = domain.Project(
            metric_sources={
                metric_source.VersionControlSystem: FakeSubversion()})
        self.__metric = metric.DocumentAge(subject=self.__document,
                                           project=self.__project)

    def test_value(self):
        ''' Test that the value of the metric equals the document age in 
            days. '''
        expected = (datetime.datetime.now() - datetime.datetime.min).days
        self.assertEqual(expected, self.__metric.value())

    def test_report(self):
        ''' Test that the report is correct. '''
        self.assertEqual('Het document "Title" is niet aangetroffen.',
                         self.__metric.report())
