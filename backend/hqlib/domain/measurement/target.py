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


import datetime

from ...utils import format_date
from hqlib.typing import DateTime, MetricValue


class TechnicalDebtTarget(object):
    """ Keep track of the current accepted technical debt for a certain metric. """
    def __init__(self, target_value: MetricValue, explanation: str= '') -> None:
        self.__target_value = target_value
        self.__explanation = explanation

    def target_value(self) -> MetricValue:
        """ Return the current technical debt target. This is the level of technical debt that is currently
            accepted. """
        return self.__target_value

    def explanation(self, unit: str='') -> str:
        """ Return the explanation for the technical debt. """
        explanation = 'De op dit moment geaccepteerde technische schuld is {val}{unit}.'.format(
            val=self.target_value(), unit=self._space_unit(unit))
        if self.__explanation:
            explanation += ' ' + self.__explanation
        return explanation

    @staticmethod
    def _space_unit(unit: str) -> str:
        """ Add a space before the unit if necessary. """
        return ' ' + unit if unit and unit != '%' and not unit.startswith(' ') else unit


class DynamicTechnicalDebtTarget(TechnicalDebtTarget):
    """ Keep track of a dynamically changing accepted technical debt for a certain metric. """
    def __init__(self, initial_target_value: MetricValue, initial_datetime: DateTime, end_target_value: MetricValue,
                 end_datetime: DateTime, explanation: str='') -> None:
        if end_datetime < initial_datetime:
            raise ValueError("Initial datetime should be before end datetime")
        if not isinstance(initial_target_value, (int, float)) or not isinstance(end_target_value, (int, float)):
            raise ValueError("Dynamical technical debt is only supported for integer or float values")
        self.__period_length = (end_datetime - initial_datetime).total_seconds()
        self.__initial_target_value = initial_target_value
        self.__initial_datetime = initial_datetime
        self.__end_datetime = end_datetime
        super().__init__(end_target_value, explanation)

    def target_value(self) -> MetricValue:
        now = datetime.datetime.now()
        end_target_value = super().target_value()
        if now < self.__initial_datetime:
            return self.__initial_target_value
        elif now > self.__end_datetime:
            return end_target_value
        else:
            assert (isinstance(self.__initial_target_value, (int, float)))
            assert (isinstance(end_target_value, (int, float)))
            period_passed = (now - self.__initial_datetime).total_seconds()
            fraction = period_passed / self.__period_length
            delta = end_target_value - self.__initial_target_value
            return int(round(fraction * delta + self.__initial_target_value))

    def explanation(self, unit: str='') -> str:
        start_date = format_date(self.__initial_datetime, year=True)
        end_date = format_date(self.__end_datetime, year=True)
        explanation = 'Het doel is dat de technische schuld vermindert van {old_val}{unit} op {old_date} ' \
            'naar {new_val}{unit} op {new_date}.'.format(unit=self._space_unit(unit),
                                                         old_val=self.__initial_target_value,
                                                         old_date=start_date,
                                                         new_val=super().target_value(),
                                                         new_date=end_date)
        return explanation + ' ' + super().explanation(unit)
