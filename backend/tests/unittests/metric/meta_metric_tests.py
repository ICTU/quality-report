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

from hqlib import domain, metric, metric_source
from tests.unittests.domain.measurement.fake import FakeHistory, FakeSubject


class MetaMetricUnderTest(metric.meta_metrics.MetaMetric, domain.HigherPercentageIsBetterMetric):
    # pylint: disable=too-few-public-methods
    """ Use MetaMetricMixin to create a concrete meta metric that can be tested. """
    pass


class MetaMetricMixinTest(unittest.TestCase):
    """ Test case for meta metric mixin class. """

    def setUp(self):
        project = domain.Project(metric_sources={metric_source.History: FakeHistory()})
        subject = [metric.CriticalViolations(FakeSubject(), project=project)]
        self.__metric = MetaMetricUnderTest(subject, project=project)

    def test_value(self):
        """ Test the value of the metric. """
        self.assertEqual(0, self.__metric.value())


class GreenMetaMetricTest(unittest.TestCase):
    """ Unit tests for the green meta metric. """
    def test_norm(self):
        """ Test the metric norm. """
        self.assertEqual("Minimaal 80% van de metrieken voldoet aan de norm (is groen). "
                         "Als minder dan 70% van de metrieken aan de norm voldoet is deze metriek rood.",
                         metric.GreenMetaMetric([], project=domain.Project()).norm())

    def test_report(self):
        """ Test the metric report. """
        self.assertEqual("100% van de metrieken (0 van de 0) voldoet aan de norm.",
                         metric.GreenMetaMetric([], project=domain.Project()).report())


class RedMetaMetricTest(unittest.TestCase):
    """ Unit tests for the red meta metric. """
    def test_norm(self):
        """ Test the metric norm. """
        self.assertEqual("Maximaal 10% van de metrieken vereist direct actie (is rood). "
                         "Als meer dan 20% van de metrieken direct actie vereist is deze metriek rood.",
                         metric.RedMetaMetric([], project=domain.Project()).norm())

    def test_report(self):
        """ Test the metric report. """
        self.assertEqual("0% van de metrieken (0 van de 0) vereist direct actie.",
                         metric.RedMetaMetric([], project=domain.Project()).report())


class YellowMetaMetricTest(unittest.TestCase):
    """ Unit tests for the yellow meta metric. """
    def test_norm(self):
        """ Test the metric norm. """
        self.assertEqual("Maximaal 20% van de metrieken voldoet net niet aan de norm (is geel). "
                         "Als meer dan 30% van de metrieken net niet aan de norm voldoet is deze metriek rood.",
                         metric.YellowMetaMetric([], project=domain.Project()).norm())

    def test_report(self):
        """ Test the metric report. """
        self.assertEqual("0% van de metrieken (0 van de 0) voldoet net niet aan de norm.",
                         metric.YellowMetaMetric([], project=domain.Project()).report())


class GreyMetaMetricTest(unittest.TestCase):
    """ Unit tests for the grey meta metric. """
    def test_norm(self):
        """ Test the metric norm. """
        self.assertEqual("Maximaal 20% van de metrieken heeft geaccepteerde technische schuld (is grijs). "
                         "Als meer dan 30% van de metrieken geaccepteerde technische schuld heeft "
                         "is deze metriek rood.", metric.GreyMetaMetric([], project=domain.Project()).norm())

    def test_report(self):
        """ Test the metric report. """
        self.assertEqual("0% van de metrieken (0 van de 0) heeft geaccepteerde technische schuld.",
                         metric.GreyMetaMetric([], project=domain.Project()).report())


class MissingMetaMetricTest(unittest.TestCase):
    """ Unit tests for the missing meta metric. """
    def test_norm(self):
        """ Test the metric norm. """
        self.assertEqual("Maximaal 20% van de metrieken kan niet gemeten worden (is wit). "
                         "Als meer dan 30% van de metrieken niet gemeten kan worden is deze metriek rood.",
                         metric.MissingMetaMetric([], project=domain.Project()).norm())

    def test_report(self):
        """ Test the metric report. """
        self.assertEqual("0% van de metrieken (0 van de 0) kan niet gemeten worden.",
                         metric.MissingMetaMetric([], project=domain.Project()).report())
