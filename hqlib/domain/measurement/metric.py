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
from __future__ import absolute_import

import datetime
import logging

from ... import utils


class Metric(object):
    """ Base class for metrics. """

    name = norm_template = target_value = low_target_value = perfect_value = template = unit = 'Subclass responsibility'
    missing_template = 'De {metric} van {name} kon niet gemeten worden omdat niet alle benodigde bronnen ' \
                       'beschikbaar zijn.'
    missing_source_template = 'De {metric} van {name} kon niet gemeten worden omdat niet alle benodigde bronnen zijn ' \
                              'geconfigureerd. Configureer de volgende bron(nen): {missing_source_classes}.'
    missing_source_id_template = 'De {metric} van {name} kon niet gemeten worden omdat niet alle benodigde ' \
                                 'bron-ids zijn geconfigureerd. Configureer ids voor de volgende bronnen: ' \
                                 '{missing_source_id_classes}.'
    perfect_template = ''
    url_label_text = comment_url_label_text = ''
    old_age = datetime.timedelta.max
    max_old_age = datetime.timedelta.max
    metric_source_classes = []

    @classmethod
    def should_be_measured(cls, requirement_subject):
        """ Return whether this metric should be measured for the specified subject. """
        return cls in requirement_subject.required_metric_classes()

    @classmethod
    def is_applicable(cls, subject):  # pylint: disable=unused-argument
        """ Return whether this metric applies to the specified subject. """
        return True

    @classmethod
    def norm_template_default_values(cls):
        """ Return the default values for parameters in the norm template. """
        return dict(unit=cls.unit, target=cls.target_value, low_target=cls.low_target_value,
                    old_age=utils.format_timedelta(cls.old_age),
                    max_old_age=utils.format_timedelta(cls.max_old_age))

    def __init__(self, subject=None, project=None):
        self._subject = subject
        self._project = project
        self._metric_source = self._project.metric_source(self.metric_source_classes[0]) if self.metric_source_classes \
            else None
        if isinstance(self._metric_source, list):
            for source in self._metric_source:
                try:
                    source_id = self._subject.metric_source_id(source)
                except AttributeError:
                    continue
                if source_id:
                    self._metric_source = source
                    self._metric_source_id = source_id
                    break
            else:
                logging.warning("Couldn't find metric source for %s", self._subject)
                self._metric_source = None
                self._metric_source_id = None
        else:
            try:
                self._metric_source_id = self._subject.metric_source_id(self._metric_source)
            except AttributeError:
                self._metric_source_id = None
        self.__id_string = self.stable_id()
        from hqlib import metric_source
        self.__history = self._project.metric_source(metric_source.History)

    def stable_id(self):
        """ Return an id that doesn't depend on numbering/order of metrics. """
        stable_id = self.__class__.__name__
        if not isinstance(self._subject, list):
            # Add the product or team to the id:
            stable_id += self._subject.name() if self._subject else str(self._subject)
        return stable_id

    def set_id_string(self, id_string):
        """ Set the identification string. This can be set by a client since the identification of a metric may
            depend on the section the metric is reported in. E.g. A-1. """
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
        """ Return the low target value for the metric. If the actual value is below the low target value, the metric
            needs immediate action and its status/color is red. """
        subject_low_target = self._subject.low_target(self.__class__) if hasattr(self._subject, 'low_target') else None
        return self.low_target_value if subject_low_target is None else subject_low_target

    def __technical_debt_target(self):
        """ Return the reduced target due to technical debt for the subject. If the subject has technical debt and
            the actual value of the metric is below the technical debt target, the metric is red, else it is grey. """
        try:
            return self._subject.technical_debt_target(self.__class__)
        except AttributeError:
            return None

    @utils.memoized
    def status(self):
        """ Return the status/color of the metric. """
        for status_string, has_status in [('missing_source', self.__missing_source_configuration),
                                          ('missing', self._missing),
                                          ('grey', self.__has_accepted_technical_debt),
                                          ('red', self._needs_immediate_action),
                                          ('yellow', self._is_below_target),
                                          ('perfect', self.__is_perfect)]:
            if has_status():
                return status_string
        return 'green'

    def status_start_date(self):
        """ Return since when the metric has the current status. """
        return self.__history.status_start_date(self.stable_id(), self.status())

    def __has_accepted_technical_debt(self):
        """ Return whether the metric is below target but above the accepted technical debt level. """
        technical_debt_target = self.__technical_debt_target()
        if technical_debt_target:
            return self._is_below_target() and self._is_value_better_than(technical_debt_target.target_value())
        else:
            return False

    def _missing(self):
        """ Return whether the metric source is missing. """
        return self.value() == -1

    def __missing_source_configuration(self):
        """ Return whether the metric sources have been completely configured. """
        return self.__missing_source_classes() or self.__missing_source_ids()

    def __missing_source_classes(self):
        """ Return the metric source classes that need to be configured for the metric to be measurable. """
        return [cls for cls in self.metric_source_classes if not self._project.metric_source(cls)]

    def __missing_source_ids(self):
        """ Return the metric source classes for which a metric source id needs to be configured. """
        return [cls for cls in self.metric_source_classes if cls.needs_metric_source_id and
                not self._subject.metric_source_id(self._project.metric_source(cls))]

    def _needs_immediate_action(self):
        """ Return whether the metric needs immediate action, i.e. its actual value is below its low target value. """
        return self._is_too_old()

    def _is_below_target(self):
        """ Return whether the actual value of the metric is below its target value. """
        return self._is_old()

    def __is_perfect(self):
        """ Return whether the actual value of the metric equals its perfect value,
            i.e. no further improvement is possible. """
        return self.value() == self.perfect_value and not self._is_old()

    def value(self):
        """ Return the actual value of the metric. """
        raise NotImplementedError  # pragma: no cover

    def _is_value_better_than(self, target):
        """ Return whether the actual value of the metric is better than the specified target value. """
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
        if self.__missing_source_classes():
            return self.missing_source_template
        if self.__missing_source_ids():
            return self.missing_source_id_template
        elif self._missing():
            return self.missing_template
        elif self.__is_perfect() and self.perfect_template:
            return self.perfect_template
        else:
            return self.template

    def _parameters(self):
        """ Return the parameters for the metric report template and for the metric norm template. """
        return dict(name=self.__subject_name(),
                    metric=self.name[0].lower()+self.name[1:],
                    unit=self.unit,
                    target=self.target(),
                    low_target=self.low_target(),
                    value=self.value(),
                    date=utils.format_date(self._date()),
                    old_age=utils.format_timedelta(self.__old_age()),
                    max_old_age=utils.format_timedelta(self.__max_old_age()),
                    age=utils.format_timedelta(self.__age()),
                    missing_source_classes=', '.join(sorted(cls.__name__ for cls in self.__missing_source_classes())),
                    missing_source_id_classes=', '.join(sorted(cls.__name__ for cls in self.__missing_source_ids())))

    def norm(self):
        """ Return a description of the norm for the metric. """
        try:
            return self.norm_template.format(**self._parameters())
        except KeyError:
            logging.error('Key missing in parameters of %s: %s', self.__class__.__name__, self._parameters())
            raise

    def url(self):
        """ Return a dictionary of urls for the metric. The key is the anchor, the value the url. """
        label = self._metric_source.metric_source_name if self._metric_source else 'Unknown metric source'
        urls = [url for url in self._metric_source_urls() if url]  # Weed out urls that are empty or None
        if len(urls) == 1:
            return {label: urls[0]}
        else:
            return {'{label} ({index}/{count})'.format(label=label, index=index, count=len(urls)): url
                    for index, url in enumerate(urls, start=1)}

    def _metric_source_urls(self):
        """ Return a list of metric source urls to be used to create the url dict. """
        if self._metric_source:
            if self._metric_source.needs_metric_source_id:
                ids = self._metric_source_id if isinstance(self._metric_source_id, list) else [self._metric_source_id]
                return self._metric_source.metric_source_urls(*[id_ for id_ in ids if id_])
            else:
                return [self._metric_source.url()]
        else:
            return []

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
        return datetime.datetime.now() - last_measurement_date if last_measurement_date else datetime.timedelta.max

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
        """ Return a comment on the metric. The comment is retrieved from either the technical debt or the subject. """
        comments = [comment for comment in (self.__technical_debt_comment(), self.__subject_comment()) if comment]
        return ' '.join(comments)

    @classmethod
    def comment_url_label(cls):
        """ Return the label for the comment urls. """
        return cls.comment_url_label_text

    @utils.memoized
    def __subject_comment(self):
        """ Return the comment of the subject about this metric, if any. """
        try:
            return self._subject.metric_options(self.__class__)['comment']
        except (AttributeError, TypeError, KeyError):
            return ''

    @utils.memoized
    def __technical_debt_comment(self):
        """ Return the comment of the accepted technical debt, if any. """
        td_target = self.__technical_debt_target()
        return td_target.explanation(self.unit) if td_target else ''

    def comment_urls(self):  # pylint: disable=no-self-use
        """ Return the source for the comment on the metric. """
        return dict()

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
        return (minimum - 1, maximum + 1) if minimum == maximum else (minimum, maximum)

    def numerical_value(self):
        """ Return a numerical version of the metric value for use in graphs. By default this simply returns the
            regular value, assuming it is already numerical. Metrics that don't have a numerical value by default
            can override this method to convert the non-numerical value into a numerical value. """
        return self.value()

    def __subject_name(self):
        """ Return the subject name, or a string representation if the subject has no name. """
        try:
            return self._subject.name()
        except AttributeError:
            return str(self._subject)
