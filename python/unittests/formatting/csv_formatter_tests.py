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


from qualitylib.formatting import CSVFormatter
from qualitylib import metric, domain
from unittests.formatting import fake_report
import unittest


class TotalLOC(metric.TotalLOC):  # pylint:disable=too-many-public-methods
    ''' Override the metric to return a fixed value. '''
    def value(self):
        return 100


class FakeMetric(object):  # pylint:disable=too-few-public-methods
    ''' Fake metric with a specified status. '''
    def __init__(self, status):
        self.__status = status

    def status(self):
        ''' Return the status (color) of the metric. '''
        return self.__status


class CSVFormatterTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit test for the CSV report formatter class. '''
    def setUp(self):  # pylint: disable=invalid-name
        self.__formatter = CSVFormatter()
        self.__project = domain.Project()
        self.__total_loc = TotalLOC(project=self.__project)
        self.__expected_date = fake_report.Report().date().strftime('%c')

    def test_prefix(self):
        ''' Test that the formatter returns the correct prefix. '''
        self.assertEqual(self.__expected_date, 
                         self.__formatter.prefix(fake_report.Report()))

    def test_metric(self):
        ''' Test that the value of the metric is returned. '''
        self.assertEqual('100', self.__formatter.metric(self.__total_loc))

    def test_process(self):
        ''' Test that the report results in one line that can be appended to
            a CSV file. '''
        green_metric = FakeMetric(status='green')
        grey_metric = FakeMetric(status='grey')
        yellow_metric = FakeMetric(status='yellow')
        invalid_metric = FakeMetric(status='invalid status')
        self.assertEqual('%s, 100, 2, 1, 4, 1\n' % self.__expected_date,
            self.__formatter.process(fake_report.Report(
                metrics=[self.__total_loc, green_metric, grey_metric, 
                         yellow_metric, invalid_metric])))
