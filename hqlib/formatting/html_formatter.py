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

from ..report import QualityReport
from ..domain import DomainObject


class SectionsFormatter(object):
    """ Return the sections of the report. """

    @classmethod
    def process(cls, report: QualityReport) -> str:
        """ Return the sections of the report as HTML. """
        doc, tag, text, line = yattag.Doc().ttl()
        doc.asis(cls.__dashboard_section(report))
        return yattag.indent(doc.getvalue())

    @classmethod
    def __dashboard_section(cls, report: QualityReport) -> str:
        """ Return a HTML formatted dashboard. """
        doc, tag, text = yattag.Doc().tagtext()
        with tag('div', id="section_dashboard"):
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
