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

# Fake report and section classes for testing purposes.

import datetime

from hqlib import metric, metric_source, requirement, domain

from . import fake_domain


class Section(object):
    """ Fake a report section. """
    def __init__(self, product=None):
        self.__product = product or fake_domain.Product()

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

    def __init__(self, products=None, metrics=None):
        self.__products = products or []
        self.__metrics = metrics or []
        self.__meta_metrics = [fake_domain.Metric('MM-{0}'.format(nr)) for nr in range(1, 5)]

    @staticmethod
    def domain_object_classes():
        """ Return the set of domain object classes the report can report on. """
        return {domain.Project, domain.Product, domain.Document, domain.Team}

    included_domain_object_classes = domain_object_classes

    @staticmethod
    def requirement_classes():
        """ Return the requirement classes the report can report on. """
        return {requirement.ART, requirement.ARTCoverage}

    @staticmethod
    def included_requirement_classes():
        """ Return the requirement classes actually included in the report. """
        return {requirement.ARTCoverage}

    @staticmethod
    def metric_classes():
        """ Return a list of metric classes that the report can report on. """
        return [metric.ARTStatementCoverage]

    @staticmethod
    def metric_source_classes():
        """ Return a list of metric source classes that the report can use. """
        return [metric_source.Git]

    def included_metric_classes(self):
        """ Return the metric classes included in the report. """
        return {each_metric.__class__ for each_metric in self.__metrics + self.__meta_metrics}

    @staticmethod
    def included_metric_source_classes():
        """ Return the metric source classes added to the project. """
        return [metric_source.Git]

    def products(self):
        """ Return the products in the report. """
        return self.__products

    def get_section(self, section_id):  # pylint: disable=unused-argument
        """ Return a fake section. """
        return self.get_meta_section()

    def get_product_section(self, product_label):  # pylint: disable=unused-argument
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

    @staticmethod
    def dashboard():
        """ Return the columns and rows of the dashboard. """
        return [('ME', 1)], [(('id', 'lightsteelblue'),), ]

    @staticmethod
    def project():
        """ Return the project. """
        # pylint: disable=too-few-public-methods,unused-argument
        class FakeProject(object):
            """ Fake a project. """
            @staticmethod
            def metric_source(metric_source_class):
                """ Return the metric source instances for a metric source class. """
                class FakeGit(object):
                    """ Fake a Git repository. """
                    @staticmethod
                    def url():
                        """ Return the url of Git. """
                        return 'http://git/'

                class FakeHistory(object):
                    """ Fake the measurement history. """
                    @staticmethod
                    def statuses():
                        """ Return the statuses. """
                        return [{'green': 1, 'date': '2012-04-05 16:16:58', 'red': 1}]

                class FakeSonar(object):
                    """ Fake Sonar for unit testing purposes. """
                    @staticmethod
                    def version(*args):
                        """ Return the version number of the component. """
                        return '2'

                if metric_source_class == metric_source.History:
                    return FakeHistory()
                elif metric_source_class == metric_source.Sonar:
                    return FakeSonar()
                else:
                    return [FakeGit()]

        return FakeProject()

    def get_meta_section(self):
        """ Return the meta section of the report. """
        return Section(self.__meta_metrics)
