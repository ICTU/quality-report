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

import logging

from . import base_formatter
from .. import metric_info


class JSONFormatter(base_formatter.Formatter):
    """ Format the report in JSON. This is used for generating a history file. """

    def __init__(self, *args, **kwargs):
        self.__sonar = kwargs.pop('sonar')
        super(JSONFormatter, self).__init__(*args, **kwargs)

    def prefix(self, report):
        """ Return a JSON formatted version of the report prefix. """
        prefix_elements = []
        # Add the product versions of trunk versions to the prefix
        for product in report.products():
            if not product.product_version():
                sonar_product_info = metric_info.SonarProductInfo(self.__sonar, product)
                sonar_id = sonar_product_info.sonar_id()
                latest_version = sonar_product_info.latest_version()
                prefix_elements.append('"{sonar_id}-version": "{version}"'.format(sonar_id=sonar_id,
                                                                                  version=latest_version))
        # Add the current date to the prefix
        prefix_elements.append('"date": "{date}"'.format(date=report.date().strftime('%Y-%m-%d %H:%M:%S')))
        return '{' + ', '.join(prefix_elements) + ', '

    @staticmethod
    def sections(report):
        """ Only return sections that describe trunk versions of products or that don't describe products.
            We ignore sections that describe tagged products, since tagged products don't have a history that
            needs to be written to the JSON file. """
        return [section for section in report.sections() if not section.product() or section.contains_trunk_product()]

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
