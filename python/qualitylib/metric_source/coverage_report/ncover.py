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

import datetime
import re

from ..abstract import coverage_report
from ... import utils


class NCover(coverage_report.CoverageReport):
    """ Class representing a NCover coverage report. """
    metric_source_name = 'NCover coverage report'

    def _parse_statement_coverage_percentage(self, soup):
        return self.__parse_coverage_percentage(soup, 'sequencePointCoverage')

    def _parse_branch_coverage_percentage(self, soup):
        return self.__parse_coverage_percentage(soup, 'branchCoverage')

    @staticmethod
    def __parse_coverage_percentage(soup, coverage_type):
        """ Return the specified coverage percentage from the NCover soup. """
        scripts = soup('script', {'type': 'text/javascript'})
        for script in scripts:
            if 'ncover.execution.stats = ' in script.string:
                json = script.string.strip()[len('ncover.execution.stats = '):-1]
                return utils.eval_json(json)[coverage_type]['coveragePercent'] * 100
        return -1

    def _parse_coverage_date(self, soup):
        scripts = soup('script', {'type': 'text/javascript'})
        for script in scripts:
            if 'ncover.createDateTime' in script.string:
                match = re.search("ncover\.createDateTime = '(\d+)'", script.string)
                return datetime.datetime.fromtimestamp(float(match.group(1))/1000)
        return datetime.datetime.now()
