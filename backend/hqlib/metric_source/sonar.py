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
import functools
import logging
import json
from typing import List, Dict, Optional, Union, Sequence
from distutils.version import LooseVersion

from . import url_opener
from .. import utils, metric_source
from ..typing import DateTime, Number


def extract_branch_decorator(func):
    """" Checks if product name has to be splitted into product and branch and performs the splitting."""
    def _branch_param(self, product: str) -> (str, str):
        """ Return the branch url parameter. """

        if self.version_number() \
                and LooseVersion(self.version_number()) >= LooseVersion('6.7') \
                and self.is_branch_plugin_installed() \
                and self.is_component_absent(product):

            prod = product.rsplit(":", 1)
            if len(prod) == 2:
                return func(self, prod[0], None if prod[1] == '' else prod[1])
            logging.warning(
                "A branch name is not defined in '%s' and no component with corresponding name is found.", product)

        return func(self, product, None)
    return _branch_param


class Sonar(metric_source.TestReport):
    """ Class representing the Sonars instance. """

    metric_source_name = 'SonarQube'

    def __init__(self, sonar_url: str, *args, **kwargs) -> None:
        self.__url_opener = url_opener.UrlOpener(username=kwargs.get("username", ""),
                                                 password=kwargs.get("password", ""))
        super().__init__(url=sonar_url, *args, **kwargs)

        self.__version_number_url = sonar_url + 'api/server/version'
        self.__base_dashboard_url = sonar_url + 'dashboard?id={project}'
        self.__base_violations_url = sonar_url + 'issues/search#resolved=false|componentRoots='
        self.__issues_api_url = sonar_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}'
        self.__analyses_api_url = sonar_url + 'api/project_analyses/search?project={project}&format=json'
        self.__components_show_api_url = sonar_url + 'api/components/show?component={component}'
        self.__resource_api_url = sonar_url + 'api/resources?resource={resource}&format=json'
        self.__projects_api_url = sonar_url + 'api/projects/index?subprojects=true'
        self.__measures_api_url = sonar_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
        self.__false_positives_api_url = sonar_url + \
            'api/issues/search?resolutions=FALSE-POSITIVE&componentRoots={resource}'
        self.__false_positives_url = sonar_url + 'issues/search#resolutions=FALSE-POSITIVE|componentRoots={resource}'
        self.__plugin_api_url = sonar_url + 'api/updatecenter/installed_plugins'  # Deprecated API
        self.__quality_profiles_api_url = sonar_url + 'api/qualityprofiles/search?language={language}&format=json'
        self.__old_quality_profiles_api_url = sonar_url + 'api/profiles/list?language={language}&format=json'

    # Coverage report API

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

    @classmethod
    def __add_branch_param_to_url(cls, url: str, branch: str) -> str:
        """" Adds branch url query param to the url, if defined. """
        return url + "&branch=" + branch if branch else url

    @extract_branch_decorator
    def version(self, product: str, branch: str) -> str:
        """ Return the version of the product. """

        url = self.__add_branch_param_to_url(
            self.__analyses_api_url.format(project=product) + '&category=VERSION', branch)

        try:
            analyses_json = self.__get_json(url, log_error=False)
            try:
                return analyses_json['analyses'][0]['events'][0]['name']
            except (KeyError, IndexError, TypeError) as reason:
                logging.warning("Couldn't get version number of %s from JSON %s (retrieved from %s): %s",
                                product, analyses_json, url, reason)
                return '?'
        except self.__url_opener.url_open_exceptions:
            # Try older API:
            url = self.__add_branch_param_to_url(self.__resource_api_url.format(resource=product), branch)
            try:
                analyses_json = self.__get_json(url)
            except self.__url_opener.url_open_exceptions:
                return '?'
            try:
                return analyses_json[0]['version']
            except (KeyError, IndexError, TypeError) as reason:
                logging.warning("Couldn't get version number of %s from JSON %s (retrieved from %s): %s",
                                product, analyses_json, url, reason)
                return '?'

    def plugin_version(self, plugin: str) -> str:
        """ Return the version of the SonarQube plugin. """
        try:
            plugins = self.__get_json(self.__plugin_api_url)
        except self.__url_opener.url_open_exceptions:
            return '0.0'
        mapping = dict((plugin['key'], plugin['version']) for plugin in plugins)
        return mapping.get(plugin, '0.0')

    def plugins_url(self) -> str:
        """ Return the url to the plugin update center. """
        return self.url() + 'updatecenter/'

    def default_quality_profile(self, language: str) -> str:
        """ Return the default quality profile for the language. """
        url = self.__quality_profiles_api_url.format(language=language)
        try:
            profiles = self.__get_json(url)['profiles']
        except self.__url_opener.url_open_exceptions + (KeyError, TypeError):
            # Try old API
            url = self.__old_quality_profiles_api_url.format(language=language)
            try:
                profiles = self.__get_json(url)
            except self.__url_opener.url_open_exceptions:
                return ''  # Give up
        for profile in profiles:
            for keyword in ('isDefault', 'default'):
                if keyword in profile and profile[keyword]:
                    return profile['name']
        logging.warning("Couldn't find a default quality profile in %s, retrieved from %s", profiles, url)
        return ''

    def quality_profiles_url(self) -> str:
        """ Return the quality profiles url. """
        return self.url() + 'profiles/'

    @functools.lru_cache(maxsize=4096)
    def is_branch_plugin_installed(self) -> bool:
        """ Return whether SonarQube has the branch plugin installed, which is needed for interpreting Sonar keys. """
        try:
            plugins = json.loads(self.__url_opener.url_read(self.__plugin_api_url))
            if "branch" in [item["key"] for item in plugins]:
                return True
            logging.info("Branch plugin not installed.")
        except self.__url_opener.url_open_exceptions as reason:
            logging.error("Couldn't open %s: %s", self.__plugin_api_url, reason)
        except ValueError as reason:
            logging.error("Error parsing response from %s: '%s'. "
                          "Assume the Branch plugin is not installed.", self.__plugin_api_url, reason)
        return False

    @functools.lru_cache(maxsize=4096)
    def is_component_absent(self, product: str) -> bool:
        """" Checks if the component with complete name, including branch, is defined """
        url = self.__components_show_api_url.format(component=product)
        try:
            if json.loads(self.__url_opener.url_read(url, log_error=False))["component"]:
                logging.info("Component '%s' found. No branch is defined.", product)
                return False
        except (ValueError, KeyError):
            pass
        except self.__url_opener.url_open_exceptions:
            pass
        return True

    # Sonar projects

    def __has_project(self, project: str, branch) -> bool:
        """ Return whether Sonar has the project (analysis). """
        found = project in self.__projects(branch)
        if not found:
            logging.warning("Sonar has no analysis of %s", project)
        return found

    def __projects(self, branch) -> List[str]:
        """ Return all projects in Sonar. """
        try:
            projects_json = self.__get_json(self.__add_branch_param_to_url(self.__projects_api_url, branch))
            return [project['k'] for project in projects_json]
        except self.__url_opener.url_open_exceptions:
            return []

    # Metrics

    @extract_branch_decorator
    def ncloc(self, product: str, branch: str) -> int:
        """ Non-comment lines of code. """
        return int(self.__metric(product, 'ncloc', branch))

    @extract_branch_decorator
    def lines(self, product: str, branch: str) -> int:
        """ Bruto lines of code, including comments, whitespace, javadoc. """
        return int(self.__metric(product, 'lines', branch))

    @extract_branch_decorator
    def major_violations(self, product: str, branch: str) -> int:
        """ Return the number of major violations for the product. """
        return int(self.__metric(product, 'major_violations', branch))

    @extract_branch_decorator
    def critical_violations(self, product: str, branch: str) -> int:
        """ Return the number of critical violations for the product. """
        return int(self.__metric(product, 'critical_violations', branch))

    @extract_branch_decorator
    def blocker_violations(self, product: str, branch: str) -> int:
        """ Return the number of blocker violations for the product. """
        return int(self.__metric(product, 'blocker_violations', branch))

    @extract_branch_decorator
    def duplicated_lines(self, product: str, branch: str) -> int:
        """ Return the number of duplicated lines for the product. """
        return int(self.__metric(product, 'duplicated_lines', branch))

    @extract_branch_decorator
    def unittest_line_coverage(self, product: str, branch: str) -> float:
        """ Return the line coverage of the unit tests for the product. """
        return float(self.__metric(product, 'line_coverage', branch))

    @extract_branch_decorator
    def unittest_branch_coverage(self, product: str, branch: str) -> float:
        """ Return the branch coverage of the unit tests for the product. """
        return float(self.__metric(product, 'branch_coverage', branch))

    @extract_branch_decorator
    def unittests(self, product: str, branch: str) -> int:
        """ Return the number of unit tests for the product. """
        return int(self.__metric(product, 'tests', branch))

    @extract_branch_decorator
    def failing_unittests(self, product: str, branch: str) -> int:
        """ Return the number of failing unit tests for the product. """
        failures = int(self.__metric(product, 'test_failures', branch))
        errors = int(self.__metric(product, 'test_errors', branch))
        return failures + errors if failures >= 0 and errors >= 0 else -1

    @extract_branch_decorator
    def methods(self, product: str, branch: str) -> int:
        """ Return the number of methods/functions in the product. """
        return int(self.__metric(product, 'functions', branch))

    @extract_branch_decorator
    def dashboard_url(self, product: str, branch: str) -> str:
        """ Return the url for the Sonar dashboard for the product. """
        return self.__add_branch_param_to_url(self.__base_dashboard_url.format(project=product), branch)

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
            nr_complex_methods = self.__rule_violation(product, rule_name, 0, branch)
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
            nr_long_methods = self.__rule_violation(product, rule_name, 0, branch)
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
            nr_many_parameters = self.__rule_violation(product, rule_name, 0, branch)
            if nr_many_parameters:
                return nr_many_parameters
        return 0

    @extract_branch_decorator
    def commented_loc(self, product: str, branch: str) -> int:
        """ Return the number of commented out lines in the source code of the product. """
        rule_names = ('csharpsquid:S125', 'csharpsquid:CommentedCode', 'squid:CommentedOutCodeLine',
                      'javascript:CommentedCode', 'python:S125', 'Web:AvoidCommentedOutCodeCheck')
        for rule_name in rule_names:
            nr_commented_loc = self.__rule_violation(product, rule_name, 0, branch)
            if nr_commented_loc:
                return nr_commented_loc
        return 0

    @extract_branch_decorator
    def no_sonar(self, product: str, branch: str) -> int:
        """ Return the number of NOSONAR usages (or other suppressions) in the source code of the product. """
        rule_names = ('squid:NoSonar', 'Pylint:I0011')
        for rule_name in rule_names:
            nr_no_sonar = self.__rule_violation(product, rule_name, 0, branch)
            if nr_no_sonar:
                return nr_no_sonar
        return 0

    @extract_branch_decorator
    def violations_url(self, product: str, branch: str) -> str:
        """ Return the url for the violations of the product. """
        return self.__add_branch_param_to_url(self.__base_violations_url + product, branch)

    # Issues

    @extract_branch_decorator
    def false_positives(self, product: str, branch: str) -> int:
        """ Return the number of false positives listed for the product. """
        return self.__false_positives(product, 0, branch)

    @extract_branch_decorator
    def false_positives_url(self, product: str, branch: str) -> str:
        """ Return the url to the list of false positives. """
        return self.__add_branch_param_to_url(self.__false_positives_url.format(resource=product), branch)

    # Meta data

    @functools.lru_cache(maxsize=1024)
    def version_number(self) -> Optional[str]:
        """ Return the version number of Sonar. """
        try:
            return self.__url_opener.url_read(self.__version_number_url)
        except self.__url_opener.url_open_exceptions:
            return None

    def datetime(self, *products: str) -> DateTime:
        """ Return the date and time of the last analysis of the product. """
        if not products:
            return datetime.datetime.min

        split_branch = extract_branch_decorator(lambda this, x, a: (x, a))
        product, branch = split_branch(self, products[0])

        server_version = self.version_number()
        if server_version and LooseVersion(server_version) >= LooseVersion('6.4'):
            # Use the components API, it should contain the analysis date both for projects and components
            url = self.__add_branch_param_to_url(self.__components_show_api_url.format(component=product), branch)
            try:
                components_json = self.__get_json(url)
                try:
                    datetime_string = components_json['component']['analysisDate']
                    datetime_string = datetime_string.split('+')[0]  # Ignore timezone
                    return datetime.datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%S')
                except (TypeError, KeyError, IndexError) as reason:
                    logging.error("Couldn't get date of last analysis of %s from JSON %s (retrieved from %s): %s",
                                  product, components_json, url, reason)
            except self.__url_opener.url_open_exceptions:
                pass
            return datetime.datetime.min
        # Use analyses API:
        url = self.__add_branch_param_to_url(self.__analyses_api_url.format(project=product), branch)
        try:
            components_json = self.__get_json(url, log_error=False)['analyses']
        except self.__url_opener.url_open_exceptions:
            # Try older API:
            url = self.__add_branch_param_to_url(self.__resource_api_url.format(resource=product), branch)
            try:
                components_json = self.__get_json(url)
            except self.__url_opener.url_open_exceptions:
                return datetime.datetime.min
        try:
            datetime_string = components_json[0]['date']
        except (TypeError, KeyError, IndexError) as reason:
            logging.warning("Couldn't get date of last analysis of %s from JSON %s (retrieved from %s): %s",
                            product, components_json, url, reason)
            return datetime.datetime.min
        datetime_string = datetime_string.split('+')[0]  # Ignore timezone
        return datetime.datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%S')

    # Helper methods

    @functools.lru_cache(maxsize=4096)
    def __metric(self, product: str, metric_name: str, branch: str) -> Number:
        """ Return a specific metric value for the product. """
        if not self.__has_project(product, branch):
            return -1
        url = self.__add_branch_param_to_url(
            self.__measures_api_url.format(component=product, metric=metric_name), branch)
        try:
            measures_json = self.__get_json(url, log_error=False)
            try:
                for measure in measures_json['component']['measures']:
                    if measure['metric'] == metric_name:
                        return float(measure['value'])
                reason = 'metric not found in component measures'
            except (TypeError, KeyError, IndexError, ValueError) as reason:
                pass  # Next lines will log exception and return from this method
            logging.warning("Can't get %s value for %s from %s (retrieved from %s): %s", metric_name, product,
                            measures_json, url, reason)
            return -1
        except self.__url_opener.url_open_exceptions:
            pass  # Keep going, and try the old API
        url = self.__add_branch_param_to_url(
            self.__resource_api_url.format(resource=product) + '&metrics=' + metric_name, branch)
        try:
            measures_json = self.__get_json(url)
            try:
                return float(measures_json[0]["msr"][0]["val"])
            except (TypeError, KeyError, IndexError, ValueError) as reason:
                logging.warning("Can't get %s value for %s from %s (retrieved from %s): %s", metric_name, product,
                                measures_json, url, reason)
                return -1
        except self.__url_opener.url_open_exceptions:
            return -1

    def __rule_violation(self, product: str, rule_name: str, default: int = 0, branch: str = None) -> int:
        """ Return a specific violation value for the product. """
        if not self.__has_project(product, branch):
            return -1
        try:
            issues_json = self.__get_json(
                self.__add_branch_param_to_url(self.__issues_api_url.format(component=product, rule=rule_name), branch))
        except self.__url_opener.url_open_exceptions:
            return default
        return int(issues_json['paging']['total'])

    def __false_positives(self, product: str, default: int = 0, branch: str = None) -> int:
        """ Return the number of issues resolved as false positive. """
        if not self.__has_project(product, branch):
            return -1
        try:
            false_positives_json = self.__get_json(
                self.__add_branch_param_to_url(self.__false_positives_api_url.format(resource=product), branch))
        except self.__url_opener.url_open_exceptions:
            return default
        return len(false_positives_json['issues'])

    @functools.lru_cache(maxsize=4096)
    def __get_json(self, url: str, *args, **kwargs) -> Union[Dict[str, Dict],
                                                             List[Dict[str, Union[str, List[Dict[str, str]]]]]]:
        """ Get and evaluate the json from the url. """
        json_string = self.__url_opener.url_read(url, *args, **kwargs)
        return utils.eval_json(json_string)
