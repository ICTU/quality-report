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
from __future__ import absolute_import

import datetime

from ...utils import format_date


class TechnicalDebtTarget(object):
    """ Keep track of the current accepted technical debt for a certain metric. """
    def __init__(self, target_value, explanation='', unit=''):
        self.__target_value = target_value
        self.__explanation = explanation
        self._unit = ' ' + unit if unit and unit != '%' else unit

    def target_value(self):
        """ Return the current technical debt target. This is the level of technical debt that is currently
            accepted. """
        return self.__target_value

    def explanation(self):
        """ Return the explanation for the technical debt. """
        explanation = 'De op dit moment geaccepteerde technische schuld is {val}{unit}.'.format(val=self.target_value(),
                                                                                                unit=self._unit)
        if self.__explanation:
            explanation += ' ' + self.__explanation
        return explanation


class DynamicTechnicalDebtTarget(TechnicalDebtTarget):
    """ Keep track of a dynamically changing accepted technical debt for a certain metric. """
    def __init__(self, initial_target_value, initial_datetime, end_target_value, end_datetime, explanation='', unit=''):
        assert end_datetime > initial_datetime
        self.__period_length = (end_datetime - initial_datetime).total_seconds()
        self.__initial_target_value = initial_target_value
        self.__initial_datetime = initial_datetime
        self.__end_target_value = end_target_value
        self.__end_datetime = end_datetime
        super(DynamicTechnicalDebtTarget, self).__init__(end_target_value, explanation, unit)

    def target_value(self):
        now = datetime.datetime.now()
        if now < self.__initial_datetime:
            return self.__initial_target_value
        elif now > self.__end_datetime:
            return self.__end_target_value
        else:
            period_passed = (now - self.__initial_datetime).total_seconds()
            fraction = period_passed / self.__period_length
            delta = self.__end_target_value - self.__initial_target_value
            return int(round(fraction * delta + self.__initial_target_value))

    def explanation(self):
        start_date = format_date(self.__initial_datetime, year=True)
        end_date = format_date(self.__end_datetime, year=True)
        explanation = 'Het doel is dat de technische schuld vermindert van {old_val}{unit} op {old_date} ' \
            'naar {new_val}{unit} op {new_date}.'.format(unit=self._unit,
                                                         old_val=self.__initial_target_value,
                                                         old_date=start_date,
                                                         new_val=self.__end_target_value,
                                                         new_date=end_date)
        return explanation + ' ' + super(DynamicTechnicalDebtTarget, self).explanation()
