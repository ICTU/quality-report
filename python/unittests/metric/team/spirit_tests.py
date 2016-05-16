"""
Copyright 2012-2016 Ministerie van Sociale Zaken en Werkgelegenheid

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

import datetime
import unittest

from qualitylib import metric, domain, metric_source


class FakeWiki(object):
    """ Fake a wiki metric source. """

    def __init__(self):
        self.date_of_last_measurement = datetime.datetime.now()

    @staticmethod
    def team_spirit(*args):  # pylint: disable=unused-argument
        """ Return a fake team spirit. """
        return ':-)'

    def date_of_last_team_spirit_measurement(self, *args):  # pylint: disable=unused-argument
        """ Return a fake date. """
        return self.date_of_last_measurement

    @staticmethod
    def url():
        """ Return a fake url. """
        return 'http://wiki'


class TeamSpiritTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the ARTstability metric. """

    def setUp(self):
        self.__wiki = FakeWiki()
        self.__team = domain.Team(metric_source_ids={self.__wiki: 'team'})
        self.__project = domain.Project(metric_sources={metric_source.Wiki: self.__wiki})
        self.__metric = metric.TeamSpirit(subject=self.__team, project=self.__project)

    def test_value(self):
        """ Test that the value of the metric equals the team spirit reported by the wiki. """
        self.assertEqual(self.__wiki.team_spirit('team'), self.__metric.value())

    def test_numerical_value(self):
        """ Test that the smiley is translated into an integer. """
        self.assertEqual(2, self.__metric.numerical_value())

    def test_y_axis_range(self):
        """ Test that the y axis range is 0-2. """
        self.assertEqual((0, 2), self.__metric.y_axis_range())

    def test_status(self):
        """ Test that the status is perfect. """
        self.assertEqual('perfect', self.__metric.status())

    def test_url(self):
        """ Test that the metric url uses the wiki url. """
        self.assertEqual(dict(Wiki=FakeWiki().url()), self.__metric.url())

    def test_can_be_measured(self):
        """ Test that the metric can be measured if the project has a Wiki. """
        self.assertTrue(metric.TeamSpirit.can_be_measured(self.__team, self.__project))

    def test_cant_be_measured_without_wiki(self):
        """ Test that the metric cannot be measured without a Wiki. """
        project = domain.Project()
        self.assertFalse(metric.TeamSpirit.can_be_measured(self.__team, project))

    def test_too_old(self):
        """ Test that the metric becomes red when too old. """
        self.__wiki.date_of_last_measurement = datetime.datetime(2000, 1, 1)
        self.assertEqual('red', self.__metric.status())

    def test_old(self):
        """ Test that the metric becomes yellow when old. """
        self.__wiki.date_of_last_measurement = datetime.datetime.now() - metric.TeamSpirit.old_age - \
                                               datetime.timedelta(hours=1)
        self.assertEqual('yellow', self.__metric.status())

    def test_norm(self):
        """ Test that the norm mentions measurement age. """
        self.assertEqual(
            'De stemming wordt door het team zelf bepaald door het kiezen van een smiley. '
            'De norm hierbij is een tevreden team, neutraal is geel, ontevreden is rood. Als de meting '
            'ouder is dan 21 dagen dagen is de status geel, ouder dan 42 dagen dagen is rood.',
            self.__metric.norm())
