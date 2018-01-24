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
import urllib.error
import unittest
from unittest.mock import patch, call, MagicMock

from hqlib.metric_source import Sonar, url_opener, extract_branch_decorator


class SonarUnderTest(Sonar):  # pylint: disable=too-few-public-methods
    """ Override the url open method to be able to return test data. """

    sonar_version = '5.6'

    api_components_show_json = '{"component": {"analysisDate": "2017-04-07T16:27:27+0000"}}'

    project_json = """[{"k": "product"}]"""

    json = violations_json = """
[
    {"lang": "java",
     "k": "product",
     "msr":
         [
            {"val": 100, "rule_name": "", "rule_key": ""},
            {"val": 50, "rule_name": "Cyclomatic complexity",
             "rule_key": "squid:MethodCyclomaticComplexity"},
            {"val": 50, "rule_name": "JavaNCSS",
             "rule_key": "checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.JavaNCSSCheck"},
            {"val": 50, "rule_name": "Parameter Number", "rule_key": "squid:S00107"},
            {"val": 40, "rule_name": "Avoid commented-out lines of code",
             "rule_key": "squid:CommentedOutCodeLine"}
        ]
    }
]"""

    no_violations_json = """
[
    {"lang": "java",
     "k": "product",
     "msr":
         []
    }
]"""

    metrics_json = """{
                "component": {
                    "id": "AVxecPLIOLHGO__A5L2R",
                    "key": "product",
                    "name": "product",
                    "qualifier": "TRK",
                    "measures": [
                                    {"metric": "critical_violations", "value": "100"},
                                    {"metric": "blocker_violations", "value": "100"},
                                    {"metric": "major_violations", "value": "100"},
                                    {"metric": "branch_coverage", "value": "100"},
                                    {"metric": "commented_loc", "value": "100"},
                                    {"metric": "duplicated_lines", "value": "100"},
                                    {"metric": "test_failures", "value": "100"},
                                    {"metric": "test_errors", "value": "100"},
                                    {"metric": "line_coverage", "value": "100"},
                                    {"metric": "lines", "value": "100"},
                                    {"metric": "ncloc", "value": "100"},
                                    {"metric": "functions", "value": "100"},
                                    {"metric": "tests", "value": "100"}
                    ]
                }
        }"""

    false_positives_json = """
{
  "maxResultsReached": false,
  "paging": {
    "pageIndex": 1,
    "pageSize": 100,
    "total": 8,
    "fTotal": "8",
    "pages": 1
  },
  "issues": [
    {
      "key": "44ff1a9a-2151-42c1-9b55-3d7473b02337",
      "component": "nl.overheid:common:src/main/java/nl/overheid/model/Model.java",
      "componentId": 651,
      "project": "nl.overheid:query-parent",
      "rule": "squid:MethodCyclomaticComplexity",
      "status": "RESOLVED",
      "resolution": "FALSE-POSITIVE",
      "severity": "MAJOR",
      "message": "The Cyclomatic Complexity of this method \\"equals\\" is 15 which is greater than 10 authorized.",
      "line": 98,
      "debt": "15min",
      "creationDate": "2015-09-16T14:18:24+0000",
      "updateDate": "2015-10-15T09:52:51+0000",
      "fUpdateAge": "7 days"
    },
    {
      "key": "48fabb2c-6f0d-4475-99ac-72295697083a",
      "component": "nl.overheid:query-service:src/main/java/nl/overheid/query/QueryService.java",
      "componentId": 280,
      "project": "nl.overheid:query-parent",
      "rule": "pmd:AvoidCatchingGenericException",
      "status": "RESOLVED",
      "resolution": "FALSE-POSITIVE",
      "severity": "MAJOR",
      "message": "Avoid catching generic exceptions in try-catch block",
      "line": 124,
      "debt": "15min",
      "creationDate": "2015-09-16T14:18:24+0000",
      "updateDate": "2015-10-15T11:36:21+0000",
      "fUpdateAge": "7 days",
      "comments": [
        {
          "key": "3d87ec0a-bf29-439d-a864-d5a848a19087",
          "login": "admin",
          "userName": "Administrator",
          "htmlText": "Deze catch-all is er om te voorkomen dat ...",
          "updatable": false,
          "createdAt": "2015-10-15T11:36:21+0000"
        }
      ]
    },
    {
      "key": "099afed1-fb17-4a38-a8ba-803a1327793a",
      "component": "nl.overheid:register-service:src/main/java/nl/overh.../AssociationService.java",
      "componentId": 625,
      "project": "nl.overheid:query-parent",
      "rule": "squid:MethodCyclomaticComplexity",
      "status": "RESOLVED",
      "resolution": "FALSE-POSITIVE",
      "severity": "MAJOR",
      "message": "The Cyclomatic Complexity of this method is 17 which is greater than 10 authorized.",
      "line": 613,
      "debt": "17min",
      "creationDate": "2015-09-16T14:18:24+0000",
      "updateDate": "2015-10-15T09:51:30+0000",
      "fUpdateAge": "7 days"
    },
    {
      "key": "b0ca9b89-43cc-4339-9b1b-2a68b6fe089a",
      "component": "nl.overheid:register-service:src/main/java/nl/overh.../AssociationService.java",
      "componentId": 625,
      "project": "nl.overheid:query-parent",
      "rule": "checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.JavaNCSSCheck",
      "status": "RESOLVED",
      "resolution": "FALSE-POSITIVE",
      "severity": "MAJOR",
      "message": "NCSS for this method is 26 (max allowed is 20).",
      "line": 613,
      "debt": "3h",
      "creationDate": "2015-09-21T16:05:07+0000",
      "updateDate": "2015-10-15T09:52:14+0000",
      "fUpdateAge": "7 days"
    },
    {
      "key": "e09759bb-192c-4b83-8353-0d8045bcdcd3",
      "component": "nl.overheid:register-service:src/main/java/nl/overh.../ResultaatCodeValidator.java",
      "componentId": 936,
      "project": "nl.overheid:query-parent",
      "rule": "squid:MethodCyclomaticComplexity",
      "status": "RESOLVED",
      "resolution": "FALSE-POSITIVE",
      "severity": "MAJOR",
      "message": "The Cyclomatic Complexity of this method \\"fail\\" is 12 which is greater than 10 authorized.",
      "line": 42,
      "debt": "12min",
      "creationDate": "2015-09-28T18:08:15+0000",
      "updateDate": "2015-10-15T09:51:53+0000",
      "fUpdateAge": "7 days"
    },
    {
      "key": "a7ffb03e-dfbd-4240-bbf5-5c2640d0ff98",
      "component": "nl.overheid:metadata:src/main/java/nl/overheid/metadata/MetadataTimerService.java",
      "componentId": 899,
      "project": "nl.overheid:query-parent",
      "rule": "pmd:AvoidCatchingGenericException",
      "status": "RESOLVED",
      "resolution": "FALSE-POSITIVE",
      "severity": "MAJOR",
      "message": "Avoid catching generic exceptions in try-catch block",
      "line": 75,
      "debt": "15min",
      "creationDate": "2015-09-28T19:39:39+0000",
      "updateDate": "2015-10-15T09:54:40+0000",
      "fUpdateAge": "7 days"
    },
    {
      "key": "9d01f697-393b-471f-874b-d32cfb1a0c1b",
      "component": "nl.overheid:metadata:src/main/java/nl/overh.../MetadataParser.java",
      "componentId": 944,
      "project": "nl.overheid:query-parent",
      "rule": "squid:MethodCyclomaticComplexity",
      "status": "RESOLVED",
      "resolution": "FALSE-POSITIVE",
      "severity": "MAJOR",
      "message": "The Cyclomatic Complexity of this method is 11 which is greater than 10 authorized.",
      "line": 550,
      "debt": "11min",
      "creationDate": "2015-09-28T19:39:39+0000",
      "updateDate": "2015-10-15T09:53:50+0000",
      "fUpdateAge": "7 days"
    },
    {
      "key": "eaf9970e-9ef7-4c5e-974b-17f1957a4341",
      "component": "nl.overheid:common:src/main/java/nl/overheid/ABC.java",
      "componentId": 678,
      "project": "nl.overheid:query-parent",
      "rule": "squid:S1192",
      "status": "RESOLVED",
      "resolution": "FALSE-POSITIVE",
      "severity": "MAJOR",
      "message": "Define a constant instead of duplicating this literal \\"password\\" 4 times.",
      "line": 139,
      "debt": "10min",
      "creationDate": "2015-10-13T07:33:45+0000",
      "updateDate": "2015-10-15T09:53:00+0000",
      "fUpdateAge": "7 days"
    }
  ]
}
"""

    def url_read(self, url: str, encoding: str='utf-8', *args, **kwargs) -> str:
        """ Return the static contents. """
        if 'raise' in url:
            raise urllib.error.HTTPError(None, None, None, None, None)
        if 'server/version' in url:
            return self.sonar_version
        if 'api/components/show' in url:
            return self.api_components_show_json
        if 'analyses' in url:
            if 'empty' in url:
                return '{"analyses": []}'
            else:
                return '{"analyses": [{"events": [{"name": "4.2"}], "date": "2016-04-07T16:27:27+0000"}]}'
        if 'projects/index' in url:
            json = self.project_json
        elif 'metricKeys' in url:
            json = self.metrics_json
        elif 'FALSE-POSITIVE' in url:
            json = self.false_positives_json
        else:
            json = self.json
        return json


class SonarTestCase(unittest.TestCase):
    """ Base class for Sonar unit tests. """
    def setUp(self):
        SonarUnderTest._Sonar__get_json.cache_clear()
        SonarUnderTest._Sonar__metric.cache_clear()
        self._sonar = SonarUnderTest('http://sonar/')


class SonarTest(SonarTestCase):
    """ Unit tests for the Sonar class. """

    def test_url(self):
        """ Test the url. """
        self.assertEqual('http://sonar/', self._sonar.url())

    def test_dashboard_url(self):
        """ Test the url of a dashboard for a specific product. """
        self.assertEqual('http://sonar/dashboard?id=product', self._sonar.dashboard_url('product'))

    def test_violations_url(self):
        """ Test the url of a violations page for a specific product. """
        self.assertEqual('http://sonar/issues/search#resolved=false|componentRoots=product',
                         self._sonar.violations_url('product'))

    def test_version(self):
        """ Test that the version of a product is equal to the version returned by the dashboard of that product. """
        self.assertEqual('4.2', self._sonar.version('product'))

    def test_version_without_analyses(self):
        """ Test that the version is unknowm if Sonar has no analyses for the product. """
        self.assertEqual('?', self._sonar.version('empty'))

    def test_ncloc(self):
        """ Test that the number of non-commented lines of code equals the ncloc returned by the dashboard. """
        self.assertEqual(100, self._sonar.ncloc('product'))

    def test_lines(self):
        """ Test that the number of lines of code equals the number of lines returned by the dashboard. """
        self.assertEqual(100, self._sonar.lines('product'))

    def test_duplicated_lines(self):
        """ Test that the number of duplicated lines equals the number of duplicated lines returned by the
            dashboard. """
        self.assertEqual(100, self._sonar.duplicated_lines('product'))

    def test_methods(self):
        """ Test that the number of methods equals the number of methods returned by the dashboard. """
        self.assertEqual(100, self._sonar.methods('product'))

    def test_commented_loc(self):
        """ Test that the number of commented loc equals the number of commented loc returned by the dashboard. """
        self._sonar.json = """{"paging": {"total": 40}}"""
        self.assertEqual(40, self._sonar.commented_loc('product'))

    def test_commented_loc_missing(self):
        """ Test that the number of commented loc is zero when none of the rules return a result. """
        self._sonar.json = """{"paging": {"total": 0}}"""
        self.assertEqual(0, self._sonar.commented_loc('product'))

    def test_complex_methods(self):
        """ Test that the number of complex methods equals the number of complex methods returned by the
            violations page. """
        self._sonar.json = """{"paging": {"total": 50}}"""
        self.assertEqual(50, self._sonar.complex_methods('product'))

    def test_complex_methods_missing(self):
        """ Test that the number of complex methods is zero when none of the rules return a result. """
        self._sonar.json = """{"paging": {"total": 0}}"""
        self.assertEqual(0, self._sonar.commented_loc('product'))

    def test_long_methods(self):
        """ Test that the number of long methods equals the number of long methods returned by the violations page. """
        self._sonar.json = """{"paging": {"total": 50}}"""
        self.assertEqual(50, self._sonar.long_methods('product'))

    def test_many_parameters_methods(self):
        """ Test that the number of methods with many parameters equals the number of methods with many parameters
            returned by the violations page. """
        self._sonar.json = """{"paging": {"total": 50}}"""
        self.assertEqual(50, self._sonar.many_parameters_methods('product'))

    def test_many_parameters_methods_missing(self):
        """ Test that the number of methods with many parameters is zero when none of the rules return a result. """
        self._sonar.json = """{"paging": {"total": 0}}"""
        self.assertEqual(0, self._sonar.many_parameters_methods('product'))

    def test_missing_metric_value(self):
        """ Test that -1 is returned for missing values. """
        self._sonar.metrics_json = '{"component": {"measures":[]}}'
        self.assertEqual(-1, self._sonar.unittests('product'))

    def test_missing_violation_value(self):
        """ Test that the default value is returned for missing violations. """
        self._sonar.json = """{"paging": {"total": 0}}"""
        self.assertEqual(0, self._sonar.long_methods('product'))

    def test_analysis_datetime(self):
        """ Test that the analysis date and time is correct. """
        self.assertEqual(datetime.datetime(2016, 4, 7, 16, 27, 27), self._sonar.datetime('product'))

    def test_analysis_datetime_without_version(self):
        """ Test that the analysis date and time is correct even if Sonar has no version number. """
        self._sonar.sonar_version = None
        self.assertEqual(datetime.datetime(2016, 4, 7, 16, 27, 27), self._sonar.datetime('product'))

    def test_analysis_datetime_without_analyses(self):
        """ Test that the analysis date and time is the minimum date and time if Sonar has no analyses. """
        self.assertEqual(datetime.datetime.min, self._sonar.datetime('empty'))

    def test_analysis_datetime_6_4(self):
        """ Test the analysis date and time using SonarQube >= 6.4. """
        self._sonar.sonar_version = '6.4'
        self.assertEqual(datetime.datetime(2017, 4, 7, 16, 27, 27), self._sonar.datetime('product'))

    def test_analysis_datetime_6_4_url_exception(self):
        """ Test the analysis date and time using SonarQube >= 6.4. """
        self._sonar.sonar_version = '6.4'
        self.assertEqual(datetime.datetime.min, self._sonar.datetime('raise'))

    def test_analysis_datetime_6_4_missing_data(self):
        """ Test the analysis date and time using SonarQube >= 6.4. """
        self._sonar.sonar_version = '6.4'
        self._sonar.api_components_show_json = '{}'
        self.assertEqual(datetime.datetime.min, self._sonar.datetime('product'))


class SonarCoverage(SonarTestCase):
    """ Unit tests for unit test, integration test, and coverage metrics. """

    def test_unittest_line_coverage(self):
        """ Test that the line coverage equals the line coverage returned by the dashboard. """
        self.assertEqual(100, self._sonar.unittest_line_coverage('product'))

    def test_unittest_branch_coverage(self):
        """ Test that the branch coverage equals the branch coverage returned by the dashboard. """
        self.assertEqual(100, self._sonar.unittest_branch_coverage('product'))

    def test_unittests(self):
        """ Test that the number of unit tests equals the number of unit tests returned by the dashboard. """
        self.assertEqual(100, self._sonar.unittests('product'))

    def test_failing_unittests(self):
        """ Test that the number of failing unit tests equals the number of unit test failures plus the number of
            unit test errors returned by the dashboard. """
        self.assertEqual(200, self._sonar.failing_unittests('product'))


class SonarViolationsTest(SonarTestCase):
    """ Unit tests for violations. """

    def test_major_violations(self):
        """ Test that the number of major violations equals the number of major violations returned by the
            dashboard. """
        self.assertEqual(100, self._sonar.major_violations('product'))

    def test_major_violation_for_missing_product(self):
        """ Test that the number of violations for a missing product is -1. """
        self.assertEqual(-1, self._sonar.major_violations('missing'))

    def test_critical_violations(self):
        """ Test that the number of critical violations equals the number of critical violations returned by the
            dashboard. """
        self.assertEqual(100, self._sonar.critical_violations('product'))

    def test_blocker_violations(self):
        """ Test that the number of blocker violations equals the number of blocker violations returned by the
            dashboard. """
        self.assertEqual(100, self._sonar.blocker_violations('product'))


class SonarSuppressionTest(SonarTestCase):
    """ Unit tests for suppression metrics. """

    def test_no_sonar(self):
        """ Test that by default the number of no sonar violations is zero. """
        self._sonar.json = """{"paging": {"total": 0}}"""
        self.assertEqual(0, self._sonar.no_sonar('product'))

    def test_no_sonar_found(self):
        """ Test that no sonar violations. """
        self._sonar.json = """{"paging": {"total": 10}}"""
        self.assertEqual(10, self._sonar.no_sonar('product'))

    def test_false_positives(self):
        """ Test the number of false positives. """
        self.assertEqual(8, self._sonar.false_positives('product'))

    def test_no_false_positives(self):
        """ Test that the number of false positives is zero. """
        self._sonar.false_positives_json = """
        {
            "issues": []
        }"""
        self.assertEqual(0, self._sonar.false_positives('product'))


class SonarVersionsTest(SonarTestCase):
    """ Unit tests for Sonar meta data. """

    def test_version_number(self):
        """ Test that the version number is correct. """
        self.assertEqual('5.6', self._sonar.version_number())

    def test_plugin_version(self):
        """ Test that the plugins can be retrieved. """
        self._sonar.json = """
        [{
            "key": "pmd",
            "name": "PMD",
            "version": "1.1"
        }]"""
        self.assertEqual('1.1', self._sonar.plugin_version('pmd'))

    def test_missing_plugin(self):
        """ Test that the version number of a missing plugin is 0.0. """
        self._sonar.json = """
        [{
            "key": "pmd",
            "name": "PMD",
            "version": "1.1"
        }]"""
        self.assertEqual('0.0', self._sonar.plugin_version('checkstyle'))

    def test_default_quality_profile(self):
        """ Test that the name of the quality profile is returned. """
        self._sonar.json = """{"profiles":
        [{
            "key": "java-findbugs-94130",
            "name": "FindBugs",
            "language": "java",
            "isDefault": false
        },
        {
            "key": "java-java-profile-v1-7-20151021-85551",
            "name": "Java profile v1.7-20151021",
            "language": "java",
            "isDefault": false
        },
        {
            "key": "java-java-profile-v1-8-20151111-91699",
            "name": "Java profile v1.8-20151111",
            "language": "java",
            "isDefault": true
        },
        {
            "key": "java-sonar-way-31199",
            "name": "Sonar way",
            "language": "java",
            "isDefault": false
        }]}"""
        self.assertEqual("Java profile v1.8-20151111", self._sonar.default_quality_profile('java'))

    def test_quality_profiles_url(self):
        """ Test that the url to the quality profiles page is correct. """
        self.assertEqual('http://sonar/profiles/', self._sonar.quality_profiles_url())

    def test_plugins_url(self):
        """ Test that the url to the plugin updatecenter page is correct. """
        self.assertEqual('http://sonar/updatecenter/', self._sonar.plugins_url())


@patch.object(url_opener.UrlOpener, 'url_read')
class SonarBranchParameterTest(unittest.TestCase):
    """" Unit tests for branch functionality """

    def test_branch_param(self, url_read_mock):
        """" Test that the correct branch name is returned, when server version is >= 6.7 """

        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:my-branch"
        server_version = '6.8.1234'
        non_json_ret_val = 'non json'
        plugins_json = '[{"key":"branch","name":"Branch","version":"1.0.0.507"}]'
        url_read_mock.side_effect = [server_version, plugins_json, non_json_ret_val]
        sonar = Sonar(fake_url)
        func = MagicMock()
        decorated_func = extract_branch_decorator(func)

        decorated_func(sonar, product)

        calls = [call(fake_url+'api/server/version'),
                 call(fake_url+'api/updatecenter/installed_plugins'),
                 call(fake_url+'api/components/show?component={component}'.format(component=product), log_error=False)]
        url_read_mock.assert_has_calls(calls)
        func.assert_called_with(sonar, "nl.ictu:quality_report", "my-branch")

    def test_branch_param_no_component_json_valid(self, url_read_mock):
        """" Test that the correct branch name is returned, when server version is >= 6.7 """

        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:my-branch"
        server_version = '6.8.1234'
        component_ret_val = '{"whatever": "not a component"}'
        plugins_json = '[{"key":"branch","name":"Branch","version":"1.0.0.507"}]'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val]
        sonar = Sonar(fake_url)
        func = MagicMock()
        decorated_func = extract_branch_decorator(func)

        decorated_func(sonar, product)

        calls = [call(fake_url + 'api/server/version'),
                 call(fake_url + 'api/updatecenter/installed_plugins'),
                 call(fake_url + 'api/components/show?component={component}'.format(component=product),
                      log_error=False)]
        url_read_mock.assert_has_calls(calls)
        func.assert_called_with(sonar, "nl.ictu:quality_report", "my-branch")

    def test_branch_param_no_branch(self, url_read_mock):
        """" Test that no branch name is returned, when the product has no : character """

        fake_url = "http://fake.url/"
        product = "nl.ictu_quality_report_my-branch"
        server_version = '6.8.1234'
        non_json_ret_val = 'non json'
        url_read_mock.side_effect = [server_version, non_json_ret_val]
        sonar = Sonar(fake_url)
        func = MagicMock()
        decorated_func = extract_branch_decorator(func)

        decorated_func(sonar, product)

        calls = [call(fake_url + 'api/server/version'),
                 call(fake_url + 'api/updatecenter/installed_plugins')]
        url_read_mock.assert_has_calls(calls)
        func.assert_called_with(sonar, product, None)

    def test_branch_param_when_component(self, url_read_mock):
        """" Test that the branch name is empty, when component exists """

        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:my-branch"
        component_ret_val = '{"component": {"organization": "my-org-1"}}'
        plugins_json = '[{"key":"branch"}]'
        server_version = '6.8.1234'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val]
        sonar = Sonar(fake_url)
        func = MagicMock()
        decorated_func = extract_branch_decorator(func)

        decorated_func(sonar, product)

        calls = [call(fake_url + 'api/server/version'),
                 call(fake_url + 'api/updatecenter/installed_plugins'),
                 call(fake_url + 'api/components/show?component={component}'.format(component=product),
                      log_error=False)]
        url_read_mock.assert_has_calls(calls)
        func.assert_called_with(sonar, product, None)

    def test_branch_param_old(self, url_read_mock):
        """" Test that the empty branch name is returned, when server version is < 6.7 """

        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:my-branch"
        server_version = '6.6.1234'
        url_read_mock.return_value = server_version
        sonar = Sonar(fake_url)
        func = MagicMock()
        decorated_func = extract_branch_decorator(func)

        decorated_func(sonar, product)

        url_read_mock.assert_called_with(fake_url + 'api/server/version')
        func.assert_called_with(sonar, product, None)

    def test_branch_param_plugin_answer_no_json(self, url_read_mock):
        """" Test that the empty branch name is returned, when no Branch plugin is installed """

        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:my-branch"
        server_version = '6.8.1234'
        plugins_json = 'non json'
        url_read_mock.side_effect = [server_version, plugins_json]
        sonar = Sonar(fake_url)
        func = MagicMock()
        decorated_func = extract_branch_decorator(func)

        decorated_func(sonar, product)

        calls = [call(fake_url + 'api/server/version'),
                 call(fake_url + 'api/updatecenter/installed_plugins')]
        url_read_mock.assert_has_calls(calls)
        func.assert_called_with(sonar, product, None)

    def test_branch_param_no_plugin(self, url_read_mock):
        """" Test that the branch name is empty, when branch plugin is not installed. """

        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:my-branch"
        plugins_json = '[{"key":"not-a-branch"}]'
        server_version = '6.8.1234'
        url_read_mock.side_effect = [server_version, plugins_json]
        sonar = Sonar(fake_url)
        func = MagicMock()
        decorated_func = extract_branch_decorator(func)

        decorated_func(sonar, product)

        calls = [call(fake_url + 'api/server/version'),
                 call(fake_url + 'api/updatecenter/installed_plugins')]
        url_read_mock.assert_has_calls(calls)
        func.assert_called_with(sonar, product, None)

    def test_branch_param_url_fault(self, url_read_mock):
        """" Test that the branch name is empty, when getting plugin information throws """

        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:my-branch"
        plugins_json = urllib.error.HTTPError(None, None, None, None, None)
        server_version = '6.8.1234'
        url_read_mock.side_effect = [server_version, plugins_json]
        sonar = Sonar(fake_url)
        func = MagicMock()
        decorated_func = extract_branch_decorator(func)

        decorated_func(sonar, product)

        calls = [call(fake_url + 'api/server/version'),
                 call(fake_url + 'api/updatecenter/installed_plugins')]
        url_read_mock.assert_has_calls(calls)
        func.assert_called_with(sonar, product, None)


@patch.object(url_opener.UrlOpener, 'url_read')
class SonarBranchVersionNumberTest(unittest.TestCase):
    """" Unit tests for branch functionality """

    def test_version_number(self, url_read_mock):
        """ Test that the server version number is acquired when Sonar object is created. """

        fake_url = "http://fake.url/"
        server_version = '6.3.0.1234'
        url_read_mock.return_value = server_version

        sonar = Sonar(fake_url)

        self.assertEqual(server_version, sonar.version_number())

    def test_version_number_when_url_opener_throws(self, url_read_mock):
        """ Test that the server version number is acquired when Sonar object created. """

        fake_url = "http://fake.url/"
        url_read_mock.side_effect = urllib.error.HTTPError(None, None, None, None, None)
        product = "product:my-branch"
        sonar = Sonar(fake_url)
        func = MagicMock()
        decorated_func = extract_branch_decorator(func)

        decorated_func(sonar, product)

        self.assertIsNone(sonar.version_number())
        func.assert_called_with(sonar, product, None)


@patch.object(url_opener.UrlOpener, 'url_read')
class SonarVersionWithBranchTest(unittest.TestCase):
    """" Unit tests for branch functionality """

    def test_version_with_branch(self, url_read_mock):
        """" Check that version function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        component_ret_val = '{"whatever": "not a component"}'
        plugins_json = '[{"key":"branch","name":"Branch","version":"1.0.0.507"}]'
        analyses_json = '{"analyses":[{"events":[{"category":"VERSION","name":"version_name"}]}]}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, analyses_json]
        sonar = Sonar(fake_url)

        result = sonar.version(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/project_analyses/search?project={project}&format=json&category=VERSION&branch={branch}'
            .format(project=product, branch=branch), log_error=False)
        self.assertEqual("version_name", result)

    def test_version_without_given_branch(self, url_read_mock):
        """" Check that version function correctly splits an empty branch and does not it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = ""
        server_version = '6.8.1234'
        component_ret_val = '{"whatever": "not a component"}'
        plugins_json = '[{"key":"branch","name":"Branch","version":"1.0.0.507"}]'
        analyses_json = '{"analyses":[{"key":"AWA","events":[{"category":"VERSION","name":"version_name"}]}]}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, analyses_json]
        sonar = Sonar(fake_url)

        result = sonar.version(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/project_analyses/search?project={project}&format=json&category=VERSION'
            .format(project=product), log_error=False)
        self.assertEqual("version_name", result)

    def test_version_wit_branch_when_url_opener_throws(self, url_read_mock):
        """" Check that version function correctly splits an empty branch and does not it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my_branch"
        server_version = '6.8.1234'
        component_ret_val = '{"whatever": "not a component"}'
        plugins_json = '[{"key":"branch","name":"Branch","version":"1.0.0.507"}]'
        analyses_json = urllib.error.HTTPError(None, None, None, None, None)
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, analyses_json, analyses_json]
        sonar = Sonar(fake_url)

        result = sonar.version(product + ':' + branch)

        calls = [call(fake_url +
                      'api/project_analyses/search?project={project}&format=json&category=VERSION&branch={branch}'
                      .format(project=product, branch=branch), log_error=False),
                 call(fake_url +
                      'api/resources?resource={project}&format=json&branch={branch}'
                      .format(project=product, branch=branch))]
        url_read_mock.assert_has_calls(calls)
        self.assertEqual("?", result)


@patch.object(url_opener.UrlOpener, 'url_read')
class SonarNclocBranchTest(unittest.TestCase):
    """" Unit tests for branch functionality """

    def test_ncloc_with_branch(self, url_read_mock):
        """" Check that ncloc function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","ncloc":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        ncloc = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"ncloc","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, ncloc, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.ncloc(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}&branch={branch}'
            .format(component=product, metric='ncloc', branch=branch), log_error=False)
        self.assertEqual(1192, result)

    def test_ncloc_without_branch(self, url_read_mock):
        """" Check that ncloc function orrectly splits an empty branch and does not it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","ncloc":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        ncloc = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"ncloc","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, ncloc, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.ncloc(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='ncloc'), log_error=False)
        self.assertEqual(1192, result)

    def test_ncloc_with_branch_old(self, url_read_mock):
        """" Check that ncloc function correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        ncloc = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"ncloc","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, ncloc, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.ncloc(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='ncloc'), log_error=False)
        self.assertEqual(1192, result)


@patch.object(url_opener.UrlOpener, 'url_read')
class SonarLinesWithBranchTest(unittest.TestCase):
    """" Unit tests for branch functionality """

    def test_lines_with_branch(self, url_read_mock):
        """" Check that lines function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","lines":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        lines = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"lines","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, lines, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.lines(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}&branch={branch}'
            .format(component=product, metric='lines', branch=branch), log_error=False)
        self.assertEqual(1192, result)

    def test_lines_without_branch(self, url_read_mock):
        """" Check that lines function orrectly splits an empty branch and does not it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","lines":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        lines = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"lines","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, lines, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.lines(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='lines'), log_error=False)
        self.assertEqual(1192, result)

    def test_lines_with_branch_old(self, url_read_mock):
        """" Check that lines function correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        lines = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"lines","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, lines, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.lines(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='lines'), log_error=False)
        self.assertEqual(1192, result)


@patch.object(url_opener.UrlOpener, 'url_read')
class SonarViolationsWithBranchTest(unittest.TestCase):
    """" Unit tests for branch functionality """

    def test_major_violations_with_branch(self, url_read_mock):
        """" Check that major_violations function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","major_violations":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        major_violations = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"major_violations","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, major_violations, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.major_violations(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}&branch={branch}'
            .format(component=product, metric='major_violations', branch=branch), log_error=False)
        self.assertEqual(1192, result)

    def test_major_violations_without_branch(self, url_read_mock):
        """" Check that major_violations function splits an empty branch and does not it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","major_violations":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        major_violations = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"major_violations","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, major_violations, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.major_violations(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='major_violations'), log_error=False)
        self.assertEqual(1192, result)

    def test_major_violations_with_branch_old(self, url_read_mock):
        """" Check that major_violations correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        major_violations = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"major_violations","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, major_violations, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.major_violations(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='major_violations'), log_error=False)
        self.assertEqual(1192, result)

    def test_critical_violations_with_branch(self, url_read_mock):
        """" Check that critical_violations correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","critical_violations":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        critical_violations = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"critical_violations","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val,
                                     critical_violations, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.critical_violations(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}&branch={branch}'
            .format(component=product, metric='critical_violations', branch=branch), log_error=False)
        self.assertEqual(1192, result)

    def test_critical_violations_without_branch(self, url_read_mock):
        """" Check that critical_violations correctly splits an empty branch and does not add it to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","critical_violations":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        critical_violations = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"critical_violations","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val,
                                     critical_violations, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.critical_violations(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='critical_violations'), log_error=False)
        self.assertEqual(1192, result)

    def test_critical_violations_with_branch_old(self, url_read_mock):
        """" Check that critical_violations correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        critical_violations = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"critical_violations","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, critical_violations, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.critical_violations(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='critical_violations'), log_error=False)
        self.assertEqual(1192, result)

    def test_blocker_violations_with_branch(self, url_read_mock):
        """" Check that blocker_violations correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","blocker_violations":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        blocker_violations = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"blocker_violations","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, blocker_violations, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.blocker_violations(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}&branch={branch}'
            .format(component=product, metric='blocker_violations', branch=branch), log_error=False)
        self.assertEqual(1192, result)

    def test_blocker_violations_without_branch(self, url_read_mock):
        """" Check that blocker_violations correctly splits an empty branch and does not add it to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","blocker_violations":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        blocker_violations = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"blocker_violations","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, blocker_violations, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.blocker_violations(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='blocker_violations'), log_error=False)
        self.assertEqual(1192, result)

    def test_blocker_violations_with_branch_old(self, url_read_mock):
        """" Check that blocker_violations correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        blocker_violations = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"blocker_violations","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, blocker_violations, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.blocker_violations(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='blocker_violations'), log_error=False)
        self.assertEqual(1192, result)


@patch.object(url_opener.UrlOpener, 'url_read')
class SonarDuplicatedLinesWithBranchTest(unittest.TestCase):
    """" Unit tests for branch functionality """

    def test_duplicated_lines_with_branch(self, url_read_mock):
        """" Check that duplicated_lines function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","duplicated_lines":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        duplicated_lines = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"duplicated_lines","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, duplicated_lines, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.duplicated_lines(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}&branch={branch}'
            .format(component=product, metric='duplicated_lines', branch=branch), log_error=False)
        self.assertEqual(1192, result)

    def test_duplicated_lines_without_branch(self, url_read_mock):
        """" Check that duplicated_lines correctly splits an empty branch and does not it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","duplicated_lines":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        duplicated_lines = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"duplicated_lines","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, duplicated_lines, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.duplicated_lines(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='duplicated_lines'), log_error=False)
        self.assertEqual(1192, result)

    def test_duplicated_lines_with_branch_old(self, url_read_mock):
        """" Check that duplicated_lines correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        duplicated_lines = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"duplicated_lines","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, duplicated_lines, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.duplicated_lines(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='duplicated_lines'), log_error=False)
        self.assertEqual(1192, result)


@patch.object(url_opener.UrlOpener, 'url_read')
class SonarCoverageWithBranchTest(unittest.TestCase):
    """" Unit tests for branch functionality """

    def test_line_coverage_with_branch(self, url_read_mock):
        """" Check that line_coverage function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","line_coverage":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        line_coverage = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"line_coverage","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, line_coverage, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.unittest_line_coverage(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}&branch={branch}'
            .format(component=product, metric='line_coverage', branch=branch), log_error=False)
        self.assertEqual(1192, result)

    def test_line_coverage_without_branch(self, url_read_mock):
        """" Check that line_coverage function splits an empty branch and does not it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","line_coverage":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        line_coverage = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"line_coverage","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, line_coverage, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.unittest_line_coverage(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='line_coverage'), log_error=False)
        self.assertEqual(1192, result)

    def test_line_coverage_with_branch_old(self, url_read_mock):
        """" Check that line_coverage function correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        line_coverage = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"line_coverage","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, line_coverage, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.unittest_line_coverage(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='line_coverage'), log_error=False)
        self.assertEqual(1192, result)

    def test_branch_coverage_with_branch(self, url_read_mock):
        """" Check that branch_coverage function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","branch_coverage":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        branch_coverage = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"branch_coverage","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, branch_coverage, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.unittest_branch_coverage(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}&branch={branch}'
            .format(component=product, metric='branch_coverage', branch=branch), log_error=False)
        self.assertEqual(1192, result)

    def test_branch_coverage_without_branch(self, url_read_mock):
        """" Check that branch_coverage correctly splits an empty branch and does not it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","branch_coverage":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        branch_coverage = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"branch_coverage","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, branch_coverage, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.unittest_branch_coverage(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='branch_coverage'), log_error=False)
        self.assertEqual(1192, result)

    def test_branch_coverage_with_branch_old(self, url_read_mock):
        """" Check that branch_coverage correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        branch_coverage = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"branch_coverage","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, branch_coverage, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.unittest_branch_coverage(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='branch_coverage'), log_error=False)
        self.assertEqual(1192, result)


@patch.object(url_opener.UrlOpener, 'url_read')
class SonarTestsWithBranchTest(unittest.TestCase):
    """" Unit tests for branch functionality """

    def test_tests_with_branch(self, url_read_mock):
        """" Check that tests function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","tests":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        tests = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"tests","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, tests, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.unittests(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}&branch={branch}'
            .format(component=product, metric='tests', branch=branch), log_error=False)
        self.assertEqual(1192, result)

    def test_tests_without_branch(self, url_read_mock):
        """" Check that tests function orrectly splits an empty branch and does not it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","tests":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        tests = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"tests","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, tests, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.unittests(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='tests'), log_error=False)
        self.assertEqual(1192, result)

    def test_tests_with_branch_old(self, url_read_mock):
        """" Check that tests function correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        tests = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"tests","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, tests, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.unittests(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='tests'), log_error=False)
        self.assertEqual(1192, result)


@patch.object(url_opener.UrlOpener, 'url_read')
class SonarFunctionsWithBranchTest(unittest.TestCase):
    """" Unit tests for branch functionality """

    def test_functions_with_branch(self, url_read_mock):
        """" Check that functions function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","functions":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        metric_json = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"functions","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, metric_json, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.methods(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}&branch={branch}'
            .format(component=product, metric='functions', branch=branch), log_error=False)
        self.assertEqual(1192, result)

    def test_functions_without_branch(self, url_read_mock):
        """" Check that functions function splits an empty branch and does not it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","functions":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        metric_json = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"functions","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, metric_json, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.methods(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='functions'), log_error=False)
        self.assertEqual(1192, result)

    def test_functions_with_branch_old(self, url_read_mock):
        """" Check that functions function correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        metric_json = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"functions","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, metric_json, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.methods(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='functions'), log_error=False)
        self.assertEqual(1192, result)


@patch.object(url_opener.UrlOpener, 'url_read')
class SonarDashboardWithBranchTest(unittest.TestCase):
    """" Unit tests for branch functionality """

    def test_dashboard_url(self, url_read_mock):
        """" Check that dashboard_url correctly splits the branch from product and completely ignores it. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","functions":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val]
        sonar = Sonar(fake_url)

        result = sonar.dashboard_url(product + ':' + branch)

        self.assertEqual(fake_url + 'dashboard?id={component}&branch={branch}'.format(component=product, branch=branch),
                         result)

    def test_dashboard_url_old(self, url_read_mock):
        """" Check that dashboard_url does not split the branch from product for sonar versions prior to 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:my-branch"
        server_version = '6.5.1234'
        plugins_json = '[{"key":"branch","name":"Branch","functions":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val]
        sonar = Sonar(fake_url)

        result = sonar.dashboard_url(product)

        self.assertEqual(fake_url + 'dashboard?id={component}'.format(component=product), result)


@patch.object(url_opener.UrlOpener, 'url_read')
class SonarMethodsWithBranchTest(unittest.TestCase):
    """" Unit tests for branch functionality """

    def test_complex_methods_with_branch(self, url_read_mock):
        """" Check that complex_methods function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","complex_methods":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        complex_methods = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.CyclomaticComplexityCheck'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, complex_methods, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.complex_methods(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}&branch={branch}'
            .format(component=product, rule=rule_name, branch=branch))
        self.assertEqual(7, result)

    def test_complex_methods_without_branch(self, url_read_mock):
        """" Check that complex_methods splits an empty branch and does not it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","complex_methods":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        complex_methods = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.CyclomaticComplexityCheck'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, complex_methods, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.complex_methods(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}'
            .format(component=product, rule=rule_name))
        self.assertEqual(7, result)

    def test_complex_methods_with_branch_old(self, url_read_mock):
        """" Check that complex_methods correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        complex_methods = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.CyclomaticComplexityCheck'
        url_read_mock.side_effect = [server_version, complex_methods, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.complex_methods(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}'
            .format(component=product, rule=rule_name))
        self.assertEqual(7, result)

    def test_long_methods_with_branch(self, url_read_mock):
        """" Check that long_methods function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","long_methods":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        long_methods = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'squid:S138'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, long_methods, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.long_methods(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}&branch={branch}'
            .format(component=product, rule=rule_name, branch=branch))
        self.assertEqual(7, result)

    def test_long_methods_without_branch(self, url_read_mock):
        """" Check that long_methods function splits an empty branch and does not it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","long_methods":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        long_methods = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'squid:S138'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, long_methods, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.long_methods(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}'
            .format(component=product, rule=rule_name))
        self.assertEqual(7, result)

    def test_long_methods_with_branch_old(self, url_read_mock):
        """" Check that long_methods function correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        long_methods = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'squid:S138'
        url_read_mock.side_effect = [server_version, long_methods, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.long_methods(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}'
            .format(component=product, rule=rule_name))
        self.assertEqual(7, result)

    def test_many_parameters_methods_with_branch(self, url_read_mock):
        """" Check that many_parameters_methods correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","many_parameters_methods":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        many_parameters_methods = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.ParameterNumberCheck'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val,
                                     many_parameters_methods, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.many_parameters_methods(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}&branch={branch}'
            .format(component=product, rule=rule_name, branch=branch))
        self.assertEqual(7, result)

    def test_many_parameters_methods_without_branch(self, url_read_mock):
        """" Check that many_parameters_methods splits an empty branch and does not it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","many_parameters_methods":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        many_parameters_methods = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.ParameterNumberCheck'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val,
                                     many_parameters_methods, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.many_parameters_methods(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}'
            .format(component=product, rule=rule_name))
        self.assertEqual(7, result)

    def test_many_parameters_methods_with_branch_old(self, url_read_mock):
        """" Check that many_parameters_methods correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        many_parameters_methods = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.ParameterNumberCheck'
        url_read_mock.side_effect = [server_version, many_parameters_methods, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.many_parameters_methods(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}'
            .format(component=product, rule=rule_name))
        self.assertEqual(7, result)


@patch.object(url_opener.UrlOpener, 'url_read')
class SonarCommentedLocWithBranchTest(unittest.TestCase):
    """" Unit tests for branch functionality """

    def test_commented_loc_with_branch(self, url_read_mock):
        """" Check that commented_loc function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","commented_loc":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        commented_loc = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'csharpsquid:S125'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, commented_loc, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.commented_loc(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}&branch={branch}'
            .format(component=product, rule=rule_name, branch=branch))
        self.assertEqual(7, result)

    def test_commented_loc_without_branch(self, url_read_mock):
        """" Check that commented_loc function splits an empty branch and does not it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","commented_loc":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        commented_loc = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'csharpsquid:S125'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, commented_loc, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.commented_loc(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}'
            .format(component=product, rule=rule_name))
        self.assertEqual(7, result)

    def test_commented_loc_with_branch_old(self, url_read_mock):
        """" Check that commented_loc function correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        commented_loc = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'csharpsquid:S125'
        url_read_mock.side_effect = [server_version, commented_loc, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.commented_loc(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}'
            .format(component=product, rule=rule_name))
        self.assertEqual(7, result)


@patch.object(url_opener.UrlOpener, 'url_read')
class SonarNoSonarWithBranchTest(unittest.TestCase):
    """" Unit tests for branch functionality """

    def test_no_sonar_with_branch(self, url_read_mock):
        """" Check that no_sonar function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","no_sonar":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        no_sonar = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'squid:NoSonar'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, no_sonar, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.no_sonar(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}&branch={branch}'
            .format(component=product, rule=rule_name, branch=branch))
        self.assertEqual(7, result)

    def test_no_sonar_without_branch(self, url_read_mock):
        """" Check that no_sonar function splits an empty branch and does not it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","no_sonar":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        no_sonar = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'squid:NoSonar'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, no_sonar, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.no_sonar(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}'
            .format(component=product, rule=rule_name))
        self.assertEqual(7, result)

    def test_no_sonar_with_branch_old(self, url_read_mock):
        """" Check that no_sonar function correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        no_sonar = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'squid:NoSonar'
        url_read_mock.side_effect = [server_version, no_sonar, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.no_sonar(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}'
            .format(component=product, rule=rule_name))
        self.assertEqual(7, result)


@patch.object(url_opener.UrlOpener, 'url_read')
class SonarFalsePositivesWithBranchTest(unittest.TestCase):
    """" Unit tests for branch functionality """

    def test_false_positives_url(self, url_read_mock):
        """" Check that false_positives_url correctly splits the branch from product and completely ignores it. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","functions":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val]
        sonar = Sonar(fake_url)

        result = sonar.false_positives_url(product + ':' + branch)

        self.assertEqual(fake_url + 'issues/search#resolutions=FALSE-POSITIVE|'
                                    'componentRoots={resource}&branch={branch}'.format(resource=product, branch=branch),
                         result)

    def test_false_positives_url_old(self, url_read_mock):
        """" Check that false_positives_url does not split the branch from product for sonar versions prior to 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:my-branch"
        server_version = '6.5.1234'
        plugins_json = '[{"key":"branch","name":"Branch","functions":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val]
        sonar = Sonar(fake_url)

        result = sonar.false_positives_url(product)

        self.assertEqual(fake_url + 'issues/search#resolutions=FALSE-POSITIVE|componentRoots={resource}'
                         .format(resource=product), result)


@patch.object(url_opener.UrlOpener, 'url_read')
class SonarUnitTestsWithBranchTest(unittest.TestCase):
    """" Unit tests for branch functionality """

    def test_failing_unittests_with_branch(self, url_read_mock):
        """" Check that failing_unittests correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","failing_unittests":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        failing_unittests = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"test_failures","value":"7"}]}}'
        measures_err_json = '{"component":{"measures":[{"metric":"test_errors","value":"4"}]}}'
        url_read_mock.side_effect = \
            [server_version, plugins_json, component_ret_val, failing_unittests, measures_json, measures_err_json]
        sonar = Sonar(fake_url)

        result = sonar.failing_unittests(product + ':' + branch)

        calls = [
            call(fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}&branch={branch}'
                 .format(component=product, metric='test_failures', branch=branch), log_error=False),
            call(fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}&branch={branch}'
                 .format(component=product, metric='test_errors', branch=branch), log_error=False)]

        url_read_mock.assert_has_calls(calls)
        self.assertEqual(11, result)

    def test_failing_unittests_without_branch(self, url_read_mock):
        """" Check that failing_unittests function splits an empty branch and does not it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","failing_unittests":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        failing_unittests = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"test_failures","value":"7"}]}}'
        measures_err_json = '{"component":{"measures":[{"metric":"test_errors","value":"4"}]}}'
        url_read_mock.side_effect = \
            [server_version, plugins_json, component_ret_val, failing_unittests, measures_json, measures_err_json]
        sonar = Sonar(fake_url)

        result = sonar.failing_unittests(product + ':')

        calls = [
            call(fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
                 .format(component=product, metric='test_failures'), log_error=False),
            call(fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
                 .format(component=product, metric='test_errors'), log_error=False)]

        url_read_mock.assert_has_calls(calls)
        self.assertEqual(11, result)

    def test_failing_unittests_with_branch_old(self, url_read_mock):
        """" Check that failing_unittests function handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        failing_unittests = '[{"id":6151,"k":"' + product + '","nm":"Name-name","sc":"PRJ","qu":"BRC"}]'
        measures_json = '{"component":{"measures":[{"metric":"test_failures","value":"7"}]}}'
        measures_err_json = '{"component":{"measures":[{"metric":"test_errors","value":"4"}]}}'
        url_read_mock.side_effect = [server_version, failing_unittests, measures_json, measures_err_json]
        sonar = Sonar(fake_url)

        result = sonar.failing_unittests(product)

        calls = [
            call(fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
                 .format(component=product, metric='test_failures'), log_error=False),
            call(fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
                 .format(component=product, metric='test_errors'), log_error=False)]

        url_read_mock.assert_has_calls(calls)
        self.assertEqual(11, result)


@patch.object(url_opener.UrlOpener, 'url_read')
class SonarDatetimeWithBranchTest(unittest.TestCase):
    """" Unit tests for branch functionality """

    def test_datetime_with_branch(self, url_read_mock):
        """" Check that datetime function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","vrs":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        show_json = '{"component":{"analysisDate":"2017-11-23T10:55:33+0000"}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, show_json]
        sonar = Sonar(fake_url)

        result = sonar.datetime(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/components/show?component={component}&branch={branch}'
            .format(component=product, branch=branch))
        self.assertEqual(datetime.datetime(2017, 11, 23, 10, 55, 33), result)

    def test_datetime_without_branch(self, url_read_mock):
        """" Check that datetime function splits an empty branch and does not it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","vrs":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        show_json = '{"component":{"analysisDate":"2017-11-23T10:55:33+0000"}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, show_json]
        sonar = Sonar(fake_url)

        result = sonar.datetime(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/components/show?component={component}'
            .format(component=product))
        self.assertEqual(datetime.datetime(2017, 11, 23, 10, 55, 33), result)

    def test_datetime_with_branch_old(self, url_read_mock):
        """" Check that datetime function correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        show_json = '{"component":{"analysisDate":"2017-11-23T10:55:33+0000"}}'
        url_read_mock.side_effect = [server_version, show_json]
        sonar = Sonar(fake_url)

        result = sonar.datetime(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/components/show?component={component}'
            .format(component=product))
        self.assertEqual(datetime.datetime(2017, 11, 23, 10, 55, 33), result)

    def test_datetime_with_branch_with_resource_url(self, url_read_mock):
        """" Check that datetime does not split the branch and calls resource url, with sonar >= 6.4 and < 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:my-branch"
        server_version = '6.3.1234'
        show_json = urllib.error.HTTPError(None, None, None, None, None)
        old_show_json = '[{"date":"2017-11-29T15:10:31+0000"}]'
        url_read_mock.side_effect = [server_version, show_json, old_show_json]
        sonar = Sonar(fake_url)

        result = sonar.datetime(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/resources?resource={resource}&format=json'.format(resource=product))
        self.assertEqual(datetime.datetime(2017, 11, 29, 15, 10, 31), result)

    def test_datetime_with_branch_with_resource_url_throwing(self, url_read_mock):
        """" Check that datetime function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:my-branch"
        server_version = '6.3.1234'
        show_json = urllib.error.HTTPError(None, None, None, None, None)
        resource_throw = urllib.error.HTTPError(None, None, None, None, None)
        url_read_mock.side_effect = [server_version, show_json, resource_throw]
        sonar = Sonar(fake_url)

        result = sonar.datetime(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/resources?resource={resource}&format=json'.format(resource=product))
        self.assertEqual(datetime.datetime.min, result)
