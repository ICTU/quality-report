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

import io
import unittest

from qualitylib.metric_source import Sonar, Maven
from qualitylib.metric_source import VersionControlSystem
from qualitylib.metric_source.sonar_runner import SonarRunner


class FakeSonar(Sonar):  # pylint: disable=too-few-public-methods
    """ Override Sonar to return a fake JSON string. """
    @staticmethod
    def url_open(*args, **kwargs):  # pylint: disable=unused-argument
        """ Return a fake JSON string. """
        return io.StringIO(u'{}')


class FakeVCS(VersionControlSystem):  # pylint: disable=too-few-public-methods
    """ Fake a VCS for testing purposes. """
    @staticmethod
    def check_out(*args):
        """ Fake check out. """
        pass


class FakeProduct(object):  # pylint: disable=too-few-public-methods
    """ Fake a product. """
    @staticmethod
    def product_label():
        """ Return the product label. """
        return 'fakeproduct'

    @staticmethod
    def product_version(*args):  # pylint: disable=unused-argument
        """ Return the product version. """
        return

    @staticmethod
    def metric_source_id(*args):  # pylint: disable=unused-argument
        """ Return the Sonar id. """
        return 'a:b'

    @staticmethod
    def users():
        """ Return the users of this product. """
        return set()

    jsf = unittests = product_branch = product_branch_id = old_metric_source_id = metric_source_options = \
        product_version


class SonarRunnerTest(unittest.TestCase):
    """ Unit tests for the Sonar runner that creates and deletes Sonar analyses. """

    def setUp(self):
        self.__runner = SonarRunner(FakeSonar('http://sonar/'), Maven(), FakeVCS())

    def test_analyse_no_products(self):
        """ Test that the runner does nothing when analysing an empty set of products. """
        self.__runner.analyse_products(set())

    def test_analyse_one_trunk_product(self):
        """ Test that the runner does nothing when analysing a trunk product. """
        self.__runner.analyse_products([FakeProduct()])
