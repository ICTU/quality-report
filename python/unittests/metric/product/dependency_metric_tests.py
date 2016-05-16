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
from qualitylib.report import Section


class FakeSonar(object):
    """ Provide for a fake Sonar object so that the unit test don't need access to an actual Sonar instance. """

    # pylint: disable=unused-argument

    @staticmethod
    def dashboard_url(*args):
        """ Return a fake dashboard url. """
        return 'http://sonar'

    @staticmethod
    def package_cycles(*args):
        """ Return the number of package cycles. """
        return 1


class FakeSubject(object):
    """ Provide for a fake subject. """

    def __init__(self, metric_source_ids=None):
        self.__metric_source_ids = metric_source_ids or dict()

    @staticmethod
    def name():
        """ Return the name of the subject. """
        return 'FakeSubject'

    @staticmethod
    def short_name():
        """ Return the short name of the subject. """
        return 'FS'

    @staticmethod
    def dependencies(**kwargs):  # pylint: disable=unused-argument
        """ Return the dependencies of the subject. """
        return [('product1', 'product1_version'), ('product2', '')]

    def metric_source_id(self, the_metric_source):
        """ Return the id of the subject for the metric source. """
        return self.__metric_source_ids.get(the_metric_source, None)


class FakeReport(object):
    """ Fake a quality report. """

    @staticmethod
    def get_product_section(product_label):  # pylint: disable=unused-argument
        """ Return the section for the product/version. """
        return Section('', [])

    @staticmethod
    def products():
        """ Return the products of the project. """
        return [FakeSubject(), FakeSubject()]

    @staticmethod
    def get_product(product, version):  # pylint: disable=unused-argument
        """ Return the specified product. """
        return FakeSubject()


class DependencyQualityTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the dependency quality metric. """

    def setUp(self):
        self.__subject = FakeSubject()
        project = domain.Project()
        self.__metric = metric.DependencyQuality(subject=self.__subject, report=FakeReport(), project=project)

    def test_value(self):
        """ Test that the value of the metric equals the percentage of dependencies without red metrics. """
        self.assertEqual(0, self.__metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertEqual('0% van de afhankelijkheden (0 van de 4) is naar componenten die "rode" metrieken hebben.',
                         self.__metric.report())

    def test_url(self):
        """ Test that the url contains the "red" products. """
        self.assertEqual({'product1:product1_version': 'index.html#section_FS',
                          'product2:trunk': 'index.html#section_FS'},
                         self.__metric.url())

    def test_url_label(self):
        """ Test that the url label is correct. """
        self.assertEqual('Componenten die "rode" metrieken hebben', self.__metric.url_label())


class SnapshotDependenciesTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the snapshot dependencies metric. """

    def setUp(self):
        self.__metric = metric.SnapshotDependencies(subject=FakeSubject(), report=FakeReport(),
                                                    project=domain.Project())

    def test_value(self):
        """ Test that the value of the metric equals the number of snapshot dependencies of the product. """
        self.assertEqual(1, self.__metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({'product2:trunk': 'index.html#section_FS'}, self.__metric.url())

    def test_report(self):
        """ Test the metric report. """
        self.assertEqual('FakeSubject heeft 1 afhankelijkheden op snapshot versies van andere producten.',
                         self.__metric.report())


class CyclicDependenciesTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the cyclic dependencies metric. """

    def setUp(self):
        project = domain.Project(metric_sources={metric_source.Sonar: FakeSonar()})
        self.__subject = domain.Product(project, 'PR', name='FakeSubject')
        self._metric = metric.CyclicDependencies(subject=self.__subject, project=project)

    def test_value(self):
        """ Test that the value of the metric equals the number of cyclic dependencies between packages. """
        self.assertEqual(FakeSonar().package_cycles(), self._metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual(dict(Sonar=FakeSonar().dashboard_url()), self._metric.url())


class FakeJenkinsOWASPDependenciesReport(object):
    """ Fake a Jenkins OWASP dependency report for unit test purposes. """

    @staticmethod
    def nr_high_priority_warnings(job_names):  # pylint: disable=unused-argument
        """ Return the number of high priority warnings tests for the jobs. """
        return 4

    @staticmethod
    def nr_normal_priority_warnings(job_names):  # pylint: disable=unused-argument
        """ Return the number of normal priority warnings tests for the jobs. """
        return 2

    @staticmethod
    def nr_low_priority_warnings(job_names):  # pylint: disable=unused-argument
        """ Return the number of low priority warnings tests for the jobs. """
        return 14

    @staticmethod
    def report_url(job_name):
        """ Return the url for the job. """
        return 'http://jenkins/%s' % job_name


class OWASPDependenciesTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the OWASP dependencies metric. """

    def setUp(self):
        self.__jenkins = FakeJenkinsOWASPDependenciesReport()
        self.__subject = FakeSubject(metric_source_ids={self.__jenkins: 'jenkins_job'})
        self.__project = domain.Project(metric_sources={metric_source.JenkinsOWASPDependencyReport: self.__jenkins})
        self.__metric = metric.OWASPDependencies(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that value of the metric equals the failing tests as reported by Jenkins. """
        self.assertEqual(self.__jenkins.nr_high_priority_warnings('jenkins_job') +
                         self.__jenkins.nr_normal_priority_warnings('jenkins_job'),
                         self.__metric.value())

    def test_value_multiple_jobs(self):
        """ Test that the value of the metric equals to total number of failing tests if there are multiple
            test reports. """
        subject = FakeSubject(metric_source_ids={self.__jenkins: ['a', 'b']})
        failing_tests = metric.OWASPDependencies(subject=subject, project=self.__project)
        expected = self.__jenkins.nr_high_priority_warnings(['a', 'b']) + \
            self.__jenkins.nr_normal_priority_warnings(['a', 'b'])
        self.assertEqual(expected, failing_tests.value())

    def test_report(self):
        """ Test that the report for the metric is correct. """
        self.assertEqual('Dependencies van FakeSubject hebben 4 high priority, 2 normal priority en '
                         '14 low priority warnings.', self.__metric.report())

    def test_url(self):
        """ Test that the url points to the Jenkins job. """
        self.assertEqual({'Jenkins OWASP dependency report': self.__jenkins.report_url('jenkins_job')},
                         self.__metric.url())

    def test_url_multiple_jobs(self):
        """ Test that the url points to the Jenkins jobs. """
        subject = FakeSubject(metric_source_ids={self.__jenkins: ['a', 'b']})
        dependencies = metric.OWASPDependencies(subject=subject, project=self.__project)
        self.assertEqual({'Jenkins OWASP dependency report a': self.__jenkins.report_url('a'),
                          'Jenkins OWASP dependency report b': self.__jenkins.report_url('b')},
                         dependencies.url())

    def test_can_be_measured(self):
        """ Test that metric can be measured when Jenkins is available and the product has a Jenkins job. """
        self.assertTrue(metric.OWASPDependencies.can_be_measured(self.__subject, self.__project))

    def test_cant_be_measured_without_jenkins(self):
        """ Test that the metric cannot be measured without Jenkins. """
        self.assertFalse(metric.OWASPDependencies.can_be_measured(self.__subject, domain.Project()))

    def test_cant_be_measured_without_jenkins_job(self):
        """ Test that the metric cannot be measured without Jenkins job. """
        self.assertFalse(metric.OWASPDependencies.can_be_measured(FakeSubject(), self.__project))
