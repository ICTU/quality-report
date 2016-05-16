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

from qualitylib.metric_source import ReleaseCandidates


class ReleaseCandidatesUnderTest(ReleaseCandidates):  # pylint: disable=too-few-public-methods
    """ Override to return a fixed string from url_open. """

    def url_open(self, url):  # pylint: disable=unused-argument,no-self-use
        """ Return the static contents. """
        return io.StringIO(u'buildnr_product1=1.0\nproduct2=2.0')


class ReleaseCandidatesTest(unittest.TestCase):
    """ Unit tests for the release candidates metric source. """

    def setUp(self):
        self.__release_candidates = ReleaseCandidatesUnderTest('http://url')

    def test_url(self):
        """ Test the url. """
        self.assertEqual('http://url', self.__release_candidates.url())

    def test_get_product(self):
        """ Test that a version number is returned for the product. """
        self.assertEqual('1.0', self.__release_candidates.release_candidate('product1'))

    def test_require_buildnr(self):
        """ Test that lines that don't start with 'buildnr_' are ignored. """
        self.assertEqual('', self.__release_candidates.release_candidate('product2'))

    def test_none(self):
        """ Test that no version number is returned when the product is
            none. """
        self.assertEqual('', self.__release_candidates.release_candidate(None))
