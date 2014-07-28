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

from qualitylib.formatting import base_formatter
import logging


class JSONFormatter(base_formatter.Formatter):
    ''' Format the report in JSON. This is used for generating a history
        file. '''

    def prefix(self, report):
        ''' Return a JSON formatted version of the report prefix. '''
        prefix_elements = []
        # Add the product versions of trunk versions to the prefix
        for product in report.products():
            if not product.product_version():
                prefix_elements.append('"%s-version": "%s"' % (product.sonar_id(),
                                       report.latest_product_version(product)))
        # Add the current date to the prefix
        prefix_elements.append('"date": "%s"' % \
                               report.date().strftime('%Y-%m-%d %H:%M:%S'))
        return '{' + ', '.join(prefix_elements) + ', '

    @staticmethod
    def sections(report):
        ''' Only return sections that describe trunk versions of products or
            that don't describe products. We ignore sections that describe
            tagged products, since tagged products don't have a history that
            needs to be written to the JSON file. '''
        return [section for section in report.sections() if \
                not section.product() or section.contains_trunk_product()]

    def metric(self, metric):
        ''' Return a JSON formatted version of the metric. '''
        # Write numerical values without decimals.
        logging.info('Formatting metric %s.', metric.stable_id())
        try:
            return '"%s": ("%.0f", "%s", "%s"), ' % (metric.stable_id(), 
                                                     metric.numerical_value(),
                                                     metric.status(),
                                                     metric.status_start_date())
        except TypeError:
            logging.error('Error formatting %s', metric.stable_id())
            raise

    @staticmethod
    def postfix():
        ''' Return a JSON formatted version of the report postfix. '''
        return '}\n'
