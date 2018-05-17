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

import json
import logging
import unittest
from unittest.mock import MagicMock, patch
from hqlib.persistence import JsonPersister, FilePersister


class JsonPersisterTestCase(unittest.TestCase):
    """ Unit tests for JsonPersister abstract class. """

    def test_read_json(self):
        """ Test that there is an abstract method.  """
        self.assertRaises(NotImplementedError, JsonPersister().read_json, 'location')

    def test_write_json(self):
        """ Test that there is an abstract method.  """
        self.assertRaises(NotImplementedError, JsonPersister().write_json, {}, 'location')


@patch('builtins.open')
class FilePersisterTestCase(unittest.TestCase):
    """ Unit tests for the FilePersister class with errors. """

    def test_read(self, mock_open):
        """ Test that the json file content is read and interpreted correctly. """
        fake_file = MagicMock()
        fake_file.read.return_value = '{"x": "y"}'
        mock_open.return_value = fake_file

        self.assertEqual({"x": "y"}, FilePersister.read_json('unimportant'))

    def test_read_invalid_json(self, mock_open):
        """ Test that it raises if the json is invalid. """
        fake_file = MagicMock()
        fake_file.read.return_value = 'non-json'
        mock_open.return_value = fake_file

        self.assertRaises(json.decoder.JSONDecodeError, FilePersister.read_json, 'unimportant')

    @patch.object(logging, 'error')
    def test_read_json_io_error(self, mock_error, mock_open):
        """ Test there is no result if io error happens and it is logged. """
        mock_error.return_value = None
        mock_open.side_effect = IOError

        self.assertEqual(None, FilePersister.read_json('file\\path'))
        mock_error.assert_called_once_with('Error reading file %s.', 'file\\path')

    def test_read_json_file_not_found(self, mock_open):
        """ Test there is no result if file is not found. """
        mock_open.side_effect = FileNotFoundError

        self.assertEqual(None, FilePersister.read_json('unimportant'))

    def test_write(self, mock_open):
        """ Test that a json is correctly written to a file. """
        fake_file = MagicMock()
        mock_open.return_value = fake_file

        FilePersister.write_json({"x": 10}, 'file\\path')

        mock_open.assert_called_once_with('file\\path', mode='w', encoding='utf-8')
        fake_file.write.assert_called()
        saved_json = json.loads(''.join([args[0] for (args, kwargs) in fake_file.write.call_args_list]))
        self.assertEqual(10, saved_json['x'])

    @patch.object(logging, 'error')
    def test_write_io_error(self, mock_error, mock_open):
        """ Test that an incorrect json raises when it is tried to write it to a file. """
        mock_error.return_value = None
        fake_file = MagicMock()
        fake_file.write.return_value = None
        mock_open.side_effect = IOError

        FilePersister.write_json('unimportant', 'file\\path')

        mock_open.assert_called_once_with('file\\path', mode='w', encoding='utf-8')
        fake_file.write.assert_not_called()
        mock_error.assert_called_once_with('Error writing file %s.', 'file\\path')
