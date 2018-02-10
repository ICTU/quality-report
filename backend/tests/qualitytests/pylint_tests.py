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


import re
import unittest
from pylint import epylint as lint


class TestCodeFormat(unittest.TestCase):
    """ Code format tests. """
    def assert_pylint_score(self, path, target):
        pylint_stdout, pylint_stderr = lint.py_run(path, return_std=True)
        score = float(re.search(r"Your code has been rated at ([-+]?\d*\.\d+|\d+)/10", pylint_stdout.read()).group(1))
        self.failUnless(score >= target, score)

    def test_pylint_score_main_script(self):
        """Test that our score is high enough."""
        self.assert_pylint_score("quality_report.py", 10.0)
