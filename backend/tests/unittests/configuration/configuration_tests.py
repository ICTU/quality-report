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

import unittest

from hqlib import configuration


class ConfigurationTest(unittest.TestCase):
    def setUp(self):
        self.module = None

    def __import(self, *args, **kwargs):  # pylint: disable=unused-argument
        """ Fake import function. """
        if self.module:
            return self.module
        else:
            raise ModuleNotFoundError

    def test_missing_project_definition(self):
        """ Test that the default project definition is returned if the actual one is missing. """
        for filename in 'folder', 'folder/definition.py':
            self.assertEqual('Default project', configuration.Configuration.project(filename, self.__import).name())

    def test_missing_project_in_module(self):
        """ Test that the default project definition is returned if the project is missing from the project
            definition. """
        self.module = 'fake module without project'
        self.assertEqual('Default project',
                         configuration.Configuration.project('folder/definition.py', self.__import).name())
