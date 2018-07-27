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

from typing import cast, Dict, List, Optional, Type, Tuple, TYPE_CHECKING
import json
import re

import datetime
import functools
import logging

from hqlib import utils
from hqlib.typing import MetricParameters, MetricValue, DateTime, Number
from .metric_source import MetricSource
from .target import AdaptedTarget
if TYPE_CHECKING:  # pragma: no cover
    from ..software_development.project import Project  # pylint: disable=unused-import


class ExtraInfo(object):
    """ The class represents extra metric information structure, that is serialized to extra_info json tag."""
    def __init__(self, **kwargs):
        """ Class is initialized with column keys and header texts."""
        self.headers = kwargs
        self.title = None
        self.data = []

    def __add__(self, *args):
        """ Adds data rows to the extra_info table, matching arguments by position to the column keys."""
        item = args[0] if isinstance(args[0], tuple) else args
        dictionary_length = len(self.headers)
        for i in range(len(item) // dictionary_length):
            self.data.append(dict(zip(self.headers.keys(), item[dictionary_length * i:dictionary_length * (i + 1)])))
        return self

    @staticmethod
    def format_extra_info_link(url: str, text: str):
        """ Formats extra info link dictionary. """
        return {"href": url, "text": text}


class Metric(object):
    """ Base class for metrics. """

    name: str = 'Subclass responsibility'
    template = '{name} heeft {value} {unit}.'
    norm_template: str = 'Subclass responsibility'
    unit: str = 'Subclass responsibility'  # Unit in plural, e.g. "lines of code"

    target_value: MetricValue = 'Subclass responsibility'
    low_target_value: MetricValue = 'Subclass responsibility'
    perfect_value: MetricValue = 'Subclass responsibility'

    missing_template: str = 'De {metric} van {name} kon niet gemeten worden omdat niet alle benodigde bronnen ' \
                            'beschikbaar zijn.'
    missing_source_template: str = 'De {metric} van {name} kon niet gemeten worden omdat de bron ' \
                                   '{metric_source_class} niet is geconfigureerd.'
    missing_source_id_template: str = 'De {metric} van {name} kon niet gemeten worden omdat niet alle benodigde ' \
                                      'bron-ids zijn geconfigureerd. Configureer ids voor de bron ' \
                                      '{metric_source_class}.'
    perfect_template: str = ''

    url_label_text: str = ''
    comment_url_label_text: str = ''

    metric_source_class: Type[MetricSource] = None
    extra_info_headers: Dict[str, str] = None

    def __init__(self, subject=None, project: 'Project' = None) -> None:
        self._subject = subject
        self._project = project
        for source in self._project.metric_sources(self.metric_source_class):
            try:
                source_id = self._subject.metric_source_id(source)
            except AttributeError:
                continue
            if source_id:
                self._metric_source = source
                self._metric_source_id = source_id
                break
        else:
            if self.metric_source_class:
                logging.warning("Couldn't find metric source of class %s for %s", self.metric_source_class.__name__,
                                self.stable_id())
            self._metric_source = None
            self._metric_source_id = None
        self.__id_string = self.stable_id()
        self._extra_info_data = list()
        from hqlib import metric_source
        history_sources = self._project.metric_sources(metric_source.History) if self._project else []
        self.__history = cast(metric_source.History, history_sources[0]) if history_sources else None

    def format_text_with_links(self, text: str) -> str:
        """ Format a text paragraph with additional url. """
        return Metric.format_comment_with_links(text, self.url(), '')

    @staticmethod
    def format_comment_with_links(text: str, url_dict: Dict[str, str],  # pylint: disable=no-self-use
                                  url_label: str) -> str:
        """ Format a text paragraph with optional urls and label for the urls. """
        comment_text = Metric._format_links_in_comment_text(text)
        links = ["<a href='{href}' target='_blank'>{anchor}</a>"
                 .format(href=href, anchor=utils.html_escape(anchor)) for (anchor, href) in list(url_dict.items())]
        if links:
            if url_label:
                url_label += ': '
            comment_text = '{0} [{1}{2}]'.format(comment_text, url_label, ', '.join(sorted(links)))
        return json.dumps(comment_text)[1:-1]  # Strip quotation marks

    @staticmethod
    def _format_links_in_comment_text(text: str) -> str:
        url_pattern = re.compile(r'(?i)\b(http(?:s?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]|'
                                 r'\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|'
                                 r'[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')
        return re.sub(url_pattern, r"<a href='\1' target='_blank'>\1</a>", utils.html_escape(text).replace('\n', ' '))

    @classmethod
    def norm_template_default_values(cls) -> MetricParameters:
        """ Return the default values for parameters in the norm template. """
        return dict(unit=cls.unit, target=cls.target_value, low_target=cls.low_target_value)

    def is_applicable(self) -> bool:  # pylint: disable=no-self-use
        """ Return whether this metric applies to the specified subject. """
        return True

    @functools.lru_cache(maxsize=1024)
    def normalized_stable_id(self):
        """ Returns stable_id where non-alphanumerics are substituted by _ and codes of other characters are added. """
        return "".join([c if c.isalnum() else "_" for c in self.stable_id()]) + '_' + \
               "".join(['' if c.isalnum() else str(ord(c)) for c in self.stable_id()])

    @functools.lru_cache(maxsize=1024)
    def stable_id(self) -> str:
        """ Return an id that doesn't depend on numbering/order of metrics. """
        stable_id = self.__class__.__name__
        if not isinstance(self._subject, list):
            stable_id += self._subject.name() if self._subject else str(self._subject)
        return stable_id

    def set_id_string(self, id_string: str) -> None:
        """ Set the identification string. This can be set by a client since the identification of a metric may
            depend on the section the metric is reported in. E.g. A-1. """
        self.__id_string = id_string

    def id_string(self) -> str:
        """ Return the identification string of the metric. """
        return self.__id_string

    def target(self) -> MetricValue:
        """ Return the target value for the metric. If the actual value of the
            metric is below the target value, the metric is not green. """
        subject_target = self._subject.target(self.__class__) if hasattr(self._subject, 'target') else None
        return self.target_value if subject_target is None else subject_target

    def low_target(self) -> MetricValue:
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

    @functools.lru_cache(maxsize=8 * 1024)
    def status(self) -> str:
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

    def status_start_date(self) -> DateTime:
        """ Return since when the metric has the current status. """
        return self.__history.status_start_date(self.stable_id(), self.status()) \
            if self.__history else datetime.datetime.min

    def __has_accepted_technical_debt(self) -> bool:
        """ Return whether the metric is below target but above the accepted technical debt level. """
        technical_debt_target = self.__technical_debt_target()
        if technical_debt_target:
            return self._is_below_target() and self._is_value_better_than(technical_debt_target.target_value())
        return False

    def _missing(self) -> bool:
        """ Return whether the metric source is missing. """
        return self.value() == -1

    def __missing_source_configuration(self) -> bool:
        """ Return whether the metric sources have been completely configured. """
        return self.__missing_source_class() or self.__missing_source_ids()

    def __missing_source_class(self) -> bool:
        """ Return whether a metric source class that needs to be configured for the metric to be measurable is
            available from the project. """
        return not self._project.metric_sources(self.metric_source_class) if self.metric_source_class else False

    def __missing_source_ids(self) -> bool:
        """ Return whether the metric source ids have been configured for the metric source class. """
        return bool(self.metric_source_class) and not self._get_metric_source_ids()

    def _needs_immediate_action(self) -> bool:
        """ Return whether the metric needs immediate action, i.e. its actual value is below its low target value. """
        return not self._is_value_better_than(self.low_target())

    def _is_below_target(self) -> bool:
        """ Return whether the actual value of the metric is below its target value. """
        return not self._is_value_better_than(self.target())

    def __is_perfect(self) -> bool:
        """ Return whether the actual value of the metric equals its perfect value,
            i.e. no further improvement is possible. """
        return self.value() == self.perfect_value

    def value(self) -> MetricValue:
        """ Return the actual value of the metric. """
        raise NotImplementedError

    def _is_value_better_than(self, target: MetricValue) -> bool:
        """ Return whether the actual value of the metric is better than the specified target value. """
        raise NotImplementedError

    def report(self, max_subject_length: int = 200) -> str:
        """ Return the actual value of the metric in the form of a short, mostly one sentence, report. """
        name = self.__subject_name()
        if len(name) > max_subject_length:
            name = name[:max_subject_length] + '...'
        logging.info('Reporting %s on %s', self.__class__.__name__, name)
        return self._get_template().format(**self._parameters())

    def _get_template(self) -> str:
        """ Return the template for the metric report. """
        if self.__missing_source_class():
            return self.missing_source_template
        if self.__missing_source_ids():
            return self.missing_source_id_template
        if self._missing():
            return self.missing_template
        if self.__is_perfect() and self.perfect_template:
            return self.perfect_template
        return self.template

    def _parameters(self) -> MetricParameters:
        """ Return the parameters for the metric report template and for the metric norm template. """
        return dict(name=self.__subject_name(),
                    metric=self.name[0].lower() + self.name[1:],
                    unit=self.unit,
                    target=self.target(),
                    low_target=self.low_target(),
                    value=self.value(),
                    metric_source_class=self.metric_source_class.__name__ if self.metric_source_class
                    else '<metric has no metric source defined>')

    def norm(self) -> str:
        """ Return a description of the norm for the metric. """
        try:
            return self.norm_template.format(**self._parameters())
        except KeyError as reason:
            class_name = self.__class__.__name__
            logging.critical('Key missing in %s parameters (%s) for norm template "%s": %s', class_name,
                             self._parameters(), self.norm_template, reason)
            raise

    def url(self) -> Dict[str, str]:
        """ Return a dictionary of urls for the metric. The key is the anchor, the value the url. """
        label = self._metric_source.metric_source_name if self._metric_source else 'Unknown metric source'
        urls = [url for url in self._metric_source_urls() if url]  # Weed out urls that are empty or None
        if len(urls) == 1:
            return {label: urls[0]}
        return {'{label} ({index}/{count})'.format(label=label, index=index, count=len(urls)): url
                for index, url in enumerate(urls, start=1)}

    def _metric_source_urls(self) -> List[str]:
        """ Return a list of metric source urls to be used to create the url dict. """
        if self._metric_source:
            if self._get_metric_source_ids():
                return self._metric_source.metric_source_urls(*self._get_metric_source_ids())
            return [self._metric_source.url()]
        return []

    def _get_metric_source_ids(self) -> List[str]:
        """ Allow for subclasses to override what the metric source id is. """
        ids = self._metric_source_id if isinstance(self._metric_source_id, list) else [self._metric_source_id]
        return [id_ for id_ in ids if id_]

    def comment(self) -> str:
        """ Return a comment on the metric. The comment is retrieved from either the technical debt or the subject. """
        comments = [comment for comment in (self.__non_default_target_comment(), self.__technical_debt_comment(),
                                            self.__subject_comment()) if comment]
        return ' '.join(comments)

    def __subject_comment(self) -> str:
        """ Return the comment of the subject about this metric, if any. """
        try:
            return self._subject.metric_options(self.__class__)['comment']
        except (AttributeError, TypeError, KeyError):
            return ''

    def __technical_debt_comment(self) -> str:
        """ Return the comment of the accepted technical debt, if any. """
        td_target = self.__technical_debt_target()
        return td_target.explanation(self.unit) if td_target else ''

    def __non_default_target_comment(self) -> str:
        """ Return a comment about a non-default target, if relevant. """
        return AdaptedTarget(self.low_target(), self.low_target_value).explanation(self.unit)

    def comment_urls(self) -> Dict[str, str]:  # pylint: disable=no-self-use
        """ Return the source for the comment on the metric. """
        return dict()

    def __history_records(self, method: callable) -> List[int]:
        history = method(self.stable_id()) if self.__history else []
        return [int(round(float(value))) if value is not None else None for value in history]

    def recent_history(self) -> List[int]:
        """ Return a list of recent values of the metric, to be used in e.g. a spark line graph. """
        return self.__history_records(self.__history.recent_history) if self.__history else []

    def long_history(self) -> List[int]:
        """ Return a long list of values of the metric, to be used in e.g. a spark line graph. """
        return self.__history_records(self.__history.long_history) if self.__history else []

    def get_recent_history_dates(self) -> str:
        """ Return a list of recent dates when report was generated. """
        return self.__history.get_dates() if self.__history else ""

    def get_long_history_dates(self) -> str:
        """ Return a long list of dates when report was generated. """
        return self.__history.get_dates(long_history=True) if self.__history else ""

    def y_axis_range(self) -> Tuple[int, int]:
        """ Return a two-tuple (min, max) for use in graphs. """
        history = [d for d in self.recent_history() if d is not None]
        if not history:
            return 0, 100
        minimum, maximum = min(history), max(history)
        return (minimum - 1, maximum + 1) if minimum == maximum else (minimum, maximum)

    def numerical_value(self) -> Number:
        """ Return a numerical version of the metric value for use in graphs. By default this simply returns the
            regular value, assuming it is already numerical. Metrics that don't have a numerical value by default
            can override this method to convert the non-numerical value into a numerical value. """
        value = self.value()
        if isinstance(value, tuple):
            value = value[0]
        if isinstance(value, (int, float)):
            return value
        raise NotImplementedError

    def extra_info(self) -> Optional[ExtraInfo]:
        """ Method can be overridden by concrete metrics that fill extra info. """
        extra_info = None
        if self._metric_source and self.extra_info_headers:
            url_list = self.extra_info_rows()
            if url_list:
                extra_info = self.__create_extra_info(url_list)
        return extra_info if extra_info is not None and extra_info.data else None

    def extra_info_rows(self) -> List:
        """ Returns rows of extra info table. """
        return self._extra_info_data

    def __create_extra_info(self, url_list):
        extra_info = ExtraInfo(**self.extra_info_headers)
        extra_info.title = self.url_label_text
        for item in url_list:
            extra_info += self.convert_item_to_extra_info(item)
        return extra_info

    @staticmethod
    def convert_item_to_extra_info(item):
        """ Method should transform an item to the form used in extra info. Should be overridden. """
        return item

    def __subject_name(self) -> str:
        """ Return the subject name, or a string representation if the subject has no name. """
        try:
            return self._subject.name()
        except AttributeError:
            return str(self._subject)
