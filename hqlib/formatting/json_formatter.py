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
from __future__ import absolute_import

import logging
import re

from . import base_formatter
from .. import metric_source


class JSONFormatter(base_formatter.Formatter):
    """ Format the report in JSON. This is used for generating a history file. """

    def prefix(self, report):
        """ Return a JSON formatted version of the report prefix. """
        prefix_elements = []
        # Add the product versions of trunk versions to the prefix
        sonar = report.project().metric_source(metric_source.Sonar)
        for product in report.products():
            sonar_id = product.metric_source_id(sonar) or ''
            latest_version = sonar.version(sonar_id) if sonar_id else ''
            prefix_elements.append('"{sonar_id}-version": "{version}"'.format(sonar_id=sonar_id,
                                                                              version=latest_version))
        # Add the current date to the prefix
        prefix_elements.append('"date": "{date}"'.format(date=report.date().strftime('%Y-%m-%d %H:%M:%S')))
        return '{' + ', '.join(prefix_elements) + ', '

    def metric(self, metric):
        """ Return a JSON formatted version of the metric. """
        # Write numerical values without decimals.
        logging.info('Formatting metric %s.', metric.stable_id())
        try:
            return '"{sid}": ("{val:.0f}", "{stat}", "{date}"), '.format(sid=metric.stable_id(),
                                                                         val=metric.numerical_value(),
                                                                         stat=metric.status(),
                                                                         date=metric.status_start_date())
        except ValueError:
            logging.error('Error formatting %s', metric.stable_id())
            raise

    @staticmethod
    def postfix():
        """ Return a JSON formatted version of the report postfix. """
        return '}\n'


class MetaMetricsHistoryFormatter(base_formatter.Formatter):
    """ Format the history of the meta metrics as a Javascript array. """

    def prefix(self, report):
        return '['

    @staticmethod
    def postfix():
        return ']\n'

    def metric(self, metric):
        return ''

    def body(self, report):
        """ Return a JSON array of dates and status counts. """
        history_table = []
        history = report.project().metric_source(metric_source.History)
        if history:
            for status_record in history.statuses():
                date_and_time = '[{0}, {1}, {2}, {3}, {4}, {5}]'.format(*self.__date_and_time(status_record))
                counts = '[{0}, {1}, {2}, {3}, {4}, {5}, {6}]'.format(*self.__status_record_counts(status_record))
                history_table.append('[{0}, {1}]'.format(date_and_time, counts))
        return ',\n'.join(history_table)

    @staticmethod
    def __date_and_time(history_record):
        """ Return the date and time of the history record. Remove leading zero from date/time elements (assuming all
            elements are 2 digits long). Turn month into zero-based value for usage within Javascript. """
        year, month, day, hour, minute, second = re.split(r' 0?|:0?|-0?|\.0?', history_record['date'])[:6]
        month = str(int(month) - 1)  # Months are zero based
        return year, month, day, hour, minute, second

    @staticmethod
    def __status_record_counts(history_record, statuses=('perfect', 'green', 'red', 'yellow', 'grey',
                                                         'missing', 'missing_source')):
        """ Return the counts per measurement status in the history record. """
        return tuple(history_record.get(status, 0) for status in statuses)
