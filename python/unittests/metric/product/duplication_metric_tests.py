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

    @staticmethod
    def duplicated_lines(*args):
        ''' Return the number of duplicated lines. '''
        return 15

    @staticmethod
    def lines(*args):
        ''' Return the number of lines. '''
        return 150


class FakeSubject(object):  # pylint: disable=too-few-public-methods
    ''' Provide for a fake subject. '''

    def __init__(self, jsf=True, jsf_id=True):
        self.__jsf = jsf
        self.__jsf_id = jsf_id

    @staticmethod
    def name():
        ''' Return the name of the subject. '''
        return 'FakeSubject'

    def jsf(self):
        ''' Return the JSF component. '''
        return FakeSubject(jsf_id=self.__jsf_id) if self.__jsf else None

    def sonar_id(self):
        ''' Return the Sonar id of the subject. '''
        return 'sonar id' if self.__jsf_id else ''


class DuplicationTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the duplication metric. '''

    def setUp(self):  # pylint: disable=invalid-name
        project = domain.Project(
            metric_sources={metric_source.Sonar: FakeSonar()})
        self._metric = metric.Duplication(subject=FakeSubject(),
                                          project=project)

    def test_value(self):
        ''' Test that the value of the metric equals the percentage of 
            duplicated lines. '''
        self.assertEqual(10., self._metric.value())

    def test_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual(dict(Sonar=FakeSonar().dashboard_url()), 
                         self._metric.url())


class JsfDuplicationTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the duplication metric. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__subject = FakeSubject()
        self.__project = domain.Project(
            metric_sources={metric_source.Sonar: FakeSonar()})
        self._metric = metric.JsfDuplication(subject=self.__subject,
                                             project=self.__project)
 
    def test_can_be_measured_(self):
        ''' Test that the JSF duplication can be measured for a JSF 
            component. '''
        self.failUnless(metric.JsfDuplication.can_be_measured(self.__subject,
                                                              self.__project))
 
    def test_cant_be_measured_without_sonar(self):
        ''' Test that the JSF duplication cannot be measured without Sonar. '''
        project = domain.Project()
        self.failIf(metric.JsfDuplication.can_be_measured(self.__subject,
                                                          project))

    def test_cant_be_measured_without_jsf(self):
        ''' Test that the JSF duplication cannot be measured if the product
            has no JSF component. '''
        product = FakeSubject(jsf=False)
        self.failIf(metric.JsfDuplication.can_be_measured(product, 
                                                          self.__project))

    def test_cant_be_measured_without_jsf_sonar_id(self):
        ''' Test that the JSF duplication cannot be measured if the product
            has no JSF Sonar id. '''
        product = FakeSubject(jsf_id=False)
        self.failIf(metric.JsfDuplication.can_be_measured(product, 
                                                          self.__project))
