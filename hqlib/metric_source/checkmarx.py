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


import functools
import logging
import urllib.parse
from typing import Dict, List, Iterable

from . import url_opener
from .. import utils, domain


class Checkmarx(domain.MetricSource):
    """ Class representing the Checkmarx API. """
    metric_source_name = 'Checkmarx'
    needs_metric_source_id = True

    def __init__(self, url: str, username: str, password: str, url_open: url_opener.UrlOpener=None, *args, **kwargs) -> None:
        self._url_open = url_open or url_opener.UrlOpener("", username, password)
        super().__init__(url=url, *args, **kwargs)

    def metric_source_urls(self, *report_urls: str) -> List[str]:
        checkmarx_report_urls = []

        for project_name in report_urls:
            try:
                json = self.__fetch_report(project_name)
                checkmarx_report_urls.append("{}/CxWebClient/ViewerMain.aspx?scanId={}&ProjectID={}".format(
                    self.url(),
                    str(json["value"][0]["LastScan"]["Id"]),
                    str(json["value"][0]["LastScan"]["ProjectId"])))
            except (IndexError, KeyError) as reason:
                logging.warning("Couldn't load values from json: %s - %s", project_name, reason)
            except url_opener.UrlOpener.url_open_exceptions:
                return []

        return checkmarx_report_urls

    def nr_warnings(self, metric_source_ids: Iterable[str], priority: str) -> int:
        """ Return the number of warnings in the reports with the specified priority. """
        nr_alerts = 0
        for project_name in metric_source_ids:
            try:
                json = self.__fetch_report(project_name)
                nr_alerts += self.__parse_alerts(json, priority)
            except Exception as reason:
                logging.warning("Couldn't parse alerts with %s risk level from %s - %s - %s",
                                priority, self.url(), reason, project_name)
                return -1
        return nr_alerts

    @staticmethod
    def __parse_alerts(json: Dict[str, List[Dict[str, Dict[str, int]]]], risk_level: str) -> int:
        """ Parse the JSON to get the number of alerts for the risk_level """
        return json["value"][0]["LastScan"][risk_level.title()]

    @functools.lru_cache(maxsize=1024)
    def __fetch_report(self, project_name: str) -> Dict[str, List[Dict[str, Dict[str, int]]]]:
        """ Create the api URL and fetch the report from it. """
        api_url = "{}/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27{}%27".format(
            self.url(), urllib.parse.quote(project_name))
        return self.__get_json(api_url)

    def __get_json(self, api_url: str) -> Dict[str, List[Dict[str, Dict[str, int]]]]:
        """ Return and evaluate the JSON at the url using Basic Authentication. """
        try:
            import ssl
            try:
                _create_unverified_https_context = ssl._create_unverified_context
            except AttributeError:
                # Legacy Python that doesn't verify HTTPS certificates by default
                pass
            else:
                # Handle target environment that doesn't support HTTPS verification
                ssl._create_default_https_context = _create_unverified_https_context

            json_string = self._url_open.url_read(api_url)
        except url_opener.UrlOpener.url_open_exceptions as reason:
            logging.warning("Couldn't open %s: %s", api_url, reason)
            raise

        return utils.eval_json(json_string)
