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


class FakeMetricSource(object):  # pylint: disable=too-few-public-methods
    """ Fake a metric source. """
    metric_source_name = 'FakeMetricSource'


class QualityReportMetricsTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the quality report class that test whether the right metrics are added. """

    def setUp(self):
        self.__birt = FakeMetricSource()
        self.__pom = FakeMetricSource()
        self.__subversion = FakeMetricSource()
        self.__jenkins = FakeMetricSource()
        self.__owasp_dependency_report = FakeMetricSource()
        self.__jmeter = FakeMetricSource()

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
        quality_report = self.__create_report(project_kwargs or dict(),
                                              team_kwargs or dict(),
                                              product_kwargs or dict(),
                                              number_of_teams)
        included = metric_class in [each_metric.__class__ for each_metric in quality_report.metrics()]
        self.assertTrue(included if include else not included)

    def test_team_progress(self):
        """ Test that the team progress metric is added if required. """
        self.__assert_metric(
            metric.TeamProgress,
            team_kwargs=dict(is_scrum_team=True, requirements=[requirement.SCRUM_TEAM]))

    def test_team_spirit(self):
        """ Test that the team spirit metric is added if required. """
        self.__assert_metric(metric.TeamSpirit, team_kwargs=dict(requirements=[requirement.TRACK_SPIRIT]))

    def test_team_absence(self):
        """ Test that the team absence metric is added if required. """
        self.__assert_metric(
            metric.TeamAbsence,
            team_kwargs=dict(requirements=[requirement.TRACK_ABSENCE]))

    def test_failing_unittests(self):
        """ Test that the failing unit tests metric is added if required. """
        self.__assert_metric(
            metric.FailingUnittests,
            product_kwargs=dict(requirements=[requirement.UNITTESTS]))

    def test_failing_regression_tests(self):
        """ Test that the failing regression tests metric is added if required. """
        self.__assert_metric(
            metric.FailingRegressionTests,
            product_kwargs=dict(requirements=[requirement.ART]))

    def test_failing_regression_tests_art(self):
        """ Test that the failing regression tests metric is added if the ART component has the ART requirement. """
        self.__assert_metric(
            metric.FailingRegressionTests,
            product_kwargs=dict(art=dict(requirements=[requirement.ART])))

    def test_regression_test_age(self):
        """ Test that the regression test age metric is added if required. """
        self.__assert_metric(
            metric.RegressionTestAge,
            product_kwargs=dict(requirements=[requirement.ART]))

    def test_regression_test_age_art(self):
        """ Test that the regression test age metric is added if the ART component has the ART requirement. """
        self.__assert_metric(
            metric.RegressionTestAge,
            product_kwargs=dict(art=dict(requirements=[requirement.ART])))

    def test_unittest_line_coverage(self):
        """ Test that the unit test line coverage metric is added if required. """
        self.__assert_metric(
            metric.UnittestLineCoverage,
            product_kwargs=dict(requirements=[requirement.UNITTESTS]))

    def test_unittest_branch_coverage(self):
        """ Test that the unit test branch coverage metric is added if required. """
        self.__assert_metric(
            metric.UnittestBranchCoverage,
            product_kwargs=dict(requirements=[requirement.UNITTESTS]))

    def test_art_statement_coverage(self):
        """ Test that the ART statement coverage metric is added if required. """
        self.__assert_metric(
            metric.ARTStatementCoverage,
            product_kwargs=dict(requirements=[requirement.ART_COVERAGE]))

    def test_art_statement_coverage_via_art(self):
        """ Test that the ART statement coverage metric is added if the ART product has the ART requirement. """
        self.__assert_metric(
            metric.ARTStatementCoverage,
            product_kwargs=dict(art=dict(requirements=[requirement.ART_COVERAGE])))

    def test_art_branch_coverage(self):
        """ Test that the ART statement coverage metric is added if required. """
        self.__assert_metric(
            metric.ARTBranchCoverage,
            product_kwargs=dict(requirements=[requirement.ART_COVERAGE]))

    def test_art_branch_coverage_via_art(self):
        """ Test that the ART statement coverage metric is added if the ART product has the ART requirement. """
        self.__assert_metric(
            metric.ARTBranchCoverage,
            product_kwargs=dict(art=dict(requirements=[requirement.ART_COVERAGE])))

    def test_art_code_metrics(self):
        """ Test that the code metric are added for the ART if required. """
        for metric_class in report.QualityReport.CODE_METRIC_CLASSES:
            self.__assert_metric(
                metric_class,
                product_kwargs=dict(art=dict(requirements=[requirement.CODE_QUALITY])))

    def test_art_code_metrics_non_trunk(self):
        """ Test that the code metrics are not added if the ART is not a trunk version. """
        for metric_class in report.QualityReport.CODE_METRIC_CLASSES:
            self.__assert_metric(
                metric_class,
                product_kwargs=dict(product_version='1.1', art=dict(requirements=[requirement.CODE_QUALITY])),
                include=False)

    def test_reviewed_us(self):
        """ Test that the reviewed user stories metric is added if required. """
        self.__assert_metric(
            metric.UserStoriesNotReviewed,
            product_kwargs=dict(requirements=[requirement.USER_STORIES_AND_LTCS]))

    def test_approved_us(self):
        """ Test that the approved user stories metric is added if required. """
        self.__assert_metric(
            metric.UserStoriesNotApproved,
            product_kwargs=dict(requirements=[requirement.USER_STORIES_AND_LTCS]))

    def test_no_reviewed_us(self):
        """ Test that the reviewed user stories metric is not added when the product is not a trunk version. """
        self.__assert_metric(
            metric.UserStoriesNotReviewed,
            project_kwargs=dict(metric_sources={metric_source.Birt: self.__birt}),
            product_kwargs=dict(product_version='1.1',
                                metric_source_ids={self.__birt: 'birt'},
                                requirements=[requirement.USER_STORIES_AND_LTCS]),
            include=False)

    def test_no_approved_us(self):
        """ Test that the approved user stories metric is not added when the product is not a trunk version. """
        self.__assert_metric(
            metric.UserStoriesNotApproved,
            project_kwargs=dict(metric_sources={metric_source.Birt: self.__birt}),
            product_kwargs=dict(product_version='1.1', metric_source_ids={self.__birt: 'birt'},
                                requirements=[requirement.USER_STORIES_AND_LTCS]),
            include=False)

    def test_reviewed_ltcs(self):
        """ Test that the reviewed logical test case metric is added if required. """
        self.__assert_metric(
            metric.LogicalTestCasesNotReviewed,
            product_kwargs=dict(requirements=[requirement.USER_STORIES_AND_LTCS]))

    def test_approved_ltcs(self):
        """ Test that the approved logical test case metric is added if required. """
        self.__assert_metric(
            metric.LogicalTestCasesNotApproved,
            product_kwargs=dict(requirements=[requirement.USER_STORIES_AND_LTCS]))

    def test_no_reviewed_ltcs(self):
        """ Test that the reviewed logical test case metric is not added when the product is not a trunk version. """
        self.__assert_metric(
            metric.LogicalTestCasesNotReviewed,
            project_kwargs=dict(metric_sources={metric_source.Birt: self.__birt}),
            product_kwargs=dict(product_version='1.1', metric_source_ids={self.__birt: 'birt'},
                                requirements=[requirement.USER_STORIES_AND_LTCS]),
            include=False)

    def test_no_approved_ltcs(self):
        """ Test that the approved logical test case metric is not added when the product is not a trunk version. """
        self.__assert_metric(
            metric.LogicalTestCasesNotApproved,
            project_kwargs=dict(metric_sources={metric_source.Birt: self.__birt}),
            product_kwargs=dict(product_version='1.1', metric_source_ids={self.__birt: 'birt'},
                                requirements=[requirement.USER_STORIES_AND_LTCS]),
            include=False)

    def test_number_manual_ltcs(self):
        """ Test that the number of manual logical test case metric is added if required. """
        self.__assert_metric(
            metric.NumberOfManualLogicalTestCases,
            product_kwargs=dict(requirements=[requirement.USER_STORIES_AND_LTCS]))

    def test_no_number_manual_ltcs(self):
        """ Test that the number of manual logical test case metric is not added when the product is not a trunk
            version. """
        self.__assert_metric(
            metric.NumberOfManualLogicalTestCases,
            project_kwargs=dict(metric_sources={metric_source.Birt: self.__birt}),
            product_kwargs=dict(product_version='1.1', metric_source_ids={self.__birt: 'birt'},
                                requirements=[requirement.USER_STORIES_AND_LTCS]),
            include=False)

    def test_duration_manual_ltcs(self):
        """ Test that the duration of manual logical test case metric is added if required. """
        self.__assert_metric(
            metric.DurationOfManualLogicalTestCases,
            project_kwargs=dict(requirements=[requirement.KEEP_TRACK_OF_MANUAL_LTCS]))

    def test_manual_ltcs_without_duration(self):
        """ Test that the manual logical test case without duration metric is added if required. """
        self.__assert_metric(
            metric.ManualLogicalTestCasesWithoutDuration,
            project_kwargs=dict(requirements=[requirement.KEEP_TRACK_OF_MANUAL_LTCS]))

    def test_jsf_duplication(self):
        """ Test that the jsf duplication metric is added if required. """
        self.__assert_metric(
            metric.JsfDuplication,
            product_kwargs=dict(jsf=dict(requirements=[requirement.JSF_CODE_QUALITY])))

    def test_open_bugs(self):
        """ Test that the open bugs metric is added if required. """
        self.__assert_metric(
            metric.OpenBugs,
            project_kwargs=dict(requirements=[requirement.KEEP_TRACK_OF_BUGS]))

    def test_open_security_bugs(self):
        """ Test that the open security bugs metric is added if required. """
        self.__assert_metric(
            metric.OpenSecurityBugs,
            project_kwargs=dict(requirements=[requirement.KEEP_TRACK_OF_BUGS]))

    def test_technical_debt_issues(self):
        """ Test that the technical debt issues metric is added if required. """
        self.__assert_metric(
            metric.TechnicalDebtIssues,
            project_kwargs=dict(requirements=[requirement.KEEP_TRACK_OF_TECHNICAL_DEBT]))

    def test_failing_ci_jobs(self):
        """ Test that the failing CI jobs metric is added if required. """
        self.__assert_metric(
            metric.FailingCIJobs,
            project_kwargs=dict(requirements=[requirement.KEEP_TRACK_OF_CI_JOBS]))

    def test_unused_ci_jobs(self):
        """ Test that the unused CI jobs metric is added if required. """
        self.__assert_metric(
            metric.UnusedCIJobs,
            project_kwargs=dict(requirements=[requirement.KEEP_TRACK_OF_CI_JOBS]))

    def test_configuration_consistency(self):
        """ Test that the configuration consistency metric is added if required. """
        self.__assert_metric(
            metric.JavaVersionConsistency,
            project_kwargs=dict(requirements=[requirement.KEEP_TRACK_OF_JAVA_CONSISTENCY]))

    def test_action_activity(self):
        """ Test that the action activity metric is added if required. """
        self.__assert_metric(
            metric.ActionActivity,
            project_kwargs=dict(requirements=[requirement.KEEP_TRACK_OF_ACTIONS]))

    def test_action_age(self):
        """ Test that the action age metric is added if required. """
        self.__assert_metric(
            metric.ActionAge,
            project_kwargs=dict(requirements=[requirement.KEEP_TRACK_OF_ACTIONS]))

    def test_risk_log(self):
        """ Test that the risk log metric is added if required. """
        self.__assert_metric(
            metric.RiskLog,
            project_kwargs=dict(requirements=[requirement.KEEP_TRACK_OF_RISKS]))

    def test_unmerged_branches(self):
        """ Test that the unmerged branches metric is added if required. """
        self.__assert_metric(
            metric.UnmergedBranches,
            product_kwargs=dict(requirements=[requirement.TRACK_BRANCHES]))

    def test_unmerged_branches_release(self):
        """ Test that the unmerged branches metric is not added if the product is released. """
        self.__assert_metric(
            metric.UnmergedBranches,
            product_kwargs=dict(requirements=[requirement.TRACK_BRANCHES], product_version='1.1'),
            include=False)

    def test_unmerged_branches_without_vcs_path(self):
        """ Test that the unmerged branches metric is still added without vcs path. """
        subversion = FakeMetricSource()
        self.__assert_metric(
            metric.UnmergedBranches,
            project_kwargs=dict(metric_sources={metric_source.VersionControlSystem: subversion}),
            product_kwargs=dict(requirements=[requirement.TRACK_BRANCHES], short_name='foo'))

    def test_art_unmerged_branches(self):
        """ Test that the unmerged branches metric is added for the ART. """
        self.__assert_metric(
            metric.UnmergedBranches,
            product_kwargs=dict(art=dict(requirements=[requirement.TRACK_BRANCHES])))

    def test_no_snapshot_dependencies(self):
        """ Test that the snapshot dependencies metric is not added for trunk versions. """
        self.__assert_metric(
            metric.SnapshotDependencies,
            project_kwargs=dict(metric_sources={metric_source.Pom: self.__pom,
                                                metric_source.Subversion: self.__subversion}),
            product_kwargs=dict(short_name='dummy', requirements=[requirement.NO_SNAPSHOT_DEPENDENCIES]),
            include=False)

    def test_snapshot_dependencies(self):
        """ Test that the snapshot dependencies metric is added if required and applicable. """
        self.__assert_metric(
            metric.SnapshotDependencies,
            product_kwargs=dict(short_name='dummy', product_version='1.1',
                                requirements=[requirement.NO_SNAPSHOT_DEPENDENCIES]))

    def test_high_prio_owasp_dependencies(self):
        """ Test that the high priority OWASP dependencies metric is added if required. """
        self.__assert_metric(metric.HighPriorityOWASPDependencyWarnings,
                             product_kwargs=dict(requirements=[requirement.OWASP]))

    def test_normal_prio_owasp_dependencies(self):
        """ Test that the normal priority OWASP dependencies metric is added if required. """
        self.__assert_metric(metric.NormalPriorityOWASPDependencyWarnings,
                             product_kwargs=dict(requirements=[requirement.OWASP]))

    def test_high_level_zap_scan_alerts(self):
        """ Test that the high risk ZAP Scan alerts metric is added if required. """
        self.__assert_metric(metric.HighRiskZAPScanAlertsMetric,
                             product_kwargs=dict(requirements=[requirement.OWASP_ZAP]))

    def test_medium_risk_level_zap_scan_alerts(self):
        """ Test that the medium risk ZAP Scan alerts metric is added if required. """
        self.__assert_metric(metric.MediumRiskZAPScanAlertsMetric,
                             product_kwargs=dict(requirements=[requirement.OWASP_ZAP]))

    def test_sonar_version(self):
        """ Test that the Sonar version number metric is added if required. """
        self.__assert_metric(
            metric.SonarVersion,
            project_kwargs=dict(requirements=[requirement.KEEP_TRACK_OF_SONAR_VERSION]))

    def test_document_age(self):
        """ Test that the document age metric is added if possible. """
        subversion = FakeMetricSource()
        document = domain.Document(name='Title', url='http://url/', metric_source_ids={subversion: 'http://url/'})
        self.__assert_metric(
            metric.DocumentAge,
            project_kwargs=dict(metric_sources={metric_source.VersionControlSystem: subversion}, documents=[document]))

    def test_document_age_without_vcs(self):
        """ Test that the document age metric is added even if the project has no version control system configured. """
        document = domain.Document(name='Title', url='http://url')
        self.__assert_metric(metric.DocumentAge,
                             project_kwargs=dict(documents=[document]))

    def test_user_story_points_ready(self):
        """ Test that the user story points ready metric is added if required. """
        self.__assert_metric(metric.ReadyUserStoryPoints,
                             project_kwargs=dict(requirements=[requirement.KEEP_TRACK_OF_READY_US]))

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

    def test_total_loc(self):
        """ Test that the total LOC metric is added if the project contains the trusted product maintainability
            standard as requirement. """
        self.__assert_metric(
            metric.TotalLOC,
            product_kwargs=dict(short_name='dummy'),
            project_kwargs=dict(requirements=[requirement.TRUSTED_PRODUCT_MAINTAINABILITY]))

    def test_java_metrics(self):
        """ Test that the Java related Sonar version metrics are added if the project has Java as requirement. """
        for metric_class in requirement.JAVA.metric_classes():
            self.__assert_metric(
                metric_class,
                project_kwargs=dict(requirements=[requirement.JAVA]))

    def test_dotnet_metrics(self):
        """ Test that the DotNet related version metrics are added if the project has DotNet as requirement. """
        for metric_class in requirement.C_SHARP.metric_classes():
            self.__assert_metric(
                metric_class,
                project_kwargs=dict(requirements=[requirement.C_SHARP]))

    def test_web_metrics(self):
        """ Test that the Web related version metrics are added if the project contains Web as requirement. """
        for metric_class in requirement.WEB.metric_classes():
            self.__assert_metric(
                metric_class,
                project_kwargs=dict(requirements=[requirement.WEB]))

    def test_js_metrics(self):
        """ Test that the JavaScript related version metrics are added if the project contains JavaScript as
            requirement. """
        for metric_class in requirement.JAVASCRIPT.metric_classes():
            self.__assert_metric(
                metric_class,
                project_kwargs=dict(requirements=[requirement.JAVASCRIPT]))

    def test_code_quality_metrics(self):
        """ Test that the code quality metrics are added if the product has code quality as requirement. """
        for metric_class in requirement.CODE_QUALITY.metric_classes():
            self.__assert_metric(
                metric_class,
                product_kwargs=dict(requirements=[requirement.CODE_QUALITY]))

    def test_performance_metrics(self):
        """ Test that the response times metrics are added if required. """
        for metric_class in requirement.PERFORMANCE.metric_classes():
            self.__assert_metric(
                metric_class,
                product_kwargs=dict(requirements=[requirement.PERFORMANCE]))
        for metric_class in requirement.PERFORMANCE_YMOR.metric_classes():
            self.__assert_metric(
                metric_class,
                product_kwargs=dict(requirements=[requirement.PERFORMANCE_YMOR]))

    def test_metric_class_units(self):
        """ Test that all metric classes have a unit. """
        for metric_class in report.QualityReport.metric_classes():
            self.assertNotEqual('Subclass responsibility', metric_class.unit, '{} has no unit'.format(metric_class))

    def test_metric_class_names(self):
        """ Test that all metric classes have a name. """
        for metric_class in report.QualityReport.metric_classes():
            self.assertNotEqual('Subclass responsibility', metric_class.name, '{} has no name'.format(metric_class))
