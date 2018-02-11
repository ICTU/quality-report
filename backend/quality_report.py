#!/usr/bin/env python
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

# Python script to retrieve metrics from different back-end systems, like Sonar and Jenkins.

import logging
import os
import sys
import pygal

import pkg_resources

from hqlib import app, formatting, commandlineargs, report, metric_source, log, filesystem, configuration, \
    NAME, VERSION


class Reporter(object):  # pylint: disable=too-few-public-methods
    """ Class for creating the quality report for a specific project. """
    def __init__(self, project_folder_or_filename):
        self.__project = configuration.project(project_folder_or_filename)

    def create_report(self, report_folder):
        """ Create, format, and write the quality report. """
        quality_report = report.QualityReport(self.__project)
        for history in self.__project.metric_sources(metric_source.History):
            if history.filename():
                history.add_report(quality_report)
        self.__create_report(quality_report, report_folder)
        return quality_report

    @classmethod
    def __create_report(cls, quality_report, report_dir):
        """ Format the quality report to HTML and write the files in the report folder. """
        report_dir = report_dir or '.'
        filesystem.create_dir(report_dir)
        filesystem.create_dir(os.path.join(report_dir, 'json'))
        cls.__create_resources(report_dir)
        json_files = dict(metrics=formatting.MetricsFormatter,
                          meta_history=formatting.MetaMetricsHistoryFormatter,
                          meta_data=formatting.MetaDataJSONFormatter)
        for filename, formatter in json_files.items():
            cls.__create_json_file(quality_report, report_dir, formatter, filename)

        cls.__create_trend_images(quality_report, report_dir)

    @classmethod
    def __create_json_file(cls, quality_report, report_dir, formatter, filename):
        """ Create the JSON file using the JSON formatter specified. """
        json_filename = os.path.join(report_dir, 'json', '{0}.json'.format(filename))
        cls.__format_and_write_report(quality_report, formatter, json_filename, 'w', 'utf-8')

    @staticmethod
    def __create_resources(report_dir):
        """ Create and write the resources. """
        resource_manager = pkg_resources.ResourceManager()
        resource_module = app.__name__
        for resource_type, encoding in (('img', None), ('dist', None), ('html', 'utf-8')):
            resource_dir = os.path.join(report_dir, resource_type) if resource_type != 'html' else report_dir
            filesystem.create_dir(resource_dir)
            for resource in resource_manager.resource_listdir(resource_module, resource_type):
                filename = os.path.join(resource_dir, resource)
                contents = resource_manager.resource_string(resource_module, resource_type + '/' + resource)
                mode = 'w' if encoding else 'wb'
                contents = contents.decode(encoding) if encoding else contents
                filesystem.write_file(contents, filename, mode, encoding)

    @classmethod
    def __create_trend_images(cls, quality_report, report_dir):
        """ Retrieve and write the trend images. """
        style = pygal.style.Style(background='transparent', plot_background='transparent')
        for metric in quality_report.metrics():
            line_chart = pygal.Line(style=style, range=metric.y_axis_range())
            line_chart.add('', metric.recent_history(), stroke_style={'width': 2})
            image = line_chart.render_sparkline()
            filename = os.path.join(report_dir, 'img', '{0!s}.svg'.format(metric.id_string()))
            filesystem.write_file(image, filename, mode='wb', encoding=None)

    @staticmethod
    def __format_and_write_report(quality_report, report_formatter, filename, mode, encoding, **kwargs):
        """ Format the report using the formatter and write it to the specified file. """
        formatted_report = report_formatter(**kwargs).process(quality_report)
        filesystem.write_file(formatted_report, filename, mode, encoding)


if __name__ == '__main__':
    # pylint: disable=invalid-name
    args = commandlineargs.parse()
    log.init_logging(args.log)
    logging.info("%s v%s starting quality report", NAME, VERSION)
    report = Reporter(args.project).create_report(args.report)
    logging.info("%s v%s done with quality report", NAME, VERSION)
    sys.exit(2 if args.failure_exit_code and report.direct_action_needed() else 0)
