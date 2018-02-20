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

from hqlib import metric, domain, metric_source


class FakeSubversion(object):  # pylint: disable=too-few-public-methods
    """ Fake Subversion for unit tests. """
    metric_source_name = metric_source.Subversion.metric_source_name

    @staticmethod
    def last_changed_date(url):
        """ Return the date the url was last changed. """
        return datetime.datetime.min if 'raise' in url else datetime.datetime.now() - datetime.timedelta(days=2.1)

    @staticmethod
    def normalize_path(svn_path):
        """ Return a normalized version of the path. """
        return svn_path


class DocumentAgeTest(unittest.TestCase):
    """ Unit tests for the document age metric. """

    def setUp(self):
        self.__subversion = FakeSubversion()
        self.__project = domain.Project(metric_sources={metric_source.ArchiveSystem: self.__subversion})
        self.__document = domain.Document(name='Title', url='http://doc',
                                          metric_source_ids={self.__subversion: 'http://doc/'})
        self.__metric = metric.DocumentAge(subject=self.__document, project=self.__project)

    def test_value(self):
        """ Test that the value of the metric equals the document age in days. """
        self.assertEqual(2, self.__metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertEqual('Het document "Title" is 2 dag(en) geleden bijgewerkt.', self.__metric.report())

    def test_norm_template_default_values(self):
        """ Test that the right values are returned to fill in the norm template. """
        self.assertTrue(metric.DocumentAge.norm_template % metric.DocumentAge.norm_template_default_values())

    def test_document_overrides_target(self):
        """ Test that the document can override the default target value. """
        document = domain.Document(name='Title', metric_options={metric.DocumentAge: dict(target=20)})
        age = metric.DocumentAge(subject=document, project=self.__project)
        self.assertEqual(document.target(metric.DocumentAge), age.target())


class MissingDocumentAgeTest(unittest.TestCase):
    """ Unit tests for the document age metric when the document is missing. """

    def setUp(self):
        self.__subversion = FakeSubversion()
        self.__document = domain.Document(name='Title', url='http://doc',
                                          metric_source_ids={self.__subversion: 'raise'})
        self.__project = domain.Project(metric_sources={metric_source.ArchiveSystem: self.__subversion})
        self.__metric = metric.DocumentAge(subject=self.__document, project=self.__project)

    def test_value(self):
        """ Test that the value of the metric equals the document age in days. """
        self.assertEqual(-1, self.__metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertEqual('Het document "Title" is niet aangetroffen.', self.__metric.report())

    def test_report_no_vcs(self):
        """ Test the report when there's no version control system. """
        project = domain.Project()
        document = domain.Document(name='Title', url='http://doc', metric_source_ids={self.__subversion: 'path'})
        age = metric.DocumentAge(subject=document, project=project)
        self.assertEqual('De document update leeftijd van Title kon niet gemeten worden omdat de bron ArchiveSystem '
                         'niet is geconfigureerd.', age.report())

    def test_report_no_vcs_path(self):
        """ Test the report when there's no version control system path. """
        document = domain.Document(name='Title', url='http://doc')
        age = metric.DocumentAge(subject=document, project=self.__project)
        self.assertEqual('De document update leeftijd van Title kon niet gemeten worden omdat niet alle '
                         'benodigde bron-ids zijn geconfigureerd. Configureer ids voor de bron ArchiveSystem.',
                         age.report())
