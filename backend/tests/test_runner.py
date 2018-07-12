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

import io
import logging
import pathlib
import sys
import unittest

import xmlrunner


def run_tests(test_folder: str, build_folder: str) -> None:
    """ Discover and run tests. """
    sys.path.insert(0, '.')
    # Make sure log messages are not shown on stdout/stderr. We can't simply
    # increase the log level since some unit tests expect logging to happen.
    logging.getLogger().addHandler(logging.StreamHandler(io.StringIO()))
    # Run the unit test with the XML test runner so that the test output
    # can be processed by Sonar.
    my_dir = pathlib.Path(__file__).resolve().parent
    tests_dir = my_dir / test_folder
    results_dir = my_dir.parent / "build" / build_folder
    results_dir.mkdir(parents=True, exist_ok=True)
    unittest.main(module=None, testRunner=xmlrunner.XMLTestRunner(output=str(results_dir)),
                  argv=[sys.argv[0], "discover", "-s", str(tests_dir), "-p", "*_tests.py"])
