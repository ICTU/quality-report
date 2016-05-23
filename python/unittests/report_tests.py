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


class FakeMetric(object):
    """ Fake metric to use in the tests below. """
    def __init__(self, status=''):
        self.__status = status

    @staticmethod
    def set_id_string(id_string):
        """ Ignore. """
        pass

    def status(self):
        """ Return the preset status. """
        return self.__status


class SectionHeaderTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the section header class. """

    def setUp(self):  # pylint: disable=invalid-name
        self.__header = report.SectionHeader('TE', 'title', 'subtitle')

    def test_title(self):
        """ Test that the title is correct. """
        self.assertEqual('title', self.__header.title())

    def test_subtitle(self):
        """ Test that the subtitle is correct. """
        self.assertEqual('subtitle', self.__header.subtitle())

    def test_id_prefix(self):
        """ Test that the id prefix is correct. """
        self.assertEqual('TE', self.__header.id_prefix())


class SectionTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the section class. """

    def setUp(self):  # pylint: disable=invalid-name
        self.__header = report.SectionHeader('TE', 'title', 'subtitle')
        self.__metrics = [FakeMetric('green'), FakeMetric('perfect'),
                          FakeMetric('yellow'), FakeMetric('grey'),
                          FakeMetric('red'), FakeMetric('missing')]
        self.__section = report.Section(self.__header, self.__metrics)

    def test_title(self):
        """ Test that the title of the section is the title of the header. """
        self.assertEqual(self.__header.title(), self.__section.title())

    def test_subtitle(self):
        """ Test that the subtitle of the section is the subtitle of the
            header. """
        self.assertEqual(self.__header.subtitle(), self.__section.subtitle())

    def test_id_prefix(self):
        """ Test that the id prefix of the section is the id prefix of the
            header. """
        self.assertEqual(self.__header.id_prefix(), self.__section.id_prefix())

    def test_str(self):
        """ Test that str(section) returns the title of the section. """
        self.assertEqual(self.__section.title(), str(self.__section))

    def test_get_metric(self):
        """ Test that the section is a list of metrics. """
        self.assertEqual(self.__metrics[0], self.__section[0])

    def test_get_all_metrics(self):
        """ Test that the section has a list of all metrics. """
        self.assertEqual(self.__metrics, self.__section.metrics())

    def test_color_red(self):
        """ Test that the section is red when one metric is red. """
        self.assertEqual('red', self.__section.color())

    def test_color_yellow(self):
        """ Test that the section is yellow when no metrics are red and at least one is yellow. """
        metrics = [FakeMetric('green'), FakeMetric('perfect'),
                   FakeMetric('yellow'), FakeMetric('grey')]
        # Using self.__header makes this unit test fail occasionally in the IDE. Don't understand why.
        header = report.SectionHeader('TE', 'another title', 'subtitle')
        section = report.Section(header, metrics)
        self.assertEqual('yellow', section.color())

    def test_color_grey(self):
        """ Test that the section is grey when no metrics are red or yellow and
            at least one is grey. """
        metrics = [FakeMetric('green'), FakeMetric('perfect'), FakeMetric('grey')]
        section = report.Section(self.__header, metrics)
        self.assertEqual('grey', section.color())

    def test_color_green(self):
        """ Test that the section is green when no metrics are red, yellow or grey. """
        metrics = [FakeMetric('green'), FakeMetric('perfect')]
        section = report.Section(self.__header, metrics)
        self.assertEqual('green', section.color())

    def test_color_perfect(self):
        """ Test that the section is green when all metrics are perfect. """
        metrics = [FakeMetric('perfect')]
        section = report.Section(self.__header, metrics)
        self.assertEqual('green', section.color())

    def test_color_white(self):
        """ Test that the section is white when it contains no metrics. """
        section = report.Section(self.__header, [])
        self.assertEqual('white', section.color())

    def test_has_no_history(self):
        """ Test that the section has no history unless its id prefix is MM (for Meta Metrics). """
        self.assertFalse(self.__section.has_history())

    def test_has_history(self):
        """ Test that the section has history when its id prefix is MM (for Meta Metrics). """
        section = report.Section(report.SectionHeader('MM', 'title', 'subtitle'), [])
        self.assertTrue(section.has_history())

    def test_history(self):
        """ Test that the section returns the history from the history metric source. """

        class FakeHistory(object):  # pylint: disable=too-few-public-methods
            """ Fake the history metric source. """
            @staticmethod
            def complete_history():
                """ Return a fake history. """
                return 'History'

        section = report.Section(None, [], history=FakeHistory())
        self.assertEqual('History', section.history())

    def test_product(self):
        """ Test that the section returns the product. """
        section = report.Section(None, [], product='Product')
        self.assertEqual('Product', section.product())

    def test_trunk_product(self):
        """ Test that the section returns whether the product is a trunk version. """

        class FakeProduct(object):  # pylint: disable=too-few-public-methods
            """ Fake a trunk product. """
            @staticmethod
            def product_version_type():
                """ Fake a trunk version. """
                return 'trunk'

        section = report.Section(None, [], product=FakeProduct())
        self.assertTrue(section.contains_trunk_product())


class FakeSonar(object):  # pylint: disable=too-few-public-methods
    """ Fake a Sonar instance. """
    @staticmethod
    def version(*args):  # pylint: disable=unused-argument
        """ Return the version number of the product. """
        return '1'


class QualityReportTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the quality report class. """

    def setUp(self):  # pylint: disable=invalid-name
        self.__sonar = FakeSonar()
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
        """ Test that the report has four sections when we add a product:
            one for overall product quality, one for overall process quality,
            one for the product itself, and one for meta metrics. """
        project = domain.Project('organization', name='project title',
                                 metric_sources={metric_source.Sonar: self.__sonar})
        project.add_product(domain.Product(project, 'FP', metric_source_ids={self.__sonar: 'sonar.id'}))
        self.assertEqual(4, len(report.QualityReport(project).sections()))

    def test_get_product_section(self):
        """ Test that the section for the product can be found. """
        product = domain.Product(self.__project, 'FP', metric_source_ids={self.__sonar: 'sonar.id'})
        self.__project.add_product(product)
        quality_report = report.QualityReport(self.__project)
        section = quality_report.get_product_section(product)
        self.assertEqual(product, section.product())

    def test_get_product_section_twice(self):
        """ Test that the product section is cached. """
        product = domain.Product(self.__project, 'FP', metric_source_ids={self.__sonar: 'sonar.id'})
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

    def test_get_product(self):
        """ Test that a product can be retrieved by version number. """
        product = domain.Product(self.__project, name='Product')
        product.set_product_version('1.1')
        self.__project.add_product(product)
        quality_report = report.QualityReport(self.__project)
        self.assertEqual(product, quality_report.get_product('Product', '1.1'))


class FakeBirt(object):
    """ Fake a Birt instance. """
    @staticmethod
    def planned_velocity(birt_id):  # pylint: disable=unused-argument
        """ Return the planned velocity of the team with the specified birt id. """
        return 5

    @staticmethod
    def has_test_design(birt_id):  # pylint: disable=unused-argument
        """ Return whether the product with the specified birt id has a test design. """
        return True


class FakeJira(object):  # pylint: disable=too-few-public-methods
    """ Fake Jira. """

    @staticmethod
    def has_open_bugs_query():
        """ Return whether Jira has a query to report the number of open bug reports. """
        return True

    has_manual_test_cases_query = has_open_security_bugs_query = has_blocking_test_issues_query = \
        has_user_stories_ready_query = has_technical_debt_issues_query = has_open_bugs_query


class FakeJenkinsTestReport(object):  # pylint: disable=too-few-public-methods
    """ Fake Jenkins. """
    pass


class FakeJenkinsOWASPDependencyReport(object):
    # pylint: disable=too-few-public-methods
    """ Fake Jenkins. """
    pass


class FakePom(object):  # pylint: disable=too-few-public-methods
    """ Fake Pom retriever. """
    pass


class FakeSubversion(object):  # pylint: disable=too-few-public-methods
    """ Fake Subversion repository. """

    metric_source_name = 'FakeSubversion'

    @staticmethod
    def normalize_path(svn_path):
        """ Return a normalized version of the path. """
        return svn_path


class FakeJMeter(object):  # pylint: disable=too-few-public-methods
    """ Fake JMeter report. """
    pass


class QualityReportMetricsTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the quality report class that test whether the right metrics are added. """

    def setUp(self):
        self.__sonar = FakeSonar()
        self.__birt = FakeBirt()
        self.__pom = FakePom()
        self.__subversion = FakeSubversion()
        self.__jenkins = FakeJenkinsTestReport()
        self.__owasp_dependency_report = FakeJenkinsOWASPDependencyReport()
        self.__jmeter = FakeJMeter()

    @staticmethod
    def __create_report(project_kwargs, team_kwargs, product_kwargs,
                        street_kwargs, number_of_teams=1):
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
        if street_kwargs:
            project.add_street(domain.Street(**street_kwargs))
        quality_report = report.QualityReport(project)
        quality_report.sections()  # Make sure the report is created
        return quality_report

    def __assert_metric(self, metric_class, project_kwargs=None,
                        team_kwargs=None, product_kwargs=None,
                        street_kwargs=None, number_of_teams=1, include=True):
        """ Check that the metric class is included in the report. """
        quality_report = self.__create_report(project_kwargs or dict(),
                                              team_kwargs or dict(),
                                              product_kwargs or dict(),
                                              street_kwargs or dict(),
                                              number_of_teams)
        included = metric_class in [each_metric.__class__ for each_metric in quality_report.metrics()]
        self.assertTrue(included if include else not included)

    def test_team_progress(self):
        """ Test that the team progress metric is added if possible. """
        self.__assert_metric(
            metric.TeamProgress,
            project_kwargs=dict(metric_sources={metric_source.Birt: self.__birt}),
            team_kwargs=dict(is_scrum_team=True, metric_source_ids={self.__birt: 'team'}))

    def test_art_stability(self):
        """ Test that the ART stability metric is added if possible. """
        self.__assert_metric(metric.ARTStability, street_kwargs=dict(name='A', job_regexp='A.*'))

    def test_team_spirit(self):
        """ Test that the team spirit metric is added if possible. """
        self.__assert_metric(metric.TeamSpirit, project_kwargs=dict(metric_sources={metric_source.Wiki: 'Wiki'}))

    def test_team_absence(self):
        """ Test that the team absence metric is added if possible. """
        self.__assert_metric(
            metric.TeamAbsence,
            project_kwargs=dict(metric_sources={metric_source.HolidayPlanner: 'Planner'}))

    def test_failing_unittests(self):
        """ Test that the failing unit tests metric is added if possible. """
        self.__assert_metric(
            metric.FailingUnittests,
            product_kwargs=dict(metric_source_ids={self.__sonar: 'id'},
                                unittests=dict(metric_source_ids={self.__sonar: 'id'})),
            project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}))

    def test_failing_regression_tests(self):
        """ Test that the failing regression tests metric is added if possible. """
        self.__assert_metric(
            metric.FailingRegressionTests,
            product_kwargs=dict(metric_source_ids={self.__jenkins: 'id'}),
            project_kwargs=dict(metric_sources={metric_source.TestReport: self.__jenkins}))

    def test_failing_regression_tests_art(self):
        """ Test that the failing regression tests metric is added if
            the ART component has the Jenkins test report. """
        self.__assert_metric(
            metric.FailingRegressionTests,
            product_kwargs=dict(art=dict(metric_source_ids={self.__jenkins: 'id'})),
            project_kwargs=dict(metric_sources={metric_source.TestReport: self.__jenkins}))

    def test_unittest_line_coverage(self):
        """ Test that the unit test line coverage metric is added if possible. """
        self.__assert_metric(
            metric.UnittestLineCoverage,
            product_kwargs=dict(metric_source_ids={self.__sonar: 'id'},
                                unittests=dict(metric_source_ids={self.__sonar: 'id'})),
            project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}))

    def test_unittest_branch_coverage(self):
        """ Test that the unit test branch coverage metric is added if possible. """
        self.__assert_metric(
            metric.UnittestBranchCoverage,
            product_kwargs=dict(metric_source_ids={self.__sonar: 'id'},
                                unittests=dict(metric_source_ids={self.__sonar: 'id'})),
            project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}))

    def test_art_statement_coverage(self):
        """ Test that the ART statement coverage metric is added if possible. """
        self.__assert_metric(
            metric.ARTStatementCoverage,
            project_kwargs=dict(metric_sources={metric_source.CoverageReport: 'NCover'}),
            product_kwargs=dict(metric_source_ids={'NCover': 'ncover'}))

    def test_art_statement_coverage_via_art(self):
        """ Test that the ART statement coverage metric is added if the ART product has the coverage report. """
        self.__assert_metric(
            metric.ARTStatementCoverage,
            project_kwargs=dict(metric_sources={metric_source.CoverageReport: 'NCover'}),
            product_kwargs=dict(art=dict(metric_source_ids={'NCover': 'ncover'})))

    def test_art_branch_coverage(self):
        """ Test that the ART statement coverage metric is added if possible. """
        self.__assert_metric(
            metric.ARTBranchCoverage,
            project_kwargs=dict(metric_sources={metric_source.CoverageReport: 'NCover'}),
            product_kwargs=dict(metric_source_ids={'NCover': 'ncover'}))

    def test_art_branch_coverage_via_art(self):
        """ Test that the ART statement coverage metric is added if the ART product has the coverage report. """
        self.__assert_metric(
            metric.ARTBranchCoverage,
            project_kwargs=dict(metric_sources={metric_source.CoverageReport: 'NCover'}),
            product_kwargs=dict(art=dict(metric_source_ids={'NCover': 'ncover'})))

    def test_art_critical_violations(self):
        """ Test that the critical violations is added for the ART. """
        for metric_class in report.QualityReport.JAVA_METRIC_CLASSES:
            self.__assert_metric(
                metric_class,
                project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}),
                product_kwargs=dict(art=dict(metric_source_ids={self.__sonar: 'id'})))

    def test_reviewed_us(self):
        """ Test that the reviewed user stories metric is added if possible. """
        self.__assert_metric(
            metric.UserStoriesNotReviewed,
            project_kwargs=dict(metric_sources={metric_source.Birt: self.__birt}),
            product_kwargs=dict(metric_source_ids={self.__birt: 'birt'}))

    def test_approved_us(self):
        """ Test that the approved user stories metric is added if possible. """
        self.__assert_metric(
            metric.UserStoriesNotApproved,
            project_kwargs=dict(metric_sources={metric_source.Birt: self.__birt}),
            product_kwargs=dict(metric_source_ids={self.__birt: 'birt'}))

    def test_no_reviewed_us(self):
        """ Test that the reviewed user stories metric is not added when the product is not a trunk version. """
        self.__assert_metric(
            metric.UserStoriesNotReviewed,
            project_kwargs=dict(metric_sources={metric_source.Birt: self.__birt}),
            product_kwargs=dict(product_version='1.1',
                                metric_source_ids={self.__birt: 'birt'}),
            include=False)

    def test_no_approved_us(self):
        """ Test that the approved user stories metric is not added when the product is not a trunk version. """
        self.__assert_metric(
            metric.UserStoriesNotApproved,
            project_kwargs=dict(metric_sources={metric_source.Birt: self.__birt}),
            product_kwargs=dict(product_version='1.1', metric_source_ids={self.__birt: 'birt'}),
            include=False)

    def test_reviewed_ltcs(self):
        """ Test that the reviewed logical test case metric is added if possible. """
        self.__assert_metric(
            metric.LogicalTestCasesNotReviewed,
            project_kwargs=dict(metric_sources={metric_source.Birt: self.__birt}),
            product_kwargs=dict(metric_source_ids={self.__birt: 'birt'}))

    def test_approved_ltcs(self):
        """ Test that the approved logical test case metric is added if possible. """
        self.__assert_metric(
            metric.LogicalTestCasesNotApproved,
            project_kwargs=dict(metric_sources={metric_source.Birt: self.__birt}),
            product_kwargs=dict(metric_source_ids={self.__birt: 'birt'}))

    def test_no_reviewed_ltcs(self):
        """ Test that the reviewed logical test case metric is not added when the product is not a trunk version. """
        self.__assert_metric(
            metric.LogicalTestCasesNotReviewed,
            project_kwargs=dict(metric_sources={metric_source.Birt: self.__birt}),
            product_kwargs=dict(product_version='1.1', metric_source_ids={self.__birt: 'birt'}),
            include=False)

    def test_no_approved_ltcs(self):
        """ Test that the approved logical test case metric is not added when the product is not a trunk version. """
        self.__assert_metric(
            metric.LogicalTestCasesNotApproved,
            project_kwargs=dict(metric_sources={metric_source.Birt: self.__birt}),
            product_kwargs=dict(product_version='1.1', metric_source_ids={self.__birt: 'birt'}),
            include=False)

    def test_number_manual_ltcs(self):
        """ Test that the number of manual logical test case metric is added if possible. """
        self.__assert_metric(
            metric.NumberOfManualLogicalTestCases,
            project_kwargs=dict(metric_sources={metric_source.Birt: self.__birt}),
            product_kwargs=dict(metric_source_ids={self.__birt: 'birt'}))

    def test_no_number_manual_ltcs(self):
        """ Test that the number of manual logical test case metric is not added when the product is not a trunk
            version. """
        self.__assert_metric(
            metric.NumberOfManualLogicalTestCases,
            project_kwargs=dict(metric_sources={metric_source.Birt: self.__birt}),
            product_kwargs=dict(product_version='1.1', metric_source_ids={self.__birt: 'birt'}),
            include=False)

    def test_duration_manual_ltcs(self):
        """ Test that the duration of manual logical test case metric is added if possible. """
        self.__assert_metric(
            metric.DurationOfManualLogicalTestCases,
            project_kwargs=dict(metric_sources={metric_source.Jira: FakeJira()}))

    def test_no_duration_manual_ltcs(self):
        """ Test that the duration of manual logical test case metric is not added without Jira. """
        self.__assert_metric(
            metric.DurationOfManualLogicalTestCases,
            project_kwargs=dict(), include=False)

    def test_manual_ltcs_without_duration(self):
        """ Test that the manual logical test case without duration metric is added if possible. """
        self.__assert_metric(
            metric.ManualLogicalTestCasesWithoutDuration,
            project_kwargs=dict(metric_sources={metric_source.Jira: FakeJira()}))

    def test_no_manual_ltcs_without_duration(self):
        """ Test that the manual logical test case without duration metric is not added without Jira. """
        self.__assert_metric(metric.ManualLogicalTestCasesWithoutDuration, project_kwargs=dict(), include=False)

    def test_jsf_duplication(self):
        """ Test that the jsf duplication metric is added if possible. """
        self.__assert_metric(
            metric.JsfDuplication,
            project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}),
            product_kwargs=dict(jsf=dict(metric_source_ids={self.__sonar: 'id'})))

    def test_no_jsf_duplication(self):
        """ Test that the jsf duplication metric is not added if the jsf component has no Sonar id. """
        self.__assert_metric(
            metric.JsfDuplication,
            project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}),
            product_kwargs=dict(jsf=dict(short_name='foo')),
            include=False)

    def test_response_times(self):
        """ Test that the response times metric is added if possible. """
        self.__assert_metric(
            metric.ResponseTimes,
            project_kwargs=dict(metric_sources={metric_source.PerformanceReport: self.__jmeter}),
            product_kwargs=dict(metric_source_ids={self.__jmeter: 'id'}))

    def test_open_bugs(self):
        """ Test that the open bugs metric is added if possible. """
        self.__assert_metric(
            metric.OpenBugs,
            project_kwargs=dict(metric_sources={metric_source.Jira: FakeJira()}))

    def test_open_security_bugs(self):
        """ Test that the open security bugs metric is added if possible. """
        self.__assert_metric(
            metric.OpenSecurityBugs,
            project_kwargs=dict(metric_sources={metric_source.Jira: FakeJira()}))

    def test_blocking_test_issues(self):
        """ Test that the blocking test issues metric is added if possible. """
        self.__assert_metric(
            metric.BlockingTestIssues,
            project_kwargs=dict(metric_sources={metric_source.Jira: FakeJira()}))

    def test_technical_debt_issues(self):
        """ Test that the technical debt issues metric is added if possible. """
        self.__assert_metric(
            metric.TechnicalDebtIssues,
            project_kwargs=dict(metric_sources={metric_source.Jira: FakeJira()}))

    def test_failing_ci_jobs(self):
        """ Test that the failing CI jobs metric is added if possible. """
        self.__assert_metric(
            metric.FailingCIJobs,
            project_kwargs=dict(metric_sources={metric_source.Jenkins: 'Jenkins'}))

    def test_unused_ci_jobs(self):
        """ Test that the unused CI jobs metric is added if possible. """
        self.__assert_metric(
            metric.UnusedCIJobs,
            project_kwargs=dict(metric_sources={metric_source.Jenkins: 'Jenkins'}))

    def test_configuration_consistency(self):
        """ Test that the configuration consistency metric is added if possible. """
        self.__assert_metric(
            metric.JavaVersionConsistency,
            project_kwargs=dict(metric_sources={metric_source.AnsibleConfigReport: 'Ansible'}))

    def test_action_activity(self):
        """ Test that the action activity metric is added if possible. """
        self.__assert_metric(
            metric.ActionActivity,
            project_kwargs=dict(metric_sources={metric_source.TrelloActionsBoard: 'Trello'}))

    def test_action_age(self):
        """ Test that the action age metric is added if possible. """
        self.__assert_metric(
            metric.ActionAge,
            project_kwargs=dict(metric_sources={metric_source.TrelloActionsBoard: 'Trello'}))

    def test_risk_log(self):
        """ Test that the risk log metric is added if possible. """
        self.__assert_metric(
            metric.RiskLog,
            project_kwargs=dict(metric_sources={metric_source.TrelloRiskBoard: 'Trello'}))

    def test_unmerged_branches(self):
        """ Test that the unmerged branches metric is added if possible. """
        subversion = FakeSubversion()
        self.__assert_metric(
            metric.UnmergedBranches,
            project_kwargs=dict(metric_sources={metric_source.VersionControlSystem: subversion}),
            product_kwargs=dict(metric_source_ids={subversion: 'svn'}))

    def test_art_unmerged_branches(self):
        """ Test that the unmerged branches metric is added for the ART. """
        subversion = FakeSubversion()
        self.__assert_metric(
            metric.UnmergedBranches,
            project_kwargs=dict(metric_sources={metric_source.VersionControlSystem: subversion}),
            product_kwargs=dict(art=dict(metric_source_ids={subversion: 'svn'})))

    def test_critical_violations(self):
        """ Test that the critical violations metric is added if possible. """
        self.__assert_metric(
            metric.CriticalViolations,
            project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}),
            product_kwargs=dict(metric_source_ids={self.__sonar: 'id'}))

    def test_no_critical_violations(self):
        """ Test that the critical violations metric is not added if the product has no Sonar id. """
        self.__assert_metric(
            metric.CriticalViolations,
            project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}),
            product_kwargs=dict(short_name='dummy'),
            include=False)

    def test_major_violations(self):
        """ Test that the major violations metric is added if possible. """
        self.__assert_metric(
            metric.MajorViolations,
            project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}),
            product_kwargs=dict(metric_source_ids={self.__sonar: 'id'}))

    def test_no_major_violations(self):
        """ Test that the major violations metric is not added if the product has no Sonar id. """
        self.__assert_metric(
            metric.MajorViolations,
            project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}),
            product_kwargs=dict(short_name='dummy'),
            include=False)

    def test_cyclomatic_complexity(self):
        """ Test that the cyclomatic complexity metric is added if possible. """
        self.__assert_metric(
            metric.CyclomaticComplexity,
            project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}),
            product_kwargs=dict(metric_source_ids={self.__sonar: 'id'}))

    def test_no_cyclomatic_complexity(self):
        """ Test that the cyclomatic complexity metric is not added if the product has no Sonar id. """
        self.__assert_metric(
            metric.CyclomaticComplexity,
            project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}),
            product_kwargs=dict(short_name='dummy'),
            include=False)

    def test_cyclic_dependencies(self):
        """ Test that the cyclic dependencies metric is added if possible. """
        self.__assert_metric(
            metric.CyclicDependencies,
            project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}),
            product_kwargs=dict(metric_source_ids={self.__sonar: 'id'}))

    def test_no_cyclic_dependencies_without_sonar_id(self):
        """ Test that the cyclic dependencies metric is not added if the product has no Sonar id. """
        self.__assert_metric(
            metric.CyclicDependencies,
            project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}),
            product_kwargs=dict(short_name='dummy'),
            include=False)

    def test_no_snapshot_dependencies(self):
        """ Test that the snapshot dependencies metric is not added for trunk versions. """
        self.__assert_metric(
            metric.SnapshotDependencies,
            project_kwargs=dict(metric_sources={metric_source.Pom: self.__pom,
                                                metric_source.Subversion: self.__subversion}),
            product_kwargs=dict(short_name='dummy'), include=False)

    def test_no_snapshot_dependencies_without_pom(self):
        """ Test that the snapshot dependencies metric is not added without pom files. """
        self.__assert_metric(
            metric.SnapshotDependencies,
            project_kwargs=dict(metric_sources={metric_source.Subversion: self.__subversion}),
            product_kwargs=dict(short_name='dummy', product_version='1.1'),
            include=False)

    def test_no_snapshot_dependencies_without_svn(self):
        """ Test that the snapshot dependencies metric is not added without pom files. """
        self.__assert_metric(
            metric.SnapshotDependencies,
            project_kwargs=dict(metric_sources={metric_source.Pom: self.__pom}),
            product_kwargs=dict(short_name='dummy', product_version='1.1'),
            include=False)

    def test_snapshot_dependencies(self):
        """ Test that the snapshot dependencies metric is added if possible. """
        self.__assert_metric(
            metric.SnapshotDependencies,
            project_kwargs=dict(metric_sources={metric_source.Pom: self.__pom,
                                                metric_source.VersionControlSystem: self.__subversion}),
            product_kwargs=dict(short_name='dummy', product_version='1.1'))

    def test_owasp_dependencies(self):
        """ Test that the OWASP dependencies metric is added if possible. """
        self.__assert_metric(
            metric.OWASPDependencies,
            project_kwargs=dict(metric_sources={metric_source.JenkinsOWASPDependencyReport:
                                                self.__owasp_dependency_report}),
            product_kwargs=dict(metric_source_ids={self.__owasp_dependency_report: 'job'}))

    def test_java_duplication(self):
        """ Test that the Java duplication metric is added if possible. """
        self.__assert_metric(
            metric.JavaDuplication,
            project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}),
            product_kwargs=dict(metric_source_ids={self.__sonar: 'id'}))

    def test_no_java_duplication(self):
        """ Test that the Java duplication metric is not added if the
            product has no Sonar id. """
        self.__assert_metric(
            metric.JavaDuplication,
            project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}),
            product_kwargs=dict(short_name='dummy'),
            include=False)

    def test_product_loc(self):
        """ Test that the product LOC metric is added if possible. """
        self.__assert_metric(
            metric.ProductLOC,
            project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}),
            product_kwargs=dict(metric_source_ids={self.__sonar: 'id'}))

    def test_no_product_loc(self):
        """ Test that the product LOC metric is not added if the product has no Sonar id. """
        self.__assert_metric(
            metric.ProductLOC,
            project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}),
            product_kwargs=dict(short_name='dummy'),
            include=False)

    def test_commented_loc(self):
        """ Test that the commented LOC metric is added if possible. """
        self.__assert_metric(
            metric.CommentedLOC,
            project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}),
            product_kwargs=dict(metric_source_ids={self.__sonar: 'id'}))

    def test_no_commented_loc(self):
        """ Test that the commented LOC metric is not added if the product has no Sonar id. """
        self.__assert_metric(
            metric.CommentedLOC,
            project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}),
            product_kwargs=dict(short_name='dummy'),
            include=False)

    def test_no_sonar(self):
        """ Test that the NoSonar metric is added if possible. """
        self.__assert_metric(
            metric.NoSonar,
            project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}),
            product_kwargs=dict(metric_source_ids={self.__sonar: 'id'}))

    def test_no_no_sonar(self):
        """ Test that the NoSonar metric is not added if the product has no Sonar id. """
        self.__assert_metric(
            metric.NoSonar,
            project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}),
            product_kwargs=dict(short_name='dummy'),
            include=False)

    def test_false_positives(self):
        """ Test that the false positives metric is added if possible. """
        self.__assert_metric(
            metric.FalsePositives,
            project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}),
            product_kwargs=dict(metric_source_ids={self.__sonar: 'id'}))

    def test_no_false_positives(self):
        """ Test that the false positives metric is not added if the product has no Sonar id. """
        self.__assert_metric(
            metric.FalsePositives,
            project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}),
            product_kwargs=dict(short_name='dummy'),
            include=False)

    def test_sonar_version(self):
        """ Test that the Sonar version number metric is included. """
        self.__assert_metric(
            metric.SonarVersion,
            project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}))

    def test_document_age(self):
        """ Test that the document age metric is added if possible. """
        subversion = FakeSubversion()
        document = domain.Document(name='Title', url='http://url/', metric_source_ids={subversion: 'http://url/'})
        self.__assert_metric(
            metric.DocumentAge,
            project_kwargs=dict(metric_sources={metric_source.VersionControlSystem: subversion}, documents=[document]))

    def test_no_document_age(self):
        """ Test that the document age metric is not added if the project has no Subversion. """
        document = domain.Document(name='Title', url='http://url')
        self.__assert_metric(metric.DocumentAge,
                             project_kwargs=dict(documents=[document]),
                             include=False)

    def test_user_story_points_ready(self):
        """ Test that the user story points ready metric is added if possible. """
        self.__assert_metric(metric.ReadyUserStoryPoints,
                             project_kwargs=dict(metric_sources={metric_source.Jira: FakeJira()}))

    def test_no_user_story_points_ready(self):
        """ Test that the user story points ready metric is not added if the project has no Jira. """
        self.__assert_metric(metric.ReadyUserStoryPoints, include=False)

    def test_sonar_analysis_age(self):
        """ Test that the analysis age metric is added if possible. """
        self.__assert_metric(metric.SonarAnalysisAge,
                             product_kwargs=dict(metric_source_ids={self.__sonar: 'id'}),
                             project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}))

    def test_no_sonar_analysis_age_without_product(self):
        """ Test that the analysis age metric is added if possible. """
        self.__assert_metric(metric.SonarAnalysisAge,
                             project_kwargs=dict(metric_sources={metric_source.Sonar: self.__sonar}),
                             include=False)

    def test_no_sonar_analysis_age(self):
        """ Test that the analysis age metric is added if possible. """
        self.__assert_metric(metric.SonarAnalysisAge, include=False)

    def test_metric_classes(self):
        """ Test that the report gives a list of metric classes. """
        self.assertTrue(metric.ARTStatementCoverage in report.QualityReport.metric_classes())

    def test_total_loc(self):
        """ Test that the total LOC metric is added if the project contains the
            trusted product maintainability standard as requirement. """
        self.__assert_metric(
            metric.TotalLOC,
            product_kwargs=dict(short_name='dummy'),
            project_kwargs=dict(
                metric_sources={metric_source.Sonar: self.__sonar},
                requirements=[requirement.TRUSTED_PRODUCT_MAINTAINABILITY]))

    def test_java_metrics(self):
        """ Test that the Java related Sonar version metrics are added if the project has Java as requirement. """
        for metric_class in (metric.SonarPluginVersionJava, metric.SonarPluginVersionCheckStyle,
                             metric.SonarPluginVersionPMD, metric.SonarPluginVersionFindBugs,
                             metric.SonarQualityProfileVersionJava):
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
        for metric_class in (metric.SonarPluginVersionWeb, metric.SonarQualityProfileVersionWeb):
            self.__assert_metric(
                metric_class,
                project_kwargs=dict(requirements=[requirement.WEB]))

    def test_js_metrics(self):
        """ Test that the JavaScript related version metrics are added if the project contains JavaScript as
            requirement. """
        for metric_class in (metric.SonarPluginVersionJS, metric.SonarQualityProfileVersionJS):
            self.__assert_metric(
                metric_class,
                project_kwargs=dict(requirements=[requirement.JAVASCRIPT]))
