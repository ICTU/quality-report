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

from ..quality_attributes import PERFORMANCE
from ... import domain, metric_source


class ResponseTimes(domain.Metric):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring reponsetimes as determined in the performance tests. """

    name = 'Responsetijden'
    norm_template = 'Geen van de performancetestqueries overschrijdt de gewenste responsetijd. ' \
        'Als een of meer queries de maximum responsetijd overschrijden is de score rood, anders geel.'
    above_target_template = 'Alle {nr_queries} performancetestqueries draaien in 90% van de gevallen binnen ' \
        'de gewenste responsetijd (meting {date}, {age} geleden).'
    below_max_target_template = '{value_max} van de {nr_queries} performancetestqueries draaien niet in 90% ' \
        'van de gevallen binnen de maximale responsetijd (meting {date}, {age} geleden).'
    below_wish_target_template = '{value_wish} van de {nr_queries} performancetestqueries draaien niet in 90% ' \
        'van de gevallen binnen de gewenste responsetijd (meting {date}, {age} geleden).'
    below_both_targets_template = '{value_max} van de {nr_queries} performancetestqueries draaien niet in 90% ' \
        'van de gevallen binnen de maximale responsetijd en {value_wish} van de {nr_queries} queries draaien niet ' \
        'in 90% van de gevallen binnen de gewenste responsetijd (meting {date}, {age} geleden).'
    missing_report_template = 'Er is geen performancetestrapport voor {name}:{version}.'
    perfect_value = 0
    target_value = 0  # Not used
    low_target_value = 0  # Not used
    quality_attribute = PERFORMANCE
    metric_source_classes = (metric_source.PerformanceReport,)

    def __init__(self, *args, **kwargs):
        super(ResponseTimes, self).__init__(*args, **kwargs)
        self.__performance_report = self._project.metric_source(
            metric_source.PerformanceReport)
        if not self._subject.product_version():
            self.old_age = datetime.timedelta(hours=7 * 24)
            self.max_old_age = datetime.timedelta(hours=14 * 24)
            self.norm_template = 'Geen van de performancetestqueries overschrijdt de gewenste responsetijd en de ' \
                'performancemeting is niet ouder dan {old_age}. Als een of meer queries de maximum ' \
                'responsetijd overschrijden of als de meting ouder is dan {max_old_age}, is de score rood, anders geel.'

    def value(self):
        return None

    def numerical_value(self):
        return self.__max_violations() + self.__wish_violations()

    def __max_violations(self):
        """ The number of performance queries that is slower than the maximum response time. """
        return self.__performance_report.queries_violating_max_responsetime(*self.__product_id())

    def __wish_violations(self):
        """ The number of performance queries that is slower than the wished for response time. """
        return self.__performance_report.queries_violating_wished_responsetime(*self.__product_id())

    def _missing(self):
        return self.numerical_value() < 0

    def _is_perfect(self):
        return self.__max_violations() == self.__wish_violations() == 0 and \
            not self._is_old() and self.__report_exists()

    def _needs_immediate_action(self):
        # pylint: disable=protected-access
        return self.__max_violations() > 0 or super(ResponseTimes, self)._is_too_old() or not self.__report_exists()

    def _is_below_target(self):
        # pylint: disable=protected-access
        return self.__max_violations() > 0 or self.__wish_violations() > 0 or super(ResponseTimes, self)._is_old() or \
            not self.__report_exists()

    def _get_template(self):
        if not self.__report_exists():
            return self.missing_report_template
        max_violations = self.__max_violations()
        wish_violations = self.__wish_violations()
        if max_violations and wish_violations:
            return self.below_both_targets_template
        elif max_violations:
            return self.below_max_target_template
        elif wish_violations:
            return self.below_wish_target_template
        else:
            return self.above_target_template

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(ResponseTimes, self)._parameters()
        if self.__report_exists():
            parameters.update(dict(nr_queries=self.__nr_queries(),
                                   value_max=self.__max_violations(),
                                   value_wish=self.__wish_violations()))
        return parameters

    def _date(self):
        return self.__performance_report.date(*self.__product_id())

    def url(self):
        urls = self.__performance_report.urls(*self.__product_id())
        total = len(urls)
        labeled_urls = {}
        for index, url in enumerate(sorted(urls)):
            label = 'Wekelijkse performancemeting ({}/{})'.format(index + 1, total)
            labeled_urls[label] = url
        return labeled_urls

    def __report_exists(self):
        """ Return whether a performance report exists for the product and version this metric reports on. """
        return self.__performance_report.exists(*self.__product_id())

    def __nr_queries(self):
        """ Return the number of performance queries in the performance report for the product. """
        return self.__performance_report.queries(*self.__product_id())

    def __product_id(self):
        """ Return the performance report id and version of the product. """
        return self.__performance_report_id(), self._subject.product_version()

    def __performance_report_id(self):
        """ Return the performance report id of the product. """
        return self._subject.metric_source_id(self.__performance_report)


class YmorResponseTimes(domain.Metric):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring reponsetimes as determined in the Ymor performance report. """
    name = 'Responsetijden (obv Ymor performance rapportage)'
    norm_template = 'Geen van de performancetestqueries overschrijdt de gewenste responsetijd. Als een of meer ' \
        'queries de maximum responsetijd overschrijden is de score rood, anders geel.'
    above_target_template = 'Alle {nr_queries} performancetestqueries draaien in 90% van de gevallen binnen de ' \
        'gewenste responsetijd (meting {date}, {age} geleden).'
    below_max_target_template = '{value_max} van de {nr_queries} performancetestqueries draaien niet in 90% ' \
        'van de gevallen binnen de maximale responsetijd (meting {date}, {age} geleden).'
    below_wish_target_template = '{value_wish} van de {nr_queries} performancetestqueries draaien niet in 90% ' \
        'van de gevallen binnen de gewenste responsetijd (meting {date}, {age} geleden).'
    below_both_targets_template = '{value_max} van de {nr_queries} performancetestqueries draaien niet in 90% ' \
        'van de gevallen binnen de maximale responsetijd en {value_wish} van de {nr_queries} queries draaien niet ' \
        'in 90% van de gevallen binnen de gewenste responsetijd (meting {date}, {age} geleden).'
    perfect_value = 0
    target_value = 0  # Not used
    low_target_value = 0  # Not used
    quality_attribute = PERFORMANCE
    metric_source_classes = (metric_source.JenkinsYmorPerformanceReport,)

    def __init__(self, *args, **kwargs):
        super(YmorResponseTimes, self).__init__(*args, **kwargs)
        self.__performance_report = self._project.metric_source(
            metric_source.JenkinsYmorPerformanceReport)
        if not self._subject.product_version():
            self.old_age = datetime.timedelta(hours=7 * 24)
            self.max_old_age = datetime.timedelta(hours=14 * 24)
            self.norm_template = 'Geen van de performancetestqueries overschrijdt de gewenste responsetijd en de ' \
                'performancemeting is niet ouder dan {old_age}. Als een of meer queries de maximum responsetijd ' \
                'overschrijden of als de meting ouder is dan {max_old_age}, is de score rood, anders geel.'

    def value(self):
        return None  # We use max_violations and wish_violations as value

    def numerical_value(self):
        return self.__max_violations() + self.__wish_violations()

    def __max_violations(self):
        """ The number of performance queries that is slower than the maximum response time. """
        return self.__performance_report.queries_violating_max_responsetime(self.__performance_report_id())

    def __wish_violations(self):
        """ The number of performance queries that is slower than the wished for response time. """
        return self.__performance_report.queries_violating_wished_responsetime(self.__performance_report_id())

    def _is_perfect(self):
        return self.__max_violations() == self.__wish_violations() == 0 and not self._is_old()

    def _needs_immediate_action(self):
        # pylint: disable=protected-access
        return self.__max_violations() > 0 or super(YmorResponseTimes, self)._is_too_old()

    def _is_below_target(self):
        # pylint: disable=protected-access
        return self.__max_violations() > 0 or self.__wish_violations() > 0 or super(YmorResponseTimes, self)._is_old()

    def _get_template(self):
        max_violations = self.__max_violations()
        wish_violations = self.__wish_violations()
        if max_violations and wish_violations:
            return self.below_both_targets_template
        elif max_violations:
            return self.below_max_target_template
        elif wish_violations:
            return self.below_wish_target_template
        else:
            return self.above_target_template

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(YmorResponseTimes, self)._parameters()
        parameters.update(dict(nr_queries=self.__nr_queries(), value_max=self.__max_violations(),
                               value_wish=self.__wish_violations()))
        return parameters

    def _date(self):
        return self.__performance_report.date(self.__performance_report_id())

    def url(self):
        url = self.__performance_report.report_url(self.__performance_report_id())
        return {'Performance report': url}

    def __nr_queries(self):
        """ Return the number of performance queries in the performance report for the product. """
        return self.__performance_report.queries(self.__performance_report_id())

    def __performance_report_id(self):
        """ Return the performance report id of the product. """
        return [self._subject.metric_source_id(self.__performance_report)]
