"""
Copyright 2012-2019 Ministerie van Sociale Zaken en Werkgelegenheid

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
import functools
import logging
import json
import re
from typing import List, Tuple, Dict, Optional, Union, Sequence
from distutils.version import LooseVersion

from . import url_opener
from .. import utils, metric_source
from ..typing import DateTime, Number


def extract_branch_decorator(func):
    """ Checks if product name has to be splitted into product and branch and performs the splitting."""
    def _branch_param(self, product: str, *args, **kwargs) -> (str, str):
        """ Return the branch url parameter. """
        if self.is_branch_name_included(product):
            prod = product.rsplit(":", 1)
            if len(prod) == 2:
                return func(self, prod[0], None if prod[1] == '' else prod[1], *args, **kwargs)
            logging.warning(
                "A branch name is not defined in '%s' and no component with corresponding name is found.", product)
        return func(self, product, None, *args, **kwargs)
    return _branch_param


class Sonar(metric_source.TestReport):
    """ Class representing the Sonar facade. """

    metric_source_name = 'SonarQube'
    suppression_rules = ("squid:NoSonar", "csharpsquid:S1309", "squid:S1309", "squid:S1310", "squid:S1315",
                         "Pylint:I0011", "Pylint:I0020")

    def __init__(self, sonar_url: str, *args, **kwargs) -> None:
        self._url_opener = \
            url_opener.UrlOpener(username=kwargs.get("username", ""), password=kwargs.get("password", ""))
        super().__init__(url=sonar_url, *args, **kwargs)

        self._version_number_url = sonar_url + 'api/server/version'

        version_number = LooseVersion(self.version_number()) if self.version_number() else None
        self.__stuff_right_sonar_version_class(version_number, sonar_url)

    def __stuff_right_sonar_version_class(self, version_number: LooseVersion, sonar_url: str):

        if version_number is not None and version_number >= LooseVersion('7.0'):
            self.__class__ = Sonar7
        else:
            self.__class__ = Sonar6

        self._init_from_facade(sonar_url=sonar_url)  # pylint: disable=no-member
        self.__log_version_messages(version_number)

    @classmethod
    def __log_version_messages(cls, version_number: LooseVersion):
        if version_number is not None:
            if version_number < LooseVersion('5.4'):
                logging.warning(
                    "SonarQube version lower than 5.4 is not supported. Version %s detected.", version_number)
            elif version_number >= LooseVersion('9.0'):
                logging.warning(
                    "SonarQube version %s is not supported. Supported versions are from 6.0 to 9.0(excluding).",
                    version_number)

    @functools.lru_cache(maxsize=4096)
    def _get_json(self, url: str, *args, **kwargs) -> \
            Union[Dict[str, Dict], List[Dict[str, Union[str, List[Dict[str, str]]]]]]:
        """ Get and evaluate the json from the url. """
        json_string = self._url_opener.url_read(url, *args, **kwargs)
        return utils.eval_json(json_string)

    @classmethod
    def _add_branch_param_to_url(cls, url: str, branch: str) -> str:
        """ Adds branch url query param to the url, if defined. """
        return url + "&branch=" + branch if branch else url

    @functools.lru_cache(maxsize=1024)
    def version_number(self) -> Optional[str]:
        """ Return the version number of Sonar. """
        try:
            version_number = self._url_opener.url_read(self._version_number_url)
            logging.info("Sonar Qube server version retrieved: %s", version_number)
            return version_number
        except self._url_opener.url_open_exceptions:
            logging.warning("Error retrieving Sonar Qube server version!")
            return None

    @functools.lru_cache(maxsize=1024)
    def violation_sorts(self) -> List[Tuple]:
        """ Returns violation sorts, depending on sonar version """
        sorts = [('BUG', 'Bugs'), ('VULNERABILITY', 'Vulnerabilities'), ('CODE_SMELL', 'Code Smell')]
        if self.is_security_hotspots_available():
            sorts.append(('SECURITY_HOTSPOT', 'Security Hotspot'))
        return sorts

    @functools.lru_cache(maxsize=1024)
    def is_security_hotspots_available(self):
        """ Returns if the security hotspot violations are available, based on sonar version """
        return self.version_number() >= LooseVersion('7.3')

    def _report_datetime(self, metric_source_id: str) -> DateTime:  # pragma: no cover
        """ Formal overriding of an abstract method. It is never used."""
        pass


class Sonar6(Sonar):
    """ Class representing the Sonar instance, for apis supported in versions 5.x and 6.x. """
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-public-methods

    metric_source_name = 'SonarQube'

    def is_branch_name_included(self, product: str) -> bool:
        """ Checks if the component name includes the branch name. """
        return self.version_number() \
            and LooseVersion(self.version_number()) >= LooseVersion('6.7') \
            and self.is_branch_plugin_installed() \
            and self.is_component_absent(product)

    def _init_from_facade(self, sonar_url: str):

        # pylint: disable=attribute-defined-outside-init
        # pylint: disable=invalid-name

        self._base_dashboard_url = sonar_url + 'dashboard?id={project}'
        self._base_violations_url = sonar_url + 'issues/search#resolved=false|componentRoots={component}'
        self._suppressions_url = sonar_url + f"issues/search#rules={','.join(self.suppression_rules)}" + \
            "|componentRoots={component}"
        self._violations_type_severity_url = sonar_url + \
            'project/issues?id={component}&resolved=false&types={type}&severities={severities}'
        self._issues_api_url = sonar_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}'
        self._issues_by_type_api_url = sonar_url + \
            'api/issues/search?componentRoots={component}&resolved=false&types={type}'
        self._issues_by_type_and_severity_api_url = sonar_url + \
            'api/issues/search?componentRoots={component}&resolved=false&types={type}&severities={severities}'
        self._analyses_api_url = sonar_url + 'api/project_analyses/search?project={project}&format=json&ps=1'
        self._components_show_api_url = sonar_url + 'api/components/show?component={component}'
        self._components_search_api_url = sonar_url + 'api/components/search?qualifiers=BRC,TRK&q={component}'
        self._resource_api_url = sonar_url + 'api/resources?resource={resource}&format=json'
        self._projects_api_url = sonar_url + 'api/projects/index?subprojects=true'
        self._measures_api_url = sonar_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
        self._false_positives_api_url = sonar_url + \
            'api/issues/search?resolutions=FALSE-POSITIVE&componentRoots={resource}'
        self._false_positives_url = sonar_url + 'issues/search#resolutions=FALSE-POSITIVE|componentRoots={resource}'
        self._wont_fix_api_url = sonar_url + 'api/issues/search?resolutions=WONTFIX&componentRoots={resource}'
        self._wont_fix_url = sonar_url + 'issues/search#resolutions=WONTFIX|componentRoots={resource}'
        self._plugin_api_url = sonar_url + 'api/updatecenter/installed_plugins?format=json'
        self._quality_profiles_api_url = sonar_url + 'api/qualityprofiles/search?format=json'
        self._old_quality_profiles_api_url = sonar_url + 'api/profiles/list?format=json'
        logging.info("Sonar class instantiated as Sonar6.")

    # Coverage report API

    @extract_branch_decorator
    def maintainability_bugs(self, product: str, branch: str) -> int:
        """ Return the number of maintainability bugs detected by sonar, for the product. """
        return self.__number_of_issues(product, branch,
                                       self._issues_by_type_api_url.format(component=product, type='BUG'), 0)

    @extract_branch_decorator
    def violations_type_severity(self, product: str, branch: str, violation_type: str, severity: str)\
            -> (str, int, str):
        """ Return the number of violations of a given type and severity, detected by sonar, for the product. """
        return (
            self._violations_type_severity_url.format(
                component=product, type=violation_type.upper(), severities=severity.upper()),
            self.__number_of_issues(
                product, branch,
                self._issues_by_type_and_severity_api_url.format(
                    component=product, type=violation_type.upper(), severities=severity.upper()), 0),
            self.__time_to_fix(
                branch,
                self._issues_by_type_and_severity_api_url.format(
                    component=product, type=violation_type.upper(), severities=severity.upper()), '-')
        )

    @extract_branch_decorator
    def vulnerabilities(self, product: str, branch: str) -> int:
        """ Return the number of vulnerabilities detected by sonar, for the product. """
        return self.__number_of_issues(product, branch,
                                       self._issues_by_type_api_url.format(component=product, type='VULNERABILITY'), 0)

    @extract_branch_decorator
    def code_smells(self, product: str, branch: str) -> int:
        """ Return the number of code smells detected by sonar, for the product. """
        return self.__number_of_issues(product, branch,
                                       self._issues_by_type_api_url.format(component=product, type='CODE_SMELL'), 0)

    @extract_branch_decorator
    def security_hotspots(self, product: str, branch: str) -> int:
        """ Return the number of code smells detected by sonar, for the product. """
        return self.__number_of_issues(
            product, branch, self._issues_by_type_api_url.format(component=product, type='SECURITY_HOTSPOT'), 0)

    def has_branch_coverage(self, metric_source_id: str) -> bool:
        """ Determines if the branch coverage is defined on Sonar. """
        # pylint: disable=no-value-for-parameter
        return self.version_number() is None or self.unittest_branch_coverage(metric_source_id) != -1

    def statement_coverage(self, metric_source_id: str) -> float:
        """ Return the statement coverage for a specific product. """
        return self.unittest_line_coverage(metric_source_id)

    def branch_coverage(self, metric_source_id: str) -> float:
        """ Return the branch coverage for a specific product. """
        return self.unittest_branch_coverage(metric_source_id)

    # Test report API

    def _passed_tests(self, metric_source_id: str) -> int:
        """ Return the number of passed tests as reported by the test report. """
        return self.unittests(metric_source_id) - self.failing_unittests(metric_source_id)

    def _failed_tests(self, metric_source_id: str) -> int:
        """ Return the number of failed tests as reported by the test report. """
        return self.failing_unittests(metric_source_id)

    # Coverage report and test report API

    def metric_source_urls(self, *metric_source_ids: str) -> Sequence[str]:
        """ Return the metric source urls for human users. """
        return [self.dashboard_url(metric_source_id) for metric_source_id in metric_source_ids]

    # Sonar

    @extract_branch_decorator
    def version(self, product: str, branch: str) -> str:
        """ Return the version of the product. """

        url = self._add_branch_param_to_url(
            self._analyses_api_url.format(project=product) + '&category=VERSION', branch)

        try:
            analyses_json = self._get_json(url, log_error=False)
            try:
                return analyses_json['analyses'][0]['events'][0]['name']
            except (KeyError, IndexError) as reason:
                logging.warning("Couldn't get version number of %s from JSON %s (retrieved from %s): %s",
                                product, analyses_json, url, reason)
                return '?'
        except self._url_opener.url_open_exceptions:
            # Try older API:
            url = self._add_branch_param_to_url(self._resource_api_url.format(resource=product), branch)
            try:
                analyses_json = self._get_json(url)
            except self._url_opener.url_open_exceptions:
                return '?'
            try:
                return analyses_json[0]['version']
            except (KeyError, IndexError) as reason:
                logging.warning("Couldn't get version number of %s from JSON %s (retrieved from %s): %s",
                                product, analyses_json, url, reason)
                return '?'

    @classmethod
    def __normalize_version_build(cls, version: str) -> str:
        if '(build' in version:
            version_parts = version.split("(build")
            return version_parts[0].strip() + '.' + version_parts[1].split(")")[0].strip()
        return version

    def plugin_version(self, plugin: str) -> str:
        """ Return the version of the SonarQube plugin. """
        try:
            plugins = self._get_plugins_json()
        except self._url_opener.url_open_exceptions:
            return '0.0'
        mapping = dict((plugin['key'], self.__normalize_version_build(plugin['version'])) for plugin in plugins)
        return mapping.get(plugin, '0.0')

    def plugins_url(self) -> str:
        """ Return the url to the plugin update center. """
        return self.url() + 'updatecenter/'

    def default_quality_profile(self, language: str) -> str:
        """ Return the default quality profile for the language. """
        url = self._quality_profiles_api_url
        try:
            profiles = self._get_json(url)['profiles']
        except self._url_opener.url_open_exceptions + (KeyError, TypeError):  # pylint: wrong-exception-operation
            # Try old API
            url = self._old_quality_profiles_api_url
            try:
                profiles = self._get_json(url)
            except self._url_opener.url_open_exceptions:
                return ''  # Give up
        for profile in profiles:
            if profile.get("language") == language:
                for keyword in ('isDefault', 'default'):
                    if profile.get(keyword):
                        return profile['name']
        logging.warning("Couldn't find a default quality profile for %s in %s, retrieved from %s", language, profiles,
                        url)
        return ''

    def quality_profiles_url(self) -> str:
        """ Return the quality profiles url. """
        return self.url() + 'profiles/'

    @functools.lru_cache(maxsize=4096)
    def is_branch_plugin_installed(self) -> bool:
        """ Return whether SonarQube has the branch plugin installed, which is needed for interpreting Sonar keys. """
        try:
            plugins = self._get_plugins_json()
            if "branch" in [item["key"] for item in plugins]:
                return True
            logging.info("Branch plugin not installed.")
        except self._url_opener.url_open_exceptions as reason:
            logging.warning("Couldn't open %s: %s", self._plugin_api_url, reason)
        except (TypeError, ValueError) as reason:
            logging.error("Error parsing response from %s: '%s'. "
                          "Assume the branch plugin is not installed.", self._plugin_api_url, reason)
        return False

    def _get_plugins_json(self):
        return self._get_json(self._plugin_api_url)

    @functools.lru_cache(maxsize=4096)
    def is_component_absent(self, product: str) -> bool:
        """ Checks if the component with complete name, including branch, is defined """
        url = self._components_show_api_url.format(component=product)
        try:
            if json.loads(self._url_opener.url_read(url, log_error=False))["component"]:
                logging.info("Component '%s' found. No branch is defined.", product)
                return False
        except (ValueError, KeyError):
            pass
        except self._url_opener.url_open_exceptions:
            pass
        return True

    # Sonar projects

    def _has_project(self, project: str, branch) -> bool:
        """ Return whether Sonar has the project (analysis). """
        version = self.version_number()
        if not version:
            return False
        if version >= "6.3":
            # We use the components/search API and not the project_analyses/search API because the former supports
            # searching for subprojects and the latter does not.
            url = self._add_branch_param_to_url(self._components_search_api_url.format(component=project), branch)
            try:
                return self._has_paging_total(project, url)
            # pylint: wrong-exception-operation
            except self._url_opener.url_open_exceptions + (KeyError, IndexError, TypeError, ValueError) as reason:
                logging.warning("Sonar has no analysis of %s: %s", project, reason)
                return False
        else:
            found = project in self.__projects(branch)
            if not found:
                logging.warning("Sonar has no analysis of %s", project)
            return found

    def _has_paging_total(self, project, url) -> bool:
        count = int(self._get_json(url)["paging"]["total"])
        if count == 0:
            logging.warning("Sonar has no analysis of %s", project)
        return count > 0

    def __projects(self, branch) -> List[str]:
        """ Return all projects in Sonar. """
        try:
            projects_json = self._get_json(self._add_branch_param_to_url(self._projects_api_url, branch))
            return [project['k'] for project in projects_json]
        except self._url_opener.url_open_exceptions:
            return []

    # Metrics

    @extract_branch_decorator
    def ncloc(self, product: str, branch: str) -> int:
        """ Non-comment lines of code. """
        return int(self._metric(product, 'ncloc', branch))

    @extract_branch_decorator
    def lines(self, product: str, branch: str) -> int:
        """ Bruto lines of code, including comments, whitespace, javadoc. """
        return int(self._metric(product, 'lines', branch))

    @extract_branch_decorator
    def major_violations(self, product: str, branch: str) -> int:
        """ Return the number of major violations for the product. """
        return int(self._metric(product, 'major_violations', branch))

    @extract_branch_decorator
    def critical_violations(self, product: str, branch: str) -> int:
        """ Return the number of critical violations for the product. """
        return int(self._metric(product, 'critical_violations', branch))

    @extract_branch_decorator
    def blocker_violations(self, product: str, branch: str) -> int:
        """ Return the number of blocker violations for the product. """
        return int(self._metric(product, 'blocker_violations', branch))

    @extract_branch_decorator
    def duplicated_lines(self, product: str, branch: str) -> int:
        """ Return the number of duplicated lines for the product. """
        return int(self._metric(product, 'duplicated_lines', branch))

    @extract_branch_decorator
    def unittest_line_coverage(self, product: str, branch: str) -> float:
        """ Return the line coverage of the unit tests for the product. """
        return float(self._metric(product, 'line_coverage', branch))

    @extract_branch_decorator
    def unittest_branch_coverage(self, product: str, branch: str) -> float:
        """ Return the branch coverage of the unit tests for the product. """
        return float(self._metric(product, 'branch_coverage', branch))

    @extract_branch_decorator
    def unittests(self, product: str, branch: str) -> int:
        """ Return the number of unit tests for the product. """
        return int(self._metric(product, 'tests', branch))

    @extract_branch_decorator
    def failing_unittests(self, product: str, branch: str) -> int:
        """ Return the number of failing unit tests for the product. """
        failures = int(self._metric(product, 'test_failures', branch))
        errors = int(self._metric(product, 'test_errors', branch))
        return failures + errors if failures >= 0 and errors >= 0 else -1

    @extract_branch_decorator
    def methods(self, product: str, branch: str) -> int:
        """ Return the number of methods/functions in the product. """
        return int(self._metric(product, 'functions', branch))

    @extract_branch_decorator
    def dashboard_url(self, product: str, branch: str) -> str:
        """ Return the url for the Sonar dashboard for the product. """
        return self._add_branch_param_to_url(self._base_dashboard_url.format(project=product), branch)

    # Violations

    @extract_branch_decorator
    def complex_methods(self, product: str, branch: str) -> int:
        """ Return the number of methods that violate the Cyclomatic complexity threshold. """
        rule_names = ('checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.CyclomaticComplexityCheck',
                      'pmd:CyclomaticComplexity',
                      'squid:MethodCyclomaticComplexity',
                      'csharpsquid:S1541',
                      'csharpsquid:FunctionComplexity',
                      'javascript:FunctionComplexity',
                      'Web:ComplexityCheck',
                      'python:FunctionComplexity',
                      'vbnet:S1541',
                      'tslint:cyclomatic-complexity')
        for rule_name in rule_names:
            nr_complex_methods = self._rule_violation(product, rule_name, 0, branch)
            if nr_complex_methods:
                return nr_complex_methods
        return 0

    @extract_branch_decorator
    def long_methods(self, product: str, branch: str) -> int:
        """ Return the number of methods in the product that have to many non-comment statements. """
        # NB: There is no long methods rule for C# and VB.NET. How to deal with this? FIXME
        rule_names = ('squid:S138',
                      'checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.JavaNCSSCheck',
                      'Pylint:R0915',
                      'Web:LongJavaScriptCheck')
        for rule_name in rule_names:
            nr_long_methods = self._rule_violation(product, rule_name, 0, branch)
            if nr_long_methods:
                return nr_long_methods
        return 0

    @extract_branch_decorator
    def many_parameters_methods(self, product: str, branch: str) -> int:
        """ Return the number of methods in the product that have too many parameters. """
        rule_names = ('checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.ParameterNumberCheck',
                      'pmd:ExcessiveParameterList',
                      'csharpsquid:S107',
                      'squid:S00107',
                      'javascript:ExcessiveParameterList',
                      'python:S107')
        for rule_name in rule_names:
            nr_many_parameters = self._rule_violation(product, rule_name, 0, branch)
            if nr_many_parameters:
                return nr_many_parameters
        return 0

    @extract_branch_decorator
    def commented_loc(self, product: str, branch: str) -> int:
        """ Return the number of commented out lines in the source code of the product. """
        rule_names = ('csharpsquid:S125', 'csharpsquid:CommentedCode', 'squid:CommentedOutCodeLine',
                      'javascript:CommentedCode', 'python:S125', 'Web:AvoidCommentedOutCodeCheck')
        for rule_name in rule_names:
            nr_commented_loc = self._rule_violation(product, rule_name, 0, branch)
            if nr_commented_loc:
                return nr_commented_loc
        return 0

    @extract_branch_decorator
    def suppressions(self, product: str, branch: str) -> int:
        """ Return the number of violation suppressions in the source code of the product. """
        total = 0
        for rule_name in self.suppression_rules:
            suppressions = self._rule_violation(product, rule_name, -1, branch)
            if suppressions == -1:
                return -1
            total += suppressions
        return total

    @extract_branch_decorator
    def suppressions_url(self, product: str, branch: str) -> str:
        """ Return the url for the suppression of rules in the source code. """
        return self._add_branch_param_to_url(self._suppressions_url.format(component=product), branch)

    @extract_branch_decorator
    def violations_url(self, product: str, branch: str) -> str:
        """ Return the url for the violations of the product. """
        return self._add_branch_param_to_url(self._base_violations_url.format(component=product), branch)

    # Issues

    @extract_branch_decorator
    def false_positives(self, product: str, branch: str) -> int:
        """ Return the number of false positives listed for the product. """
        return self.__number_of_issues(product, branch, self._false_positives_api_url.format(resource=product), 0)

    @extract_branch_decorator
    def false_positives_url(self, product: str, branch: str) -> str:
        """ Return the url to the list of false positives. """
        return self._add_branch_param_to_url(self._false_positives_url.format(resource=product), branch)

    @extract_branch_decorator
    def wont_fix(self, product: str, branch: str) -> int:
        """ Return the number of won't fix issues listed for the product. """
        return self.__number_of_issues(product, branch, self._wont_fix_api_url.format(resource=product), 0)

    @extract_branch_decorator
    def wont_fix_url(self, product: str, branch: str) -> str:
        """ Return the url to the list of won't fix issues. """
        return self._add_branch_param_to_url(self._wont_fix_url.format(resource=product), branch)

    # Meta data

    def datetime(self, *products: str) -> DateTime:
        """ Return the date and time of the last analysis of the product. """
        if not products:
            return datetime.datetime.min

        split_branch = extract_branch_decorator(lambda this, x, a: (x, a))
        product, branch = split_branch(self, products[0])

        server_version = self.version_number()
        if server_version and LooseVersion(server_version) >= LooseVersion('6.4'):
            # Use the components API, it should contain the analysis date both for projects and components
            url = self._add_branch_param_to_url(self._components_show_api_url.format(component=product), branch)
            try:
                components_json = self._get_json(url)
                try:
                    datetime_string = components_json['component']['analysisDate']
                    datetime_string = datetime_string.split('+')[0]  # Ignore timezone
                    return datetime.datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%S')
                except (TypeError, KeyError, IndexError) as reason:
                    logging.error("Couldn't get date of last analysis of %s from JSON %s (retrieved from %s): %s",
                                  product, components_json, url, reason)
            except self._url_opener.url_open_exceptions:
                pass
            return datetime.datetime.min
        # Use analyses API:
        url = self._add_branch_param_to_url(self._analyses_api_url.format(project=product), branch)
        try:
            components_json = self._get_json(url, log_error=False)['analyses']
        except self._url_opener.url_open_exceptions:
            # Try older API:
            url = self._add_branch_param_to_url(self._resource_api_url.format(resource=product), branch)
            try:
                components_json = self._get_json(url)
            except self._url_opener.url_open_exceptions:
                return datetime.datetime.min
        try:
            datetime_string = components_json[0]['date']
        except (TypeError, KeyError, IndexError) as reason:
            logging.error("Couldn't get date of last analysis of %s from JSON %s (retrieved from %s): %s",
                          product, components_json, url, reason)
            return datetime.datetime.min
        datetime_string = datetime_string.split('+')[0]  # Ignore timezone
        return datetime.datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%S')

    # Helper methods

    def _get_measure_value(self, url: str, metric_name: str, product: str):
        """ Gets measures. """
        measures_json = self._get_json(url, log_error=False)
        try:
            for measure in measures_json['component']['measures']:
                if measure['metric'] == metric_name:
                    return float(measure['value'])
            failure_reason = 'metric not found in component measures'
        except (TypeError, KeyError, IndexError, ValueError) as reason:
            failure_reason = reason
        logging.warning("Can't get %s value for %s from %s (retrieved from %s): %s", metric_name, product,
                        measures_json, url, failure_reason)
        return -1

    @functools.lru_cache(maxsize=4096)
    def _metric(self, product: str, metric_name: str, branch: str) -> Number:
        """ Return a specific metric value for the product. """
        try:
            return self._get_measure_of_product(branch, metric_name, product)
        except self._url_opener.url_open_exceptions:
            pass  # Keep going, and try the old API
        url = self._add_branch_param_to_url(
            self._resource_api_url.format(resource=product) + '&metrics=' + metric_name, branch)
        try:
            measures_json = self._get_json(url)
            try:
                return float(measures_json[0]["msr"][0]["val"])
            except (TypeError, KeyError, IndexError, ValueError) as reason:
                logging.warning("Can't get %s value for %s from %s (retrieved from %s): %s", metric_name, product,
                                measures_json, url, reason)
                return -1
        except self._url_opener.url_open_exceptions:
            return -1

    def _get_measure_of_product(self, branch, metric_name, product):
        if not self._has_project(product, branch):
            return -1
        url = self._add_branch_param_to_url(
            self._measures_api_url.format(component=product, metric=metric_name), branch)
        return self._get_measure_value(url, metric_name, product)

    def _rule_violation(self, product: str, rule_name: str, default: int = 0, branch: str = None) -> int:
        """ Return a specific violation value for the product. """
        if not self._has_project(product, branch):
            return -1
        try:
            issues_json = self._get_json(
                self._add_branch_param_to_url(self._issues_api_url.format(component=product, rule=rule_name), branch))
        except self._url_opener.url_open_exceptions:
            return default
        return int(issues_json['paging']['total'])

    def __number_of_issues(self, product: str, branch: str, url: str, default: int = 0) -> int:
        """ Return the number of issues retrieved by given url. """
        if not self._has_project(product, branch):
            return -1
        try:
            issues_json = self._get_json(self._add_branch_param_to_url(url, branch))
        except self._url_opener.url_open_exceptions:
            return default
        return int(issues_json['total'])

    def __time_to_fix(self, branch: str, url: str, default: str = '-') -> str:
        """ Return the number of issues retrieved by given url. """
        try:
            total_minutes = 0
            issues = self.__get_all_issues(url, branch)
            for issue in issues:
                total_minutes += self.__add_effort(issue['effort']) if 'effort' in issue else 0
            return self.__format_time_to_fix(total_minutes)
        except self._url_opener.url_open_exceptions:
            pass
        return default

    def __get_all_issues(self, url: str, branch: str) -> List:
        url += '&pageSize=-1&pageIndex={page_index}'
        page_index = 1
        result_list = []
        while True:
            current_json = self._get_json(self._add_branch_param_to_url(url.format(page_index=page_index), branch))
            result_list.extend(current_json['issues'])
            if page_index * current_json['paging']['pageSize'] >= current_json['paging']['total']:
                break
            page_index += 1
        return result_list

    @staticmethod
    def __format_time_to_fix(total_minutes: int) -> str:
        hours, minutes = divmod(total_minutes, 60)
        return '{0}h {1:02}min'.format(hours, minutes) if hours > 0 else '{0:2}min'.format(minutes)

    @staticmethod
    def __add_effort(effort: str) -> int:
        # Use a regex pattern to capture days, hours and minutes
        pattern = r'^((?P<days>\d+)d)? *((?P<hours>\d+)h)? *((?P<minutes>\d+)min)?$'
        match = re.match(pattern, effort)
        if not match:
            logging.warning('Invalid format of field effort: %s', effort)
            return 0

        multipliers = {'days': 24 * 60, 'hours': 60, 'minutes': 1}
        match_dict = match.groupdict()
        return sum([multipliers[key] * int(match_dict[key])
                    for key in match_dict if match_dict[key]])


class Sonar7(Sonar6):
    """ Class representing the Sonar instance, for apis supported in versions 5.x and 6.x. """

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-public-methods

    metric_source_name = 'SonarQube'

    def _init_from_facade(self, sonar_url: str):

        # pylint: disable=attribute-defined-outside-init
        # pylint: disable=invalid-name

        self._base_dashboard_url = sonar_url + 'dashboard?id={project}'
        self._base_violations_url = sonar_url + 'project/issues?id={component}&resolved=false'
        self._suppressions_url = sonar_url + "project/issues?id={component}&" + \
            f"rules={','.join(self.suppression_rules)}"
        self._violations_type_severity_url = sonar_url + \
            'project/issues?id={component}&resolved=false&types={type}&severities={severities}'
        self._issues_api_url = sonar_url + 'api/issues/search?componentKeys={component}&resolved=false&rules={rule}'
        self._issues_by_type_api_url = sonar_url + \
            'api/issues/search?componentKeys={component}&resolved=false&types={type}'
        self._issues_by_type_and_severity_api_url = sonar_url + \
            'api/issues/search?componentKeys={component}&resolved=false&types={type}&severities={severities}'
        self._analyses_api_url = sonar_url + 'api/project_analyses/search?project={project}&format=json&ps=1'
        self._components_show_api_url = sonar_url + 'api/components/show?component={component}'
        self._components_search_api_url = sonar_url + 'api/components/search?qualifiers=BRC,TRK&q={component}'
        self._measures_api_url = sonar_url + 'api/measures/component?component={component}&metricKeys={metric}'
        self._false_positives_api_url = sonar_url + \
            'api/issues/search?resolutions=FALSE-POSITIVE&componentKeys={resource}'
        self._false_positives_url = sonar_url + 'project/issues?id={resource}&resolutions=FALSE-POSITIVE'
        self._wont_fix_api_url = sonar_url + 'api/issues/search?resolutions=WONTFIX&componentKeys={resource}'
        self._wont_fix_url = sonar_url + 'project/issues?id={resource}&resolutions=WONTFIX'
        self._plugin_api_url = sonar_url + 'api/plugins/installed'
        self._quality_profiles_api_url = sonar_url + 'api/qualityprofiles/search?format=json'
        logging.info("Sonar class instantiated as Sonar7.")

    def is_branch_name_included(self, product: str) -> bool:
        """ Checks if the component name includes the branch name. """
        return self.is_branch_plugin_installed() and self.is_component_absent(product)

    def _get_plugins_json(self):
        return self._get_json(self._plugin_api_url)['plugins']

    @extract_branch_decorator
    def version(self, product: str, branch: str) -> str:
        """ Return the version of the product. """
        url = self._add_branch_param_to_url(
            self._analyses_api_url.format(project=product) + '&category=VERSION', branch)
        try:
            analyses_json = self._get_json(url, log_error=False)
            try:
                return analyses_json['analyses'][0]['events'][0]['name']
            except (KeyError, IndexError) as reason:
                logging.warning("Couldn't get version number of %s from JSON %s (retrieved from %s): %s",
                                product, analyses_json, url, reason)
                return '?'
        except self._url_opener.url_open_exceptions:
            return '?'

    def datetime(self, *products: str) -> DateTime:
        """ Return the date and time of the last analysis of the product. """
        if products:
            split_branch = extract_branch_decorator(lambda this, x, a: (x, a))
            product, branch = split_branch(self, products[0])
            if product:
                url = self._add_branch_param_to_url(self._components_show_api_url.format(component=product), branch)
                try:
                    components_json = self._get_json(url)
                    try:
                        datetime_string = components_json['component']['analysisDate']
                        datetime_string = datetime_string.split('+')[0]  # Ignore timezone
                        return datetime.datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%S')
                    except (ValueError, KeyError) as reason:
                        logging.error("Couldn't get date of last analysis of %s from JSON %s (retrieved from %s): %s",
                                      product, components_json, url, reason)
                except self._url_opener.url_open_exceptions:
                    pass
        return datetime.datetime.min

    def _has_project(self, project: str, branch) -> bool:
        """ Return whether Sonar has the project (analysis). """
        if self.version_number():
            url = self._add_branch_param_to_url(self._components_search_api_url.format(component=project), branch)
            try:
                return self._has_paging_total(project, url)
            # pylint: wrong-exception-operation
            except self._url_opener.url_open_exceptions + (KeyError, IndexError, TypeError, ValueError) as reason:
                logging.warning("Sonar has no analysis of %s: %s", project, reason)
        return False

    def __get_rule_violations(self, product, branch, rule_names, function_name):
        try:
            return self._rule_violation(product, rule_names, -1, branch)
        except KeyError as reason:
            logging.error("Error parsing json response in %s: %s", function_name, reason)
            return -1

    @extract_branch_decorator
    def many_parameters_methods(self, product: str, branch: str) -> int:
        """ Return the number of methods in the product that have too many parameters. """
        rule_names = 'checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.ParameterNumberCheck,' \
                     'pmd:ExcessiveParameterList,' \
                     'csharpsquid:S107,' \
                     'squid:S00107,' \
                     'javascript:ExcessiveParameterList,' \
                     'python:S107'
        return self.__get_rule_violations(product, branch, rule_names, 'many_parameters_methods')

    @extract_branch_decorator
    def long_methods(self, product: str, branch: str) -> int:
        """ Return the number of methods in the product that have to many non-comment statements. """
        # NB: There is no long methods rule for C# and VB.NET. How to deal with this? FIXME
        rule_names = 'squid:S138,' \
                     'checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.JavaNCSSCheck,' \
                     'Pylint:R0915,' \
                     'Web:LongJavaScriptCheck'
        return self.__get_rule_violations(product, branch, rule_names, 'long_methods')

    @extract_branch_decorator
    def complex_methods(self, product: str, branch: str) -> int:
        """ Return the number of methods that violate the Cyclomatic complexity threshold. """
        rule_names = 'checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.CyclomaticComplexityCheck,' \
                     'pmd:CyclomaticComplexity,' \
                     'squid:MethodCyclomaticComplexity,' \
                     'csharpsquid:S1541,' \
                     'csharpsquid:FunctionComplexity,' \
                     'javascript:FunctionComplexity,' \
                     'Web:ComplexityCheck,' \
                     'python:FunctionComplexity,' \
                     'vbnet:S1541,' \
                     'tslint:cyclomatic-complexity'

        return self.__get_rule_violations(product, branch, rule_names, 'complex_methods')

    @extract_branch_decorator
    def commented_loc(self, product: str, branch: str) -> int:
        """ Return the number of commented out lines in the source code of the product. """
        rule_names = 'csharpsquid:S125,' \
                     'csharpsquid:CommentedCode,' \
                     'squid:CommentedOutCodeLine,' \
                     'javascript:CommentedCode,' \
                     'python:S125,' \
                     'Web:AvoidCommentedOutCodeCheck'
        return self.__get_rule_violations(product, branch, rule_names, 'commented_loc')

    @extract_branch_decorator
    def suppressions(self, product: str, branch: str) -> int:
        """ Return the number of suppressions in the source code of the product. """
        return self.__get_rule_violations(product, branch, ','.join(self.suppression_rules), 'suppressions')

    @functools.lru_cache(maxsize=4096)
    def _metric(self, product: str, metric_name: str, branch: str) -> Number:
        """ Return a specific metric value for the product. """
        try:
            return self._get_measure_of_product(branch, metric_name, product)
        except self._url_opener.url_open_exceptions:
            return -1

    def default_quality_profile(self, language: str) -> str:
        """ Return the default quality profile for the language. """
        url = self._quality_profiles_api_url
        try:
            profiles = self._get_json(url)['profiles']
        except self._url_opener.url_open_exceptions + (KeyError, TypeError):  # pylint: wrong-exception-operation
            return ''  # Give up

        for profile in profiles:
            if profile.get("language") == language:
                for keyword in ('isDefault', 'default'):
                    if profile.get(keyword):
                        return profile['name']
        logging.warning("Couldn't find a default quality profile for %s in %s, retrieved from %s", language, profiles,
                        url)
        return ''
