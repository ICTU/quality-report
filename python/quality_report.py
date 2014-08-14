#!/usr/bin/env python
'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

# Python script to retrieve metrics from different back-end systems,
# like Sonar and Jenkins.


from qualitylib import formatting, commandlineargs, report, metric_source, \
    log, VERSION
import import_file
import codecs
import logging
import os
import stat
import pkg_resources
import xmlrpclib
import socket
import urllib2


class Reporter(object):  # pylint: disable=too-few-public-methods
    ''' Class for creating the quality report for a specific project. '''

    PROJECT_DEFINITION_FILENAME = 'project_definition.py'
    HISTORY_FILENAME = 'history.json'
    CSV_FILENAME = 'summary.csv'

    def __init__(self, project_folder):
        project_definition_filename = os.path.join(project_folder,
                                           self.PROJECT_DEFINITION_FILENAME)
        project_module = import_file.import_file(project_definition_filename)
        self.__project = project_module.PROJECT
        self.__history_filename = os.path.join(project_folder, 
                                               self.HISTORY_FILENAME)
        self.__csv_filename = os.path.join(project_folder, self.CSV_FILENAME)

    def create_report(self, report_folder):
        ''' Create, format, and write the quality report. '''
        self.__add_latest_release_of_products()
        self.__add_release_candidates_of_products()
        self.__add_dependencies()
        self.__analyse_products()

        quality_report = report.QualityReport(self.__project)
        self.__format_and_write_report(quality_report, formatting.JSONFormatter,
                                       self.__history_filename, 'a', 'ascii')
        if os.path.exists(self.__csv_filename):
            self.__format_and_write_report(quality_report,
                                           formatting.CSVFormatter,
                                           self.__csv_filename, 'a', 'ascii')
        self.__format_and_write_html_report(quality_report, report_folder)
        metric_source.History(self.__history_filename).clean_history()

    def __add_latest_release_of_products(self):
        ''' Add the latest released version of each product. '''
        for product in self.__project.products()[:]:
            latest_version = product.latest_released_product_version()
            if latest_version:
                logging.info('Adding %s:%s to the project because it is the ' \
                         'latest version.', product.name(), latest_version)
                self.__project.add_product_with_version(product.name(),
                                                        latest_version)

    def __add_release_candidates_of_products(self):
        ''' Add the versions of the products that are scheduled to be released 
            to operations. '''
        for product in self.__project.products()[:]:
            release_candidate = product.release_candidate()
            if release_candidate:
                logging.info('Adding %s:%s to the project because it is a ' \
                         'release candidate.', product.name(), 
                         release_candidate)
                self.__project.add_product_with_version(product.name(),
                                                        release_candidate)

    def __add_dependencies(self):
        ''' Add product versions that other products depend on. '''
        for name, version in self.__project.product_dependencies():
            logging.info('Adding %s:%s to the project because it is a ' \
                         'dependency.', name, version)
            self.__project.add_product_with_version(name, version)

    def __analyse_products(self):
        ''' Make sure Sonar contains the right analysis projects. '''
        sonar = self.__project.metric_source(metric_source.Sonar)
        if sonar:
            sonar.analyse_products(self.__project.products())

    def __format_and_write_html_report(self, quality_report, report_dir):
        ''' Format the quality report to HTML and write the files in the report
            folder. '''
        report_dir = report_dir or '.'
        self.__create_dir(report_dir)
        # HTML file
        tmp_filename = os.path.join(report_dir, 'tmp.html')
        latest_software_version = self.__latest_software_version()
        self.__format_and_write_report(quality_report, formatting.HTMLFormatter,
            tmp_filename, 'w', 'utf-8',
            latest_software_version=latest_software_version,
            current_software_version=VERSION)
        html_filename = os.path.join(report_dir, 'index.html')
        if os.path.exists(html_filename):
            os.remove(html_filename)
        os.rename(tmp_filename, html_filename)
        # Dependency graph
        dot_filename = os.path.join(report_dir, 'dependency.dot')
        self.__format_and_write_report(quality_report, formatting.DotFormatter,
                                       dot_filename, 'w', 'ascii')
        svg_filename = os.path.join(report_dir, 'dependency.svg')
        os.system('dot -Tsvg %s > %s' % (dot_filename, svg_filename))
        for filename in (html_filename, svg_filename):
            os.chmod(filename, stat.S_IWUSR | stat.S_IRUSR | stat.S_IRGRP | \
                     stat.S_IROTH)
        # Resources
        resource_manager = pkg_resources.ResourceManager()
        formatting_module = formatting.html_formatter.__name__
        for resource_type, encoding in (('css', 'utf-8'), ('img', None), 
                                        ('js', 'utf-8')):
            resource_dir = os.path.join(report_dir, resource_type)
            self.__create_dir(resource_dir)
            for resource in resource_manager.resource_listdir(formatting_module,
                                                              resource_type):
                filename = os.path.join(resource_dir, resource)
                contents = resource_manager.resource_string(formatting_module,
                                                resource_type + '/' + resource)
                mode = 'w' if encoding else 'wb'
                self.__write_file(contents, filename, mode, encoding)
        # Trend images
        for metric in quality_report.metrics():
            if metric.product_version_type() in ('tag', 'release'):
                continue
            try:
                history = ','.join([str(value) for value in metric.recent_history()])
            except ValueError:
                history = ''
            y_axis_range = self.__format_y_axis_range(metric.y_axis_range())
            url = "http://chart.apis.google.com/chart?" \
                  "chs=100x25&cht=ls&chf=bg,s,00000000&chd=t:%(history)s&" \
                  "chds=%(y_axis_range)s" % dict(history=history, 
                                                 y_axis_range=y_axis_range)
            logging.info('Getting %s history chart: %s', metric.id_string(),
                         url)
            image = urllib2.urlopen(url).read()
            filename = os.path.join(report_dir, 'img', 
                                    '%s.png' % metric.id_string())
            self.__write_file(image, filename, mode='wb', encoding=None)

    @classmethod
    def __format_and_write_report(cls, quality_report, report_formatter,
                                  filename, mode, encoding, **kwargs):
        ''' Format the report using the formatter and write it to the specified
            file. '''
        formatted_report = report_formatter(**kwargs).process(quality_report)
        cls.__write_file(formatted_report, filename, mode, encoding)

    @staticmethod
    def __write_file(contents, filename, mode, encoding):
        ''' Write the contents to the specified file. '''
        if os.path.exists(filename):
            os.chmod(filename, stat.S_IWUSR | stat.S_IRUSR | stat.S_IRGRP | \
                     stat.S_IROTH)
        output_file = codecs.open(filename, mode, encoding)
        output_file.write(contents)
        output_file.close()
        os.chmod(filename, stat.S_IWUSR | stat.S_IRUSR | stat.S_IRGRP | \
                 stat.S_IROTH)

    @staticmethod
    def __create_dir(dir_name):
        ''' Create a directory and make it accessible. '''
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        os.chmod(dir_name, stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH | \
                 stat.S_IRUSR | stat.S_IWUSR)

    @staticmethod
    def __latest_software_version():
        ''' Return the latest released version of the quality report
            software. '''
        python_package_index_url = 'https://pypi.python.org/pypi'
        client = xmlrpclib.ServerProxy(python_package_index_url)
        try:
            latest_version = max(client.package_releases('quality_report'))
        except socket.gaierror, reason:
            logging.warn("Can't create connection to %s: %s",
                         python_package_index_url, reason)
            return '0'
        logging.info('Latest quality_report package release is %s',
                     latest_version)
        return latest_version

    @staticmethod
    def __format_y_axis_range(y_axis_range):
        ''' Return the y axis range parameter for the Google sparkline
            graph. '''
        return '%d,%d' % y_axis_range if y_axis_range else 'a'


if __name__ == '__main__':
    # pylint: disable=invalid-name
    args = commandlineargs.parse()
    log.init_logging(args.log)
    Reporter(args.project).create_report(args.report)
