#!/usr/bin/env python
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

# Python script to retrieve metrics from different back-end systems, like Sonar and Jenkins.


import logging
import os
import socket
import sys
import urllib2
import xmlrpclib

import pkg_resources

from qualitylib import formatting, commandlineargs, report, metric_source, metric_info, log, filesystem, VERSION


class Reporter(object):  # pylint: disable=too-few-public-methods
    """ Class for creating the quality report for a specific project. """

    PROJECT_DEFINITION_FILENAME = 'project_definition.py'
    HISTORY_FILENAME = 'history.json'
    EMPTY_HISTORY_PNG = "\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00d\x00\x00\x00\x19\x08\x06\x00\x00\x00" \
                        "\xc7^\x8bK\x00\x00\x00\x06bKGD\x00\xff\x00\xff\x00\xff\xa0\xbd\xa7\x93\x00\x00\x00 " \
                        "IDATh\x81\xed\xc1\x01\r\x00\x00\x00\xc2\xa0\xf7Om\x0f\x07\x14\x00\x00\x00\x00\x00\x00" \
                        "\x00\x00\x00\x1c\x1b')\x00\x01\xbca\xfe\x1a\x00\x00\x00\x00IEND\xaeB`\x82"

    def __init__(self, project_folder):
        self.__project = self.__import_project(project_folder, self.PROJECT_DEFINITION_FILENAME)
        self.__history_filename = os.path.join(project_folder, self.HISTORY_FILENAME)

    @staticmethod
    def __import_project(project_folder, project_definition_filename):
        """ Import the project from the project definition file in the project folder. """
        # Add the parent folder of the project folder to the python path so the
        # project definition can import shared resources from other folders.
        sys.path.insert(0, os.path.abspath(os.path.join(project_folder, '..')))
        # Add the project folder itself to the python path so that we can import the project definition itself.
        sys.path.insert(0, project_folder)
        # Import the project definition and get the project from it.
        module_name = project_definition_filename[:-len('.py')]
        project_definition_module = __import__(module_name)
        return project_definition_module.PROJECT

    def create_report(self, report_folder):
        """ Create, format, and write the quality report. """
        self.__add_latest_release_of_products()
        self.__add_release_candidates_of_products()
        self.__add_branches_of_products()
        self.__add_dependencies()
        self.__analyse_products()

        quality_report = report.QualityReport(self.__project)
        self.__format_and_write_report(quality_report, formatting.JSONFormatter, self.__history_filename, 'a', 'ascii',
                                       sonar=self.__project.metric_source(metric_source.Sonar))
        self.__create_report(quality_report, report_folder)
        metric_source.History(self.__history_filename).clean_history()

    def __add_latest_release_of_products(self):
        """ Add the latest released version of each product. """
        vcs = self.__project.metric_source(metric_source.VersionControlSystem)
        for product in self.__project.products()[:]:
            vcs_product_info = metric_info.VersionControlSystemProductInfo(vcs, product)
            latest_version = vcs_product_info.latest_released_product_version()
            if latest_version:
                logging.info('Adding %s:%s to the project because it is the latest version.',
                             product.name(), latest_version)
                self.__project.add_product_with_version(product.name(), latest_version)

    def __add_release_candidates_of_products(self):
        """ Add the versions of the products that are scheduled to be released
            to operations. """
        for product in self.__project.products()[:]:
            release_candidate = product.release_candidate()
            if release_candidate:
                logging.info('Adding %s:%s to the project because it is a release candidate.',
                             product.name(), release_candidate)
                self.__project.add_product_with_version(product.name(), release_candidate)

    def __add_branches_of_products(self):
        """ Add the branches of the products that have to be monitored. """
        for product in self.__project.products()[:]:
            for branch in product.product_branches():
                logging.info('Adding %s:%s to the project because it is a branch to be monitored.',
                             product.name(), branch)
                self.__project.add_product_with_branch(product.name(), branch)

    def __add_dependencies(self):
        """ Add product versions that other products depend on. """
        for name, version in self.__project.product_dependencies():
            logging.info('Adding %s:%s to the project because it is a dependency.', name, version)
            self.__project.add_product_with_version(name, version)

    def __analyse_products(self):
        """ Make sure Sonar contains the right analysis projects. """
        sonar = self.__project.metric_source(metric_source.Sonar)
        if sonar:
            sonar.analyse_products(self.__project.products())

    @classmethod
    def __create_report(cls, quality_report, report_dir):
        """ Format the quality report to HTML and write the files in the report folder. """
        report_dir = report_dir or '.'
        filesystem.create_dir(report_dir)
        cls.__create_html_file(quality_report, report_dir)
        cls.__create_dependency_graph(quality_report, report_dir)
        cls.__create_metrics_graph(quality_report, report_dir)
        cls.__create_resources(report_dir)
        cls.__create_trend_images(quality_report, report_dir)

    @classmethod
    def __create_html_file(cls, quality_report, report_dir):
        """ Create the html file with the report. """
        tmp_filename = os.path.join(report_dir, 'tmp.html')
        latest_software_version = cls.__latest_software_version()
        cls.__format_and_write_report(quality_report, formatting.HTMLFormatter, tmp_filename, 'w', 'utf-8',
                                      latest_software_version=latest_software_version,
                                      current_software_version=VERSION)
        html_filename = os.path.join(report_dir, 'index.html')
        if os.path.exists(html_filename):
            os.remove(html_filename)
        os.rename(tmp_filename, html_filename)
        filesystem.make_file_readable(html_filename)

    @classmethod
    def __create_dependency_graph(cls, quality_report, report_dir):
        """ Create and write the dependency graph. """
        cls.__create_graph(quality_report, report_dir, formatting.DependencyFormatter, 'dependency')

    @classmethod
    def __create_metrics_graph(cls, quality_report, report_dir):
        """ Create and write the metrics graph. """
        cls.__create_graph(quality_report, report_dir, formatting.MetricClassesFormatter, 'metric_classes')

    @classmethod
    def __create_graph(cls, quality_report, report_dir, formatter, filename):
        """ Create and write a graph using the passed formatter. """
        dot_filename = os.path.join(report_dir, filename + '.dot')
        cls.__format_and_write_report(quality_report, formatter, dot_filename, 'w', 'ascii')
        svg_filename = os.path.join(report_dir, filename + '.svg')
        os.system('dot -Tsvg %s > %s' % (dot_filename, svg_filename))
        filesystem.make_file_readable(svg_filename)

    @staticmethod
    def __create_resources(report_dir):
        """ Create and write the resources. """
        resource_manager = pkg_resources.ResourceManager()
        formatting_module = formatting.html_formatter.__name__
        for resource_type, encoding in (('css', 'utf-8'), ('img', None), ('js', 'utf-8')):
            resource_dir = os.path.join(report_dir, resource_type)
            filesystem.create_dir(resource_dir)
            for resource in resource_manager.resource_listdir(formatting_module, resource_type):
                filename = os.path.join(resource_dir, resource)
                contents = resource_manager.resource_string(formatting_module, resource_type + '/' + resource)
                mode = 'w' if encoding else 'wb'
                filesystem.write_file(contents, filename, mode, encoding)

    @classmethod
    def __create_trend_images(cls, quality_report, report_dir):
        """ Retrieve and write the trend images. """
        for metric in quality_report.metrics():
            if metric.product_version_type() in ('tag', 'release'):
                continue
            try:
                history = ','.join([str(value) for value in metric.recent_history()])
            except ValueError:
                history = ''
            y_axis_range = cls.__format_y_axis_range(metric.y_axis_range())
            url = "http://chart.apis.google.com/chart?" \
                  "chs=100x25&cht=ls&chf=bg,s,00000000&chd=t:{history}&" \
                  "chds={y_axis_range}".format(history=history, y_axis_range=y_axis_range)
            try:
                image = urllib2.urlopen(url).read()
            except urllib2.URLError as reason:
                logging.warn("Couldn't open %s history chart at %s: %s", metric.id_string(), url, reason)
                image = cls.EMPTY_HISTORY_PNG
            filename = os.path.join(report_dir, 'img', '%s.png' % metric.id_string())
            filesystem.write_file(image, filename, mode='wb', encoding=None)

    @staticmethod
    def __format_and_write_report(quality_report, report_formatter, filename, mode, encoding, **kwargs):
        """ Format the report using the formatter and write it to the specified file. """
        formatted_report = report_formatter(**kwargs).process(quality_report)
        filesystem.write_file(formatted_report, filename, mode, encoding)

    @staticmethod
    def __latest_software_version():
        """ Return the latest released version of the quality report software. """
        python_package_index_url = 'https://pypi.python.org/pypi'
        client = xmlrpclib.ServerProxy(python_package_index_url)
        try:
            latest_version = max(client.package_releases('quality_report'))
        except (socket.gaierror, xmlrpclib.ProtocolError) as reason:
            logging.warn("Can't create connection to %s: %s", python_package_index_url, reason)
            return '0'

        logging.info('Latest quality_report package release is %s', latest_version)
        return latest_version

    @staticmethod
    def __format_y_axis_range(y_axis_range):
        """ Return the y axis range parameter for the Google sparkline graph. """
        return '%d,%d' % y_axis_range if y_axis_range else 'a'


if __name__ == '__main__':
    # pylint: disable=invalid-name
    args = commandlineargs.parse()
    log.init_logging(args.log)
    Reporter(args.project).create_report(args.report)
