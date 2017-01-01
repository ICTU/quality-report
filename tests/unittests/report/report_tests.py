"""
Copyright 2012-2017 Ministerie van Sociale Zaken en Werkgelegenheid

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

from hqlib import report, domain, metric, metric_source, requirement


class QualityReportTest(unittest.TestCase):
    """ Unit tests for the quality report class. """

    def setUp(self):
        self.__project = domain.Project('organization', name='project title')
        self.__report = report.QualityReport(self.__project)

    def test_project(self):
        """ Test that the report has the project. """
        self.assertEqual(self.__project, self.__report.project())

    def test_title(self):
        """ Test that the title of the report is equal to the title of the project. """
        self.assertTrue(self.__project.name() in self.__report.title())

    def test_str_returns_title(self):
        """ Test that casting the report to a string returns the title. """
        self.assertEqual(str(self.__report), self.__report.title())

    def test_report_date_is_now(self):
        """ Test that the report date is now. """
        self.assertTrue(datetime.datetime.now() - self.__report.date() < datetime.timedelta(seconds=10))

    def test_sections(self):
        """ Test that the report has one section, the meta metrics, by default. """
        self.assertEqual(1, len(self.__report.sections()))

    def test_sections_twice(self):
        """ Test that the sections are cached. """
        self.assertTrue(self.__report.sections() is self.__report.sections())

    def test_get_section(self):
        """ Test that a section can be retrieved by section id. """
        section = self.__report.sections()[0]
        self.assertEqual(section, self.__report.get_section(section.id_prefix()))

    def test_get_section_with_unknown_id(self):
        """ Test that a unknown id results in None returned. """
        self.assertEqual(None, self.__report.get_section('unknown'))

    def test_product(self):
        """ Test that the report has three sections when we add a product:
            one for the product itself, and one for meta metrics. """
        project = domain.Project()
        project.add_product(domain.Product(project, 'FP', requirements=[requirement.CodeQuality]))
        self.assertEqual(2, len(report.QualityReport(project).sections()))

    def test_get_product_section(self):
        """ Test that the section for the product can be found. """
        product = domain.Product(self.__project, 'FP', requirements=[requirement.CodeQuality])
        self.__project.add_product(product)
        quality_report = report.QualityReport(self.__project)
        section = quality_report.get_product_section(product)
        self.assertEqual(product, section.product())

    def test_get_product_section_twice(self):
        """ Test that the product section is cached. """
        product = domain.Product(self.__project, 'FP', requirements=[requirement.CodeQuality])
        self.__project.add_product(product)
        quality_report = report.QualityReport(self.__project)
        section1 = quality_report.get_product_section(product)
        section2 = quality_report.get_product_section(product)
        self.assertTrue(section1 is section2)

    def test_get_meta_section(self):
        """ Test that the report has no meta section by default. """
        self.assertFalse(self.__report.get_meta_section())

    def test_dashboard(self):
        """ Test that the report has an empty dashboard by default. """
        self.assertEqual(([], []), self.__report.dashboard())

    def test_team(self):
        """ Test that the report has 2 sections when we add a team. """
        team = domain.Team(name='Team')
        self.__project.add_team(team)
        quality_report = report.QualityReport(self.__project)
        self.assertEqual(2, len(quality_report.sections()))

    def test_teams(self):
        """ Test that the report returns the team. """
        team = domain.Team(name='Team')
        self.__project.add_team(team)
        quality_report = report.QualityReport(self.__project)
        self.assertEqual([team], quality_report.teams())

    def test_products(self):
        """ Test that the report returns the products. """
        product = domain.Product(self.__project, 'FP')
        self.__project.add_product(product)
        quality_report = report.QualityReport(self.__project)
        self.assertEqual([product], quality_report.products())


class QualityReportMetaDataTest(unittest.TestCase):
    """ Unit tests for the meta data methods of the quality report. """

    def setUp(self):
        self.__project = domain.Project('organization', name='project title')
        self.__report = report.QualityReport(self.__project)
        self.__report.sections()  # Generate report

    def test_get_included_metric_classes(self):
        """ Test the list of included metric classes. """
        self.assertEqual({metric.RedMetaMetric, metric.YellowMetaMetric, metric.GreenMetaMetric,
                          metric.GreyMetaMetric, metric.MissingMetaMetric}, self.__report.included_metric_classes())

    def test_get_included_requirements(self):
        """ Test the list of included requirements. """
        self.assertEqual(set(), self.__report.included_requirement_classes())

    def test_get_domain_object_classes(self):
        """ Test the set of all domain objects. """
        self.assertEqual({domain.Project, domain.Product, domain.Component, domain.Application,
                          domain.Team, domain.Document}, self.__report.domain_object_classes())

    def test_get_included_domain_object_classes(self):
        """ Test the set of included domain objects. """
        self.assertEqual({self.__report.project().__class__}, self.__report.included_domain_object_classes())


class ReportFactory(object):  # pylint: disable=too-few-public-methods
    """ Create a report according to provided arguments. """

    @staticmethod
    def report(project_kwargs, team_kwargs, product_kwargs):
        """ Create the quality report. """
        documents = project_kwargs.pop('documents', [])
        project = domain.Project('organization', name='project', **project_kwargs)
        for document in documents:
            project.add_document(document)
        if team_kwargs:
            project.add_team(ReportFactory.__create_team(team_kwargs))
        if product_kwargs:
            project.add_product(ReportFactory.__create_product(project, product_kwargs))
        quality_report = report.QualityReport(project)
        quality_report.sections()  # Make sure the report is created
        return quality_report

    @staticmethod
    def __create_product(project, product_kwargs):
        """ Create a product according to the provided arguments. """
        for component_name in 'unittests', 'jsf', 'art':
            component_kwargs = product_kwargs.pop(component_name, dict())
            if component_kwargs:
                component = domain.Product(project, **component_kwargs)
                product_kwargs[component_name] = component
        return domain.Product(project, **product_kwargs)

    @staticmethod
    def __create_team(team_kwargs):
        """ Create a team according to the provided arguments. """
        team = domain.Team(name='Team', **team_kwargs)
        team.add_member(domain.Person(name='Piet Programmer'))
        team.add_member(domain.Person(name='Tara Tester'))
        return team


class QualityReportMetricsTest(unittest.TestCase):
    """ Unit tests for the quality report class that test whether the right metrics are added. """

    def __assert_metric(self, metric_class, project_kwargs=None, team_kwargs=None, product_kwargs=None):
        """ Check that the metric class is included in the report. """
        quality_report = ReportFactory.report(project_kwargs or dict(), team_kwargs or dict(),
                                              product_kwargs or dict())
        included = metric_class in [each_metric.__class__ for each_metric in quality_report.metrics()]
        self.assertTrue(included, '{} should be included in the report but was not.'.format(metric_class))

    def test_project_requirements(self):
        """ Test for each project requirement that its metrics are added if the project has the requirement. """
        for req in [requirement.Java, requirement.CSharp, requirement.Web, requirement.JavaScript,
                    requirement.TrustedProductMaintainability, requirement.TrackReadyUS,
                    requirement.TrackSonarVersion, requirement.TrackActions,
                    requirement.TrackRisks, requirement.TrackJavaConsistency,
                    requirement.TrackCIJobs, requirement.TrackTechnicalDebt,
                    requirement.TrackBugs, requirement.TrackManualLTCs, requirement.TrackSecurityAndPerformanceRisks,
                    requirement.OpenVAS]:
            for metric_class in req.metric_classes():
                self.__assert_metric(metric_class, project_kwargs=dict(requirements=[req]))

    def test_team_requirements(self):
        """ Test that the team metrics are added if required. """
        for req in domain.Team.default_requirements():
            for metric_class in req.metric_classes():
                self.__assert_metric(metric_class, team_kwargs=dict(short_name='TE'))
        for req in domain.Team.optional_requirements():
            for metric_class in req.metric_classes():
                self.__assert_metric(metric_class, team_kwargs=dict(added_requirements=[req]))

    def test_document_requirements(self):
        """ Test that the document metrics are added if a document is added to the project. """
        for req in [requirement.TrackDocumentAge]:
            for metric_class in req.metric_classes():
                self.__assert_metric(metric_class, project_kwargs=dict(documents=[domain.Document()]))

    def test_product_requirements(self):
        """ Test that the product metrics are added if required. """
        for req in [requirement.CodeQuality, requirement.ART, requirement.ARTCoverage,
                    requirement.UserStoriesAndLTCs, requirement.TrackBranches, requirement.OWASPDependencies,
                    requirement.OWASPZAP, requirement.PerformanceLoad, requirement.PerformanceEndurance,
                    requirement.PerformanceScalability]:
            for metric_class in req.metric_classes():
                self.__assert_metric(metric_class, product_kwargs=dict(requirements=[req]))

    def test_product_art_requirements(self):
        """ Test that the product ART metrics are added if required. """
        for req in [requirement.CodeQuality, requirement.ART, requirement.ARTCoverage, requirement.TrackBranches]:
            for metric_class in req.metric_classes():
                self.__assert_metric(metric_class, product_kwargs=dict(art=dict(requirements=[req])))

    def test_product_jsf_requirements(self):
        """ Test that the product JSF metrics are added if required. """
        for req in [requirement.JSFCodeQuality]:
            for metric_class in req.metric_classes():
                self.__assert_metric(metric_class, product_kwargs=dict(jsf=dict(requirements=[req])))

    def test_unittest_metrics(self):
        """ Test that the unit test metrics are added if required. """
        for metric_class in [metric.FailingUnittests, metric.UnittestLineCoverage, metric.UnittestBranchCoverage]:
            self.__assert_metric(metric_class, product_kwargs=dict(requirements=[requirement.UnitTests]))

    def test_document_age(self):
        """ Test that the document age metric is added if possible. """
        document = domain.Document(name='Title', url='http://url/')
        self.__assert_metric(metric.DocumentAge, project_kwargs=dict(documents=[document]))

    def test_metric_classes(self):
        """ Test that the report gives a list of metric classes. """
        self.assertTrue(metric.ARTStatementCoverage in report.QualityReport.metric_classes())

    def test_metric_source_classes(self):
        """ Test that the report gives a list of metric source classes. """
        self.assertTrue(metric_source.VersionControlSystem in report.QualityReport.metric_source_classes())

    def test_included_metric_source_classes(self):
        """ Test that the report gives a list of included metric source classes, based on the project's metric
            source classes. """
        project = domain.Project()
        self.assertEqual(project.metric_source_classes(),
                         report.QualityReport(project).included_metric_source_classes())

    def test_metric_class_units(self):
        """ Test that all metric classes have a unit. """
        for metric_class in report.QualityReport.metric_classes():
            self.assertNotEqual('Subclass responsibility', metric_class.unit, '{} has no unit'.format(metric_class))

    def test_metric_class_names(self):
        """ Test that all metric classes have a name. """
        for metric_class in report.QualityReport.metric_classes():
            self.assertNotEqual('Subclass responsibility', metric_class.name, '{} has no name'.format(metric_class))
