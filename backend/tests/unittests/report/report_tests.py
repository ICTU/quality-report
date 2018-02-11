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

    def test_get_section(self):
        """ Test that a section can be retrieved by section id. """
        section = self.__report.sections()[0]
        self.assertEqual(section, self.__report.get_section(section.id_prefix()))

    def test_get_section_with_unknown_id(self):
        """ Test that a unknown id results in None returned. """
        self.assertEqual(None, self.__report.get_section('unknown'))

    def test_process(self):
        """ Test that the report has two sections when we add a process:
            one for the process itself, and one for meta metrics. """
        project = domain.Project()
        project.add_process(domain.Process(short_name='FP', requirements=[requirement.TrackActions]))
        self.assertEqual(2, len(report.QualityReport(project).sections()))

    def test_product(self):
        """ Test that the report has two sections when we add a product:
            one for the product itself, and one for meta metrics. """
        project = domain.Project()
        project.add_product(domain.Product(short_name='FP', requirements=[requirement.CodeQuality]))
        self.assertEqual(2, len(report.QualityReport(project).sections()))

    def test_get_environment_section(self):
        """ Test that the environment can be found. """
        environment = domain.Environment(short_name='ENV')
        self.__project.add_environment(environment)
        quality_report = report.QualityReport(self.__project)
        section = quality_report.get_section('ENV')
        self.assertEqual('ENV', section.id_prefix())

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
        """ Test that the report contains the team section. """
        team = domain.Team(name='Team')
        self.__project.add_team(team)
        quality_report = report.QualityReport(self.__project)
        self.assertEqual(2, len(quality_report.sections()))

    def test_products(self):
        """ Test that the report returns the products. """
        product = domain.Product(short_name='FP')
        self.__project.add_product(product)
        quality_report = report.QualityReport(self.__project)
        self.assertEqual([product], quality_report.products())

    def test_direct_action_needed_without_metrics(self):
        """ Test that direct action is needed if the report doesn't contain any metrics. """
        quality_report = report.QualityReport(self.__project)
        self.assertTrue(quality_report.direct_action_needed())

    def test_no_direct_action_needed_when_all_metrics_green(self):
        """ Test that the report needs no direct action when all metrics are green. """
        quality_report = report.QualityReport(self.__project)
        quality_report.sections()  # Generate the report
        self.assertFalse(quality_report.direct_action_needed())

    def test_direct_action_needed_when_metrics_are_missing(self):
        """ Test that the report needs direct action when the report has missing metrics. """
        project = domain.Project('organization', name='project title',
                                 added_requirements={requirement.TrustedProductMaintainability})
        quality_report = report.QualityReport(project)
        quality_report.sections()  # Generate the report
        self.assertTrue(quality_report.direct_action_needed())

    def test_sonar_id(self):
        """ Test that the Sonar id of a product can be retrieved. """
        sonar = 'Sonar'
        project = domain.Project('organization', metric_sources={metric_source.Sonar: sonar})
        product = domain.Product(metric_source_ids={sonar: 'sonar-id'})
        quality_report = report.QualityReport(project)
        self.assertEqual(('Sonar', 'sonar-id'), quality_report.sonar_id(product))

    def test_sonar_id_empty(self):
        """ Test that the Sonar id of a product can be retrieved. """
        sonar = 'Sonar'
        project = domain.Project('organization', metric_sources={metric_source.Sonar: sonar})
        product = domain.Product(metric_source_ids={sonar: ''})
        quality_report = report.QualityReport(project)
        self.assertEqual((None, ''), quality_report.sonar_id(product))

    def test_vcs_id(self):
        """ Test that the VCS id can be retrieved. """
        vcs = 'VCS'
        project = domain.Project('organization', metric_sources={metric_source.VersionControlSystem: vcs})
        product = domain.Product(metric_source_ids={vcs: 'vcs_id'})
        quality_report = report.QualityReport(project)
        self.assertEqual(('VCS', 'vcs_id'), quality_report.vcs_id(product))

    def test_vcs_id_when_product_is_none(self):
        """ Test that the empty VCS id is retrieved for None product. """
        vcs = 'VCS'
        project = domain.Project('organization', metric_sources={metric_source.VersionControlSystem: vcs})
        product = None
        quality_report = report.QualityReport(project)
        self.assertEqual((None, ''), quality_report.vcs_id(product))

    def test_vcs_id_when_no_metric_source_id(self):
        """ Test that the empty VCS id is retrieved when there is no metric source id """
        vcs = 'VCS'
        project = domain.Project('organization', metric_sources={metric_source.VersionControlSystem: vcs})
        product = domain.Product(metric_source_ids={})
        quality_report = report.QualityReport(project)
        self.assertEqual((None, ''), quality_report.vcs_id(product))

    def test_last_product_change_date(self):
        """ Test that the report can retrieve the last changed date of a product. """
        class FakeVCS(object):  # pylint: disable=too-few-public-methods
            """ Fake VCS metric source with a fixed changed date. """
            @staticmethod
            def last_changed_date(vcs_id):  # pylint: disable=unused-argument
                """ Return the date the product was last changed. """
                return datetime.datetime(2017, 1, 1)

        vcs = FakeVCS()
        project = domain.Project('organization', metric_sources={metric_source.VersionControlSystem: vcs})
        product = domain.Product(metric_source_ids={vcs: 'vcs_id'})
        quality_report = report.QualityReport(project)
        self.assertEqual(datetime.datetime(2017, 1, 1), quality_report.latest_product_change_date(product))


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
        self.assertEqual({domain.Project, domain.Environment, domain.Process, domain.Product, domain.Component,
                          domain.Application, domain.Team, domain.Document}, self.__report.domain_object_classes())

    def test_get_included_domain_object_classes(self):
        """ Test the set of included domain objects. """
        self.assertEqual({self.__report.project().__class__}, self.__report.included_domain_object_classes())


class ReportFactory(object):  # pylint: disable=too-few-public-methods
    """ Create a report according to provided arguments. """

    @staticmethod
    def report(project_kwargs, team_kwargs, process_kwargs, product_kwargs):
        """ Create the quality report. """
        documents = project_kwargs.pop('documents', [])
        project = domain.Project('organization', name='project', **project_kwargs)
        for document in documents:
            project.add_document(document)
        if team_kwargs:
            project.add_team(ReportFactory.__create_team(team_kwargs))
        if process_kwargs:
            project.add_process(ReportFactory.__create_process(process_kwargs))
        if product_kwargs:
            project.add_product(ReportFactory.__create_product(product_kwargs))
        quality_report = report.QualityReport(project)
        quality_report.sections()  # Make sure the report is created
        return quality_report

    @staticmethod
    def __create_process(process_kwargs):  # pylint: disable=unused-argument
        """ Create a process according to the provided arguments. """
        return domain.Process(**process_kwargs)

    @staticmethod
    def __create_product(product_kwargs):
        """ Create a product according to the provided arguments. """
        art_kwargs = product_kwargs.pop("art", dict())
        if art_kwargs:
            component = domain.Product(**art_kwargs)
            product_kwargs["art"] = component
        return domain.Product(**product_kwargs)

    @staticmethod
    def __create_team(team_kwargs):
        """ Create a team according to the provided arguments. """
        nr_members = team_kwargs.pop("nr_members", 2)
        team = domain.Team(name='Team', **team_kwargs)
        for index in range(nr_members):
            team.add_member(domain.Person(name='Member {0}'.format(index)))
        return team


class QualityReportMetricsTest(unittest.TestCase):
    """ Unit tests for the quality report class that test whether the right metrics are added. """

    def __assert_metric(self, metric_class, project_kwargs=None, team_kwargs=None, process_kwargs=None,
                        product_kwargs=None, should_be_included=True):
        """ Check that the metric class is included in the report. """
        quality_report = ReportFactory.report(project_kwargs or dict(), team_kwargs or dict(),
                                              process_kwargs or dict(), product_kwargs or dict())
        included = metric_class in [each_metric.__class__ for each_metric in quality_report.metrics()]
        if should_be_included:
            self.assertTrue(included, '{0} should be included in the report but was not.'.format(metric_class))
        else:
            self.assertFalse(included, '{0} should not be included in the report but was.'.format(metric_class))

    def test_project_requirements(self):
        """ Test for each project requirement that its metrics are added if the project has the requirement. """
        self.assertFalse(domain.Project.default_requirements())
        for req in domain.Project.optional_requirements():
            for metric_class in req.metric_classes():
                self.__assert_metric(metric_class, project_kwargs=dict(added_requirements=[req]))

    def test_process_requirements(self):
        """ Test for each process requirement that its metrics are added if the process has the requirement. """
        self.assertFalse(domain.Process.default_requirements())
        for req in domain.Process.optional_requirements():
            for metric_class in req.metric_classes():
                self.__assert_metric(metric_class, process_kwargs=dict(added_requirements=[req]))

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

    def test_document_added_requirements(self):
        """ Test that the document metrics are added if a document with added requirements is added to the project. """
        for req in [requirement.TrackDocumentAge, requirement.TrackSecurityTestDate]:
            for metric_class in req.metric_classes():
                self.__assert_metric(metric_class,
                                     project_kwargs=dict(documents=[domain.Document()],
                                                         added_requirements=[requirement.TrackSecurityTestDate]))

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

    def test_unittest_metrics(self):
        """ Test that the unit test metrics are added if required. """
        for metric_class in [metric.FailingUnittests, metric.UnittestReportAge]:
            self.__assert_metric(metric_class, product_kwargs=dict(requirements=[requirement.UnitTests]))

    def test_unittest_coverage_metrics(self):
        """ Test that the unit test coverage metrics are added if required. """
        for metric_class in [metric.UnittestLineCoverage, metric.UnittestBranchCoverage]:
            self.__assert_metric(metric_class, product_kwargs=dict(requirements=[requirement.UnitTestCoverage]))

    def test_non_applicable_metric(self):
        """ Test that the team metric isn't added if the team has one member. """
        self.__assert_metric(metric.TeamAbsence, team_kwargs=dict(short_name='TE', nr_members=1,
                                                                  added_requirements=[requirement.TrackAbsence]),
                             should_be_included=False)

    def test_document_age(self):
        """ Test that the document age metric is added if possible. """
        document = domain.Document(name='Title', url='http://url/')
        self.__assert_metric(metric.DocumentAge, project_kwargs=dict(documents=[document]))

    def test_last_security_test_metrics(self):
        """ Test that the document age metric is added if possible. """
        document = domain.Document(name='Title', url='http://url/')
        self.__assert_metric(metric.LastSecurityTest,
                             project_kwargs=dict(documents=[document],
                                                 added_requirements=[requirement.TrackSecurityTestDate]))

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
            self.assertNotEqual('Subclass responsibility', metric_class.unit, '{0} has no unit'.format(metric_class))

    def test_metric_class_names(self):
        """ Test that all metric classes have a name. """
        for metric_class in report.QualityReport.metric_classes():
            self.assertNotEqual('Subclass responsibility', metric_class.name, '{0} has no name'.format(metric_class))
