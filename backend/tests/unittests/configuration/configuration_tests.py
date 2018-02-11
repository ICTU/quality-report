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

import unittest.mock

from hqlib import configuration


class ConfigurationTest(unittest.TestCase):
    """ Unit tests for the configuration module. """

    @unittest.mock.patch("builtins.__import__")
    def test_get_project_from_py_file(self, import_function):
        """ Test that a project definition can be loaded. """
        project = unittest.mock.MagicMock()
        project.PROJECT = "Project"
        import_function.return_value = project
        self.assertEqual("Project", configuration.project("folder/definition.py"))

    @unittest.mock.patch("builtins.__import__")
    def test_get_project_from_folder(self, import_function):
        """ Test that a project definition can be loaded. """
        project = unittest.mock.MagicMock()
        project.PROJECT = "Project"
        import_function.return_value = project
        self.assertEqual("Project", configuration.project("folder"))

    @unittest.mock.patch("builtins.__import__")
    def test_missing_project_definition(self, import_function):
        """ Test that an exception is thrown if the actual project definition is missing. """
        import_function.side_effect = ModuleNotFoundError
        for filename in 'folder', 'folder/definition.py':
            self.assertRaises(ModuleNotFoundError, configuration.project, filename)

    @unittest.mock.patch("builtins.__import__")
    def test_missing_project_in_module(self, import_function):
        """ Test that the default project definition is returned if the project is missing from the project
            definition. """
        import_function.side_effect = AttributeError
        self.assertRaises(AttributeError, configuration.project, 'folder/definition.py')
