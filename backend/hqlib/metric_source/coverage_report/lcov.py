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


import logging
import datetime
import functools

from hqlib.typing import DateTime
from .html_coverage_report import HTMLCoverageReport
from ... import utils


class LCOV(HTMLCoverageReport):
    """ Class representing a LCOV coverage report. """
    metric_source_name = 'LCOV coverage rapport'

    def _parse_statement_coverage_percentage(self, soup) -> float:
        return self.__parse_coverage_data(soup, 'Lines:', -1, self.__calculate_percentage)

    def _parse_branch_coverage_percentage(self, soup) -> float:
        return self.__parse_coverage_data(soup, 'Branches:', -1, self.__calculate_percentage)

    @classmethod
    def _parse_coverage_date(cls, soup) -> DateTime:
        return cls.__parse_coverage_data(soup, 'Date:', datetime.datetime.min, cls.__parse_element_text_for_date)

    @staticmethod
    @functools.lru_cache(maxsize=1024)
    def __get_report_tds(soup):
        return soup.table.find('table').find_all('td')

    @classmethod
    def __parse_coverage_data(cls, soup, header: str, default_value, get_data_from_element):
        try:
            data_elements = cls.__get_report_tds(soup)
        except AttributeError as reason:
            logging.error('Error parsing html. Reason: %s', reason)
            return default_value

        for i, td_element in enumerate(data_elements):
            if td_element.text == header:
                return get_data_from_element(header, data_elements, i)

        logging.error('Header %s is not found in the report.', header.strip(':'))
        return default_value

    @staticmethod
    def __calculate_percentage(header: str, tds: list, index: int) -> float:
        try:
            return 100 * int(tds[index + 1].text) / int(tds[index + 2].text)
        except ValueError as reason:
            logging.error('Error calculating coverage percentage for %s. Reason: %s', header.strip(':'), reason)
            return -1
        except ZeroDivisionError:
            logging.error('Total reported number of %s is found to be zero!', header.strip(':'))
            return -1

    @staticmethod
    def __parse_element_text_for_date(header: str, tds: list, index: int) -> DateTime:
        try:
            return utils.parse_sql_datetime(tds[index + 1].text)
        except ValueError as reason:
            logging.error('Error parsing report for %s. Reason: %s', header.strip(':'), reason)
            return datetime.datetime.min
