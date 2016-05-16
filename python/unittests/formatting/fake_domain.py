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

# Fake domain classes for testing purposes.

import datetime

from qualitylib import domain


class Product(object):
    """ Fake the product domain class. """
    def __init__(self, dependencies=False, version='1', is_release_candidate=False, is_latest_release=False):
        self.__dependencies = dependencies
        self.__branch = ''
        self.__version = version
        self.__is_release_candidate = is_release_candidate
        self.__is_latest_release = is_latest_release

    @staticmethod
    def old_metric_source_id(*args):  # pylint: disable=unused-argument
        """ Return the old Sonar id of the product. """
        return ''

    @staticmethod
    def metric_source_id(*args):  # pylint: disable=unused-argument
        """ Return the Sonar id of the product. """
        return 'Product'

    @staticmethod
    def name():
        """ Return the name of the product. """
        return 'Fake Product'

    @staticmethod
    def short_name():
        """ Return the short version of the name of the product. """
        return 'FP'

    def product_branch(self):
        """ Return the branch of the product. """
        return self.__branch

    def product_version(self):
        """ Return the version of the product. """
        return self.__version

    def product_label(self):
        """ Return the label of the product. """
        return self.name() + ':' + self.branch_version_label()

    def branch_version_label(self):
        """ Return the branch and/or version. """
        return self.product_version() or 'trunk'

    def dependencies(self, recursive=False):  # pylint: disable=unused-argument
        """ Return a list of dependencies of the product. """
        return [('Fake Dependency', 1)] if self.__dependencies else []

    @staticmethod
    def users(recursive=False):  # pylint: disable=unused-argument
        """ Return a list of users of the product. """
        return []

    def is_latest_release(self):
        """ Return whether this product version is the latest release. """
        return self.__is_latest_release

    def is_release_candidate(self):
        """ Return whether this product version is a release candidate. """
        return self.__is_release_candidate


class Metric(object):
    """ Fake a metric class. """
    quality_attribute = domain.QualityAttribute('quality', name='Quality')

    def __init__(self, id_string='id_string-1', status_start_date=datetime.datetime(2012, 1, 1, 12, 0, 0)):
        self.__id_string = id_string
        self.__status_start_date = status_start_date

    @staticmethod
    def stable_id():
        """ Return the stable id of the metric. """
        return 'metric_id'

    def id_string(self):
        """ Return the id string of the metric. """
        return self.__id_string

    @staticmethod
    def numerical_value():
        """ Return the numerical value of the metric. """
        return 15

    @staticmethod
    def status():
        """ Return the status of the metric. """
        return 'red'

    def status_start_date(self):
        """ Return the start date of the current status. """
        return self.__status_start_date

    @staticmethod
    def url():
        """ Return the url of the metric. """
        return dict(anchor='http://url')

    @staticmethod
    def url_label():
        """ Return the label for the urls. """
        return ''

    @staticmethod
    def report():
        """ Return the report of the metric. """
        return 'report'

    @staticmethod
    def norm():
        """ Return the norm of the metric. """
        return 'norm'

    @staticmethod
    def comment():
        """ Return the comment for the metric. """
        return ''

    @staticmethod
    def comment_urls():
        """ Return the urls for the comment. """
        return {}

    @staticmethod
    def comment_url_label():
        """ Return the label for the urls. """
        return ''

    @staticmethod
    def product_version_type():
        """ Return a fake version type. """
        return 'trunk'
