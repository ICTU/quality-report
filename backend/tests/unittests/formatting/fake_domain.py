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

# Fake domain classes for testing purposes.

import datetime


class Product(object):  # pylint: disable=too-few-public-methods
    """ Fake the product domain class. """
    def __init__(self, dependencies=False):
        self.__dependencies = dependencies

    @staticmethod
    def metric_source_id(*args):  # pylint: disable=unused-argument
        """ Return the Sonar id of the product. """
        return 'Product'


class Metric(object):
    """ Fake a metric class. """
    url_label_text = 'label'
    comment_url_label_text = ''

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
        return 'Comment with \\backslash'

    @staticmethod
    def comment_urls():
        """ Return the urls for the comment. """
        return {}
