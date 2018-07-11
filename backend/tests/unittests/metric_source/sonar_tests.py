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

import logging
import datetime
import urllib.error
import unittest
from unittest.mock import patch, call, MagicMock
from distutils.version import LooseVersion
from json import JSONDecodeError

from hqlib.metric_source import Sonar, Sonar6, Sonar7, url_opener, extract_branch_decorator


def clear_method_cache(class_object, function_name: str):
    """ Function clears the cache of a method class_object.function_name """
    sonar_method_list = [getattr(class_object, method) for method in dir(class_object) if function_name == method]
    if sonar_method_list and sonar_method_list[0]:
        cache_clear = getattr(sonar_method_list[0], 'cache_clear')
        if cache_clear:
            cache_clear()


class SonarFacadeTest(unittest.TestCase):
    """ Tests Sonar facade class. """

    @patch.object(Sonar, 'version_number')
    @patch.object(logging, 'warning')
    def test_version_too_low(self, mock_log_warning, mock_version_number):
        """ Test that the error is logged when Sonar version is lower than 6.0. """
        mock_version_number.return_value = '3.6'

        sonar = Sonar('unimportant')

        mock_log_warning.assert_called_once_with(
            "SonarQube version lower than 5.4 is not supported. Version %s detected.", LooseVersion('3.6'))
        self.assertIsNotNone(sonar)
        self.assertIsInstance(sonar, Sonar6)

    @patch.object(Sonar, 'version_number')
    @patch.object(logging, 'warning')
    def test_version_not_supported(self, mock_log_warning, mock_version_number):
        """ Test that the error is logged when Sonar version is not supported. """
        mock_version_number.return_value = '999.6'

        sonar = Sonar('unimportant')

        mock_log_warning.assert_called_once_with(
            "SonarQube version %s is not supported. Supported versions are from 6.0 to 9.0(excluding).",
            LooseVersion('999.6'))
        self.assertIsNotNone(sonar)
        self.assertIsInstance(sonar, Sonar7)

    @patch.object(Sonar, 'version_number')
    def test_version_6(self, mock_version_number):
        """ Test that the Sonar6 is instantiated when version number 6.x is passed. """
        mock_version_number.return_value = '6.3'

        sonar = Sonar('unimportant')

        self.assertIsNotNone(sonar)
        self.assertIsInstance(sonar, Sonar6)

    @patch.object(Sonar, 'version_number')
    def test_version_7(self, mock_version_number):
        """ Test that the Sonar7 is instantiated when version number 7.x is passed. """
        mock_version_number.return_value = '7.0'

        sonar = Sonar('unimportant')

        self.assertIsNotNone(sonar)
        self.assertIsInstance(sonar, Sonar7)

    @patch.object(Sonar, 'version_number')
    def test_version_none(self, mock_version_number):
        """ Test that the Sonar6 is instantiated when none version number is is passed. """
        mock_version_number.return_value = None

        sonar = Sonar('unimportant')

        self.assertIsNotNone(sonar)
        self.assertIsInstance(sonar, Sonar6)

    @patch.object(url_opener.UrlOpener, 'url_read')
    @patch.object(logging, 'info')
    def test_version_number(self, mock_info, mock_url_read):
        """ Test that the version number is correct. """
        mock_url_read.return_value = "5.6"
        self.assertEqual('5.6', Sonar('unimportant').version_number())
        self.assertEqual(call("Sonar Qube server version retrieved: %s", '5.6'), mock_info.call_args_list[0])
        self.assertEqual(call('Sonar class instantiated as Sonar6.'), mock_info.call_args_list[1])

    @patch.object(url_opener.UrlOpener, 'url_read')
    @patch.object(logging, 'warning')
    def test_version_number_none(self, mock_warning, mock_url_read):
        """ Test that the version number is correct. """
        mock_url_read.side_effect = urllib.error.HTTPError(None, None, None, None, None)
        self.assertEqual(None, Sonar('unimportant').version_number())
        mock_warning.assert_called_once_with("Error retrieving Sonar Qube server version!")


class Sonar6PublicMethodsTest(unittest.TestCase):
    """ Test methods of Sonar6 that do not need url mocking """

    @patch.object(Sonar6, 'version_number')
    @patch.object(Sonar6, 'unittest_branch_coverage')
    def test_has_branch_coverage(self, mock_unittest_branch_coverage, mock_version_number):
        """ Test that Sonar6 has branch coverage """
        mock_version_number.return_value = '6.3'
        mock_unittest_branch_coverage.return_value = 2
        sonar = Sonar6('url')
        self.assertTrue(sonar.has_branch_coverage('metric_source_id'))

    @patch.object(Sonar6, 'version_number')
    @patch.object(Sonar6, 'unittest_branch_coverage')
    def test_has_branch_coverage_not(self, mock_unittest_branch_coverage, mock_version_number):
        """ Test that Sonar6 has no branch coverage if unittest_branch_coverage returns -1. """
        mock_version_number.return_value = '6.3'
        mock_unittest_branch_coverage.return_value = -1
        sonar = Sonar6('url')
        self.assertFalse(sonar.has_branch_coverage('metric_source_id'))

    @patch.object(Sonar6, 'version_number')
    def test_has_branch_coverage_when_no_version(self, mock_version_number):
        """ Test that Sonar6 formally has branch coverage when no valid version number is returne. """
        mock_version_number.return_value = None
        sonar = Sonar6('url')
        self.assertTrue(sonar.has_branch_coverage('metric_source_id'))


class Sonar6TestCase(unittest.TestCase):
    """ Base class for Sonar unit tests. """
    def setUp(self):
        clear_method_cache(Sonar, '_get_json')
        clear_method_cache(Sonar6, '_metric')
        clear_method_cache(Sonar6, 'is_branch_plugin_installed')

        with patch.object(Sonar, 'version_number') as mock_version_number:
            mock_version_number.return_value = '6.3'
            self._sonar = Sonar('http://sonar/')


@patch.object(url_opener.UrlOpener, 'url_read')
class Sonar6Test(Sonar6TestCase):
    """ Unit tests for the Sonar class. """

    # pylint: disable=no-member

    def test_is_branch_plugin_installed(self, mock_url_read):
        """" Test that the branch plugin is installed. """
        mock_url_read.return_value = '[{"key":"branch","name":"Branch","version":"1.0.0.507"}]'
        self.assertTrue(self._sonar.is_branch_plugin_installed())

    @patch.object(logging, 'info')
    def test_is_branch_plugin_not_installed(self, mock_info, mock_url_read):
        """" Test that the branch plugin is not installed. """
        mock_url_read.return_value = '[{"key":"x","name":"X"}]'

        result = self._sonar.is_branch_plugin_installed()

        mock_info.assert_called_once_with("Branch plugin not installed.")
        self.assertFalse(result)

    @patch.object(logging, 'error')
    def test_is_branch_plugin_json_error(self, mock_error, mock_url_read):
        """" Test that the branch plugin is reported not installed if json decode error happens. """
        mock_url_read.side_effect = 'not-valid-json'
        result = self._sonar.is_branch_plugin_installed()
        mock_error.assert_called()
        self.assertEqual(mock_error.call_args[0][0],
                         "Error parsing response from %s: '%s'. Assume the branch plugin is not installed.")
        self.assertEqual(mock_error.call_args[0][1], 'http://sonar/api/updatecenter/installed_plugins?format=json')
        self.assertIsInstance(mock_error.call_args[0][2], JSONDecodeError)
        self.assertFalse(result)

    @patch.object(logging, 'error')
    def test_is_branch_plugin_type_error(self, mock_error, mock_url_read):
        """" Test that the branch plugin is reported not installed if json type error happens. """
        mock_url_read.side_effect = 'not-valid-json'
        result = self._sonar.is_branch_plugin_installed()
        mock_error.assert_called()
        self.assertEqual(mock_error.call_args[0][0],
                         "Error parsing response from %s: '%s'. Assume the branch plugin is not installed.")
        self.assertEqual(mock_error.call_args[0][1], 'http://sonar/api/updatecenter/installed_plugins?format=json')
        self.assertIsInstance(mock_error.call_args[0][2], JSONDecodeError)
        self.assertFalse(result)

    @patch.object(logging, 'warning')
    def test_is_branch_plugin_http_error(self, mock_warning, mock_url_read):
        """" Test that the branch plugin is reported not installed if http error happens. """
        mock_url_read.side_effect = urllib.error.HTTPError(None, None, None, None, None)
        result = self._sonar.is_branch_plugin_installed()
        # mock_warning.assert_called_once_with("Couldn't open %s: %s", 'xxxxxxx', '')
        mock_warning.assert_called_once()
        self.assertEqual(mock_warning.call_args[0][0], "Couldn't open %s: %s")
        self.assertEqual(mock_warning.call_args[0][1], 'http://sonar/api/updatecenter/installed_plugins?format=json')
        self.assertIsInstance(mock_warning.call_args[0][2], urllib.error.HTTPError)
        self.assertFalse(result)

    def test_is_component_absent_http_error(self, mock_url_read):
        """ Test that it returns true if the component is absent. """
        mock_url_read.side_effect = urllib.error.HTTPError(None, None, None, None, None)
        self.assertTrue(self._sonar.is_component_absent('product'))

    @patch.object(logging, 'info')
    def test_is_component_absent(self, mock_info, mock_url_read):
        """ Test that it returns true if the component is absent. """
        mock_url_read.return_value = '{"component": "x"}'
        self.assertFalse(self._sonar.is_component_absent('product'))
        mock_info.assert_called_once_with("Component '%s' found. No branch is defined.", "product")

    def test_is_component_absent_key_error(self, mock_url_read):
        """ Test that it returns true if the component is absent. """
        mock_url_read.return_value = '{"xomponent": "x"}'
        self.assertTrue(self._sonar.is_component_absent('product'))

    def test_version(self, mock_url_read):
        """ Test that the version of a product is equal to the version returned by the dashboard of that product. """
        mock_url_read.side_effect = ["5.6", '{"analyses": [{"events": [{"name": "4.2"}]}]}']
        self.assertEqual('4.2', self._sonar.version('product'))

    @patch.object(Sonar6, 'is_branch_plugin_installed')
    @patch.object(Sonar6, 'is_component_absent')
    def test_version_with_branch(self, mock_is_component_absent, mock_is_branch_plugin_installed, mock_url_read):
        """ Test that the version of a product is equal to the version returned by the dashboard of that product. """
        mock_is_component_absent.return_value = True
        mock_is_branch_plugin_installed.return_value = True
        mock_url_read.side_effect = ["6.8", '{"analyses": [{"events": [{"name": "4.2"}]}]}']
        self.assertEqual('4.2', self._sonar.version('product:branch'))

    @patch.object(logging, 'warning')
    def test_version_index_error(self, mock_warning, mock_url_read):
        """ Test that the version is unknown if Sonar has incomplete analyses. """
        mock_url_read.side_effect = ["5.6", '{"analyses": [{"events": []}]}']

        result = self._sonar.version('prod')

        mock_warning.assert_called_once()
        self.assertIsInstance(mock_warning.call_args[0][4], IndexError)
        self.assertEqual('?', result)

    @patch.object(logging, 'warning')
    def test_version_key_error(self, mock_warning, mock_url_read):
        """ Test that the version is unknown if Sonar has unknown json key. """
        mock_url_read.side_effect = ["5.6", '{"analyses": [{"xvents": [{"name": "4.2"}]}]}']

        result = self._sonar.version('prod')

        mock_warning.assert_called_once()
        self.assertIsInstance(mock_warning.call_args[0][4], KeyError)
        self.assertEqual('?', result)

    @patch.object(logging, 'warning')
    def test_version_older_index_error(self, mock_warning, mock_url_read):
        """ Test that the version is unknown if Sonar has empty version keys, in older server versions. """
        mock_url_read.side_effect = ["5.6", urllib.error.HTTPError(None, None, None, None, None), '[]']

        result = self._sonar.version('prod')

        mock_warning.assert_called_once()
        self.assertIsInstance(mock_warning.call_args[0][4], IndexError)
        self.assertEqual('?', result)

    def test_version_http_errors(self, mock_url_read):
        """ Test that the version is unknown if Sonar constantly returns http faults. """
        mock_url_read.side_effect = \
            ["5.6",
             urllib.error.HTTPError(None, None, None, None, None),
             urllib.error.HTTPError(None, None, None, None, None)]

        result = self._sonar.version('prod')

        self.assertEqual('?', result)

    @patch.object(logging, 'warning')
    def test_version_older_key_error(self, mock_warning, mock_url_read):
        """ Test that the version is unknown if Sonar has no version key, in older server versions. """
        mock_url_read.side_effect = ["5.6", urllib.error.HTTPError(None, None, None, None, None), '{"analyses": []}']

        result = self._sonar.version('prod')

        mock_warning.assert_called_once()
        self.assertIsInstance(mock_warning.call_args[0][4], KeyError)
        self.assertEqual('?', result)

    def test_version_older_key(self, mock_url_read):
        """ Test that the version is unknown if Sonar has no version key, in older server versions. """
        mock_url_read.side_effect = ["5", urllib.error.HTTPError(None, None, None, None, None), '[{"version": "5.2"}]']

        result = self._sonar.version('prod')

        self.assertEqual('5.2', result)

    def test_ncloc(self, mock_url_read):
        """ Test that the number of non-commented lines of code equals the ncloc returned by the dashboard. """
        mock_url_read.side_effect = ["5.6", '[{"k": "product"}]',
                                     '{"component": {"measures": [{"metric": "ncloc", "value": "8554"}]}}']
        self.assertEqual(8554, self._sonar.ncloc('product'))

    def test_lines(self, mock_url_read):
        """ Test that the number of lines of code equals the number of lines returned by the dashboard. """
        mock_url_read.side_effect = ["5.6", '[{"k": "product"}]',
                                     '{"component": {"measures": [{"metric": "lines", "value": "9554"}]}}']
        self.assertEqual(9554, self._sonar.lines('product'))

    def test_duplicated_lines(self, mock_url_read):
        """ Test that the number of duplicated lines equals the number of duplicated lines returned by the
            dashboard. """
        mock_url_read.side_effect = ["5.6", '[{"k": "product"}]',
                                     '{"component": {"measures": [{"metric": "duplicated_lines", "value": "124"}]}}']
        self.assertEqual(124, self._sonar.duplicated_lines('product'))

    def test_methods(self, mock_url_read):
        """ Test that the number of methods equals the number of methods returned by the dashboard. """
        mock_url_read.side_effect = ["5.6", '[{"k": "product"}]',
                                     '{"component": {"measures": [{"metric": "functions", "value": "54"}]}}']
        self.assertEqual(54, self._sonar.methods('product'))

    def test_commented_loc(self, mock_url_read):
        """ Test that the number of commented loc equals the number of commented loc returned by the dashboard. """
        mock_url_read.side_effect = ["5.6", '[{"k": "product"}]', '{"paging": {"total": "40"}}']
        self.assertEqual(40, self._sonar.commented_loc('product'))

    def test_commented_loc_missing(self, mock_url_read):
        """ Test that the number of commented loc is zero when none of the rules return a result. """
        mock_url_read.side_effect = ["5.6", '[{"k": "product"}]'] + ['{"paging": {"total": "0"}}'] * 20
        self.assertEqual(0, self._sonar.commented_loc('product'))

    def test_complex_methods(self, mock_url_read):
        """ Test that the number of complex methods equals the number of complex methods returned by the
            violations page. """
        mock_url_read.side_effect = ["5.6", '[{"k": "product"}]', '{"paging": {"total": "50"}}']
        self.assertEqual(50, self._sonar.complex_methods('product'))

    def test_complex_methods_http_error(self, mock_url_read):
        """ Test that the number of complex methods is -1 when http errors. """
        mock_url_read.side_effect = ["5.6", urllib.error.HTTPError(None, None, None, None, None)]
        self.assertEqual(-1, self._sonar.complex_methods('product'))

    def test_complex_methods_missing(self, mock_url_read):
        """ Test that the number of complex methods is zero when none of the rules return a result. """
        mock_url_read.side_effect = ["5.6", '[{"k": "product"}]'] + ['{"paging": {"total": "0"}}'] * 20
        self.assertEqual(0, self._sonar.complex_methods('product'))

    def test_long_methods(self, mock_url_read):
        """ Test that the number of long methods equals the number of long methods returned by the violations page. """
        mock_url_read.side_effect = ["5.6", '[{"k": "product"}]', '{"paging": {"total": "30"}}']
        self.assertEqual(30, self._sonar.long_methods('product'))

    def test_many_parameters_methods(self, mock_url_read):
        """ Test that the number of methods with many parameters equals the number of methods with many parameters
            returned by the violations page. """
        mock_url_read.side_effect = ["5.6", '[{"k": "product"}]', '{"paging": {"total": "25"}}']
        self.assertEqual(25, self._sonar.many_parameters_methods('product'))

    def test_many_parameters_methods_missing(self, mock_url_read):
        """ Test that the number of methods with many parameters is zero when none of the rules return a result. """
        mock_url_read.side_effect = ["5.6", '[{"k": "product"}]'] + ['{"paging": {"total": "0"}}'] * 20
        self.assertEqual(0, self._sonar.many_parameters_methods('product'))

    def test_missing_metric_value(self, mock_url_read):
        """ Test that -1 is returned for missing values. """
        mock_url_read.side_effect = ["5.6", '[{"k": "product"}]', '{"component": {"measures": []}}']
        self.assertEqual(-1, self._sonar.unittests('product'))

    def test_missing_violation_value(self, mock_url_read):
        """ Test that the default value is returned for missing violations. """
        mock_url_read.side_effect = ["5.6", '[{"k": "product"}]'] + ['{"paging": {"total": "0"}}'] * 20
        self.assertEqual(0, self._sonar.long_methods('product'))

    def test_analysis_datetime(self, mock_url_read):
        """ Test that the analysis date and time is correct. """
        mock_url_read.side_effect = ["5.6", '{"analyses": [{"date": "2016-04-07T16:27:27+0000"}]}']
        self.assertEqual(datetime.datetime(2016, 4, 7, 16, 27, 27), self._sonar.datetime('product'))

    def test_analysis_datetime_without_version(self, mock_url_read):
        """ Test that the analysis date and time is correct even if Sonar has no version number. """
        mock_url_read.side_effect = ["", '{"analyses": [{"date": "2016-04-07T16:27:27+0000"}]}']
        self.assertEqual(datetime.datetime(2016, 4, 7, 16, 27, 27), self._sonar.datetime('product'))

    def test_analysis_datetime_without_analyses(self, mock_url_read):
        """ Test that the analysis date and time is the minimum date and time if Sonar has no analyses. """
        mock_url_read.side_effect = ["5.6", '{"analyses": []}']
        self.assertEqual(datetime.datetime.min, self._sonar.datetime('product'))

    def test_analysis_datetime_6_4(self, mock_url_read):
        """ Test the analysis date and time using SonarQube >= 6.4. """
        mock_url_read.side_effect = ["6.4", '{"component": {"analysisDate": "2017-04-07T16:27:27+0000"}}']
        self.assertEqual(datetime.datetime(2017, 4, 7, 16, 27, 27), self._sonar.datetime('product'))

    def test_analysis_datetime_6_4_url_exception(self, mock_url_read):
        """ Test the analysis date and time using SonarQube >= 6.4. """
        mock_url_read.side_effect = ["6.4", urllib.error.HTTPError(None, None, None, None, None)]
        self.assertEqual(datetime.datetime.min, self._sonar.datetime('product'))

    def test_analysis_datetime_6_4_missing_data(self, mock_url_read):
        """ Test the analysis date and time using SonarQube >= 6.4. """
        mock_url_read.side_effect = ["6.4", '{"component": {}}']
        self.assertEqual(datetime.datetime.min, self._sonar.datetime('product'))


@patch.object(url_opener.UrlOpener, 'url_read')
class Sonar6Coverage(Sonar6TestCase):
    """ Unit tests for unit test, integration test, and coverage metrics. """

    # pylint: disable=no-member

    def test_unittest_line_coverage(self, mock_url_read):
        """ Test that the line coverage equals the line coverage returned by the dashboard. """
        mock_url_read.side_effect = ["5.6", '[{"k": "product"}]',
                                     '{"component": {"measures": [{"metric": "line_coverage", "value": "95"}]}}']
        self.assertEqual(95, self._sonar.unittest_line_coverage('product'))

    def test_unittest_branch_coverage(self, mock_url_read):
        """ Test that the branch coverage equals the branch coverage returned by the dashboard. """
        mock_url_read.side_effect = ["5.6", '[{"k": "product"}]',
                                     '{"component": {"measures": [{"metric": "branch_coverage", "value": "85"}]}}']
        self.assertEqual(85, self._sonar.unittest_branch_coverage('product'))

    def test_unittests(self, mock_url_read):
        """ Test that the number of unit tests equals the number of unit tests returned by the dashboard. """
        mock_url_read.side_effect = ["5.6", '[{"k": "product"}]',
                                     '{"component": {"measures": [{"metric": "tests", "value": "1111"}]}}']
        self.assertEqual(1111, self._sonar.unittests('product'))

    def test_failing_unittests(self, mock_url_read):
        """ Test that the number of failing unit tests equals the number of unit test failures plus the number of
            unit test errors returned by the dashboard. """
        mock_url_read.side_effect = ["5.6", '[{"k": "product"}]',
                                     '{"component": {"measures": [{"metric": "test_failures", "value": "100"}]}}',
                                     '{"component": {"measures": [{"metric": "test_errors", "value": "50"}]}}']
        self.assertEqual(150, self._sonar.failing_unittests('product'))


@patch.object(url_opener.UrlOpener, 'url_read')
class Sonar6ViolationsTest(Sonar6TestCase):
    """ Unit tests for violations. """

    # pylint: disable=no-member

    def test_major_violations(self, mock_url_read):
        """ Test that the number of major violations equals the number of major violations returned by the
            dashboard. """
        mock_url_read.side_effect = ["5.6", '[{"k": "product"}]',
                                     '{"component": {"measures": [{"metric": "major_violations", "value": "26"}]}}']
        self.assertEqual(26, self._sonar.major_violations('product'))

    def test_major_violation_for_missing_product(self, mock_url_read):
        """ Test that the number of violations for a missing product is -1. """
        mock_url_read.side_effect = ["5.6", '[{"k": "product"}]',
                                     '{"component": {"measures": [{"metric": "major_violations", "value": "26"}]}}']
        self.assertEqual(-1, self._sonar.major_violations('missing'))

    def test_critical_violations(self, mock_url_read):
        """ Test that the number of critical violations equals the number of critical violations returned by the
            dashboard. """
        mock_url_read.side_effect = ["5.6", '[{"k": "product"}]',
                                     '{"component": {"measures": [{"metric": "critical_violations", "value": "6"}]}}']
        self.assertEqual(6, self._sonar.critical_violations('product'))

    def test_blocker_violations(self, mock_url_read):
        """ Test that the number of blocker violations equals the number of blocker violations returned by the
            dashboard. """
        mock_url_read.side_effect = ["5.6", '[{"k": "product"}]',
                                     '{"component": {"measures": [{"metric": "blocker_violations", "value": "1"}]}}']
        self.assertEqual(1, self._sonar.blocker_violations('product'))


@patch.object(url_opener.UrlOpener, 'url_read')
class Sonar6SuppressionTest(Sonar6TestCase):
    """ Unit tests for suppression metrics. """

    # pylint: disable=no-member

    def test_no_sonar(self, mock_url_read):
        """ Test that by default the number of no sonar violations is zero. """
        mock_url_read.side_effect = ["5.6", '[{"k": "product"}]'] + ['{"paging": {"total": "0"}}'] * 20
        self.assertEqual(0, self._sonar.no_sonar('product'))

    def test_no_sonar_found(self, mock_url_read):
        """ Test that no sonar violations. """
        self._sonar.json = """{"paging": {"total": 10}}"""
        mock_url_read.side_effect = ["5.6", '[{"k": "product"}]', '{"paging": {"total": "10"}}']
        self.assertEqual(10, self._sonar.no_sonar('product'))

    def test_false_positives(self, mock_url_read):
        """ Test the number of false positives. """
        mock_url_read.side_effect = ["5.6", '[{"k": "product"}]', '{"issues": [{}, {}, {}, {}, {}, {}, {}, {}]}']
        self.assertEqual(8, self._sonar.false_positives('product'))

    def test_no_false_positives(self, mock_url_read):
        """ Test that the number of false positives is zero. """
        mock_url_read.side_effect = ["5.6", '[{"k": "product"}]', '{"issues": []}']
        self.assertEqual(0, self._sonar.false_positives('product'))

    def test_no_false_positives_no_product(self, mock_url_read):
        """ Test that the number of false positives is zero. """
        mock_url_read.side_effect = ["5.6", urllib.error.HTTPError(None, None, None, None, None)]
        self.assertEqual(-1, self._sonar.false_positives('product'))


@patch.object(url_opener.UrlOpener, 'url_read')
class Sonar6VersionsTest(Sonar6TestCase):
    """ Unit tests for Sonar meta data. """

    # pylint: disable=no-member

    def test_plugin_version(self, mock_url_read):
        """ Test that the plugin's version is retrieved correctly. """
        mock_url_read.return_value = '[{"key": "pmd", "name": "PMD", "version": "1.1"}]'
        self.assertEqual('1.1', self._sonar.plugin_version('pmd'))

    def test_plugin_version_with_build(self, mock_url_read):
        """ Test that the plugin's version is retrieved correctly if the build number is put in the brackets. """
        mock_url_read.return_value = '[{"key": "pmd", "name": "PMD", "version": "1.1 (build 1495)"}]'
        self.assertEqual('1.1.1495', self._sonar.plugin_version('pmd'))

    def test_missing_plugin(self, mock_url_read):
        """ Test that the version number of a missing plugin is 0.0. """
        mock_url_read.return_value = '[{"key": "pmd", "name": "PMD", "version": "1.1"}]'
        self.assertEqual('0.0', self._sonar.plugin_version('checkstyle'))

    def test_plugin_version_http_error(self, mock_url_read):
        """ Test that the version number of a missing plugin is 0.0. """
        mock_url_read.side_effect = urllib.error.HTTPError(None, None, None, None, None)
        self.assertEqual('0.0', self._sonar.plugin_version('pmd'))

    def test_default_quality_profile(self, mock_url_read):
        """ Test that the name of the default quality profile is returned. """
        mock_url_read.return_value = """{"profiles":
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

    def test_default_quality_profile_http_errors(self, mock_url_read):
        """ Test that the name of the quality profile is empty if http errors happen. """
        mock_url_read.side_effect =\
            [
                urllib.error.HTTPError(None, None, None, None, None),
                urllib.error.HTTPError(None, None, None, None, None)
            ]

        self.assertEqual("", self._sonar.default_quality_profile('some-strange-language'))

    @patch.object(logging, 'warning')
    def test_default_quality_profile_no_language(self, mock_warning, mock_url_read):
        """ Test that the name of the quality profile is empty if there is no profile for the given language. """
        mock_url_read.return_value = """{"profiles":
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
        result = self._sonar.default_quality_profile('some-strange-language')
        mock_warning.assert_called_once()
        self.assertEqual(mock_warning.call_args[0][0],
                         "Couldn't find a default quality profile for %s in %s, retrieved from %s")
        self.assertEqual(mock_warning.call_args[0][1], 'some-strange-language')
        self.assertEqual("", result)

    @patch.object(logging, 'warning')
    def test_default_quality_profile_no_default(self, mock_warning, mock_url_read):
        """ Test that the name of the quality profile is empty if there is no default profile for the language. """
        mock_url_read.return_value = """{"profiles":
                    [{
                        "key": "java-findbugs-94130",
                        "name": "FindBugs",
                        "language": "java",
                        "isDefault": false
                    }]}"""
        result = self._sonar.default_quality_profile('java')
        mock_warning.assert_called_once()
        self.assertEqual(mock_warning.call_args[0][0],
                         "Couldn't find a default quality profile for %s in %s, retrieved from %s")
        self.assertEqual(mock_warning.call_args[0][1], 'java')
        self.assertEqual("", result)

    @patch.object(logging, 'warning')
    def test_default_quality_profile_no_profiles(self, mock_warning, mock_url_read):
        """ Test that the name of the quality profile is empty if there are no profiles at all. """
        mock_url_read.return_value = """{"profiles": []}"""
        result = self._sonar.default_quality_profile('java')
        mock_warning.assert_called_once()
        self.assertEqual(mock_warning.call_args[0][0],
                         "Couldn't find a default quality profile for %s in %s, retrieved from %s")
        self.assertEqual(mock_warning.call_args[0][1], 'java')
        self.assertEqual("", result)


class Sonar6UrlsTest(Sonar6TestCase):
    """ Unit tests for the Sonar methods that return urls. """

    # pylint: disable=no-member

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

    def test_quality_profiles_url(self):
        """ Test that the url to the quality profiles page is correct. """
        self.assertEqual('http://sonar/profiles/', self._sonar.quality_profiles_url())

    def test_plugins_url(self):
        """ Test that the url to the plugin updatecenter page is correct. """
        self.assertEqual('http://sonar/updatecenter/', self._sonar.plugins_url())


@patch.object(url_opener.UrlOpener, 'url_read')
class Sonar6BranchParameterTest(unittest.TestCase):
    """ Unit tests for branch functionality. """

    # pylint: disable=no-self-use

    def test_branch_param(self, url_read_mock):
        """ Test that the correct branch name is returned, when server version is >= 6.7. """

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

        calls = [call(fake_url + 'api/server/version'),
                 call(fake_url + 'api/updatecenter/installed_plugins?format=json'),
                 call(fake_url + 'api/components/show?component={component}'.format(component=product),
                      log_error=False)]
        url_read_mock.assert_has_calls(calls)
        func.assert_called_with(sonar, "nl.ictu:quality_report", "my-branch")

    def test_branch_param_no_component_json_valid(self, url_read_mock):
        """ Test that the correct branch name is returned, when server version is >= 6.7 """

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
                 call(fake_url + 'api/updatecenter/installed_plugins?format=json'),
                 call(fake_url + 'api/components/show?component={component}'.format(component=product),
                      log_error=False)]
        url_read_mock.assert_has_calls(calls)
        func.assert_called_with(sonar, "nl.ictu:quality_report", "my-branch")

    def test_branch_param_no_branch(self, url_read_mock):
        """ Test that no branch name is returned, when the product has no : character """

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
                 call(fake_url + 'api/updatecenter/installed_plugins?format=json')]
        url_read_mock.assert_has_calls(calls)
        func.assert_called_with(sonar, product, None)

    def test_branch_param_when_component(self, url_read_mock):
        """ Test that the branch name is empty, when component exists """

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
                 call(fake_url + 'api/updatecenter/installed_plugins?format=json'),
                 call(fake_url + 'api/components/show?component={component}'.format(component=product),
                      log_error=False)]
        url_read_mock.assert_has_calls(calls)
        func.assert_called_with(sonar, product, None)

    def test_branch_param_old(self, url_read_mock):
        """ Test that the empty branch name is returned, when server version is < 6.7 """

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
        """ Test that the empty branch name is returned, when no branch plugin is installed """

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
                 call(fake_url + 'api/updatecenter/installed_plugins?format=json')]
        url_read_mock.assert_has_calls(calls)
        func.assert_called_with(sonar, product, None)

    def test_branch_param_no_plugin(self, url_read_mock):
        """ Test that the branch name is empty, when branch plugin is not installed. """

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
                 call(fake_url + 'api/updatecenter/installed_plugins?format=json')]
        url_read_mock.assert_has_calls(calls)
        func.assert_called_with(sonar, product, None)

    def test_branch_param_url_fault(self, url_read_mock):
        """ Test that the branch name is empty, when getting plugin information throws """

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
                 call(fake_url + 'api/updatecenter/installed_plugins?format=json')]
        url_read_mock.assert_has_calls(calls)
        func.assert_called_with(sonar, product, None)


@patch.object(url_opener.UrlOpener, 'url_read')
class Sonar6BranchVersionNumberTest(unittest.TestCase):
    """ Unit tests for branch functionality """

    def test_version_number(self, url_read_mock):
        """ Test that the server version number is acquired when Sonar object is created. """

        fake_url = "http://fake.url/"
        server_version = '6.3.0.1234'
        url_read_mock.return_value = server_version

        sonar = Sonar(fake_url)

        self.assertEqual(server_version, sonar.version_number())

    def test_version_number_when_url_opener_throws(self, url_read_mock):
        """ Test that server version number is None and the error is logged when retrieval fails. """

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
class Sonar6VersionWithBranchTest(unittest.TestCase):
    """ Unit tests for branch functionality """

    # pylint: disable=no-member

    def test_version_with_branch(self, url_read_mock):
        """ Check that version function correctly splits the branch and adds it as a parameter to the url. """
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
            fake_url + 'api/project_analyses/search?project={project}&format=json&ps=1&category=VERSION&branch={branch}'
            .format(project=product, branch=branch), log_error=False)
        self.assertEqual("version_name", result)

    def test_version_without_given_branch(self, url_read_mock):
        """ Check that version function correctly splits an empty branch and does not add it as a parameter to the
            url. """
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
            fake_url + 'api/project_analyses/search?project={project}&format=json&ps=1&category=VERSION'
            .format(project=product), log_error=False)
        self.assertEqual("version_name", result)

    def test_version_wit_branch_when_url_opener_throws(self, url_read_mock):
        """ Check that version function correctly splits an empty branch and does not add it as a parameter to the
            url. """
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

        calls = [call(fake_url + 'api/project_analyses/search?project={project}&format=json&ps=1&category=VERSION&'
                                 'branch={branch}'.format(project=product, branch=branch), log_error=False),
                 call(fake_url + 'api/resources?resource={project}&format=json&'
                                 'branch={branch}'.format(project=product, branch=branch))]
        url_read_mock.assert_has_calls(calls)
        self.assertEqual("?", result)


@patch.object(url_opener.UrlOpener, 'url_read')
class Sonar6NclocBranchTest(unittest.TestCase):
    """ Unit tests for branch functionality """

    # pylint: disable=no-member

    def test_ncloc_with_branch(self, url_read_mock):
        """ Check that ncloc function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","ncloc":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"ncloc","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json,
                                     measures_json]
        sonar = Sonar(fake_url)

        result = sonar.ncloc(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}&branch={branch}'
            .format(component=product, metric='ncloc', branch=branch), log_error=False)
        self.assertEqual(1192, result)

    def test_ncloc_without_branch(self, url_read_mock):
        """ Check that ncloc function correctly splits an empty branch and does not add it as a parameter to the
            url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","ncloc":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"ncloc","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json,
                                     measures_json]
        sonar = Sonar(fake_url)

        result = sonar.ncloc(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='ncloc'), log_error=False)
        self.assertEqual(1192, result)

    def test_ncloc_with_branch_old(self, url_read_mock):
        """ Check that ncloc function correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"ncloc","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, components_search_json, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.ncloc(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='ncloc'), log_error=False)
        self.assertEqual(1192, result)


@patch.object(url_opener.UrlOpener, 'url_read')
class Sonar6LinesWithBranchTest(unittest.TestCase):
    """ Unit tests for branch functionality """

    # pylint: disable=no-member

    def test_lines_with_branch(self, url_read_mock):
        """ Check that lines function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","lines":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"lines","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json,
                                     measures_json]
        sonar = Sonar(fake_url)

        result = sonar.lines(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}&branch={branch}'
            .format(component=product, metric='lines', branch=branch), log_error=False)
        self.assertEqual(1192, result)

    def test_lines_without_branch(self, url_read_mock):
        """ Check that lines function correctly splits an empty branch and does not add it as a parameter to the
             url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","lines":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"lines","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json,
                                     measures_json]
        sonar = Sonar(fake_url)

        result = sonar.lines(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='lines'), log_error=False)
        self.assertEqual(1192, result)

    def test_lines_with_branch_old(self, url_read_mock):
        """ Check that lines function correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"lines","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, components_search_json, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.lines(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='lines'), log_error=False)
        self.assertEqual(1192, result)


@patch.object(url_opener.UrlOpener, 'url_read')
class Sonar6ViolationsWithBranchTest(unittest.TestCase):
    """ Unit tests for branch functionality """

    # pylint: disable=no-member

    def test_major_violations_with_branch(self, url_read_mock):
        """ Check that major_violations function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","major_violations":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"major_violations","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json,
                                     measures_json]
        sonar = Sonar(fake_url)

        result = sonar.major_violations(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}&branch={branch}'
            .format(component=product, metric='major_violations', branch=branch), log_error=False)
        self.assertEqual(1192, result)

    def test_major_violations_without_branch(self, url_read_mock):
        """ Check that major_violations function splits an empty branch and does not add it as a parameter to the
            url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","major_violations":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"major_violations","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json,
                                     measures_json]
        sonar = Sonar(fake_url)

        result = sonar.major_violations(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='major_violations'), log_error=False)
        self.assertEqual(1192, result)

    def test_major_violations_with_branch_old(self, url_read_mock):
        """ Check that major_violations correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"major_violations","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, components_search_json, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.major_violations(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='major_violations'), log_error=False)
        self.assertEqual(1192, result)

    def test_critical_violations_with_branch(self, url_read_mock):
        """ Check that critical_violations correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","critical_violations":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"critical_violations","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val,
                                     components_search_json, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.critical_violations(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}&branch={branch}'
            .format(component=product, metric='critical_violations', branch=branch), log_error=False)
        self.assertEqual(1192, result)

    def test_critical_violations_without_branch(self, url_read_mock):
        """ Check that critical_violations correctly splits an empty branch and does not add it to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","critical_violations":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"critical_violations","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val,
                                     components_search_json, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.critical_violations(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='critical_violations'), log_error=False)
        self.assertEqual(1192, result)

    def test_critical_violations_with_branch_old(self, url_read_mock):
        """ Check that critical_violations correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"critical_violations","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, components_search_json, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.critical_violations(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='critical_violations'), log_error=False)
        self.assertEqual(1192, result)

    def test_blocker_violations_with_branch(self, url_read_mock):
        """ Check that blocker_violations correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","blocker_violations":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"blocker_violations","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json,
                                     measures_json]
        sonar = Sonar(fake_url)

        result = sonar.blocker_violations(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}&branch={branch}'
            .format(component=product, metric='blocker_violations', branch=branch), log_error=False)
        self.assertEqual(1192, result)

    def test_blocker_violations_without_branch(self, url_read_mock):
        """ Check that blocker_violations correctly splits an empty branch and does not add it to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","blocker_violations":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"blocker_violations","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json,
                                     measures_json]
        sonar = Sonar(fake_url)

        result = sonar.blocker_violations(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='blocker_violations'), log_error=False)
        self.assertEqual(1192, result)

    def test_blocker_violations_with_branch_old(self, url_read_mock):
        """ Check that blocker_violations correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"blocker_violations","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, components_search_json, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.blocker_violations(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='blocker_violations'), log_error=False)
        self.assertEqual(1192, result)


@patch.object(url_opener.UrlOpener, 'url_read')
class Sonar6DuplicatedLinesWithBranchTest(unittest.TestCase):
    """ Unit tests for branch functionality """

    # pylint: disable=no-member

    def test_duplicated_lines_with_branch(self, url_read_mock):
        """ Check that duplicated_lines function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","duplicated_lines":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"duplicated_lines","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json,
                                     measures_json]
        sonar = Sonar(fake_url)

        result = sonar.duplicated_lines(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}&branch={branch}'
            .format(component=product, metric='duplicated_lines', branch=branch), log_error=False)
        self.assertEqual(1192, result)

    def test_duplicated_lines_without_branch(self, url_read_mock):
        """ Check that duplicated_lines correctly splits an empty branch and does not add it as a parameter to the
            url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","duplicated_lines":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"duplicated_lines","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json,
                                     measures_json]
        sonar = Sonar(fake_url)

        result = sonar.duplicated_lines(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='duplicated_lines'), log_error=False)
        self.assertEqual(1192, result)

    def test_duplicated_lines_with_branch_old(self, url_read_mock):
        """ Check that duplicated_lines correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"duplicated_lines","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, components_search_json, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.duplicated_lines(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='duplicated_lines'), log_error=False)
        self.assertEqual(1192, result)


@patch.object(url_opener.UrlOpener, 'url_read')
class Sonar6CoverageWithBranchTest(unittest.TestCase):
    """ Unit tests for branch functionality """

    # pylint: disable=no-member

    def test_line_coverage_with_branch(self, url_read_mock):
        """ Check that line_coverage function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","line_coverage":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"line_coverage","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json,
                                     measures_json]
        sonar = Sonar(fake_url)

        result = sonar.unittest_line_coverage(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}&branch={branch}'
            .format(component=product, metric='line_coverage', branch=branch), log_error=False)
        self.assertEqual(1192, result)

    def test_line_coverage_without_branch(self, url_read_mock):
        """ Check that line_coverage function splits an empty branch and does not add it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","line_coverage":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"line_coverage","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json,
                                     measures_json]
        sonar = Sonar(fake_url)

        result = sonar.unittest_line_coverage(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='line_coverage'), log_error=False)
        self.assertEqual(1192, result)

    def test_line_coverage_with_branch_old(self, url_read_mock):
        """ Check that line_coverage function correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"line_coverage","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, components_search_json, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.unittest_line_coverage(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='line_coverage'), log_error=False)
        self.assertEqual(1192, result)

    def test_branch_coverage_with_branch(self, url_read_mock):
        """ Check that branch_coverage function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","branch_coverage":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"branch_coverage","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json,
                                     measures_json]
        sonar = Sonar(fake_url)

        result = sonar.unittest_branch_coverage(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}&branch={branch}'
            .format(component=product, metric='branch_coverage', branch=branch), log_error=False)
        self.assertEqual(1192, result)

    def test_branch_coverage_without_branch(self, url_read_mock):
        """ Check that branch_coverage correctly splits an empty branch and does not add it as a parameter to the
            url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","branch_coverage":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"branch_coverage","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json,
                                     measures_json]
        sonar = Sonar(fake_url)

        result = sonar.unittest_branch_coverage(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='branch_coverage'), log_error=False)
        self.assertEqual(1192, result)

    def test_branch_coverage_with_branch_old(self, url_read_mock):
        """ Check that branch_coverage correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"branch_coverage","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, components_search_json, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.unittest_branch_coverage(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='branch_coverage'), log_error=False)
        self.assertEqual(1192, result)


@patch.object(url_opener.UrlOpener, 'url_read')
class Sonar6TestsWithBranchTest(unittest.TestCase):
    """ Unit tests for branch functionality """

    # pylint: disable=no-member

    def test_tests_with_branch(self, url_read_mock):
        """ Check that tests function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","tests":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"tests","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json,
                                     measures_json]
        sonar = Sonar(fake_url)

        result = sonar.unittests(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}&branch={branch}'
            .format(component=product, metric='tests', branch=branch), log_error=False)
        self.assertEqual(1192, result)

    def test_tests_without_branch(self, url_read_mock):
        """ Check that tests function orrectly splits an empty branch and does not add it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","tests":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"tests","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json,
                                     measures_json]
        sonar = Sonar(fake_url)

        result = sonar.unittests(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='tests'), log_error=False)
        self.assertEqual(1192, result)

    def test_tests_with_branch_old(self, url_read_mock):
        """ Check that tests function correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"tests","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, components_search_json, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.unittests(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='tests'), log_error=False)
        self.assertEqual(1192, result)


@patch.object(url_opener.UrlOpener, 'url_read')
class Sonar6FunctionsWithBranchTest(unittest.TestCase):
    """ Unit tests for branch functionality """

    # pylint: disable=no-member

    def test_functions_with_branch(self, url_read_mock):
        """ Check that functions function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","functions":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"functions","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json,
                                     measures_json]
        sonar = Sonar(fake_url)

        result = sonar.methods(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}&branch={branch}'
            .format(component=product, metric='functions', branch=branch), log_error=False)
        self.assertEqual(1192, result)

    def test_functions_without_branch(self, url_read_mock):
        """ Check that functions function splits an empty branch and does not add it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","functions":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"functions","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json,
                                     measures_json]
        sonar = Sonar(fake_url)

        result = sonar.methods(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='functions'), log_error=False)
        self.assertEqual(1192, result)

    def test_functions_with_branch_old(self, url_read_mock):
        """ Check that functions function correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"functions","value":"1192"}]}}'
        url_read_mock.side_effect = [server_version, components_search_json, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.methods(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
            .format(component=product, metric='functions'), log_error=False)
        self.assertEqual(1192, result)


@patch.object(url_opener.UrlOpener, 'url_read')
class Sonar6DashboardWithBranchTest(unittest.TestCase):
    """ Unit tests for branch functionality """

    # pylint: disable=no-member

    def test_dashboard_url(self, url_read_mock):
        """ Check that dashboard_url correctly splits the branch from product and completely ignores it. """
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
        """ Check that dashboard_url does not split the branch from product for sonar versions prior to 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:my-branch"
        server_version = '6.5.1234'
        plugins_json = '[{"key":"branch","name":"Branch","functions":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val]
        sonar = Sonar(fake_url)

        result = sonar.dashboard_url(product)

        self.assertEqual(fake_url + 'dashboard?id={component}'.format(component=product), result)

    def test_metric_source_urls(self, url_read_mock):
        """ Check that dashboard_url correctly splits the branch from product and completely ignores it. """
        fake_url = "http://fake.url/"
        products = "quality_report"
        server_version = '6.3'
        plugins_json = '[]'
        url_read_mock.side_effect = [server_version, plugins_json]
        sonar = Sonar(fake_url)

        result = sonar.metric_source_urls(products)

        self.assertEqual([fake_url + 'dashboard?id={component}'.format(component=products)], result)


@patch.object(url_opener.UrlOpener, 'url_read')
class Sonar6MethodsWithBranchTest(unittest.TestCase):
    """ Unit tests for branch functionality """

    # pylint: disable=no-member

    def test_complex_methods_with_branch(self, url_read_mock):
        """ Check that complex_methods function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","complex_methods":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.CyclomaticComplexityCheck'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json,
                                     measures_json]
        sonar = Sonar(fake_url)

        result = sonar.complex_methods(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}&branch={branch}'
            .format(component=product, rule=rule_name, branch=branch))
        self.assertEqual(7, result)

    def test_complex_methods_without_branch(self, url_read_mock):
        """ Check that complex_methods splits an empty branch and does not add it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","complex_methods":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.CyclomaticComplexityCheck'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json,
                                     measures_json]
        sonar = Sonar(fake_url)

        result = sonar.complex_methods(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}'
            .format(component=product, rule=rule_name))
        self.assertEqual(7, result)

    def test_complex_methods_with_branch_old(self, url_read_mock):
        """ Check that complex_methods correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.CyclomaticComplexityCheck'
        url_read_mock.side_effect = [server_version, components_search_json, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.complex_methods(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}'
            .format(component=product, rule=rule_name))
        self.assertEqual(7, result)

    def test_long_methods_with_branch(self, url_read_mock):
        """ Check that long_methods function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","long_methods":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'squid:S138'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json,
                                     measures_json]
        sonar = Sonar(fake_url)

        result = sonar.long_methods(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}&branch={branch}'
            .format(component=product, rule=rule_name, branch=branch))
        self.assertEqual(7, result)

    def test_long_methods_without_branch(self, url_read_mock):
        """ Check that long_methods function splits an empty branch and does not add it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","long_methods":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'squid:S138'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json,
                                     measures_json]
        sonar = Sonar(fake_url)

        result = sonar.long_methods(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}'
            .format(component=product, rule=rule_name))
        self.assertEqual(7, result)

    def test_long_methods_with_branch_old(self, url_read_mock):
        """ Check that long_methods function correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'squid:S138'
        url_read_mock.side_effect = [server_version, components_search_json, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.long_methods(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}'
            .format(component=product, rule=rule_name))
        self.assertEqual(7, result)

    def test_many_parameters_methods_with_branch(self, url_read_mock):
        """ Check that many_parameters_methods correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","many_parameters_methods":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.ParameterNumberCheck'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val,
                                     components_search_json, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.many_parameters_methods(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}&branch={branch}'
            .format(component=product, rule=rule_name, branch=branch))
        self.assertEqual(7, result)

    def test_many_parameters_methods_without_branch(self, url_read_mock):
        """ Check that many_parameters_methods splits an empty branch and does not add it as a parameter to the
             url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","many_parameters_methods":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.ParameterNumberCheck'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val,
                                     components_search_json, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.many_parameters_methods(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}'
            .format(component=product, rule=rule_name))
        self.assertEqual(7, result)

    def test_many_parameters_methods_with_branch_old(self, url_read_mock):
        """ Check that many_parameters_methods correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.ParameterNumberCheck'
        url_read_mock.side_effect = [server_version, components_search_json, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.many_parameters_methods(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}'
            .format(component=product, rule=rule_name))
        self.assertEqual(7, result)


@patch.object(url_opener.UrlOpener, 'url_read')
class Sonar6CommentedLocWithBranchTest(unittest.TestCase):
    """ Unit tests for branch functionality """

    # pylint: disable=no-member

    def test_commented_loc_with_branch(self, url_read_mock):
        """ Check that commented_loc function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","commented_loc":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'csharpsquid:S125'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json,
                                     measures_json]
        sonar = Sonar(fake_url)

        result = sonar.commented_loc(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}&branch={branch}'
            .format(component=product, rule=rule_name, branch=branch))
        self.assertEqual(7, result)

    def test_commented_loc_without_branch(self, url_read_mock):
        """ Check that commented_loc function splits an empty branch and does not add it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","commented_loc":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'csharpsquid:S125'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json,
                                     measures_json]
        sonar = Sonar(fake_url)

        result = sonar.commented_loc(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}'
            .format(component=product, rule=rule_name))
        self.assertEqual(7, result)

    def test_commented_loc_with_branch_old(self, url_read_mock):
        """ Check that commented_loc function correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'csharpsquid:S125'
        url_read_mock.side_effect = [server_version, components_search_json, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.commented_loc(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}'
            .format(component=product, rule=rule_name))
        self.assertEqual(7, result)


@patch.object(url_opener.UrlOpener, 'url_read')
class Sonar6NoSonarWithBranchTest(unittest.TestCase):
    """ Unit tests for branch functionality """

    # pylint: disable=no-member

    def test_no_sonar_with_branch(self, url_read_mock):
        """ Check that no_sonar function correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","no_sonar":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'squid:NoSonar'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json,
                                     measures_json]
        sonar = Sonar(fake_url)

        result = sonar.no_sonar(product + ':' + branch)

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}&branch={branch}'
            .format(component=product, rule=rule_name, branch=branch))
        self.assertEqual(7, result)

    def test_no_sonar_without_branch(self, url_read_mock):
        """ Check that no_sonar function splits an empty branch and does not add it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","no_sonar":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'squid:NoSonar'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json,
                                     measures_json]
        sonar = Sonar(fake_url)

        result = sonar.no_sonar(product + ':')

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}'
            .format(component=product, rule=rule_name))
        self.assertEqual(7, result)

    def test_no_sonar_with_branch_old(self, url_read_mock):
        """ Check that no_sonar function correctly handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"paging":{"pageIndex":1,"pageSize":100,"total":7}}'
        rule_name = 'squid:NoSonar'
        url_read_mock.side_effect = [server_version, components_search_json, measures_json]
        sonar = Sonar(fake_url)

        result = sonar.no_sonar(product)

        url_read_mock.assert_called_with(
            fake_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}'
            .format(component=product, rule=rule_name))
        self.assertEqual(7, result)


@patch.object(url_opener.UrlOpener, 'url_read')
class Sonar6FalsePositivesWithBranchTest(unittest.TestCase):
    """ Unit tests for branch functionality """

    # pylint: disable=no-member

    def test_false_positives_url(self, url_read_mock):
        """ Check that false_positives_url correctly splits the branch from product and completely ignores it. """
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
        """ Check that false_positives_url does not split the branch from product for sonar versions prior to 6.7. """
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
class Sonar6UnitTestsWithBranchTest(unittest.TestCase):
    """ Unit tests for branch functionality """

    # pylint: disable=no-member

    def test_failing_unittests_with_branch(self, url_read_mock):
        """ Check that failing_unittests correctly splits the branch and adds it as a parameter to the url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        branch = "my-branch"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","failing_unittests":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"test_failures","value":"7"}]}}'
        measures_err_json = '{"component":{"measures":[{"metric":"test_errors","value":"4"}]}}'
        url_read_mock.side_effect = \
            [server_version, plugins_json, component_ret_val, components_search_json, measures_json, measures_err_json]
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
        """ Check that failing_unittests function splits an empty branch and does not add it as a parameter to the
            url. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report"
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","failing_unittests":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"test_failures","value":"7"}]}}'
        measures_err_json = '{"component":{"measures":[{"metric":"test_errors","value":"4"}]}}'
        url_read_mock.side_effect = \
            [server_version, plugins_json, component_ret_val, components_search_json, measures_json, measures_err_json]
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
        """ Check that failing_unittests function handles product with branch, for sonar version before 6.7. """
        fake_url = "http://fake.url/"
        product = "nl.ictu:quality_report:brnch"
        server_version = '6.5.1234'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"test_failures","value":"7"}]}}'
        measures_err_json = '{"component":{"measures":[{"metric":"test_errors","value":"4"}]}}'
        url_read_mock.side_effect = [server_version, components_search_json, measures_json, measures_err_json]
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
class Sonar6DatetimeWithBranchTest(unittest.TestCase):
    """ Unit tests for branch functionality """

    # pylint: disable=no-member

    def test_datetime_with_branch(self, url_read_mock):
        """ Check that datetime function correctly splits the branch and adds it as a parameter to the url. """
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
        """ Check that datetime function splits an empty branch and does not add it as a parameter to the url. """
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
        """ Check that datetime function correctly handles product with branch, for sonar version before 6.7. """
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
        """ Check that datetime does not split the branch and calls resource url, with sonar >= 6.4 and < 6.7. """
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
        """ Check that datetime function correctly splits the branch and adds it as a parameter to the url. """
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


@patch.object(url_opener.UrlOpener, 'url_read')
class Sonar6HasProjectTest(unittest.TestCase):
    """ Unit tests for the __has_project method. """

    # pylint: disable=no-member

    def test_components_search_api(self, url_read_mock):
        """ Test that the project can be found. """
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","failing_unittests":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "1"}}'
        measures_json = '{"component":{"measures":[{"metric":"test_failures","value":"7"}]}}'
        measures_err_json = '{"component":{"measures":[{"metric":"test_errors","value":"4"}]}}'
        url_read_mock.side_effect = \
            [server_version, plugins_json, component_ret_val, components_search_json, measures_json, measures_err_json]

        self.assertEqual(11, Sonar("http://fake.url/").failing_unittests("nl.ictu:quality_report"))

    def test_no_components_found(self, url_read_mock):
        """ Test that if no components can be found, the metric is -1. """
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","failing_unittests":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {"total": "0"}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json]

        self.assertEqual(-1, Sonar("http://fake.url/").failing_unittests("nl.ictu:quality_report"))

    def test_search_components_error(self, url_read_mock):
        """ Test that if no components can be found, the metric is -1. """
        server_version = '6.8.1234'
        plugins_json = '[{"key":"branch","name":"Branch","failing_unittests":"1.0.0.507"}]'
        component_ret_val = '{"whatever": "not a component"}'
        components_search_json = '{"paging": {}}'
        url_read_mock.side_effect = [server_version, plugins_json, component_ret_val, components_search_json]

        self.assertEqual(-1, Sonar("http://fake.url/").failing_unittests("nl.ictu:quality_report"))

    def test_search_components_version_error(self, url_read_mock):
        """ Test that if the SonarQube version can't be retrieved, the metric is -1. """
        server_version = None
        url_read_mock.side_effect = [server_version]

        self.assertEqual(-1, Sonar("http://fake.url/").failing_unittests("nl.ictu:quality_report"))


class Sonar7TestCase(unittest.TestCase):
    """ Base class for Sonar unit tests. """

    # pylint: disable=no-member

    def setUp(self):
        clear_method_cache(Sonar, '_get_json')
        clear_method_cache(Sonar7, '_metric')

        with patch.object(Sonar, 'version_number') as mock_version_number:
            mock_version_number.return_value = '7.3'
            self._sonar = Sonar('http://sonar/')


@patch.object(url_opener.UrlOpener, 'url_read')
class Sonar7Test(Sonar7TestCase):
    """ Unit tests for the Sonar class. """

    # pylint: disable=no-member

    @patch.object(Sonar7, 'is_branch_plugin_installed')
    def test_version_with_branch_without_plugin(self, mock_is_branch_plugin_installed, mock_url_read):
        """ Test that the version of a product is equal to the version returned by the dashboard of that product. """
        mock_is_branch_plugin_installed.return_value = False
        mock_url_read.side_effect = ['{"analyses": [{"events": [{"name": "4.2"}]}]}']
        self.assertEqual('4.2', self._sonar.version('product:branch'))

    @patch.object(logging, 'warning')
    @patch.object(Sonar7, 'is_branch_name_included')
    def test_version_index_error(self, mock_is_branch_name_included, mock_warning, mock_url_read):
        """ Test that the version is unknown if Sonar has incomplete analyses. """
        mock_is_branch_name_included.return_value = False
        mock_url_read.return_value = '{"analyses": [{"events": []}]}'

        result = self._sonar.version('prod')

        mock_warning.assert_called_once()
        self.assertIsInstance(mock_warning.call_args[0][4], IndexError)
        self.assertEqual('?', result)

    @patch.object(logging, 'warning')
    @patch.object(Sonar7, 'is_branch_name_included')
    def test_version_key_error(self, mock_is_branch_name_included, mock_warning, mock_url_read):
        """ Test that the version is unknown if Sonar has unknown json key. """
        mock_is_branch_name_included.return_value = False
        mock_url_read.return_value = '{"analyses": [{"xvents": [{"name": "4.2"}]}]}'

        result = self._sonar.version('prod')

        mock_warning.assert_called_once()
        self.assertIsInstance(mock_warning.call_args[0][4], KeyError)
        self.assertEqual('?', result)

    @patch.object(Sonar7, 'is_branch_name_included')
    def test_version_http_error(self, mock_is_branch_name_included, mock_url_read):
        """ Test that the version is unknown if Sonar returns http error. """
        mock_is_branch_name_included.return_value = False
        mock_url_read.side_effect = [urllib.error.HTTPError(None, None, None, None, None)]

        result = self._sonar.version('prod')

        self.assertEqual('?', result)

    @patch.object(Sonar7, 'is_branch_name_included')
    def test_analysis_datetime_empty_product(self, mock_is_branch_name_included, mock_url_read):
        """ Test that the analysis date and time is min when there is no product. """
        mock_is_branch_name_included.return_value = False
        mock_url_read.side_effect = ['{"component": {"analysisDate": "2017-04-07T16:27:27+0000"}}']
        self.assertEqual(datetime.datetime.min, self._sonar.datetime(''))

    @patch.object(Sonar7, 'is_branch_name_included')
    def test_analysis_datetime_none_product(self, mock_is_branch_name_included, mock_url_read):
        """ Test that the analysis date and time is min when there is no product. """
        mock_is_branch_name_included.return_value = False
        mock_url_read.side_effect = ['{"component": {"analysisDate": "2017-04-07T16:27:27+0000"}}']
        self.assertEqual(datetime.datetime.min, self._sonar.datetime(None))

    @patch.object(Sonar7, 'is_branch_name_included')
    def test_analysis_datetime(self, mock_is_branch_name_included, mock_url_read):
        """ Test the analysis date and time are correct. """
        mock_is_branch_name_included.return_value = False
        mock_url_read.side_effect = ['{"component": {"analysisDate": "2017-04-07T16:27:27+0000"}}']
        self.assertEqual(datetime.datetime(2017, 4, 7, 16, 27, 27), self._sonar.datetime('product'))

    @patch.object(Sonar7, 'is_branch_name_included')
    def test_analysis_datetime_http_error(self, mock_is_branch_name_included, mock_url_read):
        """ Test the analysis date and time with http error. """
        mock_is_branch_name_included.return_value = False
        mock_url_read.side_effect = [urllib.error.HTTPError(None, None, None, None, None)]
        self.assertEqual(datetime.datetime.min, self._sonar.datetime('product'))

    @patch.object(Sonar7, 'is_branch_name_included')
    @patch.object(logging, 'error')
    def test_analysis_datetime_missing_key(self, mock_error, mock_is_branch_name_included, mock_url_read):
        """ Test the analysis date and time when the key is missing. """
        mock_is_branch_name_included.return_value = False
        mock_url_read.return_value = '{"component": {}}'

        result = self._sonar.datetime('product')

        mock_error.assert_called_once()
        self.assertIsInstance(mock_error.call_args[0][4], KeyError)
        self.assertEqual(datetime.datetime.min, result)

    @patch.object(Sonar7, 'is_branch_name_included')
    @patch.object(logging, 'error')
    def test_analysis_datetime_wrong(self, mock_error, mock_is_branch_name_included, mock_url_read):
        """ Test the analysis date and time when the date is invalid. """
        mock_is_branch_name_included.return_value = False
        mock_url_read.return_value = '{"component": {"analysisDate": "2017-99-07T16:27:27+0000"}}'

        result = self._sonar.datetime('product')

        mock_error.assert_called_once()
        self.assertIsInstance(mock_error.call_args[0][4], ValueError)
        self.assertEqual(datetime.datetime.min, result)


@patch.object(url_opener.UrlOpener, 'url_read')
@patch.object(Sonar7, 'is_branch_name_included')
class Sonar7Metric(Sonar7TestCase):
    """ Unit tests for unit test, integration test, and coverage metrics. """

    # pylint: disable=no-member

    def test_unittests(self, mock_is_branch_name_included, mock_url_read):
        """ Test that the number of unit tests equals the number of unit tests returned by the dashboard. """
        mock_is_branch_name_included.return_value = False
        mock_url_read.side_effect = ['[{"k": "product"}]', '{"paging": {"total": "40"}}',
                                     '{"component": {"measures": [{"metric": "tests", "value": "1111"}]}}']
        self.assertEqual(1111, self._sonar.unittests('product'))

    def test_unittests_http_error(self, mock_is_branch_name_included, mock_url_read):
        """ Test that the number of unit tests equals the number of unit tests returned by the dashboard. """
        mock_is_branch_name_included.return_value = False
        mock_url_read.side_effect = [urllib.error.HTTPError(None, None, None, None, None)]

        self.assertEqual(-1, self._sonar.unittests('product'))

    @patch.object(logging, 'warning')
    def test_unittests_no_component(self, mock_warning, mock_is_branch_name_included, mock_url_read):
        """ Test that the number of unit tests returns -1 when there is no component. """
        mock_is_branch_name_included.return_value = False
        mock_url_read.side_effect = ['[{"k": "product"}]', '{"paging": {"total": "0"}}']

        result = self._sonar.unittests('product')

        mock_warning.assert_called_once_with("Sonar has no analysis of %s", 'product')
        self.assertEqual(-1, result)

    @patch.object(logging, 'warning')
    def test_unittests_no_tests(self, mock_warning, mock_is_branch_name_included, mock_url_read):
        """ Test that the number of unit tests returns -1 when there is no required metric. """
        mock_is_branch_name_included.return_value = False
        mock_url_read.side_effect = ['[{"k": "product"}]', '{"paging": {"total": "40"}}',
                                     '{"component": {"measures": [{"metric": "somathing-else", "value": "1111"}]}}']

        result = self._sonar.unittests('product')

        mock_warning.assert_called_once()
        self.assertEqual(mock_warning.call_args[0][0], "Can't get %s value for %s from %s (retrieved from %s): %s")
        self.assertEqual(mock_warning.call_args[0][1], 'tests')
        self.assertEqual(mock_warning.call_args[0][2], 'product')
        self.assertIsInstance(mock_warning.call_args[0][3], dict)
        self.assertEqual(mock_warning.call_args[0][4],
                         'http://sonar/api/measures/component?component=product&metricKeys=tests')
        self.assertEqual(mock_warning.call_args[0][5], 'metric not found in component measures')
        self.assertEqual(-1, result)

    @patch.object(logging, 'warning')
    def test_unittests_key_error(self, mock_warning, mock_is_branch_name_included, mock_url_read):
        """ Test that the number of unit tests returns -1 when measures key is not found. """
        mock_is_branch_name_included.return_value = False
        mock_url_read.side_effect = ['[{"k": "product"}]', '{"paging": {"total": "40"}}', '{"component": {}}']

        result = self._sonar.unittests('product')

        mock_warning.assert_called_once()
        self.assertEqual(mock_warning.call_args[0][0], "Can't get %s value for %s from %s (retrieved from %s): %s")
        self.assertEqual(mock_warning.call_args[0][1], 'tests')
        self.assertEqual(mock_warning.call_args[0][2], 'product')
        self.assertIsInstance(mock_warning.call_args[0][3], dict)
        self.assertEqual(mock_warning.call_args[0][4],
                         'http://sonar/api/measures/component?component=product&metricKeys=tests')
        self.assertIsInstance(mock_warning.call_args[0][5], KeyError)
        self.assertEqual(-1, result)

    @patch.object(logging, 'warning')
    def test_unittests_type_error(self, mock_warning, mock_is_branch_name_included, mock_url_read):
        """ Test that the number of unit tests returns -1 when type is not correct. """
        mock_is_branch_name_included.return_value = False
        mock_url_read.side_effect = ['[{"k": "product"}]', '{"paging": {"total": "40"}}',
                                     '{"component": {"measures": 99}}']

        result = self._sonar.unittests('product')

        mock_warning.assert_called_once()
        self.assertEqual(mock_warning.call_args[0][0], "Can't get %s value for %s from %s (retrieved from %s): %s")
        self.assertEqual(mock_warning.call_args[0][1], 'tests')
        self.assertEqual(mock_warning.call_args[0][2], 'product')
        self.assertIsInstance(mock_warning.call_args[0][3], dict)
        self.assertEqual(mock_warning.call_args[0][4],
                         'http://sonar/api/measures/component?component=product&metricKeys=tests')
        self.assertIsInstance(mock_warning.call_args[0][5], TypeError)
        self.assertEqual(-1, result)


@patch.object(url_opener.UrlOpener, 'url_read')
class Sonar7PluginTest(Sonar7TestCase):
    """ Unit tests for Sonar meta data. """

    # pylint: disable=no-member

    def test_is_branch_plugin_installed(self, mock_url_read):
        """" Test that the branch plugin is installed. """
        mock_url_read.return_value = '{"plugins":[{"key":"branch","name":"Branch"}]}'
        self.assertTrue(self._sonar.is_branch_plugin_installed())

    @patch.object(logging, 'info')
    def test_is_branch_plugin_not_installed(self, mock_info, mock_url_read):
        """" Test that the branch plugin is not installed. """
        mock_url_read.return_value = '{"plugins":[{"key":"x","name":"X"}]}'

        result = self._sonar.is_branch_plugin_installed()

        mock_info.assert_called_once_with("Branch plugin not installed.")
        self.assertFalse(result)


@patch.object(url_opener.UrlOpener, 'url_read')
@patch.object(Sonar7, 'is_branch_name_included')
class Sonar7VersionsTest(Sonar7TestCase):
    """ Unit tests for Sonar meta data. """

    # pylint: disable=no-member

    def test_default_quality_profile(self, mock_is_branch_name_included, mock_url_read):
        """ Test that the name of the default quality profile is returned. """
        mock_is_branch_name_included.return_value = False
        mock_url_read.return_value = """{"profiles":
        [{
            "key": "java-java-profile-v1-8-20151111-91699",
            "name": "Java profile v1.8-20151111",
            "language": "java",
            "isDefault": true
        }]}"""
        self.assertEqual("Java profile v1.8-20151111", self._sonar.default_quality_profile('java'))

    @patch.object(logging, 'warning')
    def test_default_quality_profile_http_errors(self, mock_warning, mock_is_branch_name_included, mock_url_read):
        """ Test that the name of the quality profile is empty if http errors happen. """
        mock_is_branch_name_included.return_value = False
        mock_url_read.side_effect = [urllib.error.HTTPError(None, None, None, None, None)]

        self.assertEqual("", self._sonar.default_quality_profile('some-strange-language'))
        mock_warning.assert_not_called()

    def test_default_quality_profile_key_error(self, mock_is_branch_name_included, mock_url_read):
        """ Test that the empty string is returned when key not found. """
        mock_is_branch_name_included.return_value = False
        mock_url_read.return_value = """{"xprofiles": [{}]}"""
        self.assertEqual("", self._sonar.default_quality_profile('java'))

    @patch.object(logging, 'warning')
    def test_default_quality_profile_no_language(self, mock_warning, mock_is_branch_name_included, mock_url_read):
        """ Test that the name of the quality profile is empty if there is no profile for the given language. """
        mock_is_branch_name_included.return_value = False
        mock_url_read.return_value = """{"profiles":
                [{
                    "key": "java-java-profile-v1-8-20151111-91699",
                    "name": "Java profile v1.8-20151111",
                    "language": "java",
                    "isDefault": true
                }]}"""
        result = self._sonar.default_quality_profile('some-strange-language')
        mock_warning.assert_called_once()
        self.assertEqual(mock_warning.call_args[0][0],
                         "Couldn't find a default quality profile for %s in %s, retrieved from %s")
        self.assertEqual(mock_warning.call_args[0][1], 'some-strange-language')
        self.assertEqual("", result)

    @patch.object(logging, 'warning')
    def test_default_quality_profile_no_default(self, mock_warning, mock_is_branch_name_included, mock_url_read):
        """ Test that the name of the quality profile is empty if there is no default profile for the language. """
        mock_is_branch_name_included.return_value = False
        mock_url_read.return_value = """{"profiles":
                    [{
                        "key": "java-findbugs-94130",
                        "name": "FindBugs",
                        "language": "java",
                        "isDefault": false
                    }]}"""
        result = self._sonar.default_quality_profile('java')
        mock_warning.assert_called_once()
        self.assertEqual(mock_warning.call_args[0][0],
                         "Couldn't find a default quality profile for %s in %s, retrieved from %s")
        self.assertEqual(mock_warning.call_args[0][1], 'java')
        self.assertEqual("", result)

    @patch.object(logging, 'warning')
    def test_default_quality_profile_no_profiles(self, mock_warning, mock_is_branch_name_included, mock_url_read):
        """ Test that the name of the quality profile is empty if there are no profiles at all. """
        mock_is_branch_name_included.return_value = False
        mock_url_read.return_value = """{"profiles": []}"""
        result = self._sonar.default_quality_profile('java')
        mock_warning.assert_called_once()
        self.assertEqual(mock_warning.call_args[0][0],
                         "Couldn't find a default quality profile for %s in %s, retrieved from %s")
        self.assertEqual(mock_warning.call_args[0][1], 'java')
        self.assertEqual("", result)
