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

# Fake report and section classes for testing purposes.

import datetime

from qualitylib import metric
from unittests.formatting import fake_domain


class Section(object):
    """ Fake a report section. """
    def __init__(self, metrics=None, product=None):
        self.__metrics = metrics or []
        self.__product = product or fake_domain.Product()

    def metrics(self):
        """ Return the metrics in this section. """
        return self.__metrics

    def product(self):
        """ Return product of this section. """
        return self.__product

    @staticmethod
    def contains_trunk_product():
        """ Return whether the product of the section is a trunk version. """
        return True

    @staticmethod
    def history():
        """ Return the history of this section. """
        return [{'GreyMetaMetric': 0, 'GreenMetaMetric': '94',
                 'YellowMetaMetric': 0, 'date': '2012-04-05 16:16:58',
                 'RedMetaMetric': '1', 'metric_id': '0'},
                {'GreenMetaMetric': '94',
                 'date': '2012-04-05 17:16:58',
                 'RedMetaMetric': '1', 'metric_id': '0'}]

    @staticmethod
    def color():
        """ Return an arbitrary color. """
        return 'green'

    @staticmethod
    def title():
        """ Return the title of the section. """
        return 'Section title'

    @staticmethod
    def subtitle():
        """ Return the subtitle of the section. """
        return 'Section subtitle'

    @staticmethod
    def id_prefix():
        """ Return the id prefix of the section. """
        return 'id'

    def __getitem__(self, index):
        if index < 2:
            return fake_domain.Metric()
        else:
            raise IndexError


class Report(object):
    """ Fake a quality report. """

    def __init__(self, products=None, metrics=None, teams=None, number_of_meta_metrics=5, project_metric_sources=None):
        self.__products = products or []
        self.__metrics = metrics or []
        self.__teams = teams or []
        self.__meta_metrics = [fake_domain.Metric('MM-%d' % nr) for nr in range(1, number_of_meta_metrics)]
        self.project_metric_sources = project_metric_sources or dict()

    @classmethod
    def metric_classes(cls):
        """ Return a list of metric classes that the report can report on. """
        return [metric.ARTStatementCoverage]

    def products(self):
        """ Return the products in the report. """
        return self.__products

    @staticmethod
    def get_product(name, version):  # pylint: disable=unused-argument
        """ Return a fake product. """
        return fake_domain.Product()

    def get_section(self, section_id):  # pylint: disable=unused-argument
        """ Return a fake section. """
        return self.get_meta_section()

    def get_product_section(self, product_label):
        # pylint: disable=unused-argument
        """ Return a fake section. """
        return Section(product=self.__products[0]) if self.__products else Section()

    @staticmethod
    def title():
        """ Return the title of the report. """
        return 'Report title'

    @staticmethod
    def date():
        """ Return the date of the report. """
        return datetime.datetime(2012, 1, 1, 12, 0, 0)

    def sections(self):
        """ Return a list of report sections. """
        return [self.get_product_section('whatever:1.0')]

    def metrics(self):
        """ Return the metrics in the report. """
        return self.__metrics + self.__meta_metrics

    @staticmethod
    def dashboard():
        """ Return the columns and rows of the dashboard. """
        return [('ME', 1)], [(('id', 'lightsteelblue'),), ]

    def project(self):
        """ Return the project resources. """
        class FakeProject(object):  # pylint: disable=too-few-public-methods
            """ Fake a project. """
            @staticmethod
            def project_resources():
                """ Return the project's resources. """
                return [('resource', 'url'), ('missing', None)]

            @staticmethod
            def metric_source(metric_source_class):
                # pylint: disable=unused-argument
                """ Return the metric source for the given metric source
                    class. """
                return self.project_metric_sources.get(metric_source_class, None)

        return FakeProject()

    def get_meta_section(self):
        """ Return the meta section of the report. """
        return Section(self.__meta_metrics)
