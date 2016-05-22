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
from __future__ import absolute_import

import datetime
import logging
import urllib2

from . import url_opener, sonar_runner
from .maven import Maven
from .. import utils, domain


class Sonar(domain.MetricSource, url_opener.UrlOpener):
    """ Class representing the Sonar instance. """

    metric_source_name = 'SonarQube'

    def __init__(self, sonar_url, maven=None, version_control_system=None,
                 *args, **kwargs):
        super(Sonar, self).__init__(url=sonar_url, *args, **kwargs)
        maven = maven or Maven()
        self.__runner = sonar_runner.SonarRunner(self, maven, version_control_system)
        self.__base_dashboard_url = sonar_url + 'dashboard/index/'
        self.__base_violations_url = sonar_url + 'drilldown/violations/'
        self.__violations_api_url = sonar_url + 'api/resources?resource={resource}&' \
            'metrics=blocker_violations,critical_violations,major_violations,' \
            'minor_violations,info_violations&rules=true&includetrends=true'
        self.__resource_api_url = sonar_url + 'api/resources?resource={resource}'
        self.__resources_api_url = sonar_url + 'api/resources/index'
        self.__metrics_api_url = self.__resource_api_url + '&metrics={metrics}'
        self.__false_positives_api_url = sonar_url + \
            'api/issues/search?resolutions=FALSE-POSITIVE&componentRoots={resource}'
        self.__false_positives_url = sonar_url + 'issues/search#resolutions=FALSE-POSITIVE|componentRoots={resource}'
        self.__version_number_url = sonar_url + 'api/server/index'
        self.__projects_api_url = sonar_url + 'api/projects/{project}'
        self.__plugin_api_url = sonar_url + 'api/updatecenter/installed_plugins'
        self.__quality_profiles_api_url = sonar_url + 'api/profiles/list?language={language}'

    @utils.memoized
    def version(self, product):
        """ Return the version of the product. """
        json = self.url_open(self.__resource_api_url.format(resource=product)).read()
        version = utils.eval_json(json)[0]['version']
        logging.debug('Retrieving Sonar version for %s -> %s', product, version)
        return version

    @utils.memoized
    def plugin_version(self, plugin):
        """ Return the version of the plugin. """
        try:
            plugins = self.__get_json(self.__plugin_api_url)
        except urllib2.HTTPError as reason:
            logging.warning("Can't retrieve plugins url %s from Sonar: %s", self.__plugin_api_url, reason)
            return -1
        mapping = dict((plugin['key'], plugin['version']) for plugin in plugins)
        return mapping.get(plugin, -1)

    def plugins_url(self):
        """ Return the url to the plugin update center. """
        return self.url() + 'updatecenter/'

    @utils.memoized
    def default_quality_profile(self, language):
        """ Return the default quality profile for the language. """
        url = self.__quality_profiles_api_url.format(language=language)
        try:
            profiles = self.__get_json(url)
        except (urllib2.HTTPError, urllib2.URLError) as reason:
            logging.warning("Can't retrieve quality profiles url %s from Sonar: %s", url, reason)
            return ''
        for profile in profiles:
            if profile['default']:
                return profile['name']
        return ''

    def quality_profiles_url(self):
        """ Return the quality profiles url. """
        return self.url() + 'profiles/'

    # Sonar projects

    @utils.memoized
    def has_project(self, project):
        """ Return whether Sonar has the project (analysis). """
        found = project in self.projects()
        if not found:
            logging.warning("Sonar has no analysis of %s", project)
        return found

    @utils.memoized
    def projects(self):
        """ Return all projects in Sonar. """
        try:
            json = self.__get_json(self.__resources_api_url)
            return [resource['key'] for resource in json]
        except (urllib2.HTTPError, urllib2.URLError) as reason:
            logging.warning("Can't retrieve resources url %s from Sonar: %s", self.__resources_api_url, reason)
        return []

    def delete_project(self, project):
        """ Delete a project (analysis) from Sonar. """
        try:
            self.url_delete(self.__projects_api_url.format(project=project))
            logging.info('Removed Sonar analysis for %s', project)
            return True
        except urllib2.HTTPError as reason:
            logging.warning("Can't remove Sonar analysis for %s: %s", project, reason)
            return False

    # Metrics

    def ncloc(self, product):
        """ Non-comment lines of code. """
        return int(self.__metric(product, 'ncloc'))

    def lines(self, product):
        """ Bruto lines of code, including comments, whitespace, javadoc. """
        return int(self.__metric(product, 'lines'))

    def major_violations(self, product):
        """ Return the number of major violations for the product. """
        return int(self.__metric(product, 'major_violations'))

    def critical_violations(self, product):
        """ Return the number of critical violations for the product. """
        return int(self.__metric(product, 'critical_violations'))

    def blocker_violations(self, product):
        """ Return the number of blocker violations for the product. """
        return int(self.__metric(product, 'blocker_violations'))

    def duplicated_lines(self, product):
        """ Return the number of duplicated lines for the product. """
        return int(self.__metric(product, 'duplicated_lines'))

    def line_coverage(self, product):
        """ Return the line coverage of the unit tests for the product. """
        return self.__metric(product, 'line_coverage')

    def branch_coverage(self, product):
        """ Return the branch coverage of the unit tests for the product. """
        return self.__metric(product, 'branch_coverage')

    def unittests(self, product):
        """ Return the number of unit tests for the product. """
        return int(self.__metric(product, 'tests'))

    def failing_unittests(self, product):
        """ Return the number of failing unit tests for the product. """
        return int(self.__metric(product, 'test_failures') + self.__metric(product, 'test_errors'))

    def package_cycles(self, product):
        """ Return the number of cycles in the package dependencies for the product. """
        return int(self.__metric(product, 'package_cycles'))

    def methods(self, product):
        """ Return the number of methods/functions in the product. """
        return int(self.__metric(product, 'functions'))

    def dashboard_url(self, product):
        """ Return the url for the Sonar dashboard for the product. """
        return self.__base_dashboard_url + product

    # Violations

    def complex_methods(self, product):
        """ Return the number of methods that violate the Cyclomatic complexity threshold. """
        violation_names = ('checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.CyclomaticComplexityCheck',
                           'pmd:CyclomaticComplexity',
                           'squid:MethodCyclomaticComplexity',
                           'FunctionComplexity',
                           'Web:ComplexityCheck',
                           'python:FunctionComplexity')
        for violation_name in violation_names:
            nr_complex_methods = self.__violation(product, violation_name)
            if nr_complex_methods:
                return nr_complex_methods
        return 0

    def long_methods(self, product):
        """ Return the number of methods in the product that have to many non-comment statements. """
        violation_names = ('checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.JavaNCSSCheck',
                           'AvoidLongMethodsRule',
                           'Pylint:R0915')
        for violation_name in violation_names:
            nr_long_methods = self.__violation(product, violation_name)
            if nr_long_methods:
                return nr_long_methods
        return 0

    def many_parameters_methods(self, product):
        """ Return the number of methods in the product that have too many parameters. """
        violation_names = ('checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.ParameterNumberCheck',
                           'pmd:ExcessiveParameterList',
                           'csharpsquid:S107',
                           'squid:S00107',
                           'AvoidLongParameterListsRule',
                           'python:S107')
        for violation_name in violation_names:
            nr_many_parameters = self.__violation(product, violation_name)
            if nr_many_parameters:
                return nr_many_parameters
        return 0

    def commented_loc(self, product):
        """ Return the number of commented out lines in the source code of the product. """
        violation_names = ('csharpsquid:CommentedCode', 'squid:CommentedOutCodeLine',
                           'javascript:CommentedCode', 'python:S125')
        for violation_name in violation_names:
            nr_commented_loc = self.__violation(product, violation_name)
            if nr_commented_loc:
                return nr_commented_loc
        return 0

    def no_sonar(self, product):
        """ Return the number of NOSONAR usages in the source code of the product. """
        return self.__violation(product, 'squid:NoSonar')

    def violations_url(self, product):
        """ Return the url for the violations of the product. """
        return self.__base_violations_url + product

    # Issues

    def false_positives(self, product):
        """ Return the number of false positives listed for the product. """
        return self.__false_positives(product)

    def false_positives_url(self, product):
        """ Return the url to the list of false positives. """
        return self.__false_positives_url.format(resource=product)

    # Meta data

    def version_number(self):
        """ Return the version number of Sonar. """
        return self.__get_json(self.__version_number_url)['version']

    def analysis_datetime(self, product):
        """ Return the date and time of the last analysis of the product. """
        try:
            datetime_string = self.__get_json(self.__resource_api_url.format(resource=product))[0]['date']
        except urllib2.HTTPError:
            return datetime.datetime.min
        datetime_string = datetime_string.split('+')[0]  # Ignore timezone
        return datetime.datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%S')

    # Analysis

    def analyse_products(self, products):
        """ Run Sonar on the products and remove old analyses. """
        self.__runner.analyse_products(products)

    # Helper methods

    @utils.memoized
    def __metric(self, product, metric_name, default=0):
        """ Return a specific metric value for the product. """
        if not self.has_project(product):
            return -1
        json = self.__all_metrics(product)
        for metric in json[0]['msr']:
            if metric['key'] == metric_name:
                return metric['val']
        logging.debug("Can't get %s value for %s from %s", metric_name, product, json)
        return default

    @utils.memoized
    def __all_metrics(self, product):
        """ Return all available metric values for the product. """
        try:
            return self.__get_json(self.__metrics_api_url.format(resource=product, metrics='true'))
        except urllib2.HTTPError:
            return [{'msr': []}]

    @utils.memoized
    def __violation(self, product, violation_name, default=0):
        """ Return a specific violation value for the product. """
        if not self.has_project(product):
            return -1
        try:
            json = self.__get_json(self.__violations_api_url.format(resource=product))
        except urllib2.HTTPError:
            return default
        try:
            violations = json[0]['msr']
        except (IndexError, KeyError):
            logging.debug("Can't get %s value for %s from %s", violation_name, product, json)
            return default
        violation_name = violation_name.lower()
        for violation in violations:
            if violation_name in violation['rule_name'].lower() or violation_name in violation['rule_key'].lower():
                return int(violation['val'])
        return default

    def __false_positives(self, product, default=0):
        """ Return the number of issues resolved as false positive. """
        if not self.has_project(product):
            return -1
        try:
            json = self.__get_json(self.__false_positives_api_url.format(resource=product))
        except urllib2.HTTPError:
            return default
        return len(json['issues'])

    @utils.memoized
    def __get_json(self, url):
        """ Get and evaluate the json from the url. """
        try:
            json_string = self.url_open(url).read()
        except urllib2.HTTPError as reason:
            logging.warning("Can't retrieve resource url %s from Sonar: %s", url, reason)
            raise
        return utils.eval_json(json_string)
