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


import datetime
import re

from ..abstract import coverage_report
from ... import utils
from hqlib.typing import DateTime


class NCover(coverage_report.CoverageReport):
    """ Class representing a NCover coverage report. """
    metric_source_name = 'NCover coverage rapport'

    def _parse_statement_coverage_percentage(self, soup) -> int:
        return self.__parse_coverage_percentage(soup, 'sequencePointCoverage')

    def _parse_branch_coverage_percentage(self, soup) -> int:
        return self.__parse_coverage_percentage(soup, 'branchCoverage')

    @staticmethod
    def __parse_coverage_percentage(soup, coverage_type: str) -> int:
        """ Return the specified coverage percentage from the NCover soup. """
        scripts = soup('script', {'type': 'text/javascript'})
        for script in scripts:
            if 'ncover.execution.stats = ' in script.string:
                json = script.string.strip()[len('ncover.execution.stats = '):-1]
                coverage_percent = utils.eval_json(json)[coverage_type]['coveragePercent']
                return coverage_percent * 100 if coverage_percent else -1
        return -1

    def _parse_coverage_date(self, soup) -> DateTime:
        scripts = soup('script', {'type': 'text/javascript'})
        for script in scripts:
            if 'ncover.createDateTime' in script.string:
                match = re.search(r"ncover\.createDateTime = '(\d+)'", script.string)
                return datetime.datetime.fromtimestamp(float(match.group(1))/1000)
        return datetime.datetime.now()
