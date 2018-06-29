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
from unittest.mock import call, patch
import sys

from hqlib import commandlineargs


class ParseTest(unittest.TestCase):
    """ Unit tests for the parse method. """

    @patch.object(sys, "argv", ["quality_report.py"])
    @patch.object(sys.stderr, "write")
    def test_missing_all(self, mock_write):
        """ Test missing all required values. """
        self.assertRaises(SystemExit, commandlineargs.parse)
        self.assertEqual(
            [
                call("usage: quality_report.py [-h] --project PROJECT --report REPORT\n"
                     "                         [--failure-exit-code]\n"
                     "                         [--log {DEBUG,INFO,WARNING,ERROR,CRITICAL}]\n"
                     "                         [--frontend {yes,no}] [--version]\n"),
                call("quality_report.py: error: the following arguments are required: --project, --report\n")],
            mock_write.call_args_list)

    @patch.object(sys, "argv", ["quality_report.py", "--project", "project", "--report", "report"])
    def test_all_required(self):
        """ Test all required arguments are provided. """
        namespace = commandlineargs.parse()
        self.assertEqual("project", namespace.project)
        self.assertEqual("report", namespace.report)
        self.assertEqual("WARNING", namespace.log)
        self.assertFalse(namespace.failure_exit_code)
        self.assertTrue(namespace.frontend)
