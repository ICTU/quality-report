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
import functools
import logging
from typing import List, Dict, Optional, Union

from . import url_opener
from .. import utils, domain
from hqlib.typing import DateTime, Number


class Sonar(domain.MetricSource, url_opener.UrlOpener):
    """ Class representing the Sonar instance. """

    metric_source_name = 'SonarQube'

    def __init__(self, sonar_url: str, *args, **kwargs) -> None:
        super().__init__(url=sonar_url, *args, **kwargs)
        self.__base_dashboard_url = sonar_url + 'dashboard/index/'
        self.__base_violations_url = sonar_url + 'issues/search#resolved=false|componentRoots='
        self.__issues_api_url = sonar_url + 'api/issues/search?componentRoots={component}&resolved=false&rules={rule}'
        # FIXME: Resource API is deprecated!
        self.__resource_api_url = sonar_url + 'api/resources?resource={resource}&format=json'
        self.__analyses_api_url = sonar_url + 'api/project_analyses/search?project={project}&format=json'
        self.__projects_api_url = sonar_url + 'api/projects/index'
        self.__project_api_url = sonar_url + 'api/projects/{project}'
        self.__metrics_api_url = self.__resource_api_url + '&metrics={metrics}'
        self.__measures_api_url = sonar_url + 'api/measures/component?componentKey={component}&metricKeys={metric}'
        self.__false_positives_api_url = sonar_url + \
            'api/issues/search?resolutions=FALSE-POSITIVE&componentRoots={resource}'
        self.__false_positives_url = sonar_url + 'issues/search#resolutions=FALSE-POSITIVE|componentRoots={resource}'
        self.__version_number_url = sonar_url + 'api/server/version'
        self.__plugin_api_url = sonar_url + 'api/updatecenter/installed_plugins'  # Deprecated API
        self.__quality_profiles_api_url = sonar_url + 'api/qualityprofiles/search?language={language}&format=json'

    def version(self, product: str) -> str:
        """ Return the version of the product. """
        try:
            return self.__get_json(self.__analyses_api_url.format(project=product)+'&category=VERSION')['analyses'][0]['events'][0]['name']
        except self.url_open_exceptions:
            return '?'

    def plugin_version(self, plugin: str) -> str:
        try:
            plugins = self.__get_json(self.__plugin_api_url)
        except self.url_open_exceptions:
            return '0.0'
        mapping = dict((plugin['key'], plugin['version']) for plugin in plugins)
        return mapping.get(plugin, '0.0')

    def plugins_url(self) -> str:
        """ Return the url to the plugin update center. """
        return self.url() + 'updatecenter/'

    def default_quality_profile(self, language: str) -> str:
        """ Return the default quality profile for the language. """
        try:
            response = self.__get_json(self.__quality_profiles_api_url.format(language=language))
        except self.url_open_exceptions:
            return ''
        for profile in response["profiles"]:
            if profile['isDefault']:
                return profile['name']
        return ''

    def quality_profiles_url(self) -> str:
        """ Return the quality profiles url. """
        return self.url() + 'profiles/'

    # Sonar projects

    def __has_project(self, project: str) -> bool:
        """ Return whether Sonar has the project (analysis). """
        found = project in self.__projects()
        if not found:
            logging.warning("Sonar has no analysis of %s", project)
        return found

    def __projects(self) -> List[str]:
        """ Return all projects in Sonar. """
        try:
            json = self.__get_json(self.__projects_api_url)
            return [project['k'] for project in json]
        except self.url_open_exceptions:
            return []

    # Metrics

    def ncloc(self, product: str) -> int:
        """ Non-comment lines of code. """
        return int(self.__metric(product, 'ncloc'))

    def lines(self, product: str) -> int:
        """ Bruto lines of code, including comments, whitespace, javadoc. """
        return int(self.__metric(product, 'lines'))

    def major_violations(self, product: str) -> int:
        """ Return the number of major violations for the product. """
        return int(self.__metric(product, 'major_violations'))

    def critical_violations(self, product: str) -> int:
        """ Return the number of critical violations for the product. """
        return int(self.__metric(product, 'critical_violations'))

    def blocker_violations(self, product: str) -> int:
        """ Return the number of blocker violations for the product. """
        return int(self.__metric(product, 'blocker_violations'))

    def duplicated_lines(self, product: str) -> int:
        """ Return the number of duplicated lines for the product. """
        return int(self.__metric(product, 'duplicated_lines'))

    def unittest_line_coverage(self, product: str) -> float:
        """ Return the line coverage of the unit tests for the product. """
        return float(self.__metric(product, 'line_coverage'))

    def unittest_branch_coverage(self, product: str) -> float:
        """ Return the branch coverage of the unit tests for the product. """
        return float(self.__metric(product, 'branch_coverage'))

    def unittests(self, product: str) -> int:
        """ Return the number of unit tests for the product. """
        return int(self.__metric(product, 'tests'))

    def failing_unittests(self, product: str) -> int:
        """ Return the number of failing unit tests for the product. """
        failures = int(self.__metric(product, 'test_failures'))
        errors = int(self.__metric(product, 'test_errors'))
        return failures + errors if failures >= 0 and errors >= 0 else -1

    def integration_test_line_coverage(self, product: str) -> float:
        """ Return the line coverage of the integration tests for the product. """
        return float(self.__metric(product, 'it_line_coverage'))

    def integration_test_branch_coverage(self, product: str) -> float:
        """ Return the branch coverage of the integration tests for the product. """
        return float(self.__metric(product, 'it_branch_coverage'))

    def overall_test_line_coverage(self, product: str) -> float:
        """ Return the overall line coverage of the tests for the product. """
        return float(self.__metric(product, 'overall_line_coverage'))

    def overall_test_branch_coverage(self, product: str) -> float:
        """ Return the overall branch coverage of the tests for the product. """
        return float(self.__metric(product, 'overall_branch_coverage'))

    def methods(self, product: str) -> int:
        """ Return the number of methods/functions in the product. """
        return int(self.__metric(product, 'functions'))

    def dashboard_url(self, product: str) -> str:
        """ Return the url for the Sonar dashboard for the product. """
        return self.__base_dashboard_url + product

    # Violations

    def complex_methods(self, product: str) -> int:
        """ Return the number of methods that violate the Cyclomatic complexity threshold. """
        rule_names = ('checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.CyclomaticComplexityCheck',
                      'pmd:CyclomaticComplexity',
                      'squid:MethodCyclomaticComplexity',
                      'csharpsquid:S1541',
                      'csharpsquid:FunctionComplexity',
                      'javascript:FunctionComplexity',
                      'Web:ComplexityCheck',
                      'python:FunctionComplexity',
                      'vb:S1541',
                      'tslint:cyclomatic-complexity')
        for rule_name in rule_names:
            nr_complex_methods = self.__rule_violation(product, rule_name)
            if nr_complex_methods:
                return nr_complex_methods
        return 0

    def long_methods(self, product: str) -> int:
        """ Return the number of methods in the product that have to many non-comment statements. """
        # NB: There is no long methods rule for C#. How to deal with this? FIXME
        rule_names = ('squid:S138',
                      'checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.JavaNCSSCheck',
                      'Pylint:R0915',
                      'Web:LongJavaScriptCheck',
                      'vb:S138')
        for rule_name in rule_names:
            nr_long_methods = self.__rule_violation(product, rule_name)
            if nr_long_methods:
                return nr_long_methods
        return 0

    def many_parameters_methods(self, product: str) -> int:
        """ Return the number of methods in the product that have too many parameters. """
        rule_names = ('checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.ParameterNumberCheck',
                      'pmd:ExcessiveParameterList',
                      'csharpsquid:S107',
                      'squid:S00107',
                      'javascript:ExcessiveParameterList',
                      'python:S107')
        for rule_name in rule_names:
            nr_many_parameters = self.__rule_violation(product, rule_name)
            if nr_many_parameters:
                return nr_many_parameters
        return 0

    def commented_loc(self, product: str) -> int:
        """ Return the number of commented out lines in the source code of the product. """
        rule_names = ('csharpsquid:CommentedCode', 'csharpsquid:S125', 'squid:CommentedOutCodeLine',
                      'javascript:CommentedCode', 'python:S125', 'Web:AvoidCommentedOutCodeCheck')
        for rule_name in rule_names:
            nr_commented_loc = self.__rule_violation(product, rule_name)
            if nr_commented_loc:
                return nr_commented_loc
        return 0

    def no_sonar(self, product: str) -> int:
        """ Return the number of NOSONAR usages in the source code of the product. """
        return self.__rule_violation(product, 'squid:NoSonar')

    def violations_url(self, product: str) -> str:
        """ Return the url for the violations of the product. """
        return self.__base_violations_url + product

    # Issues

    def false_positives(self, product: str) -> int:
        """ Return the number of false positives listed for the product. """
        return self.__false_positives(product)

    def false_positives_url(self, product: str) -> str:
        """ Return the url to the list of false positives. """
        return self.__false_positives_url.format(resource=product)

    # Meta data

    def version_number(self) -> Optional[str]:
        """ Return the version number of Sonar. """
        try:
            return self.url_read(self.__version_number_url)
        except self.url_open_exceptions:
            return None

    def datetime(self, *products: str) -> DateTime:
        """ Return the date and time of the last analysis of the product. """
        url = self.__analyses_api_url.format(project=products[0])
        try:
            datetime_string = self.__get_json(url)['analyses'][0]['date']
        except self.url_open_exceptions:
            return datetime.datetime.min
        datetime_string = datetime_string.split('+')[0]  # Ignore timezone
        return datetime.datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%S')

    # Helper methods

    @functools.lru_cache(maxsize=4096)
    def __metric(self, product: str, metric_name: str, default=0) -> Number:
        """ Return a specific metric value for the product. """
        if not self.__has_project(product):
            return -1

        # First try API starting with SonarQube 5.4:
        try:
            json = self.__get_json(self.__measures_api_url.format(component=product, metric=metric_name))
            for measure in json['component']['measures']:
                if measure['metric'] == metric_name:
                    return float(measure['value'])
        except self.url_open_exceptions:
            pass
        except (TypeError, KeyError):
            pass
        # Then try older API:
        json = self.__all_metrics(product)
        for metric in json[0]['msr']:
            if metric['key'] == metric_name:
                return metric['val']
        logging.debug("Can't get %s value for %s from %s", metric_name, product, json)
        return default

    def __all_metrics(self, product: str) -> Union[Dict, List[Dict]]:
        """ Return all available metric values for the product. """
        try:
            return self.__get_json(self.__metrics_api_url.format(resource=product, metrics='true'))
        except self.url_open_exceptions:
            return [{'msr': []}]

    def __rule_violation(self, product: str, rule_name: str, default=0) -> int:
        """ Return a specific violation value for the product. """
        if not self.__has_project(product):
            return -1
        try:
            json = self.__get_json(self.__issues_api_url.format(component=product, rule=rule_name))
        except self.url_open_exceptions:
            return default
        return int(json['paging']['total'])

    def __false_positives(self, product: str, default=0) -> int:
        """ Return the number of issues resolved as false positive. """
        if not self.__has_project(product):
            return -1
        try:
            json = self.__get_json(self.__false_positives_api_url.format(resource=product))
        except self.url_open_exceptions:
            return default
        return len(json['issues'])

    @functools.lru_cache(maxsize=4096)
    def __get_json(self, url: str) -> Union[Dict, List[Dict]]:
        """ Get and evaluate the json from the url. """
        try:
            json_string = self.url_read(url)
        except self.url_open_exceptions as reason:
            logging.warning("Can't retrieve url %s from Sonar: %s", url, reason)
            raise
        if not json_string:
            logging.error("Received empty json from %s", url)
        return utils.eval_json(json_string)
