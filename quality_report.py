#!/usr/bin/env python
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

# Python script to retrieve metrics from different back-end systems, like Sonar and Jenkins.

import logging
import os
import sys
import urllib.request

import pkg_resources

from hqlib import app, formatting, commandlineargs, report, metric_source, log, filesystem, configuration


class Reporter(object):  # pylint: disable=too-few-public-methods
    """ Class for creating the quality report for a specific project. """

    EMPTY_HISTORY_PNG = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00d\x00\x00\x00\x19\x08\x06\x00\x00\x00" \
                        b"\xc7^\x8bK\x00\x00\x00\x06bKGD\x00\xff\x00\xff\x00\xff\xa0\xbd\xa7\x93\x00\x00\x00 " \
                        b"IDATh\x81\xed\xc1\x01\r\x00\x00\x00\xc2\xa0\xf7Om\x0f\x07\x14\x00\x00\x00\x00\x00\x00" \
                        b"\x00\x00\x00\x1c\x1b')\x00\x01\xbca\xfe\x1a\x00\x00\x00\x00IEND\xaeB`\x82"

    def __init__(self, project_folder_or_filename):
        self.__project = configuration.Configuration.project(project_folder_or_filename)

    def create_report(self, report_folder):
        """ Create, format, and write the quality report. """
        quality_report = report.QualityReport(self.__project)
        history_filename = self.__project.metric_source(metric_source.History).filename()
        if history_filename:
            self.__format_and_write_report(quality_report, formatting.JSONFormatter, history_filename, 'a', 'ascii')
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
        for metric in quality_report.metrics():
            try:
                history = ','.join([str(value) for value in metric.recent_history()])
            except ValueError:
                history = ''
            y_axis_range = cls.__format_y_axis_range(metric.y_axis_range())
            url = "http://chart.apis.google.com/chart?" \
                  "chs=100x25&cht=ls&chf=bg,s,00000000&chd=t:{history}&" \
                  "chds={y_axis_range}".format(history=history, y_axis_range=y_axis_range)
            try:
                image = urllib.request.urlopen(url).read()
            except metric_source.UrlOpener.url_open_exceptions as reason:
                logging.warning("Couldn't open %s history chart at %s: %s", metric.id_string(), url, reason)
                image = cls.EMPTY_HISTORY_PNG
            filename = os.path.join(report_dir, 'img', '{0!s}.png'.format(metric.id_string()))
            filesystem.write_file(image, filename, mode='wb', encoding=None)

    @staticmethod
    def __format_and_write_report(quality_report, report_formatter, filename, mode, encoding, **kwargs):
        """ Format the report using the formatter and write it to the specified file. """
        formatted_report = report_formatter(**kwargs).process(quality_report)
        filesystem.write_file(formatted_report, filename, mode, encoding)

    @staticmethod
    def __format_y_axis_range(y_axis_range):
        """ Return the y axis range parameter for the Google sparkline graph. """
        return '{0:d},{1:d}'.format(*y_axis_range) if y_axis_range else 'a'


if __name__ == '__main__':
    # pylint: disable=invalid-name
    args = commandlineargs.parse()
    log.init_logging(args.log)
    report = Reporter(args.project).create_report(args.report)
    sys.exit(2 if args.failure_exit_code and report.direct_action_needed() else 0)
