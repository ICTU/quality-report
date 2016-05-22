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
import io
import unittest

from qualitylib.metric_source import Sonar


class SonarUnderTest(Sonar):  # pylint: disable=too-few-public-methods
    """ Override the url open method to be able to return test data. """

    json = violations_json = u"""
[
    {"version": "4.2",
     "lang": "java",
     "date": "2016-04-07T16:27:27+0000",
     "key": "product",
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

    no_violations_json = u"""
[
    {"version": "4.2",
     "lang": "java",
     "key": "product",
     "msr":
         []
    }
]"""

    metrics_json = u"""
    [
        {"version": "4.2",
         "lang": "java",
         "key": "product",
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
                {"val": 100, "key": "lines"},
                {"val": 100, "key": "ncloc"},
                {"val": 100, "key": "functions"},
                {"val": 100, "key": "tests"},
                {"val": 100, "key": "package_cycles"}
            ]
        }
    ]"""

    false_positives_json = u"""
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

    def url_open(self, url):
        """ Return the static contents. """
        if 'metrics=true' in url:
            json = self.metrics_json
        elif 'FALSE-POSITIVE' in url:
            json = self.false_positives_json
        else:
            json = self.json
        return io.StringIO(json)


class SonarTest(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """ Unit tests for the Sonar class. """

    def setUp(self):
        self.__sonar = SonarUnderTest('http://sonar/')

    def test_url(self):
        """ Test the url. """
        self.assertEqual('http://sonar/', self.__sonar.url())

    def test_dashboard_url(self):
        """ Test the url of a dashboard for a specific product. """
        self.assertEqual('http://sonar/dashboard/index/product', self.__sonar.dashboard_url('product'))

    def test_violations_url(self):
        """ Test the url of a violations page for a specific product. """
        self.assertEqual('http://sonar/drilldown/violations/product', self.__sonar.violations_url('product'))

    def test_version(self):
        """ Test that the version of a product is equal to the version returned by the dashboard of that product. """
        self.assertEqual('4.2', self.__sonar.version('product'))

    def test_ncloc(self):
        """ Test that the number of non-commented lines of code equals the ncloc returned by the dashboard. """
        self.assertEqual(100, self.__sonar.ncloc('product'))

    def test_lines(self):
        """ Test that the number of lines of code equals the number of lines returned by the dashboard. """
        self.assertEqual(100, self.__sonar.lines('product'))

    def test_major_violations(self):
        """ Test that the number of major violations equals the number of major violations returned by the
            dashboard. """
        self.assertEqual(100, self.__sonar.major_violations('product'))

    def test_critical_violations(self):
        """ Test that the number of critical violations equals the number of critical violations returned by the
            dashboard. """
        self.assertEqual(100, self.__sonar.critical_violations('product'))

    def test_blocker_violations(self):
        """ Test that the number of blocker violations equals the number of blocker violations returned by the
            dashboard. """
        self.assertEqual(100, self.__sonar.blocker_violations('product'))

    def test_duplicated_lines(self):
        """ Test that the number of duplicated lines equals the number of duplicated lines returned by the
            dashboard. """
        self.assertEqual(100, self.__sonar.duplicated_lines('product'))

    def test_line_coverage(self):
        """ Test that the line coverage equals the line coverage returned by the dashboard. """
        self.assertEqual(100, self.__sonar.line_coverage('product'))

    def test_branch_coverage(self):
        """ Test that the branch coverage equals the branch coverage returned by the dashboard. """
        self.assertEqual(100, self.__sonar.branch_coverage('product'))

    def test_unittests(self):
        """ Test that the number of unit tests equals the number of unit tests returned by the dashboard. """
        self.assertEqual(100, self.__sonar.unittests('product'))

    def test_failing_unittests(self):
        """ Test that the number of failing unit tests equals the number of unit test failures plus the number of
            unit test errors returned by the dashboard. """
        self.assertEqual(200, self.__sonar.failing_unittests('product'))

    def test_package_cycles(self):
        """ Test that the number of package cycles equals the number of package cycles returned by the dashboard. """
        self.assertEqual(100, self.__sonar.package_cycles('product'))

    def test_methods(self):
        """ Test that the number of methods equals the number of methods returned by the dashboard. """
        self.assertEqual(100, self.__sonar.methods('product'))

    def test_commented_loc(self):
        """ Test that the number of commented loc equals the number of commented loc returned by the dashboard. """
        self.assertEqual(40, self.__sonar.commented_loc('product'))

    def test_commented_loc_cs(self):
        """ Test that the number of commented loc equals the number of commented loc returned by the dashboard. """
        self.__sonar.json = u"""
        [
            {"version": "4.2",
             "lang": "cs",
             "key": "product",
             "msr":
                 [
                    {"val": 30, "rule_name": "Comment should not include code",
                     "rule_key": "csharpsquid:CommentedCode"}
                ]
            }
        ]"""
        self.assertEqual(30, self.__sonar.commented_loc('product'))

    def test_commented_loc_missing(self):
        """ Test that the number of commented loc is zero when none of the rules return a result. """
        self.__sonar.json = self.__sonar.no_violations_json
        self.assertEqual(0, self.__sonar.commented_loc('product'))

    def test_complex_methods(self):
        """ Test that the number of complex methods equals the number of complex methods returned by the
            violations page. """
        self.assertEqual(50, self.__sonar.complex_methods('product'))

    def test_complex_methods_missing(self):
        """ Test that the number of complex methods is zero when none of the rules return a result. """
        self.__sonar.json = self.__sonar.no_violations_json
        self.assertEqual(0, self.__sonar.commented_loc('product'))

    def test_long_methods(self):
        """ Test that the number of long methods equals the number of long methods returned by the violations page. """
        self.assertEqual(50, self.__sonar.long_methods('product'))

    def test_many_parameters_methods(self):
        """ Test that the number of methods with many parameters equals the number of methods with many parameters
            returned by the violations page. """
        self.assertEqual(50, self.__sonar.many_parameters_methods('product'))

    def test_many_parameters_methods_missing(self):
        """ Test that the number of methods with many parameters is zero when none of the rules return a result. """
        self.__sonar.json = self.__sonar.no_violations_json
        self.assertEqual(0, self.__sonar.many_parameters_methods('product'))

    def test_missing_metric_value(self):
        """ Test that the default value is returned for missing values. """
        self.__sonar.metrics_json = u'[{"msr": []}]'
        self.assertEqual(0, self.__sonar.unittests('product'))

    def test_missing_violation_value(self):
        """ Test that the default value is returned for missing violations. """
        self.__sonar.json = u'[{"key": "product", "lang": "java"}]'
        self.assertEqual(0, self.__sonar.long_methods('product'))

    def test_no_sonar(self):
        """ Test that by default the number of no sonar violations is zero. """
        self.assertEqual(0, self.__sonar.no_sonar('product'))

    def test_no_sonar_found(self):
        """ Test that no sonar violations. """
        self.__sonar.json = u"""
        [
            {"key": "product",
             "msr":
                 [
                    {"val": 10, "rule_key": "squid:NoSonar",
                     "rule_name": "Avoid use of //NOSONAR marker"}
                ]
            }
        ]"""
        self.assertEqual(10, self.__sonar.no_sonar('product'))

    def test_false_positives(self):
        """ Test the number of false positives. """
        self.assertEqual(8, self.__sonar.false_positives('product'))

    def test_no_false_positives(self):
        """ Test that the number of false positives is zero. """
        self.__sonar.false_positives_json = u"""
        {
            "issues": []
        }"""
        self.assertEqual(0, self.__sonar.false_positives('product'))

    def test_version_number(self):
        """ Test that the version number is correct. """
        self.__sonar.json = u"""
        {
            "id": "23422",
             "version": "1.2.3",
             "status": "UP"
        }"""
        self.assertEqual('1.2.3', self.__sonar.version_number())

    def test_analysis_datetime(self):
        """ Test that the analysis date and time is correct. """
        self.assertEqual(datetime.datetime(2016, 4, 7, 16, 27, 27), self.__sonar.analysis_datetime('product'))

    def test_plugin_version(self):
        """ Test that the plugins can be retrieved. """
        self.__sonar.json = u"""
        [{
            "key": "pmd",
            "name": "PMD",
            "version": "1.1"
        }]"""
        self.assertEqual('1.1', self.__sonar.plugin_version('pmd'))

    def test_missing_plugin(self):
        """ Test that the version number of a missing plugin is -1. """
        self.__sonar.json = u"""
        [{
            "key": "pmd",
            "name": "PMD",
            "version": "1.1"
        }]"""
        self.assertEqual(-1, self.__sonar.plugin_version('checkstyle'))

    def test_default_quality_profile(self):
        """ Test that the name of the quality profile is returned. """
        self.__sonar.json = u"""
        [{
            "key": "java-findbugs-94130",
            "name": "FindBugs",
            "language": "java",
            "default": false
        },
        {
            "key": "java-ictu-java-profile-v1-7-20151021-85551",
            "name": "ICTU Java profile v1.7-20151021",
            "language": "java",
            "default": false
        },
        {
            "key": "java-ictu-java-profile-v1-8-20151111-91699",
            "name": "ICTU Java profile v1.8-20151111",
            "language": "java",
            "default": true
        },
        {
            "key": "java-sonar-way-31199",
            "name": "Sonar way",
            "language": "java",
            "default": false
        }]"""
        self.assertEqual("ICTU Java profile v1.8-20151111", self.__sonar.default_quality_profile('java'))

    def test_quality_profiles_url(self):
        """ Test that the url to the quality profiles page is correct. """
        self.assertEqual('http://sonar/profiles/', self.__sonar.quality_profiles_url())

    def test_plugins_url(self):
        """ Test that the url to the plugin updatecenter page is correct. """
        self.assertEqual('http://sonar/updatecenter/', self.__sonar.plugins_url())
