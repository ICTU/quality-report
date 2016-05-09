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
import logging

from . import metric_mixin
from ..software_development.quality_attribute import QualityAttribute
from ... import utils


class Metric(object):
    """ Base class for metrics. """

    name = norm_template = target_value = low_target_value = perfect_value = template = 'Subclass responsibility'
    url_label_text = comment_url_label_text = ''
    old_age = datetime.timedelta.max
    max_old_age = datetime.timedelta.max
    quality_attribute = QualityAttribute('', name='')
    metric_source_classes = []

    @classmethod
    def can_be_measured(cls, subject, project):
        """ Return whether this metric can be measured for the specified
            subject, i.e. whether the necessary metric sources are available. """
        for metric_source_class in cls.metric_source_classes:
            metric_source_instance = project.metric_source(metric_source_class)
            if not metric_source_instance:
                return False
            if metric_source_class.needs_metric_source_id:
                if not subject.metric_source_id(metric_source_instance):
                    return False
        return bool(subject)

    @classmethod
    def should_be_measured(cls, project):
        """ Return whether this metric should be measured for the specified project. """
        return cls in project.required_metric_classes()

    @classmethod
    def norm_template_default_values(cls):
        """ Return the default values for parameters in the norm template. """
        return dict(target=cls.target_value, low_target=cls.low_target_value,
                    old_age=utils.format_timedelta(cls.old_age),
                    max_old_age=utils.format_timedelta(cls.max_old_age))

    def __init__(self, subject=None, project=None):
        self._subject = subject
        self.__id_string = self.stable_id()
        self._project = project
        from qualitylib import metric_source
        self._wiki = self._project.metric_source(metric_source.Wiki)
        self.__history = self._project.metric_source(metric_source.History)

    def stable_id(self):
        """ Return an id that doesn't depend on numbering/order of metrics. """
        stable_id = self.__class__.__name__
        if not isinstance(self._subject, list):
            # Add the product or team to the id:
            stable_id += self._subject.name() if self._subject else str(self._subject)
        return stable_id

    def set_id_string(self, id_string):
        """ Set the identification string. This can be set by a client since
            the identification of a metric may depend on the section the
            metric is reported in. E.g. A-1. """
        self.__id_string = id_string

    def id_string(self):
        """ Return the identification string of the metric. """
        return self.__id_string

    def target(self):
        """ Return the target value for the metric. If the actual value of the
            metric is below the target value, the metric is not green. """
        subject_target = self._subject.target(self.__class__) if hasattr(self._subject, 'target') else None
        return self.target_value if subject_target is None else subject_target

    def low_target(self):
        """ Return the low target value for the metric. If the actual value
            is below the low target value, the metric needs immediate
            action and its status/color is red. """
        subject_low_target = self._subject.low_target(self.__class__) if hasattr(self._subject, 'low_target') else None
        return self.low_target_value if subject_low_target is None else subject_low_target

    def __technical_debt_target(self):
        """ Return the reduced target due to technical debt for the subject.
            If the subject has technical debt and the actual value of the
            metric is below the technical debt target, the metric is red,
            else it is grey. """
        try:
            return self._subject.technical_debt_target(self.__class__)
        except AttributeError:
            return None

    @utils.memoized
    def status(self):
        """ Return the status/color of the metric. """
        if self._missing():
            return 'missing'
        below_target = self._is_below_target()
        if below_target and self.__is_above_technical_debt_target():
            return 'grey'
        if self._needs_immediate_action():
            return 'red'
        elif below_target:
            return 'yellow'
        elif self._is_perfect():
            return 'perfect'
        else:
            return 'green'

    def status_start_date(self):
        """ Return since when the metric has the current status. """
        return self.__history.status_start_date(self.stable_id(), self.status())

    def __is_above_technical_debt_target(self):
        """ Return whether a score below target is considered to be
            accepted technical debt. """
        target = self.__technical_debt_target()
        return self._is_value_better_than(target.target_value()) if target else False

    def _missing(self):
        """ Return whether the metric source is missing. """
        return self.value() == -1

    def _needs_immediate_action(self):
        """ Return whether the metric needs immediate action, i.e. its actual value is below its low target value. """
        return self._is_too_old()

    def _is_below_target(self):
        """ Return whether the actual value of the metric is below its target value. """
        return self._is_old()

    def _is_perfect(self):
        """ Return whether the actual value of the metric equals its perfect
            value, i.e. no further improvement is possible. """
        return self.value() == self.perfect_value and not self._is_old()

    def value(self):
        """ Return the actual value of the metric. """
        raise NotImplementedError  # pragma: no cover

    def _is_value_better_than(self, target):
        """ Return whether the actual value of the metric is better than the
            specified target value. """
        raise NotImplementedError  # pragma: no cover

    def report(self, max_subject_length=200):
        """ Return the actual value of the metric in the form of a short, mostly one sentence, report. """
        name = self.__subject_name()
        if len(name) > max_subject_length:
            name = name[:max_subject_length] + '...'
        logging.info('Reporting %s on %s', self.__class__.__name__, name)
        return self._get_template().format(**self._parameters())

    def _get_template(self):
        """ Return the template for the metric report. """
        return self.template

    def _parameters(self):
        """ Return the parameters for the metric report template and for the metric norm template. """
        try:
            version = self._subject.product_version()
        except AttributeError:
            version = '<no version>'
        return dict(name=self.__subject_name(),
                    version=version,
                    target=self.target(),
                    low_target=self.low_target(),
                    value=self.value(),
                    date=utils.format_date(self._date()),
                    old_age=utils.format_timedelta(self.__old_age()),
                    max_old_age=utils.format_timedelta(self.__max_old_age()),
                    age=utils.format_timedelta(self.__age()))

    def norm(self):
        """ Return a description of the norm for the metric. """
        try:
            return self.norm_template.format(**self._parameters())
        except KeyError:
            logging.error('Key missing in parameters of %s: %s', self.__class__.__name__, self._parameters())
            raise

    def url(self):  # pylint: disable=no-self-use
        """ Return a dictionary of urls for the metric. The key is the anchor, the value the url. """
        return dict()

    @classmethod
    def url_label(cls):
        """ Return the label to be used to explain the urls. """
        return cls.url_label_text

    def _date(self):  # pylint: disable=no-self-use
        """ Return the date when the metric was last measured. """
        return None

    def _is_old(self):
        """ Return whether this metric was measured recently. """
        return self.__age() > self.__old_age()

    def _is_too_old(self):
        """ Return whether this metric was measured too long ago. """
        return self.__age() > self.__max_old_age()

    def __age(self):
        """ Return how long ago this metric was measured (in hours). """
        last_measurement_date = self._date()
        if last_measurement_date:
            return datetime.datetime.now() - last_measurement_date
        else:
            return datetime.timedelta.max

    def __old_age(self):
        """ Return the age when we consider the metric to have been measured long ago. """
        try:
            return self._subject.metric_options(self.__class__)['old_age']
        except (AttributeError, TypeError, KeyError):
            return self.old_age

    def __max_old_age(self):
        """ Return the age when we consider the metric to have been measured too long ago. """
        try:
            return self._subject.metric_options(self.__class__)['max_old_age']
        except (AttributeError, TypeError, KeyError):
            return self.max_old_age

    @utils.memoized
    def comment(self):
        """ Return a comment on the metric. The comment is retrieved from the wiki. """
        return self.__technical_debt_comment() or self._wiki.comment(self.id_string()) or ''

    @classmethod
    def comment_url_label(cls):
        """ Return the label for the comment urls. """
        return cls.comment_url_label_text

    @utils.memoized
    def __technical_debt_comment(self):
        """ Return the comment of the accepted technical debt, if any. """
        if self.__technical_debt_target():
            return self.__technical_debt_target().explanation()
        else:
            return ''

    def comment_urls(self):
        """ Return the source for the comment on the metric. """
        urls = {}
        if self.__technical_debt_comment():
            pass  # No URL; the comment comes from the project definition.
        elif self.comment():
            urls['Wiki'] = self._wiki.comment_url()
        return urls

    def recent_history(self):
        """ Return a list of recent values of the metric, to be used in e.g. a spark line graph. """
        history = self.__history.recent_history(self.stable_id(), self.id_string())
        return [int(round(float(value))) for value in history]

    def y_axis_range(self):
        """ Return a two-tuple (min, max) for use in graphs. """
        history = self.recent_history()
        if not history:
            return 0, 100
        minimum, maximum = min(history), max(history)
        if minimum == maximum:
            return minimum - 1, maximum + 1
        else:
            return minimum, maximum

    def numerical_value(self):
        """ Return a numerical version of the metric value for use in graphs.
            By default this simply returns the regular value, assuming it is
            already numerical. Metrics that don't have a numerical value by
            default can override this method to convert the non-numerical
            value into a numerical value. """
        return self.value()

    def product_version_type(self):
        """ Return whether this metric measures a product and if so, whether
            it's a trunk version, a tagged version or a release candidate. """
        try:
            return self._subject.product_version_type()
        except AttributeError:
            return 'no_product'

    def __subject_name(self):
        """ Return the subject name, or a string representation if the subject has no name. """
        try:
            return self._subject.name()
        except AttributeError:
            return str(self._subject)


class LowerIsBetterMetric(Metric):
    """ Metric for which a lower value means the metric is scoring better. """

    perfect_value = 0

    def value(self):
        raise NotImplementedError  # pragma: no cover

    def _is_below_target(self):
        """ Return whether the metric meets or exceeds the target. """
        # The metric is below target when the actual value is *higher*
        # than the target value, because the target value is the maximum value
        # pylint: disable=protected-access
        value = self.value()
        return value < self.perfect_value or value > self.target() or \
            super(LowerIsBetterMetric, self)._is_below_target()

    def _needs_immediate_action(self):
        """ Return whether the metric scores so bad that immediate action is required. """
        # pylint: disable=protected-access
        value = self.value()
        return value < self.perfect_value or value > self.low_target() or \
            super(LowerIsBetterMetric, self)._needs_immediate_action()

    def _is_value_better_than(self, target):
        return self.perfect_value <= self.value() <= target


class HigherIsBetterMetric(Metric):
    """ Metric for which a higher value means the metric is scoring better. """

    def value(self):
        raise NotImplementedError  # pragma: no cover

    def _is_below_target(self):
        """ Return whether the metric meets or exceeds the target. """
        # The metric is below target when the actual value is *lower*
        # than the target value, because the target value is the minimum value
        # pylint: disable=protected-access
        return self.value() < self.target() or super(HigherIsBetterMetric, self)._is_below_target()

    def _needs_immediate_action(self):
        """ Return whether the metric scores so bad that immediate action is required. """
        # pylint: disable=protected-access
        return self.value() < self.low_target() or super(HigherIsBetterMetric, self)._needs_immediate_action()

    def _is_value_better_than(self, target):
        return self.value() >= target


class LowerPercentageIsBetterMetric(metric_mixin.PercentageMixin,
                                    LowerIsBetterMetric):
    """ Metric measured as a percentage with lower values being better. """

    zero_divided_by_zero_is_zero = True

    def _numerator(self):
        raise NotImplementedError  # pragma: no cover

    def _denominator(self):
        raise NotImplementedError  # pragma: no cover

    def _is_perfect(self):
        """ Return whether the metric has a perfect value. This is the case
            when the numerator is zero. We ignore the denominator to prevent
            a ZeroDivisionError exception. """
        # pylint: disable=protected-access
        return self._numerator() == 0 and super(LowerPercentageIsBetterMetric, self)._is_perfect()


class HigherPercentageIsBetterMetric(metric_mixin.PercentageMixin,
                                     HigherIsBetterMetric):
    """ Metric measured as a percentage with higher values being better. """

    perfect_value = 100
    zero_divided_by_zero_is_zero = False

    def _numerator(self):
        raise NotImplementedError  # pragma: no cover

    def _denominator(self):
        raise NotImplementedError  # pragma: no cover

    def _is_perfect(self):
        """ Return whether the metric has a perfect value. This is the case
            when the numerator and denominator are equal. """
        # pylint: disable=protected-access
        return self._numerator() == self._denominator() and super(HigherPercentageIsBetterMetric, self)._is_perfect()
