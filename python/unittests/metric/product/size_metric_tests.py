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
from qualitylib import metric, domain, metric_source


class FakeSonar(object):
    ''' Provide for a fake Sonar object so that the unit test don't need 
        access to an actual Sonar instance. '''
    # pylint: disable=unused-argument

    @staticmethod
    def dashboard_url(*args):  
        ''' Return a fake dashboard url. '''
        return 'http://sonar'

    url = dashboard_url

    @staticmethod
    def ncloc(*args):
        ''' Return the number of non-comment LOC. '''
        return 123


class FakeSubject(object):  # pylint: disable=too-few-public-methods
    ''' Provide for a fake subject. '''

    @staticmethod
    def name():
        ''' Return the name of the subject. '''
        return 'FakeSubject'

    @staticmethod
    def sonar_id():
        ''' Return the Sonar id of the subject. '''
        return ''


class FakeHistory(object):  # pylint: disable=too-few-public-methods
    ''' Fake the history for testing purposes. '''
    @staticmethod  # pylint: disable=unused-argument
    def recent_history(*args):
        ''' Return a fake recent history. '''
        return [100, 200]


class ProductLOCTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the product LOC metric. '''

    def setUp(self):  # pylint: disable=invalid-name
        project = domain.Project(
            metric_sources={metric_source.Sonar: FakeSonar()})
        self._metric = metric.ProductLOC(subject=FakeSubject(), project=project)

    def test_value(self):
        ''' Test that the value of the metric equals the NCLOC returned by
            Sonar. '''
        self.assertEqual(FakeSonar().ncloc(), self._metric.value())

    def test_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual(dict(Sonar=FakeSonar().dashboard_url()), 
                         self._metric.url())


class TotalLOCTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the total LOC metric. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__subject = FakeSubject()
        project = domain.Project(
            metric_sources={metric_source.Sonar: FakeSonar(),
                            metric_source.History: FakeHistory()})
        self.__metric = metric.TotalLOC(subject=[self.__subject,
                                                 self.__subject],
                                        project=project)

    def test_value(self):
        ''' Test that the value of the metric equals the sum of the NCLOC 
            returned by Sonar. '''
        self.assertEqual(FakeSonar().ncloc() * 2, self.__metric.value())
 
    def test_url(self):
        ''' Test that the url refers to Sonar. '''
        self.assertEqual(dict(Sonar=FakeSonar().url()), self.__metric.url())

    def test_recent_history(self):
        ''' Test that the recent history substracts the minimum value of 
            each value so that more data can be plotted. '''
        self.assertEqual([0, 100], self.__metric.recent_history())
