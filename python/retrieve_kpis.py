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


Python script to retrieve metrics from different back-end systems,
like Sonar and Jenkins.
'''

from qualitylib import formatting, commandlineargs, report, metric_source, log
import import_file
import codecs
import logging


class Reporter(object):  # pylint: disable=too-few-public-methods
    ''' Class for creating the quality report for a specific project. '''
    def __init__(self, project_module):
        self.__project = project_module.PROJECT

    def create_report(self, json_filename, html_filename, dot_filename):
        ''' Create, format, and write the quality report. '''
        self.__add_latest_release_of_products()
        self.__add_release_candidates_of_products()
        self.__add_dependencies()
        self.__project.analyse_products()

        quality_report = report.QualityReport(self.__project)
        formats = [(json_filename, formatting.JSONFormatter, 'a', 'ascii'),
                   (html_filename, formatting.HTMLFormatter, 'w', 'utf-8'),
                   (dot_filename, formatting.DotFormatter, 'w', 'ascii')]
        for filename, formatter_class, mode, encoding in formats:
            if filename:
                self.__format_and_write_report(quality_report, formatter_class,
                                               filename, mode, encoding)
        if json_filename:
            metric_source.History(json_filename).clean_history()

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

    @staticmethod
    def __format_and_write_report(quality_report, report_formatter,
                                  filename, mode, encoding):
        ''' Format the report using the formatter and write it to the specified
            file. '''
        formatted_report = report_formatter().process(quality_report)
        output_file = codecs.open(filename, mode, encoding)
        output_file.write(formatted_report)
        output_file.close()


if __name__ == '__main__':
    # pylint: disable=invalid-name
    args = commandlineargs.parse()
    log.init_logging(args.log)
    project_definition_module = import_file.import_file(args.project)
    Reporter(project_definition_module).create_report(args.json, args.html, 
                                                      args.dot)
