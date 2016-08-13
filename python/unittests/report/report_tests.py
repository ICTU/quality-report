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

import datetime
import unittest

from qualitylib import report, domain, metric, metric_source, requirement


class QualityReportTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
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
        project.add_product(domain.Product(project, 'FP', requirements=[requirement.CODE_QUALITY]))
        self.assertEqual(2, len(report.QualityReport(project).sections()))

    def test_get_product_section(self):
        """ Test that the section for the product can be found. """
        product = domain.Product(self.__project, 'FP', requirements=[requirement.CODE_QUALITY])
        self.__project.add_product(product)
        quality_report = report.QualityReport(self.__project)
        section = quality_report.get_product_section(product)
        self.assertEqual(product, section.product())

    def test_get_product_section_twice(self):
        """ Test that the product section is cached. """
        product = domain.Product(self.__project, 'FP', requirements=[requirement.CODE_QUALITY])
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
        team = domain.Team(name='Team', requirements=[requirement.TRACK_SPIRIT])
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

    def test_get_product(self):
        """ Test that a product can be retrieved by version number. """
        product = domain.Product(self.__project, name='Product')
        product.set_product_version('1.1')
        self.__project.add_product(product)
        quality_report = report.QualityReport(self.__project)
        self.assertEqual(product, quality_report.get_product('Product', '1.1'))

    def test_get_included_metric_classes(self):
        """ Test the list of included metric classes. """
        self.__report.sections()  # Generate report
        self.assertEqual({metric.RedMetaMetric, metric.YellowMetaMetric, metric.GreenMetaMetric,
                          metric.GreyMetaMetric, metric.MissingMetaMetric}, self.__report.included_metric_classes())


class QualityReportMetricsTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the quality report class that test whether the right metrics are added. """

    @staticmethod
    def __create_report(project_kwargs, team_kwargs, product_kwargs, number_of_teams=1):
        """ Create the quality report. """
        documents = project_kwargs.pop('documents', [])
        project = domain.Project('organization', name='project', **project_kwargs)
        for document in documents:
            project.add_document(document)
        for index in range(number_of_teams):
            team = domain.Team(name='Team %d' % index, **team_kwargs)
            team.add_member(domain.Person(name='Piet Programmer'))
            team.add_member(domain.Person(name='Tara Tester'))
            project.add_team(team)
        if product_kwargs:
            for component_name in ('unittests', 'jsf', 'art'):
                component_kwargs = product_kwargs.pop(component_name, dict())
                if component_kwargs:
                    component = domain.Product(project, **component_kwargs)
                    product_kwargs[component_name] = component
            product = domain.Product(project, **product_kwargs)
            project.add_product(product)
        quality_report = report.QualityReport(project)
        quality_report.sections()  # Make sure the report is created
        return quality_report

    def __assert_metric(self, metric_class, project_kwargs=None, team_kwargs=None, product_kwargs=None,
                        number_of_teams=1, include=True):
        """ Check that the metric class is included in the report. """
        quality_report = self.__create_report(project_kwargs or dict(), team_kwargs or dict(),
                                              product_kwargs or dict(), number_of_teams)
        included = metric_class in [each_metric.__class__ for each_metric in quality_report.metrics()]
        if include:
            self.assertTrue(included, '{} should be included in the report but was not.'.format(metric_class))
        else:
            self.assertFalse(included, '{} should not be included in the report but was.'.format(metric_class))

    def test_project_requirements(self):
        """ Test for each project requirement that its metrics are added if the project has the requirement. """
        for req in [requirement.JAVA, requirement.C_SHARP, requirement.WEB, requirement.JAVASCRIPT,
                    requirement.TRUSTED_PRODUCT_MAINTAINABILITY, requirement.TRACK_READY_US,
                    requirement.TRACK_SONAR_VERSION, requirement.TRACK_ACTIONS,
                    requirement.TRACK_RISKS, requirement.TRACK_JAVA_CONSISTENCY,
                    requirement.TRACK_CI_JOBS, requirement.TRACK_TECHNICAL_DEBT,
                    requirement.TRACK_BUGS, requirement.TRACK_MANUAL_LTCS]:
            for metric_class in req.metric_classes():
                self.__assert_metric(metric_class, project_kwargs=dict(requirements=[req]))

    def test_team_requirements(self):
        """ Test that the team metrics are added if required. """
        for req in [requirement.SCRUM_TEAM, requirement.TRACK_SPIRIT, requirement.TRACK_ABSENCE]:
            for metric_class in req.metric_classes():
                self.__assert_metric(metric_class, team_kwargs=dict(requirements=[req]))

    def test_document_requirements(self):
        """ Test that the document metrics are added if a document is added to the project. """
        for req in [requirement.TRACK_DOCUMENT_AGE]:
            for metric_class in req.metric_classes():
                self.__assert_metric(metric_class, project_kwargs=dict(documents=[domain.Document()]))

    def test_product_requirements(self):
        """ Test that the product metrics are added if required. """
        for req in [requirement.CODE_QUALITY, requirement.ART, requirement.ART_COVERAGE,
                    requirement.USER_STORIES_AND_LTCS, requirement.TRACK_BRANCHES, requirement.OWASP_DEPENDENCIES,
                    requirement.OWASP_ZAP, requirement.PERFORMANCE, requirement.PERFORMANCE_YMOR]:
            for metric_class in req.metric_classes():
                self.__assert_metric(metric_class, product_kwargs=dict(requirements=[req]))

    def test_product_requirements_not_applicable(self):
        """ Test that product metrics that can't be measured on trunk versions are not included. """
        for req in [requirement.NO_SNAPSHOT_DEPENDENCIES]:
            for metric_class in req.metric_classes():
                self.__assert_metric(metric_class, product_kwargs=dict(requirements=[req]), include=False)

    def test_product_art_requirements(self):
        """ Test that the product ART metrics are added if required. """
        for req in [requirement.CODE_QUALITY, requirement.ART, requirement.ART_COVERAGE, requirement.TRACK_BRANCHES]:
            for metric_class in req.metric_classes():
                self.__assert_metric(metric_class, product_kwargs=dict(art=dict(requirements=[req])))

    def test_product_jsf_requirements(self):
        """ Test that the product JSF metrics are added if required. """
        for req in [requirement.JSF_CODE_QUALITY]:
            for metric_class in req.metric_classes():
                self.__assert_metric(metric_class, product_kwargs=dict(jsf=dict(requirements=[req])))

    def test_product_with_version_requirements(self):
        """ Test that metrics that can only be measured on non-trunk product versions are included. """
        for req in [requirement.NO_SNAPSHOT_DEPENDENCIES]:
            for metric_class in req.metric_classes():
                self.__assert_metric(metric_class, product_kwargs=dict(product_version='1.1', requirements=[req]))

    def test_product_art_code_with_version(self):
        """ Test that the code metrics are not added if the ART is not a trunk version. """
        for req in [requirement.CODE_QUALITY]:
            for metric_class in req.metric_classes():
                self.__assert_metric(metric_class,
                                     product_kwargs=dict(product_version='1.1', art=dict(requirements=[req])),
                                     include=False)

    def test_product_with_version_exclude(self):
        """ Test that metrics that can't be measured on non-trunk product versions aren't included ."""
        for metric_class in [metric.UserStoriesNotApproved, metric.UserStoriesNotReviewed,
                             metric.UserStoriesWithTooFewLogicalTestCases, metric.LogicalTestCasesNotApproved,
                             metric.LogicalTestCasesNotReviewed, metric.LogicalTestCasesNotAutomated,
                             metric.UnmergedBranches]:
            self.__assert_metric(metric_class,
                                 product_kwargs=dict(product_version='1.1',
                                                     requirements=[requirement.USER_STORIES_AND_LTCS,
                                                                   requirement.TRACK_BRANCHES]),
                                 include=False)

    def test_unittest_metrics(self):
        """ Test that the unit test metrics are added if required. """
        for metric_class in [metric.FailingUnittests, metric.UnittestLineCoverage, metric.UnittestBranchCoverage]:
            self.__assert_metric(metric_class, product_kwargs=dict(requirements=[requirement.UNITTESTS]))

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
