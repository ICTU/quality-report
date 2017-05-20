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


import yattag
from typing import List, Dict, Iterable

from ..report import QualityReport, Section
from ..domain import DomainObject


class SectionsFormatter(object):
    """ Return the sections of the report. """

    @classmethod
    def process(cls, report: QualityReport) -> str:
        """ Return the sections of the report as HTML. """
        doc, tag, text, line = yattag.Doc().ttl()
        doc.asis(cls.__dashboard_section(report))
        doc.asis(cls.__all_metrics_section())
        for section in report.sections():
            doc.asis(cls.__section(section))
        return yattag.indent(doc.getvalue())

    @classmethod
    def __dashboard_section(cls, report: QualityReport) -> str:
        """ Return a HTML formatted dashboard. """
        doc, tag, text = yattag.Doc().tagtext()
        with tag('div', id="section_dashboard"):
            doc.stag('br')
            with tag('table', klass="table table-condensed table-bordered"):
                with tag('thead'):
                    doc.asis(cls.__dashboard_headers(report))
                with tag('tbody'):
                    doc.asis(cls.__dashboard_rows(report))
        return doc.getvalue()

    @staticmethod
    def __dashboard_headers(report: QualityReport) -> str:
        """ Return the headers of the dashboard. """
        doc, tag, text, line = yattag.Doc().ttl()
        with tag('tr', style="color: white; font-weight: bold; background-color: #2F95CF;"):
            for section_type, colspan in report.dashboard()[0]:
                line('th', section_type, colspan=colspan, style="text-align: center;")
        return doc.getvalue()

    @classmethod
    def __dashboard_rows(cls, report: QualityReport) -> str:
        """ Return the rows of the dashboard. """
        doc, tag, text, line = yattag.Doc().ttl()
        for row in report.dashboard()[1]:
            with tag('tr'):
                for cell in row:
                    colspan, rowspan = cell[2] if len(cell) == 3 else (1, 1)
                    with tag('td', colspan=colspan, rowspan=rowspan, align='center', bgcolor=cell[1]):
                        section_id = cell[0].short_name() if isinstance(cell[0], DomainObject) else cell[0].upper()
                        section = report.get_section(section_id)
                        title = section.title() if section else '???'
                        line('div', '', klass="link_section_{}".format(section_id), title=title)
                        line('div', '', id="section_summary_chart_{}".format(section_id))
        return doc.getvalue()

    @classmethod
    def __all_metrics_section(cls) -> str:
        """ Return the section with all metrics. """
        doc, tag, text, line = yattag.Doc().ttl()
        with tag('section', id="section_all", style="display:none"):
            line('div', '', id="table_all")
        return doc.getvalue()

    @classmethod
    def __section(cls, section) -> str:
        """ Return the section formatted as HTML. """
        doc, tag, text, line = yattag.Doc().ttl()
        with tag('section', id="section_{0}".format(section.id_prefix())):
            doc.stag('br')
            doc.asis(cls.__section_title(section))
            line('div', '', id="table_{0}".format(section.id_prefix()))
        return doc.getvalue()

    @classmethod
    def __section_title(cls, section) -> str:
        """ Return the section title formatted as HTML. """
        doc, tag, text = yattag.Doc().tagtext()
        with tag('div', klass="page-header"):
            with tag('h1'):
                text(section.title())
                if section.subtitle():
                    doc.text(' ')
                    with tag('small'):
                        text(section.subtitle())
        return doc.getvalue()


class SectionNavigationMenuFormatter(object):
    """ Return the section navigation menu for the report. """
    @classmethod
    def process(cls, report: QualityReport) -> str:
        """ Return the section navigation menu, """
        menu_items = []

        menu_item_template = '<li><a class="link_section_{section_id}" href="#section_{section_id}">{menu_label}</a>' \
                             '</li>'

        def add_menu_item(section: Section, title: str) -> None:
            """ Add a menu item that links to the specified section. """
            menu_items.append(menu_item_template.format(section_id=section.id_prefix(), menu_label=title))

        def add_menu_items(sections: Iterable[Section]) -> None:
            """ Add a header with menu items that link to the specified sections. """
            for each_section in sections:
                add_menu_item(each_section, each_section.title() + ' ' + each_section.subtitle())

        # First, group related sections
        sections: Dict[str, List[Section]] = {}
        titles: List[str] = []
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
