"""
Copyright 2012-2018 Ministerie van Sociale Zaken en Werkgelegenheid

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

import unittest

from hqlib import domain
from hqlib import requirement


class DocumentTest(unittest.TestCase):
    """ Unit tests for the Document domain class. """
    def setUp(self):
        self.__document = domain.Document(name='Document name')

    def test_name(self):
        """ Test the name of the document. """
        self.assertEqual('Document name', self.__document.name())

    def test_str(self):
        """ Test that the string formatting of a document equals the document name. """
        self.assertEqual('document_name', str(self.__document))

    def test_optional_requirements(self):
        """ Test optional requirements. """
        self.assertEqual((requirement.TrackSecurityTestDate,), self.__document.optional_requirements())

    def test_default_requirements(self):
        """ Test default requirements. """
        self.assertEqual((requirement.TrackDocumentAge,), self.__document.default_requirements())
