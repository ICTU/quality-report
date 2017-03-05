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

import logging
import pkg_resources

from . import base_formatter
from .. import utils


class HTMLFormatter(base_formatter.Formatter):
    """ Format the report in HTML. """

    column_list = [u"{{f: '{metric_id}', v: '{metric_number}'}}",
                   u"'{section}'",
                   u"'{status}'",
                   u"""'<img src="img/{metric_id}.png" border="0" width="100" height="25" />'""",
                   u"""{{v: '{status_nr}', f: '<img src="img/{image}.png" """
                   u"""alt="{alt}" width="48" height="48" title="{hover}" """
                   u"""border="0" />'}}""",
                   u"'{text}'",
                   u"'{norm}'",
                   u"'{comment}'"]
    columns = u'[' + u', '.join(column_list) + u']'
    kwargs_by_status = dict(
        red=dict(image='sad', alt=':-(', status_nr=0,
                 hover='Direct actie vereist: norm niet gehaald'),
        yellow=dict(image='plain', alt=':-|', status_nr=1, hover='Bijna goed: norm net niet gehaald'),
        green=dict(image='smile', alt=':-)', status_nr=2, hover='Goed: norm gehaald'),
        perfect=dict(image='biggrin', alt=':-D', status_nr=3, hover='Perfect: score kan niet beter'),
        grey=dict(image='ashamed', alt=':-o', status_nr=4, hover='Technische schuld: lossen we later op'),
        missing=dict(image='missing', alt='x', status_nr=5, hover='Ontbrekend: metriek kan niet gemeten worden'),
        missing_source=dict(image='missing_source', alt='%', status_nr=6,
                            hover='Ontbrekend: niet alle benodigde bronnen zijn geconfigureerd'))

    def __init__(self, *args, **kwargs):
        self.__latest_software_version = kwargs.pop('latest_software_version', '0')
        self.__current_software_version = kwargs.pop('current_software_version', '0')
        super(HTMLFormatter, self).__init__(*args, **kwargs)

    def prefix(self, report):
        """ Return a HTML formatted version of the report prefix. """
        parameters = dict(
            title=report.title(),
            date=report.date().strftime('%d-%m-%y %H:%M'),
            current_version=self.__current_software_version,
            new_version_available=self.__new_release_text())
        parameters['section_menu'] = self.__section_navigation_menu(report)
        parameters['dashboard'] = DashboardFormatter.format(report)
        parameters['domain_object_classes'] = self.__domain_object_classes(report)
        parameters['metric_classes'] = self.__metric_classes(report)
        parameters['metric_sources'] = self.__metric_sources(report)
        parameters['requirements'] = self.__requirements(report)
        parameters['report_date'] = self.__report_date(report)

        metrics = []
        for metric in report.metrics():
            data = self.__metric_data(metric)
            metric_number = int(data['metric_id'].split('-')[1])
            data['metric_number'] = '{sec}-{num:02d}'.format(sec=data['section'], num=metric_number)
            metrics.append(self.columns.format(**data))
        parameters['metrics'] = '[' + ',\n'.join(metrics) + ']'
        prefix = self.__get_html_fragment('prefix')
        return prefix.format(**parameters)

    @staticmethod
    def __get_html_fragment(name):
        """ Read and return a HTML fragment from the html folder. """
        fragment = pkg_resources.ResourceManager().resource_string(__name__, 'html/{name}.html'.format(name=name))
        return unicode(fragment)

    def section(self, report, section):
        """ Return a HTML formatted version of the section. """
        subtitle = self.__format_subtitle(section.subtitle())
        extra = '<div id="meta_metrics_history_relative_graph"></div>\n' \
                '<div id="meta_metrics_history_absolute_graph"></div>' if section.id_prefix() == 'MM' else ''
        parameters = dict(title=section.title(), id=section.id_prefix(), subtitle=subtitle, extra=extra)
        return self.__get_html_fragment('section').format(**parameters)

    def metric(self, metric):
        """ Return a HTML formatted version of the metric. """
        return ''  # pragma: no cover

    @staticmethod
    def __section_navigation_menu(report):
        """ Return the menu for jumping to specific sections. """
        menu_items = []

        menu_item_template = '<li><a class="link_section_{section_id}" href="#section_{section_id}">{menu_label}</a>' \
                             '</li>'

        def add_menu_item(section, title):
            """ Add a menu item that links to the specified section. """
            menu_items.append(menu_item_template.format(section_id=section.id_prefix(), menu_label=title))

        def add_menu_items(sections):
            """ Add a header with menu items that link to the specified sections. """
            for each_section in sections:
                add_menu_item(each_section, each_section.title() + ' ' + each_section.subtitle())

        # First, group related sections
        sections = {}
        titles = []
        for section in report.sections():
            title = section.title()
            sections.setdefault(title, []).append(section)
            if title not in titles:
                titles.append(title)
        # Next, create the menu items
        for title in titles:
            if len(sections[title]) == 1:
                section = sections[title][0]
                add_menu_item(section, section.title())
            else:
                add_menu_items(sections[title])
        # Finally, return the HTML as one string
        return '\n'.join(menu_items)

    def __metric_data(self, metric):
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
    def __report_date(cls, report):
        """ Return a Javascript version of the report date. """
        date_time = report.date()
        return 'new Date({0}, {1}, {2}, {3}, {4}, {5})'.format(date_time.year, date_time.month - 1, date_time.day,
                                                               date_time.hour, date_time.minute, date_time.second)

    @staticmethod
    def postfix():
        """ Return a HTML formatted version of the report postfix. """
        return HTMLFormatter.__get_html_fragment('postfix')

    @classmethod
    def __format_text_with_links(cls, text, url_dict, url_label):
        """ Format a text paragraph with optional urls and label for the urls. """
        text = utils.html_escape(text)
        links = [cls.__format_url(anchor, href) for (anchor, href) in url_dict.items()]
        if links:
            if url_label:
                url_label += ': '
            text = u'{0} [{1}{2}]'.format(text, url_label, ', '.join(sorted(links)))
        return text

    @staticmethod
    def __format_subtitle(subtitle):
        """ Return a HTML formatted subtitle. """
        template = u' <small>{sub}</small>'
        return template.format(sub=subtitle) if subtitle else ''

    @staticmethod
    def __format_url(anchor, href):
        """ Return a HTML formatted url. """
        template = u'<a href="{href}" target="_blank">{anchor}</a>'
        return template.format(href=href, anchor=utils.html_escape(anchor))

    @staticmethod
    def __metric_classes(report):
        """ Return a HTML table of the metrics the software can measure. """
        row = '  <tr><td>{icon}</td><td>{name} (<code><small>{id}</small></code>)</td><td>{norm}</td></tr>'
        icon_span = '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>'
        result = list()
        result.append('<table class="table table-striped first-col-centered">\n  <tr><th>In dit rapport?</th>'
                      '<th>Metriek (<code><small>Identifier</small></code>)</th><th>Norm</th></tr>')
        for metric_class in report.metric_classes():
            name = metric_class.name
            identifier = metric_class.__name__
            icon = icon_span if metric_class in report.included_metric_classes() else ''
            try:
                norm = metric_class.norm_template.format(**metric_class.norm_template_default_values())
            except ValueError:
                logging.error('Metric class %s had faulty norm template', metric_class.__name__)
                raise
            result.append(row.format(icon=icon, name=name, id=identifier, norm=norm))
        result.append('</table>')
        return '\n'.join(result)

    @staticmethod
    def __metric_sources(report):
        """ Return a HTML table of the metric sources the software can collect data from. """
        row = '  <tr><td>{icon}</td><td>{name} (<code><small>{id}</small></code>)</td><td>{ins}</td></tr>'
        icon_span = '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>'
        anchor = '<a href="{url}" target="_blank">{url}</a>'
        result = list()
        result.append('<table class="table table-striped first-col-centered">\n  <tr><th>In dit rapport?</th>'
                      '<th>Metriekbron (<code><small>Identifier</small></code>)</th><th>Instanties</th></tr>')
        for metric_source_class in report.metric_source_classes():
            name = metric_source_class.metric_source_name
            identifier = metric_source_class.__name__
            icon = icon_span if metric_source_class in report.included_metric_source_classes() else ''
            instances = report.project().metric_source(metric_source_class)
            instances = instances if isinstance(instances, list) else [instances]
            instances = '<br>'.join([anchor.format(url=instance.url()) for instance in instances if instance.url()])
            result.append(row.format(icon=icon, name=name, id=identifier, ins=instances))
        result.append('</table>')
        return '\n'.join(result)

    @staticmethod
    def __requirements(report):
        """ Return a HTML table of the requirements. """
        row = '  <tr><td>{icon}</td><td>{name} (<code><small>{id}</small></code>)</td><td>{metrics}</td></tr>'
        icon_span = '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>'
        result = list()
        result.append('<table class="table table-striped first-col-centered">\n  <tr><th>In dit rapport?</th>'
                      '<th>Eis (<code><small>Identifier</small></code>)</th><th>Metrieken</th></tr>')
        for requirement_class in report.requirement_classes():
            name = requirement_class.name()
            identifier = requirement_class.__name__
            metrics = ', '.join(metric_class.name for metric_class in requirement_class.metric_classes())
            icon = icon_span if requirement_class in report.included_requirement_classes() else ''
            result.append(row.format(icon=icon, name=name, id=identifier, metrics=metrics))
        result.append('</table>')
        return '\n'.join(result)

    @staticmethod
    def __domain_object_classes(report):
        """ Return a HTML table of the domain objects. """
        row = '  <tr><td>{icon}</td><td>{name} (<code><small>{id}</small></code>)</td><td>{default_requirements}</td>' \
              '<td>{optional_requirements}</td></tr>'
        icon_span = '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>'
        result = list()
        result.append('<table class="table table-striped first-col-centered">\n  <tr><th>In dit rapport?</th>'
                      '<th>Domeinobject (<code><small>Identifier</small></code>)</th><th>Default eisen</th>'
                      '<th>Optionele eisen</th></tr>')
        for domain_object_class in report.domain_object_classes():
            name = identifier = domain_object_class.__name__
            default_requirements = ', '.join(req.name() for req in domain_object_class.default_requirements())
            optional_requirements = ', '.join(req.name() for req in domain_object_class.optional_requirements())
            icon = icon_span if domain_object_class in report.included_domain_object_classes() else ''
            result.append(row.format(icon=icon, name=name, id=identifier, default_requirements=default_requirements,
                                     optional_requirements=optional_requirements))
        result.append('</table>')
        return '\n'.join(result)

    def __new_release_text(self):
        """ Return a line of text if there is a new version of the software available. """
        latest = self.__latest_software_version
        current = self.__current_software_version
        return ' Versie {ver} is beschikbaar.'.format(ver=latest) if latest > current else ''


class DashboardFormatter(object):  # pylint: disable=too-few-public-methods
    """ Return a HTML formatted dashboard for the quality report. """
    @classmethod
    def format(cls, report):
        """ Return a HTML formatted dashboard. """
        table_indent = ' ' * 24
        thead_indent = tbody_indent = table_indent + ' ' * 4
        tr_indent = thead_indent + ' ' * 4
        td_indent = tr_indent + ' ' * 4

        dashboard = list()
        dashboard.append(table_indent + '<table class="table table-condensed table-bordered">')
        dashboard.append(thead_indent + '<thead>')
        dashboard.extend(cls.__dashboard_headers(report, tr_indent, td_indent))
        dashboard.append(thead_indent + '</thead>')
        dashboard.append(tbody_indent + '<tbody>')
        dashboard.extend(cls.__dashboard_rows(report, tr_indent, td_indent))
        dashboard.append(tbody_indent + '</tbody>')
        dashboard.append(table_indent + '</table>')
        return '\n'.join(dashboard)

    @staticmethod
    def __dashboard_headers(report, tr_indent, td_indent):
        """ Return the headers of the dashboard. """
        dashboard_headers = report.dashboard()[0]
        th_template = td_indent + '<th colspan="{span}" style="text-align: center;">{sec}</th>'
        rows = list()
        rows.append(tr_indent + '<tr style="color: white; font-weight: bold; background-color: #2F95CF;">')
        for section_type, colspan in dashboard_headers:
            table_header = th_template.format(span=colspan, sec=section_type)
            rows.append(table_header)
        rows.append(tr_indent + '</tr>')
        return rows

    @classmethod
    def __dashboard_rows(cls, report, tr_indent, td_indent):
        """ Return the rows of the dashboard. """
        dashboard_rows = report.dashboard()[1]
        rows = list()
        for row in dashboard_rows:
            rows.append(tr_indent + '<tr>')
            for column in row:
                rows.append(cls.__dashboard_cell(report, column, td_indent))
            rows.append(tr_indent + '</tr>')
        return rows

    @staticmethod
    def __dashboard_cell(report, column, td_indent):
        """ Return a cell of the dashboard. """
        td_template = td_indent + \
            '''<td colspan={colspan} rowspan={rowspan} align="center" bgcolor="{bg_color}">
                                        <div class="link_section_{ID}" title="{title}"></div>
                                        <div id="section_summary_chart_{ID}"></div>
                                    </td>
'''
        try:
            section_id = column[0].short_name()
        except AttributeError:
            section_id = column[0].upper()
        section = report.get_section(section_id)
        title = section.title() if section else '???'
        colspan, rowspan = column[2] if len(column) == 3 else (1, 1)
        return td_template.format(ID=section_id, title=title, bg_color=column[1], colspan=colspan, rowspan=rowspan)
