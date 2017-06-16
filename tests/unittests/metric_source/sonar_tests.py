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

from hqlib.metric_source import Sonar


class SonarUnderTest(Sonar):  # pylint: disable=too-few-public-methods
    """ Override the url open method to be able to return test data. """

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

    metrics_json = """
    [
        {"lang": "java",
         "msr":
             [
                {"val": 100, "key": "critical_violations"},
                {"val": 100, "key": "blocker_violations"},
                {"val": 100, "key": "major_violations"},
                {"val": 100, "key": "branch_coverage"},
                {"val": 100, "key": "commented_loc"},
                {"val": 100, "key": "duplicated_lines"},
                {"val": 100, "key": "test_failures"},
                {"val": 100, "key": "test_errors"},
                {"val": 100, "key": "line_coverage"},
                {"val": 100, "key": "it_line_coverage"},
                {"val": 100, "key": "it_branch_coverage"},
                {"val": 100, "key": "overall_line_coverage"},
                {"val": 100, "key": "overall_branch_coverage"},
                {"val": 100, "key": "lines"},
                {"val": 100, "key": "ncloc"},
                {"val": 100, "key": "functions"},
                {"val": 100, "key": "tests"}
            ]
        }
    ]"""

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
      "component": "nl.overheid.bsnk:bsnk-common:src/main/java/nl/overheid/bsnk/association/model/Association.java",
      "componentId": 651,
      "project": "nl.overheid.bsnk:bsnkquery-parent",
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
      "component": "nl.overheid.bsnk:bsnkquery-service:src/main/java/nl/overheid/bsnk/bsnkquery/BSNKQueryService.java",
      "componentId": 280,
      "project": "nl.overheid.bsnk:bsnkquery-parent",
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
      "component": "nl.overheid.bsnk:bsnkregister-service:src/main/java/nl/overh.../AssociationService.java",
      "componentId": 625,
      "project": "nl.overheid.bsnk:bsnkquery-parent",
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
      "component": "nl.overheid.bsnk:bsnkregister-service:src/main/java/nl/overh.../AssociationService.java",
      "componentId": 625,
      "project": "nl.overheid.bsnk:bsnkquery-parent",
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
      "component": "nl.overheid.bsnk:bsnkregister-service:src/main/java/nl/overh.../ResultaatCodeValidator.java",
      "componentId": 936,
      "project": "nl.overheid.bsnk:bsnkquery-parent",
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
      "component": "nl.overheid.bsnk:bsnk-metadata:src/main/java/nl/overheid/bsnk/metadata/MetadataTimerService.java",
      "componentId": 899,
      "project": "nl.overheid.bsnk:bsnkquery-parent",
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
      "component": "nl.overheid.bsnk:bsnk-metadata:src/main/java/nl/overh.../MetadataParser.java",
      "componentId": 944,
      "project": "nl.overheid.bsnk:bsnkquery-parent",
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
      "component": "nl.overheid.bsnk:bsnk-common:src/main/java/nl/overheid/bsnk/CFG.java",
      "componentId": 678,
      "project": "nl.overheid.bsnk:bsnkquery-parent",
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

    def url_read(self, url):
        """ Return the static contents. """
        if 'server/version' in url:
            return '1.2.3'
        if 'analyses' in url:
            if 'empty' in url:
                return '{"analyses": []}'
            else:
                return '{"analyses": [{"events": [{"name": "4.2"}], "date": "2016-04-07T16:27:27+0000"}]}'
        if 'projects/index' in url:
            json = self.project_json
        elif 'metrics=true' in url:
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
        self.assertEqual('http://sonar/dashboard/index/product', self._sonar.dashboard_url('product'))

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
        """ Test that the default value is returned for missing values. """
        self._sonar.metrics_json = '[{"msr": []}]'
        self.assertEqual(0, self._sonar.unittests('product'))

    def test_missing_violation_value(self):
        """ Test that the default value is returned for missing violations. """
        self._sonar.json = """{"paging": {"total": 0}}"""
        self.assertEqual(0, self._sonar.long_methods('product'))

    def test_analysis_datetime(self):
        """ Test that the analysis date and time is correct. """
        self.assertEqual(datetime.datetime(2016, 4, 7, 16, 27, 27), self._sonar.datetime('product'))

    def test_analysis_datetime_without_analyses(self):
        """ Test that the analysis date and time is the minimum date and time if Sonar has no analyses. """
        self.assertEqual(datetime.datetime.min, self._sonar.datetime('empty'))


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

    def test_integration_test_line_coverage(self):
        """ Test that the integration test line coverage equals the line coverage returned by the dashboard. """
        self.assertEqual(100, self._sonar.integration_test_line_coverage('product'))

    def test_integration_test_branch_coverage(self):
        """ Test that the integration test branch coverage equals the branch coverage returned by the dashboard. """
        self.assertEqual(100, self._sonar.integration_test_branch_coverage('product'))

    def test_overall_test_line_coverage(self):
        """ Test that the overall test line coverage equals the line coverage returned by the dashboard. """
        self.assertEqual(100, self._sonar.overall_test_line_coverage('product'))

    def test_overall_test_branch_coverage(self):
        """ Test that the overall test branch coverage equals the branch coverage returned by the dashboard. """
        self.assertEqual(100, self._sonar.overall_test_branch_coverage('product'))

    def test_overall_line_coverage(self):
        """ Test that the overall test line coverage equals the line coverage returned by the dashboard. """
        self.assertEqual(100, self._sonar.overall_test_line_coverage('product'))

    def test_overall_branch_coverage(self):
        """ Test that the overall test branch coverage equals the branch coverage returned by the dashboard. """
        self.assertEqual(100, self._sonar.overall_test_branch_coverage('product'))


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
        self.assertEqual('1.2.3', self._sonar.version_number())

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
