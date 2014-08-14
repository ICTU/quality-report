'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from qualitylib import utils
from qualitylib.formatting import base_formatter
import datetime
import os
import re
import pkg_resources


class HTMLFormatter(base_formatter.Formatter):
    ''' Format the report in HTML. '''

    column_list = ["{f: '%(metric_id)s', v: '%(metric_number)s'}",
                   "'%(section)s'",
                   "'%(status)s'",
                   "'%(teams)s'",
                   """'<img src="img/%(metric_id)s.png" border="0" />'""",
                   """{v: '%(status_nr)d', f: '<img src="img/%(image)s.png" """
                   """alt="%(alt)s" title="%(hover)s" """
                   """border="0" />'}""",
                   "'%(text)s'",
                   "'%(norm)s'",
                   "'%(tasks)s'",
                   "'%(comment)s'",
                   "'%(version)s'",
                   "'%(quality_attribute)s'"]
    columns = '[' + ', '.join(column_list) + ']'

    def __init__(self, *args, **kwargs):
        self.__latest_software_version = kwargs.pop('latest_software_version', 
                                                    '0')
        self.__current_software_version = kwargs.pop('current_software_version',
                                                     '0')
        super(HTMLFormatter, self).__init__(*args, **kwargs)

    def prefix(self, report):
        ''' Return a HTML formatted version of the report prefix. '''
        parameters = dict(
            title=report.title(),
            date=report.date().strftime('%d-%m-%y %H:%M'),
            current_version=self.__current_software_version,
            new_version_available=self.__new_release_text())
        parameters['section_menu'] = self.__section_navigation_menu(report)
        parameters['quality_attribute_filter_menu'] = \
            self.__quality_attribute_filter_menu(report)
        parameters['team_filter_menu'] = self.__team_filter_menu(report)
        parameters['dashboard'] = self.__dashboard(report)
        parameters['project_resources'] = self.__project_resources(report)
        parameters['metric_classes'] = self.__metric_classes(report)
        parameters['history'] = self.__trend_data(report.get_meta_section())

        metrics = []
        for metric in report.metrics():
            data = self.__metric_data(metric)
            metric_number = int(data['metric_id'].split('-')[1])
            data['metric_number'] = '%s-%02d' % (data['section'],
                                                 metric_number)
            metrics.append(self.columns % data)
        parameters['metrics'] = '[' + ',\n'.join(metrics) + ']'
        prefix = self.__get_html_fragment('prefix')
        return prefix % parameters

    @staticmethod
    def __get_html_fragment(name):
        ''' Read and return a HTML fragment from the html folder. '''
        module_path = os.path.dirname(os.path.abspath(__file__))
        filename = module_path + '/../../../html/%s.html' % name
        try:
            return file(filename).read()
        except IOError:
            return pkg_resources.ResourceManager().\
                resource_string(__name__, 'html/%s.html' % name)

    def section(self, report, section):
        ''' Return a HTML formatted version of the section. '''
        subtitle = self.__format_subtitle(section.subtitle())
        links = self.__format_product_links(report, section.product())
        meta_data = self.__format_product_meta_data(section.product())
        parameters = dict(title=section.title(), id=section.id_prefix(),
                          subtitle=subtitle, product_meta_data=meta_data,
                          product_links=links)
        return self.__get_html_fragment('section') % parameters

    def metric(self, metric):
        ''' Return a HTML formatted version of the metric. '''
        return ''  # pragma: no cover

    @staticmethod
    def __section_navigation_menu(report):
        ''' Return the menu for jumping to specific sections. '''
        menu_items = []

        def add_menu_item(section_id, menu_label):
            ''' Add a menu item that links to the specified section. '''
            menu_items.append('<li><a ' \
                'class="link_section_%(section_id)s" ' \
                'href="#section_%(section_id)s">%(menu_label)s</a></li>' % \
                dict(section_id=section_id, menu_label=menu_label))

        def add_sub_menu(sections, title):
            ''' Add a sub menu with menu items that link to the specified
                sections. '''
            menu_items.append('<li class="dropdown-submenu"> ' \
                '<a tabindex="-1" href="#">%s</a>' \
                '<ul class="dropdown-menu">' % title)
            for section in sections:
                add_menu_item(section.id_prefix(), section.subtitle())
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
        ''' Return the menu for filtering on quality attributes. '''
        quality_attributes = set([metric.quality_attribute \
                                  for metric in report.metrics() \
                                  if metric.quality_attribute])
        quality_attributes = sorted(list(quality_attributes))
        menu_item_template = '''
            <li>
                <a class="filter_quality_attribute"
                   id="filter_quality_attribute_%(attribute_id)s" 
                   href="#">
                    <i class=""></i> Alleen %(attribute_name)s-metingen
                </a>
            </li>'''
        menu_items = [menu_item_template % \
                      dict(attribute_id=attribute.id_string(),
                           attribute_name=attribute.name()) \
                      for attribute in quality_attributes]
        return '\n'.join(menu_items)

    @staticmethod
    def __team_filter_menu(report):
        ''' Return the menu for filtering on team. '''
        team_filter_menu_items = []
        for team in report.teams():
            team_filter_menu_items.append('<li><a class="filter_team" ' \
                'id="filter_team_%(team_id)s" href="#"><i class=""></i> ' \
                "Alleen metingen van team %(team)s</a></li>" % \
                dict(team=team, team_id=team.id_string()))
        return '\n'.join(team_filter_menu_items)

    def __trend_data(self, meta_metrics_section):
        ''' Return a JSON representation of the history in the meta metrics
           section. '''
        history_table = []
        grey_id = yellow_id = ''
        for metric in meta_metrics_section.metrics():
            if metric.id_string() == 'MM-1':
                green_id = metric.stable_id()
            elif metric.id_string() == 'MM-2':
                red_id = metric.stable_id()
            elif metric.id_string() == 'MM-3':
                yellow_id = metric.stable_id()
            elif metric.id_string() == 'MM-4':
                grey_id = metric.stable_id()
        for history_record in meta_metrics_section.history():
            date_and_time = self.__date_and_time(history_record)
            percentages = self.__percentages(history_record, green_id, red_id,
                                             yellow_id, grey_id)
            history_table.append(\
                '[new Date(%s, %s, %s, %s, %s, %s), %s, %s, %s, %s]' % \
                (date_and_time + percentages))
        return '[' + ',\n'.join(history_table) + ']'

    @staticmethod
    def __date_and_time(history_record):
        ''' Return the date and time of the history record. Remove leading zero 
            from date/time elements (assuming all elements are 2 digits long).
            Turn month into zero-based value for usage within Javascript. '''
        year, month, day, hour, minute, second = \
            re.split(r' 0?|:0?|\-0?|\.0?', history_record['date'])[:6]
        month = str(int(month) - 1)  # Months are zero based
        return year, month, day, hour, minute, second

    @staticmethod
    def __percentages(history_record, green_id, red_id, yellow_id, grey_id):
        ''' Return the percentages red, yellow and green of the
            history record. '''
        percentage_green = history_record[green_id]
        percentage_red = history_record[red_id]
        try:
            percentage_yellow = history_record[yellow_id]
        except KeyError:
            percentage_yellow = 100. - (float(percentage_green) +
                                        float(percentage_red))
        try:
            percentage_grey = history_record[grey_id]
        except KeyError:
            percentage_grey = 0
        return (percentage_green, percentage_yellow, percentage_red,
                percentage_grey)

    def __metric_data(self, metric):
        ''' Return the metric data as a dictionary, so it can be used in string
            templates. '''
        status = metric.status()
        kwargs_by_status = dict(
            red=dict(image='sad', alt=':-(', status_nr=0,
                     hover='Direct actie vereist: norm niet gehaald of meting '
                           'te oud'),
            yellow=dict(image='plain', alt=':-|', status_nr=1, 
                        hover='Bijna goed: norm net niet gehaald'),
            green=dict(image='smile', alt=':-)', status_nr=2, 
                       hover='Goed: norm gehaald'),
            perfect=dict(image='biggrin', alt=':-D', status_nr=3,
                         hover='Perfect: score kan niet beter'),
            grey=dict(image='ashamed', alt=':-o', status_nr=4,
                      hover='Technische schuld: lossen we later op'))
        kwargs = kwargs_by_status[status]
        qualifier = 'tenminste ' if metric.status_start_date() <= \
                    datetime.datetime(2013, 3, 19, 23, 59, 59) else ''
        kwargs['hover'] += ' (sinds %s%s)' % (qualifier,
            utils.format_date(metric.status_start_date(), year=True))
        kwargs['status'] = self.__metric_status(metric)
        kwargs['metric_id'] = metric.id_string()
        kwargs['section'] = metric.id_string().split('-')[0]
        kwargs['version'] = metric.product_version_type()
        kwargs['text'] = self.__format_metric_text(metric)
        kwargs['tasks'] = self.__format_metric_tasks(metric)
        kwargs['norm'] = metric.norm()
        attribute_id = metric.quality_attribute.id_string()
        if attribute_id:
            attribute_id = 'filter_quality_attribute_' + attribute_id
        kwargs['quality_attribute'] = attribute_id
        kwargs['comment'] = self.__format_metric_comment(metric)
        kwargs['teams'] = ','.join(['filter_team_%s' % team.id_string() \
                                    for team in metric.responsible_teams()])
        return kwargs

    def postfix(self):  # pylint: disable=arguments-differ
        ''' Return a HTML formatted version of the report postfix. '''
        return self.__get_html_fragment('postfix')

    @classmethod
    def __format_metric_text(cls, metric):
        ''' Return a HTML formatted version of the metric text that includes one
            or more links to the metric source(s) if available. '''
        return cls.__format_text_with_links(metric.report(), metric.url(), 
                                            metric.url_label())

    @staticmethod
    def __metric_status(metric):
        ''' Return the status of the metric, including corrective actions. '''
        status = metric.status()
        if status in ('red', 'yellow') and metric.has_tasks():
            status += '_with_action'
        return status

    @classmethod
    def __format_metric_tasks(cls, metric):
        ''' Return a HTML formatted version of the metric action(s). '''
        return cls.__format_text_with_links('', metric.task_urls())

    @classmethod
    def __format_metric_comment(cls, metric):
        ''' Return a HTML formatted version of the metric comment that includes
            a link to the comment source (the wiki). '''
        return cls.__format_text_with_links(metric.comment(), 
                                            metric.comment_urls(), 
                                            metric.comment_url_label())

    @classmethod
    def __format_text_with_links(cls, text, url_dict, url_label=''):
        ''' Format a text paragraph with optional urls and label for the 
            urls. '''
        links = [cls.__format_url(anchor, href) \
                 for (anchor, href) in url_dict.items()]
        if links:
            if url_label:
                url_label += ': '
            sep = ', '
            text = '%(text)s [%(url_label)s%(links)s]' % dict(text=text,
                url_label=url_label, links=sep.join(sorted(links)))
        return text

    @staticmethod
    def __format_subtitle(subtitle):
        ''' Return a HTML formatted subtitle. '''
        return ' <small>%s</small>' % subtitle if subtitle else ''

    @staticmethod
    def __format_url(anchor, href):
        ''' Return a HTML formatted url. '''
        return '<a href="%(href)s" target="_blank">%(anchor)s</a>' % \
            dict(href=href, anchor=utils.html_escape(anchor))

    @classmethod
    def __format_product_links(cls, report, product):
        ''' Return a HTML formatted paragraph with the dependencies and users
            of the product. '''
        result = ''
        if not product:
            return result
        product_label = '%s:%s' % (product.name(),
                                   product.product_version() or 'trunk')
        dependencies = product.dependencies(recursive=False)
        users = [(user.name(), user.product_version()) \
                  for user in product.users(recursive=False)]
        for linked_products, link_text in ((dependencies, 'gebruikt'),
                                           (users, 'wordt gebruikt door')):
            if not linked_products:
                continue
            links = []
            for name, version in sorted(linked_products):
                link = cls.__format_product_link(report, name, version)
                links.append(link)
            result += '<p>%s %s: %s</p>\n' % (product_label, link_text,
                                              ', '.join(links))
        return result

    @classmethod
    def __format_product_meta_data(cls, product):
        ''' Return a HTML formatted paragraph with meta data about the 
            product. '''
        result = ''
        if not product:
            return result
        product_label = '%s:%s' % (product.name(),
                                   product.product_version() or 'trunk')
        if product.is_latest_release():
            result += '<p>%s is de meest recente versie.</p>\n' % product_label
        if product.is_release_candidate():
            result += '<p>%s is een releasekandidaat.</p>\n' % product_label
        return result

    @classmethod
    def __format_product_link(cls, report, product_name, product_version):
        ''' Return a HTML formatted product link. '''
        section = report.get_product_section(product_name, product_version)
        color = section.color()
        color = 'gold' if color == 'yellow' else color
        section_id = section.id_prefix()
        return '<span class="link_section_%s" title="%s:%s" ' \
               'style="color: %s;"></span>' % (section_id, product_name, 
                                               product_version or 'trunk', 
                                               color)

    @staticmethod
    def __dashboard(report):
        ''' Return a HTML formatted dashboard. '''
        dashboard = '<table width="100%%" border="1">\n'
        table_indent = ' ' * 24
        tr_indent = table_indent + '    '
        td_indent = tr_indent + '    '
        dashboard += tr_indent + \
            '<tr style="color: white; font-weight: bold;">\n'
        dashboard_header, dashboard_rows = report.dashboard()
        for section_type, colspan in dashboard_header:
            dashboard += td_indent + '<th colspan="%d" align="center" ' \
                'bgcolor="#2c2c2c">%s</th>\n' % (colspan, section_type)
        dashboard += tr_indent + '</tr>\n'
        for row in dashboard_rows:
            dashboard += tr_indent + '<tr>\n'
            for column in row:
                try:
                    section_id = column[0].short_name()
                except AttributeError:
                    section_id = column[0].upper()
                title = report.get_section(section_id).title() or '???'
                row_parameters = dict(ID=section_id, title=title,
                                      bg_color=column[1])
                colspan, rowspan = column[2] if len(column) == 3 else (1, 1)
                row_parameters['colspan'] = colspan
                row_parameters['rowspan'] = rowspan
                dashboard += td_indent + '<td colspan=%(colspan)d ' \
                    'rowspan=%(rowspan)d align="center" ' \
                    'bgcolor="%(bg_color)s">\n' \
                    '<div class="link_section_%(ID)s" title="%(title)s">' \
                    '</div><div id="section_summary_chart_%(ID)s"></div>' \
                    '<div id="section_summary_trunk_chart_%(ID)s"></div>' \
                    '</td>\n' % row_parameters
            dashboard += tr_indent + '</tr>\n'
        dashboard += table_indent + '</table>'
        return dashboard

    @staticmethod
    def __project_resources(report):
        ''' Return a HTML version of the project resources. '''
        result = ['<h4>Project resources</h4>']
        result.append('<ul>')
        for name, url in report.project_resources():
            url_text = '<a href="%(url)s">%(url)s</a>' % dict(url=url) if url \
                else '<font color="red">ontbreekt</font>'
            parameters = dict(name=name, url_text=url_text)
            result.append('<li>%(name)s: %(url_text)s</li>' % parameters)
        result.append('</ul>')
        return '\n'.join(result)

    @staticmethod
    def __metric_classes(report):
        ''' Return a HTML table of the metrics the software can measure. '''
        result = []
        result.append('<table>')
        result.append('<tr><th>Metriek</th><th>Kwaliteitsattribuut</th>' \
                      '<th>Norm</th></tr>')
        for metric_class in report.metric_classes():
            name = metric_class.name
            quality_attribute = metric_class.quality_attribute.name()
            norm = metric_class.norm_template % \
                metric_class.norm_template_default_values()
            result.append('<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (name,
                                                      quality_attribute, norm))
        result.append('</table>')
        return '\n'.join(result)

    @staticmethod
    def product_url(product):
        ''' Return a url to the product section in the HTML report for the
            specified product. '''
        return 'index.html#section_%s' % product.short_name()

    def __new_release_text(self):
        ''' Return a line of text if there is a new version of the software
            available. '''
        latest = self.__latest_software_version
        current = self.__current_software_version
        return ' Versie %s is beschikbaar.' % latest if latest > current else ''
