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

# Run the integration tests.

import io
import logging
import os
import sys
import unittest

import xmlrunner

if __name__ == '__main__':  # pragma: no branch
    sys.path.insert(0, os.path.abspath('.'))
    # Make sure log messages are not shown on stdout/stderr. We can't simply
    # increase the log level since some integration tests may expect logging to happen.
    logging.getLogger().addHandler(logging.StreamHandler(io.StringIO()))
    # Run the unit test with the XML test runner so that the test output
    # can be processed by Sonar.
    if not os.path.exists('build'):  # pragma: no branch
        os.mkdir('build')  # pragma: no cover
    os.system('python3 setup.py bundle')
    unittest.main(module=None, testRunner=xmlrunner.XMLTestRunner(output='build/integration-test-reports'))
