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


import json
import logging
import re
from typing import Dict, Any, Tuple

from . import base_formatter
from .. import metric_source, utils, VERSION
from ..report import QualityReport
from ..domain import Metric, DomainObject


class JSONFormatter(base_formatter.Formatter):
    """ Format the report in JSON. This is used for generating a history file. """

    def prefix(self, report: QualityReport) -> str:
        """ Return a JSON formatted version of the report prefix. """
        prefix_elements = []
        # Add the product versions of trunk versions to the prefix
        sonar = report.project().metric_source(metric_source.Sonar)
        for product in report.products():
            sonar_id = product.metric_source_id(sonar) or ''
            latest_version = sonar.version(sonar_id) if sonar_id else ''
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
            logging.error('Error formatting %s', metric.stable_id())
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
        history = report.project().metric_source(metric_source.History)
        if history:
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
    column_list = ['''{{"f": "{metric_id}", "v": "{metric_number}"}}''',
                   '''"{section}"''',
                   '''"{status}"''',
                   '''"<img src='img/{metric_id}.png' border='0' width='100' height='25' />"''',
                   '''{{"v": "{status_nr}", "f": "<img src='img/{image}.png' '''
                   '''alt='{alt}' width='48' height='48' title='{hover}' '''
                   '''border='0' />"}}''',
                   '''"{text}"''',
                   '''"{norm}"''',
                   '''"{comment}"''']
    columns = '[' + ', '.join(column_list) + ']'
    kwargs_by_status: Dict[str, Any] = dict(
        red=dict(image='sad', alt=':-(', status_nr=0, hover='Direct actie vereist: norm niet gehaald'),
        yellow=dict(image='plain', alt=':-|', status_nr=1, hover='Bijna goed: norm net niet gehaald'),
        green=dict(image='smile', alt=':-)', status_nr=2, hover='Goed: norm gehaald'),
        perfect=dict(image='biggrin', alt=':-D', status_nr=3, hover='Perfect: score kan niet beter'),
        grey=dict(image='ashamed', alt=':-o', status_nr=4, hover='Technische schuld: lossen we later op'),
        missing=dict(image='missing', alt='x', status_nr=5, hover='Ontbrekend: metriek kan niet gemeten worden'),
        missing_source=dict(image='missing_source', alt='%', status_nr=6,
                            hover='Ontbrekend: niet alle benodigde bronnen zijn geconfigureerd'))

    def prefix(self, report: QualityReport) -> str:
        return '{{"report_date": {report_date}, "report_title": "{report_title}", ' \
               '"hq_version": "{version}", "sections": [{sections}], "dashboard": {dashboard}, "metrics": ['.format(
            report_date=self.__report_date(report), report_title=report.title(), sections=self.__sections(report),
            dashboard=self.__dashboard(report), version=VERSION)

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
        kwargs = self.kwargs_by_status[status].copy()
        kwargs['hover'] += ' (sinds {date})'.format(date=utils.format_date(metric.status_start_date(), year=True))
        kwargs['status'] = status
        kwargs['metric_id'] = metric.id_string()
        kwargs['section'] = metric.id_string().split('-')[0]
        kwargs['norm'] = metric.norm()
        kwargs['text'] = self.__format_text_with_links(metric.report(), metric.url(), metric.url_label_text)
        kwargs['comment'] = self.__format_text_with_links(metric.comment(), metric.comment_urls(),
                                                          metric.comment_url_label_text)
        return kwargs

    @classmethod
    def __format_text_with_links(cls, text: str, url_dict: Dict[str, str], url_label: str) -> str:
        """ Format a text paragraph with optional urls and label for the urls. """
        text = utils.html_escape(text).replace('\n', ' ')
        links = [cls.__format_url(anchor, href) for (anchor, href) in list(url_dict.items())]
        if links:
            if url_label:
                url_label += ': '
            text = '{0} [{1}{2}]'.format(text, url_label, ', '.join(sorted(links)))
        return json.dumps(text)[1:-1]  # Strip quotation marks

    @staticmethod
    def __format_url(anchor: str, href: str) -> str:
        """ Return a HTML formatted url. """
        template = "<a href='{href}' target='_blank'>{anchor}</a>"
        return template.format(href=href, anchor=utils.html_escape(anchor))

    @classmethod
    def __report_date(cls, report: QualityReport) -> str:
        """ Return a Javascript version of the report date. """
        date_time = report.date()
        return '[{0}, {1}, {2}, {3}, {4}, {5}]'.format(date_time.year, date_time.month - 1, date_time.day,
                                                       date_time.hour, date_time.minute, date_time.second)

    @classmethod
    def __sections(cls, report: QualityReport) -> str:
        """ Return a JSON list of the report sections. """
        return ', '.join(['{{"id": "{id_}", "title": "{title}", "subtitle": "{subtitle}"}}'.format(
            id_=section.id_prefix(), title=section.title(), subtitle=section.subtitle())
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
                section_title = section.title() if section else '???'
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
        except ValueError:
            logging.error('Metric class %s has faulty norm template', metric_class.__name__)
            raise
        return '{{"included": {0}, "name": "{1}", "id": "{2}", "norm": "{3}"}}'.format(included, name, id_, norm)

    @classmethod
    def __format_metric_sources(cls, report: QualityReport) -> str:
        """ Return the metric sources as JSON list. """
        metric_sources = sorted(report.metric_source_classes(), key=lambda klass: klass.metric_source_name)
        return ', '.join([cls.__format_metric_source(report, metric_source) for metric_source in metric_sources])

    @classmethod
    def __format_metric_source(cls, report: QualityReport, metric_source) -> str:
        """ Return the metric source as JSON. """
        included = 'true' if metric_source in report.included_metric_source_classes() else 'false'
        name = metric_source.metric_source_name
        id_ = metric_source.__name__
        instances = report.project().metric_source(metric_source)
        instances = instances if isinstance(instances, list) else [instances]
        urls = ', '.join(sorted(['"{0}"'.format(instance.url()) for instance in instances if instance.url()]))
        return '{{"included": {0}, "name": "{1}", "id": "{2}", "urls": [{3}]}}'.format(included, name, id_, urls)
