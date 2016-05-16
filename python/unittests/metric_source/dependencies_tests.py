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

import unittest

from qualitylib.metric_source import Dependencies


class FakeFile(object):
    """ Provide a fake file object so we don't need to access to the file system. """

    def __init__(self):
        self.contents = str(dict())

    def __call__(self, filename, mode='r'):  # pylint: disable=unused-argument
        return self

    def read(self):
        """ Return the file contents. """
        return self.contents

    def write(self, contents):
        """ Save the contents. """
        self.contents = contents

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        pass


class DependenciesTest(unittest.TestCase):
    """ Unit tests for the dependencies database. """

    def setUp(self):
        self.__file = FakeFile()
        self.__dependencies = Dependencies('filename', file_=self.__file)

    def test_set_and_get_dependencies(self):
        """ Test that the dependencies for a product can be put into the database. """
        self.__dependencies.set_dependencies('name', 'version', 1)
        self.assertEqual(1, self.__dependencies.get_dependencies('name', 'version'))

    def test_save_and_load(self):
        """ Test the the dependencies can be saved. """
        self.__dependencies.set_dependencies('name', 'version', 1)
        self.__dependencies.save()
        self.assertEqual({'name:version': 1}, self.__dependencies.load())

    def test_load_empty_file(self):
        """ Test that an empty file can be loaded. """
        self.__file.contents = ''
        self.__dependencies.load()
        self.assertFalse(self.__dependencies.has_dependencies('name', 'version'))

    def test_repr(self):
        """ Test that the contents of the dependencies cache can be printed. """
        self.assertEqual('{}', repr(self.__dependencies))
