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

import StringIO
import logging
import unittest
import urllib2

from qualitylib import domain, metric_source

MINIMAL_POM = '<version>1</version>'
ONE_DEPENDENCY = MINIMAL_POM + """
    <dependency>
        <artifactid>artifact_id</artifactid>
        <version>1.0</version>
    </dependency>"""
ONE_PROPERTY = """
    <properties>
        <version>2.0 </version><!-- Spaces should be ignored -->
    </properties>
    <dependency>
        <artifactid>artifact_id</artifactid>
        <version>${version}</version>
    </dependency>"""
RECURSIVE_PROPERTY = """
    <properties>
        <empty></empty>
        <other>3.0</other>
        <version>${other}</version>
    </properties>
    <dependency>
        <artifactid>artifact_id</artifactid>
        <version>${version}</version>
    </dependency>"""


class PomUnderTest(metric_source.Pom):
    """ Override class to return a static pom file. """
    def url_open(self, url):
        """ Return static contents or raise an exception. """
        if 'raise' in url:
            raise urllib2.HTTPError(None, None, None, None, None)
        else:
            return url


class PomTest(unittest.TestCase):
    """ Unit tests for the pom file metric source. """

    def setUp(self):
        self.__sonar = metric_source.Sonar('http://sonar')
        self.__subversion = metric_source.Subversion()
        self.__pom = PomUnderTest(sonar=self.__sonar, version_control_system=self.__subversion)

    def test_no_dependencies(self):
        """ Test pom without dependencies. """
        self.assertEqual(set(), self.__pom.dependencies(MINIMAL_POM, []))

    def test_log_http_error(self):
        """ Test that a HTTP error while opening a pom file is logged. """
        stream = StringIO.StringIO()
        logging.getLogger().addHandler(logging.StreamHandler(stream))
        self.__pom.dependencies('raise', [])
        stream.seek(0)
        self.assertEqual("Couldn't open raise/pom.xml: HTTP Error None: None\n", stream.getvalue())

    def test_dependency(self):
        """ Test a pom with one dependency. """
        project = domain.Project(metric_sources={metric_source.Sonar: self.__sonar})
        product = domain.Product(project, 'product', metric_source_ids={self.__sonar: 'group_id:artifact_id'})
        self.assertEqual({('artifact_id', '1.0')}, self.__pom.dependencies(ONE_DEPENDENCY, [product]))

    def test_property(self):
        """ Test a pom with a property. """
        project = domain.Project(metric_sources={metric_source.Sonar: self.__sonar})
        product = domain.Product(project, 'product', metric_source_ids={self.__sonar: 'group_id:artifact_id'})
        self.assertEqual({('artifact_id', '2.0')}, self.__pom.dependencies(ONE_PROPERTY, [product]))

    def test_recursive_property(self):
        """ Test a pom with a property whose value is a property. """
        project = domain.Project(metric_sources={metric_source.Sonar: self.__sonar})
        product = domain.Product(project, 'product', metric_source_ids={self.__sonar: 'group_id:artifact_id'})
        self.assertEqual({('artifact_id', '3.0')}, self.__pom.dependencies(RECURSIVE_PROPERTY, [product]))

    def test_product_without_sonar_id(self):
        """ Test that getting dependencies works when there is a product without Sonar id. """
        project = domain.Project(metric_sources={metric_source.Sonar: self.__sonar})
        product = domain.Product(project, 'product', metric_source_ids={self.__sonar: 'group_id:artifact_id'})
        product_no_sonar = domain.Product(project, 'product no sonar')
        self.assertEqual({('artifact_id', '1.0')}, self.__pom.dependencies(ONE_DEPENDENCY, [product_no_sonar, product]))
