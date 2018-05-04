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


import json
import logging
import re
from typing import cast, Dict, Any, Tuple, Type

from . import base_formatter
from .. import metric_source, VERSION
from ..report import QualityReport
from ..domain import Metric, DomainObject, MetricSource


class JSONFormatter(base_formatter.Formatter):
    """ Format the report in JSON. This is used for generating a history file. """

    def prefix(self, report: QualityReport) -> str:
        """ Return a JSON formatted version of the report prefix. """
        prefix_elements = []
        # Add the product versions of trunk versions to the prefix
        for product in report.products():
            sonar_id = report.sonar_id(product)[1]
            latest_version = report.latest_product_version(product)
            prefix_elements.append('"{sonar_id}-version": "{version}"'.format(sonar_id=sonar_id,
                                                                              version=latest_version))
        # Add the current date to the prefix
        prefix_elements.append('"date": "{date}"'.format(date=report.date().strftime('%Y-%m-%d %H:%M:%S')))
        return '{' + ', '.join(prefix_elements) + ', '

    def metric(self, metric: Metric) -> str:
        """ Return a JSON formatted version of the metric. """
        # Write numerical values without decimals.
        logging.info('Formatting metric %s.', metric.stable_id())
        try:
            return '"{sid}": ("{val:.0f}", "{stat}", "{date}"), '.format(sid=metric.stable_id(),
                                                                         val=metric.numerical_value(),
                                                                         stat=metric.status(),
                                                                         date=metric.status_start_date())
        except ValueError:
            logging.critical('Error formatting %s', metric.stable_id())
            raise

    @staticmethod
    def postfix() -> str:
        """ Return a JSON formatted version of the report postfix. """
        return '}\n'


class MetaMetricsHistoryFormatter(base_formatter.Formatter):
    """ Format the history of the meta metrics as a Javascript array. """

    def prefix(self, report: QualityReport) -> str:
        return '['

    @staticmethod
    def postfix() -> str:
        return ']\n'

    def metric(self, metric: Metric) -> str:
        return ''  # pragma: no cover

    def body(self, report: QualityReport) -> str:
        """ Return a JSON array of dates and status counts. """
        history_table = []
        for history in report.project().metric_sources(metric_source.History):
            history = cast(metric_source.History, history)
            for status_record in history.statuses():
                date_and_time = '[{0}, {1}, {2}, {3}, {4}, {5}]'.format(*self.__date_and_time(status_record))
                counts = '[{0}, {1}, {2}, {3}, {4}, {5}, {6}]'.format(*self.__status_record_counts(status_record))
                history_table.append('[{0}, {1}]'.format(date_and_time, counts))
        return ',\n'.join(history_table)

    @staticmethod
    def __date_and_time(history_record: Dict[str, str]) -> Tuple[str, str, str, str, str, str]:
        """ Return the date and time of the history record. Remove leading zero from date/time elements (assuming all
            elements are 2 digits long). Turn month into zero-based value for usage within Javascript. """
        year, month, day, hour, minute, second = re.split(r' 0?|:0?|-0?|\.0?', history_record['date'])[:6]
        month = str(int(month) - 1)  # Months are zero based
        return year, month, day, hour, minute, second

    @staticmethod
    def __status_record_counts(history_record: Dict[str, int],
                               statuses=('perfect', 'green', 'red', 'yellow', 'grey', 'missing', 'missing_source')) -> \
            Tuple[int, ...]:
        """ Return the counts per measurement status in the history record. """
        return tuple(history_record.get(status, 0) for status in statuses)


class MetricsFormatter(base_formatter.Formatter):
    """ Format the metrics as a JavaScript array. """

    sep = ', '
    columns = '''{{"id_value": "{metric_number}", "id_format": "{metric_id}", "stable_metric_id": "{stable_id}", \
"name": "{name}", "unit": "{unit}", "section": "{section}", "status": "{status}", "status_value": "{status_nr}", \
"status_start_date": {status_start_date}, "measurement": "{text}", "norm": "{norm}", "comment": "{comment}", \
"metric_class": "{class}", "extra_info": {extra_info}}}'''
    kwargs_by_status: Dict[str, Any] = dict(red=dict(status_nr=0), yellow=dict(status_nr=1), green=dict(status_nr=2),
                                            perfect=dict(status_nr=3), grey=dict(status_nr=4),
                                            missing=dict(status_nr=5), missing_source=dict(status_nr=6))

    def prefix(self, report: QualityReport) -> str:
        return '{{"report_date": {report_date}, "report_title": "{report_title}", ' \
               '"hq_version": "{version}", "sections": [{sections}], "dashboard": {dashboard}, ' \
               '"metrics": ['.format(report_date=self.__report_date(report), report_title=report.title(),
                                     sections=self.__sections(report), dashboard=self.__dashboard(report),
                                     version=VERSION)

    @staticmethod
    def postfix() -> str:
        return ']}\n'

    def metric(self, metric: Metric) -> str:
        data = self.__metric_data(metric)
        metric_number = int(data['metric_id'].split('-')[1])
        data['metric_number'] = '{sec}-{num:02d}'.format(sec=data['section'], num=metric_number)
        return self.columns.format(**data)

    def __metric_data(self, metric: Metric) -> Dict[str, Any]:
        """ Return the metric data as a dictionary, so it can be used in string templates. """
        status = metric.status()
        status_start_date = metric.status_start_date()
        extra_info = metric.extra_info()
        kwargs = self.kwargs_by_status[status].copy()
        kwargs['status'] = status
        kwargs['status_start_date'] = self.__date_array(status_start_date) if status_start_date else []
        kwargs['metric_id'] = metric.id_string()
        kwargs['stable_id'] = metric.normalized_stable_id()
        kwargs['name'] = metric.name
        kwargs['unit'] = metric.unit
        kwargs['section'] = metric.id_string().split('-')[0]
        kwargs['norm'] = metric.norm()
        kwargs['text'] = metric.format_text_with_links(metric.report())
        kwargs['comment'] = Metric.format_comment_with_links(metric.comment(), metric.comment_urls(),
                                                             metric.comment_url_label_text)
        kwargs["class"] = metric.__class__.__name__
        kwargs['extra_info'] = '{}' if extra_info is None else json.dumps(extra_info.__dict__)
        return kwargs

    @classmethod
    def __report_date(cls, report: QualityReport) -> str:
        """ Return a Javascript version of the report date. """
        return cls.__date_array(report.date())

    @staticmethod
    def __date_array(date_time):
        """ Return a JSON array representing the date. """
        return '[{0}, {1}, {2}, {3}, {4}, {5}]'.format(date_time.year, date_time.month, date_time.day,
                                                       date_time.hour, date_time.minute, date_time.second)

    @classmethod
    def __sections(cls, report: QualityReport) -> str:
        """ Return a JSON list of the report sections. """
        return ', '.join(['{{"id": "{id_}", "title": "{title}", "subtitle": "{subtitle}", '
                          '"latest_change_date": "{latest_change_date}"}}'.format(
                              id_=section.id_prefix(), title=section.title(), subtitle=section.subtitle(),
                              latest_change_date=report.latest_product_change_date(section.product()))
                          for section in report.sections()])

    @classmethod
    def __dashboard(cls, report: QualityReport) -> str:
        """ Return a JSON representation of the report dashboard. """
        return '{{"headers": {headers}, "rows": {rows}}}'.format(headers=cls.__dashboard_headers(report),
                                                                 rows=cls.__dashboard_rows(report))

    @classmethod
    def __dashboard_headers(cls, report: QualityReport) -> str:
        """ Return the headers of the dashboard. """
        return '[' + ', '.join(['{{"header": "{0}", "colspan": {1}}}'.format(section_type, colspan)
                                for section_type, colspan in report.dashboard()[0]]) + ']'

    @classmethod
    def __dashboard_rows(cls, report: QualityReport) -> str:
        """ Return the rows of the dashboard. """
        rows = []
        for row in report.dashboard()[1]:
            cells = []
            for cell in row:
                section_id = cell[0].short_name() if isinstance(cell[0], DomainObject) else cell[0].upper()
                section = report.get_section(section_id)
                if section:
                    section_title = section.title()
                else:  # No section found, use the text in the cell as header.
                    section_id = ''
                    section_title = cast(str, cell[0])
                bgcolor = cell[1]
                colspan, rowspan = cell[2] if len(cell) == 3 else (1, 1)
                cells.append('{{"section_id": "{0}", "section_title": "{1}", "bgcolor": "{2}", "colspan": {3}, '
                             '"rowspan": {4}}}'.format(section_id, section_title, bgcolor, colspan, rowspan))
            rows.append('[' + ', '.join(cells) + ']')
        return '[' + ', '.join(rows) + ']'


class MetaDataJSONFormatter(object):
    """ Return the domain objects in the report formatted as JSON. """

    @classmethod
    def process(cls, report: QualityReport) -> str:
        """ Return a JSON representation of the domain objects. """
        return '{"domain_objects": [' + cls.__format_domain_object_classes(report) + '], "requirements": [' + \
               cls.__format_requirement_classes(report) + '], "metrics": [' + cls.__format_metric_classes(report) + \
               '], "metric_sources": [' + cls.__format_metric_sources(report) + ']}\n'

    @classmethod
    def __format_domain_object_classes(cls, report: QualityReport) -> str:
        """ Return the domain object classes as JSON list. """
        domain_object_classes = sorted(report.domain_object_classes(), key=lambda klass: klass.__name__)
        return ', '.join([cls.__format_domain_object_class(report, domain_object_class)
                          for domain_object_class in domain_object_classes])

    @classmethod
    def __format_domain_object_class(cls, report: QualityReport, domain_object_class) -> str:
        """ Return the domain object as JSON. """
        included = 'true' if domain_object_class in report.included_domain_object_classes() else 'false'
        name = domain_object_class.__name__
        id_ = domain_object_class.__name__
        default_requirements = ', '.join(
            sorted('"{0}"'.format(req.name()) for req in domain_object_class.default_requirements()))
        optional_requirements = ', '.join(
            sorted('"{0}"'.format(req.name()) for req in domain_object_class.optional_requirements()))
        return '{{"included": {0}, "name": "{1}", "id": "{2}", "default_requirements": [{3}], ' \
               '"optional_requirements": [{4}]}}'.format(included, name, id_, default_requirements,
                                                         optional_requirements)

    @classmethod
    def __format_requirement_classes(cls, report: QualityReport) -> str:
        """ Return the requirements as JSON list. """
        requirement_classes = sorted(report.requirement_classes(), key=lambda klass: klass.name())
        return ', '.join([cls.__format_requirement_class(report, requirement_class)
                          for requirement_class in requirement_classes])

    @classmethod
    def __format_requirement_class(cls, report: QualityReport, requirement_class) -> str:
        """ Return the requirement as JSON. """
        included = 'true' if requirement_class in report.included_requirement_classes() else 'false'
        name = requirement_class.name()
        id_ = requirement_class.__name__
        metric_classes = ', '.join(sorted('"{0}"'.format(metric_class.name)
                                          for metric_class in requirement_class.metric_classes()))
        return '{{"included": {0}, "name": "{1}", "id": "{2}", "metrics": [{3}]}}'.format(included, name, id_,
                                                                                          metric_classes)

    @classmethod
    def __format_metric_classes(cls, report: QualityReport) -> str:
        """ Return the metrics as JSON list. """
        metric_classes = sorted(report.metric_classes(), key=lambda klass: klass.name)
        return ', '.join([cls.__format_metric_class(report, metric_class) for metric_class in metric_classes])

    @classmethod
    def __format_metric_class(cls, report: QualityReport, metric_class) -> str:
        """ Return the metric as JSON. """
        included = 'true' if metric_class in report.included_metric_classes() else 'false'
        name = metric_class.name
        id_ = metric_class.__name__
        try:
            norm = metric_class.norm_template.format(**metric_class.norm_template_default_values())
        except ValueError as reason:
            logging.critical("Metric class %s has faulty norm template: %s", metric_class.__name__, reason)
            raise
        return '{{"included": {0}, "name": "{1}", "id": "{2}", "norm": "{3}"}}'.format(included, name, id_, norm)

    @classmethod
    def __format_metric_sources(cls, report: QualityReport) -> str:
        """ Return the metric sources as JSON list. """
        metric_sources = sorted(report.metric_source_classes(), key=lambda klass: klass.metric_source_name)
        return ', '.join([cls.__format_metric_source(report, metric_source_class)
                          for metric_source_class in metric_sources])

    @classmethod
    def __format_metric_source(cls, report: QualityReport, metric_source_class: Type[MetricSource]) -> str:
        """ Return the metric source as JSON. """
        included = 'true' if metric_source_class in report.included_metric_source_classes() else 'false'
        name = metric_source_class.metric_source_name
        id_ = metric_source_class.__name__
        instances = report.project().metric_sources(metric_source_class)
        urls = ', '.join(sorted(['"{0}"'.format(instance.url()) for instance in instances if instance.url()]))
        return '{{"included": {0}, "name": "{1}", "id": "{2}", "urls": [{3}]}}'.format(included, name, id_, urls)
