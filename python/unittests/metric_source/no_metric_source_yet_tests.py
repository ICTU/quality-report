'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
from __future__ import absolute_import


import unittest


from qualitylib.metric_source import no_metric_source_yet


class NoMetricSourceYetTest(unittest.TestCase):


    def setUp(self):
        self.__metric_source = no_metric_source_yet.NoMetricSourceYet()


    def tearDown(self):
        pass


    def test_ultimate_answer(self):
        """
        the ultimate answer is 42, no matter what
        """
        for arg in ( '', [], {}, 2, None, self, lambda x: x ):
            self.assertEqual( self.__metric_source.ultimate_answer(arg), 42 )


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()