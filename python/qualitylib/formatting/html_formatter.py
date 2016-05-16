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

import codecs
import datetime
import logging
import os
import re

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
                   u"'{comment}'",
                   u"'{version}'",
                   u"'{quality_attribute}'"]
    columns = u'[' + u', '.join(column_list) + u']'

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
        parameters['quality_attribute_filter_menu'] = self.__quality_attribute_filter_menu(report)
        parameters['dashboard'] = DashboardFormatter.format(report)
        parameters['project_resources'] = self.__project_resources(report)
        parameters['metric_classes'] = self.__metric_classes(report)
        parameters['history'] = self.__trend_data(report.get_meta_section())

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
        module_path = os.path.dirname(os.path.abspath(__file__))
        filename = module_path + '/../../../html/{name}.html'.format(name=name)
        try:
            fragment = codecs.open(filename, 'r', 'utf-8').read()
        except IOError:
            fragment = pkg_resources.ResourceManager().resource_string(__name__, 'html/{name}.html'.format(name=name))
        return unicode(fragment)

    def section(self, report, section):
        """ Return a HTML formatted version of the section. """
        subtitle = self.__format_subtitle(section.subtitle())
        links = self.__format_product_links(report, section.product())
        meta_data = self.__format_product_meta_data(section.product())
        parameters = dict(title=section.title(), id=section.id_prefix(), subtitle=subtitle, product_meta_data=meta_data,
                          product_links=links)
        return self.__get_html_fragment('section').format(**parameters)

    def metric(self, metric):
        """ Return a HTML formatted version of the metric. """
        return ''  # pragma: no cover

    @staticmethod
    def __section_navigation_menu(report):
        """ Return the menu for jumping to specific sections. """
        menu_items = []

        menu_item_template = '''<li><a class="link_section_{section_id}" href="#section_{section_id}">{menu_label}</a>
        </li>'''
        sub_menu_template = '''<li class="dropdown-submenu"><a tabindex="-1" href="#">{title}</a>
        <ul class="dropdown-menu">'''

        def add_menu_item(section_id, menu_label):
            """ Add a menu item that links to the specified section. """
            menu_items.append(menu_item_template.format(section_id=section_id, menu_label=menu_label))

        def add_sub_menu(sections, title):
            """ Add a sub menu with menu items that link to the specified sections. """
            menu_items.append(sub_menu_template.format(title=title))
            for each_section in sections:
                add_menu_item(each_section.id_prefix(), each_section.subtitle())
            menu_items.append('</ul></li>')

        # First, group related sections so we can create sub menu's
        sections = {}
        titles = []
        for section in report.sections():
            title = section.title()
            sections.setdefault(title, []).append(section)
            if title not in titles:
                titles.append(title)
        # Next, create the menu's and submenu's
        for title in titles:
            if len(sections[title]) == 1:
                section = sections[title][0]
                add_menu_item(section.id_prefix(), section.title())
            else:
                add_sub_menu(sections[title], title)
        # Finally, return the HTML as one string
        return '\n'.join(menu_items)

    @staticmethod
    def __quality_attribute_filter_menu(report):
        """ Return the menu for filtering on quality attributes. """
        quality_attributes = set([metric.quality_attribute for metric in report.metrics() if metric.quality_attribute])
        menu_item_template = """
            <li>
                <a class="filter_quality_attribute"
                   id="filter_quality_attribute_{attribute_id}"
                   href="#">
                    <i class=""></i> Alleen {attribute_name}-metingen
                </a>
            </li>"""
        menu_items = [menu_item_template.format(attribute_id=attribute.id_string(), attribute_name=attribute.name())
                      for attribute in sorted(quality_attributes)]
        return '\n'.join(menu_items)

    def __trend_data(self, meta_metrics_section):
        """ Return a JSON representation of the history in the meta metrics section. """
        history_table = []
        missing_id = grey_id = green_id = red_id = yellow_id = ''
        for metric in meta_metrics_section.metrics():
            if metric.id_string() == 'MM-1':
                green_id = metric.stable_id()
            elif metric.id_string() == 'MM-2':
                red_id = metric.stable_id()
            elif metric.id_string() == 'MM-3':
                yellow_id = metric.stable_id()
            elif metric.id_string() == 'MM-4':
                grey_id = metric.stable_id()
            elif metric.id_string() == 'MM-5':
                missing_id = metric.stable_id()
        for history_record in meta_metrics_section.history():
            date_and_time = self.__date_and_time(history_record)
            percentages = self.__percentages(history_record, green_id, red_id, yellow_id, grey_id, missing_id)
            history_table.append(
                '[new Date({}, {}, {}, {}, {}, {}), {}, {}, {}, {}, {}]'.format(*(date_and_time + percentages)))
        return '[' + ',\n'.join(history_table) + ']'

    @staticmethod
    def __date_and_time(history_record):
        """ Return the date and time of the history record. Remove leading zero
            from date/time elements (assuming all elements are 2 digits long).
            Turn month into zero-based value for usage within Javascript. """
        year, month, day, hour, minute, second = re.split(r' 0?|:0?|\-0?|\.0?', history_record['date'])[:6]
        month = str(int(month) - 1)  # Months are zero based
        return year, month, day, hour, minute, second

    @staticmethod
    def __percentages(history_record, green_id, red_id, yellow_id, grey_id, missing_id):
        """ Return the percentages red, yellow and green of the history record. """
        percentage_green = history_record[green_id]
        percentage_red = history_record[red_id]
        try:
            percentage_yellow = history_record[yellow_id]
        except KeyError:
            percentage_yellow = 100. - (float(percentage_green) + float(percentage_red))
        try:
            percentage_grey = history_record[grey_id]
        except KeyError:
            percentage_grey = 0
        try:
            percentage_missing = history_record[missing_id]
        except KeyError:
            percentage_missing = 0
        return percentage_green, percentage_yellow, percentage_red, percentage_grey, percentage_missing

    def __metric_data(self, metric):
        """ Return the metric data as a dictionary, so it can be used in string templates. """
        status = metric.status()
        kwargs_by_status = dict(
            red=dict(image='sad', alt=':-(', status_nr=0,
                     hover='Direct actie vereist: norm niet gehaald of meting te oud'),
            yellow=dict(image='plain', alt=':-|', status_nr=1, hover='Bijna goed: norm net niet gehaald'),
            green=dict(image='smile', alt=':-)', status_nr=2, hover='Goed: norm gehaald'),
            perfect=dict(image='biggrin', alt=':-D', status_nr=3, hover='Perfect: score kan niet beter'),
            grey=dict(image='ashamed', alt=':-o', status_nr=4, hover='Technische schuld: lossen we later op'),
            missing=dict(image='missing', alt='x', status_nr=5, hover='Ontbrekend: metriek kan niet gemeten worden'))
        kwargs = kwargs_by_status[status]
        qualifier = 'tenminste ' if metric.status_start_date() <= datetime.datetime(2013, 3, 19, 23, 59, 59) else ''
        kwargs['hover'] += ' (sinds {qual}{date})'.format(qual=qualifier,
                                                          date=utils.format_date(metric.status_start_date(), year=True))
        kwargs['status'] = metric.status()
        kwargs['metric_id'] = metric.id_string()
        kwargs['section'] = metric.id_string().split('-')[0]
        kwargs['version'] = metric.product_version_type()
        kwargs['text'] = self.__format_metric_text(metric)
        kwargs['norm'] = metric.norm()
        attribute_id = metric.quality_attribute.id_string()
        if attribute_id:
            attribute_id = 'filter_quality_attribute_' + attribute_id
        kwargs['quality_attribute'] = attribute_id
        kwargs['comment'] = self.__format_metric_comment(metric)
        return kwargs

    @staticmethod
    def postfix():
        """ Return a HTML formatted version of the report postfix. """
        return HTMLFormatter.__get_html_fragment('postfix')

    @classmethod
    def __format_metric_text(cls, metric):
        """ Return a HTML formatted version of the metric text that includes one
            or more links to the metric source(s) if available. """
        return cls.__format_text_with_links(metric.report(), metric.url(), metric.url_label())

    @classmethod
    def __format_metric_comment(cls, metric):
        """ Return a HTML formatted version of the metric comment that includes
            a link to the comment source (the wiki). """
        return cls.__format_text_with_links(metric.comment(),
                                            metric.comment_urls(),
                                            metric.comment_url_label())

    @classmethod
    def __format_text_with_links(cls, text, url_dict, url_label=''):
        """ Format a text paragraph with optional urls and label for the urls. """
        text = utils.html_escape(text)
        links = [cls.__format_url(anchor, href) for (anchor, href) in url_dict.items()]
        if links:
            if url_label:
                url_label += ': '
            sep = ', '
            text = u'{text} [{url_label}{links}]'.format(text=text, url_label=url_label, links=sep.join(sorted(links)))
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

    @classmethod
    def __format_product_links(cls, report, product):
        """ Return a HTML formatted paragraph with the dependencies and users of the product. """
        if not product:
            return ''
        product_label = '{prod}:{ver}'.format(prod=product.name(), ver=product.product_version() or 'trunk')
        dependencies = product.dependencies(recursive=False)
        users = [(user.name(), user.product_version()) for user in product.users(recursive=False)]
        product_template = '<p>{prod} {rel}: {links}</p>'
        result = []
        for linked_products, link_text in ((dependencies, 'gebruikt'), (users, 'wordt gebruikt door')):
            if not linked_products:
                continue
            links = [cls.__format_product_link(report, name, version) for name, version in sorted(linked_products)]
            result.append(product_template.format(prod=product_label, rel=link_text, links=', '.join(links)))
        if result:
            result.append('')
        return '\n'.join(result)

    @classmethod
    def __format_product_meta_data(cls, product):
        """ Return a HTML formatted paragraph with meta data about the product. """
        if not product:
            return ''
        product_label = '{prod}:{ver}'.format(prod=product.name(), ver=product.product_version() or 'trunk')
        latest_release_template = '<p>{prod} is de meest recente versie.</p>'
        release_candidate_template = '<p>{prod} is een releasekandidaat.</p>'
        result = []
        if product.is_latest_release():
            result.append(latest_release_template.format(prod=product_label))
        if product.is_release_candidate():
            result.append(release_candidate_template.format(prod=product_label))
        if result:
            result.append('')
        return '\n'.join(result)

    @classmethod
    def __format_product_link(cls, report, product_name, product_version):
        """ Return a HTML formatted product link. """
        product = report.get_product(product_name, product_version)
        section = report.get_product_section(product)
        color = section.color()
        color = 'gold' if color == 'yellow' else color
        section_id = section.id_prefix()
        return '<span class="link_section_{sec}" title="{prd}:{ver}" ' \
               'style="color: {clr};"></span>'.format(sec=section_id, prd=product_name, ver=product_version or 'trunk',
                                                      clr=color)

    @staticmethod
    def __project_resources(report):
        """ Return a HTML version of the project resources. """
        result = list()
        result.append('<ul>')
        for name, url in report.project().project_resources():
            url_text = '<a href="{url}">{url}</a>'.format(url=url) if url else 'Geen url geconfigureerd'
            result.append('<li>{name}: {url_text}</li>'.format(name=name, url_text=url_text))
        result.append('</ul>')
        return '\n'.join(result)

    @staticmethod
    def __metric_classes(report):
        """ Return a HTML table of the metrics the software can measure. """
        result = list()
        result.append('<table>')
        result.append('<tr><th>Metriek</th><th>Class naam</th>'
                      '<th>Kwaliteitsattribuut</th><th>Norm</th></tr>')
        for metric_class in report.metric_classes():
            name = metric_class.name
            class_name = metric_class.__name__
            quality_attribute = metric_class.quality_attribute.name()
            try:
                norm = metric_class.norm_template.format(**metric_class.norm_template_default_values())
            except ValueError:
                logging.error('Metric class %s had faulty norm template', metric_class.__name__)
                raise
            result.append('<tr><td>{name}</td><td>{cls}</td><td>{qattr}</td><td>{norm}</td></tr>'.format(
                name=name, cls=class_name, qattr=quality_attribute, norm=norm))
        result.append('</table>')
        return '\n'.join(result)

    @staticmethod
    def product_url(product):
        """ Return a url to the product section in the HTML report for the specified product. """
        return 'index.html#section_{prd}'.format(prd=product.short_name())

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
        tr_indent = table_indent + ' ' * 4
        td_indent = tr_indent + ' ' * 4

        dashboard = list()
        dashboard.append(table_indent + '<table width="100%" border="1">')
        dashboard.extend(cls.__dashboard_headers(report, tr_indent, td_indent))
        dashboard.extend(cls.__dashboard_rows(report, tr_indent, td_indent))
        dashboard.append(table_indent + '</table>')
        return '\n'.join(dashboard)

    @staticmethod
    def __dashboard_headers(report, tr_indent, td_indent):
        """ Return the headers of the dashboard. """
        dashboard_headers = report.dashboard()[0]
        th_template = td_indent + '<th colspan="{span}" align="center" bgcolor="#2c2c2c">{sec}</th>'
        rows = list()
        rows.append(tr_indent + '<tr style="color: white; font-weight: bold;">')
        for section_type, colspan in dashboard_headers:
            table_header = th_template.format(span=colspan, sec=section_type)
            rows.append(table_header)
        rows.append(tr_indent + '</tr>')
        return rows

    @staticmethod
    def __dashboard_rows(report, tr_indent, td_indent):
        """ Return the rows of the dashboard. """
        dashboard_rows = report.dashboard()[1]
        td_template = td_indent + '''<td colspan={colspan} rowspan={rowspan} align="center" bgcolor="{bg_color}">
                                        <div class="link_section_{ID}" title="{title}"></div>
                                        <div id="section_summary_chart_{ID}"></div>
                                        <div id="section_summary_trunk_chart_{ID}"></div>
                                    </td>
'''
        rows = list()
        for row in dashboard_rows:
            rows.append(tr_indent + '<tr>')
            for column in row:
                try:
                    section_id = column[0].short_name()
                except AttributeError:
                    section_id = column[0].upper()
                section = report.get_section(section_id)
                title = (section and section.title()) or '???'
                colspan, rowspan = column[2] if len(column) == 3 else (1, 1)
                table_data = td_template.format(ID=section_id, title=title, bg_color=column[1],
                                                colspan=colspan, rowspan=rowspan)
                rows.append(table_data)
            rows.append(tr_indent + '</tr>')
        return rows
