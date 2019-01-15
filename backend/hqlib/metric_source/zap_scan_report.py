"""
Copyright 2012-2019 Ministerie van Sociale Zaken en Werkgelegenheid

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


import functools
import logging
import hashlib
import json
import bs4

from . import url_opener
from .. import domain


class ZAPScanReport(domain.MetricSource):
    """ Class representing ZAP Scan reports. """
    metric_source_name = 'ZAP Scan rapport'
    false_positives_list = []
    false_positive_api_url = ''

    def __init__(self, false_positive_api_url: str = '', **kwargs) -> None:
        self._url_opener = url_opener.UrlOpener(**kwargs)
        self.false_positive_api_url = false_positive_api_url
        self.false_positives_list = self.__get_false_positives()
        super().__init__()

    @functools.lru_cache(maxsize=1024)
    def alerts(self, risk_level: str, *report_urls: str) -> int:
        """ Returns the number of alerts of the specified risk level. Does not include false positives."""
        nr_alerts = 0
        for url in report_urls:
            nr_alerts += len(self.__parse_warnings(url, risk_level, False))
        return nr_alerts

    def get_warnings_info(self, risk_level: str, *report_urls: str) -> list:
        """ Returns warning details from a zap scan report of a certain risk level. Includes false positives."""
        warnings = []
        for url in report_urls:
            warnings += self.__parse_warnings(url, risk_level, True)
        return warnings

    def __get_false_positives(self) -> str:
        """ Return a list with false-positives from the False Postive API. """
        try:
            if not self.false_positive_api_url:
                logging.info("No false-positive API URL specified")
                return []

            opener = url_opener.UrlOpener()
            json_string = opener.url_read(self.false_positive_api_url + 'api/fp')
            logging.info("get_false_positives: %s", json_string)
            return json.loads(json_string)
        except url_opener.UrlOpener.url_open_exceptions:
            logging.error("HTTP error during the retrieving of false-positive list!")
        except (KeyError, ValueError) as reason:
            logging.error("Couldn't load false-positive list from json: %s.", reason)
        self.false_positive_api_url = ''
        return []

    def __parse_warnings(self, report_url: str, risk_level: str, include_false_positives: bool) -> list:
        """ Get all the warnings from the HTML soup. """
        try:
            warnings = []
            soup = self.__get_soup(report_url)
            risk_headers = self.__get_report_headers(soup, risk_level)
            for risk_header in risk_headers:
                risk_name = risk_header.find_all('th')[1].string
                risk_instances = self.__get_risk_instances(risk_header)
                warnings = self.__get_warnings(risk_instances, risk_name, report_url, include_false_positives)
            if not warnings:
                logging.warning("Couldn't find any entries with %s risk level.", risk_level)
            return warnings
        except url_opener.UrlOpener.url_open_exceptions:
            return []

    def __get_warnings(self, risk_instances, risk_name, report_url, include_false_positives) -> list:
        warnings = []
        for risk_instance in risk_instances:
            warning = self.__parse_warning_instance(risk_instance,
                                                    risk_name,
                                                    report_url,
                                                    include_false_positives)
            if warning:
                warnings.append(warning)
        return warnings

    def __parse_warning_instance(self, risk_instance, risk_name: str, report_url: str, include_false_positives: bool):
        instance_url = risk_instance.find_next_sibling().get_text()

        if not self.false_positive_api_url:
            return (risk_name, instance_url, 'Not available')

        warning_hash = self.__get_warning_hash(risk_instance, risk_name, report_url, instance_url)
        is_false_positive = warning_hash in self.false_positives_list

        if include_false_positives or not is_false_positive:
            false_positive_reason = ''
            if is_false_positive:
                false_positive_reason = self.false_positives_list[warning_hash]["reason"]

            return (risk_name, instance_url, (warning_hash,
                                              is_false_positive,
                                              false_positive_reason,
                                              self.false_positive_api_url))
        return None

    @staticmethod
    @functools.lru_cache(maxsize=1024)
    def __get_report_headers(soup, risk_level):
        return soup.find_all('tr', attrs={"class": "risk-{level}".format(level=risk_level)})

    @staticmethod
    @functools.lru_cache(maxsize=1024)
    def __get_risk_instances(risk_header):
        return risk_header.findParent('table').find_all('td', attrs={"class": "indent1"})

    def __get_warning_hash(self, risk_instance, risk_name, report_url, instance_url):
        # Create a unique hash for this warning to use as an identifier in False-Positive suppression
        property_hash = ''
        location_propteries = risk_instance.parent.find_next_siblings('tr')
        for location_property in location_propteries:
            property_title = location_property.find('td', attrs={"class": "indent2"})
            if not property_title:
                break

            property_name = property_title.get_text()
            property_value = property_title.find_next_sibling().get_text()
            property_hash += '_{}-{}'.format(property_name, property_value)

        warning_id_hash_value = '{}_{}_{}_{}_{}' \
                                .format(self.metric_source_name,
                                        report_url,
                                        risk_name,
                                        instance_url,
                                        property_hash) \
                                .encode('utf-8')

        md5_hash = hashlib.md5()  # nosec
        md5_hash.update(warning_id_hash_value)
        return md5_hash.hexdigest()

    @functools.lru_cache(maxsize=1024)
    def __get_soup(self, url: str):
        """ Return the HTML soup. """
        return bs4.BeautifulSoup(self._url_opener.url_read(url), "lxml")
