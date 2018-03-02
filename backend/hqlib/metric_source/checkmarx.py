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


import datetime
import functools
import logging
import urllib.parse
from typing import Dict, List, Iterable

import dateutil.parser

from hqlib.typing import DateTime
from . import url_opener
from .. import utils, domain


class Checkmarx(domain.MetricSource):
    """ Class representing the Checkmarx API. """
    metric_source_name = 'Checkmarx'

    def __init__(self, url: str, username: str, password: str, url_open: url_opener.UrlOpener = None,
                 *args, **kwargs) -> None:
        self._url_open = url_open or url_opener.UrlOpener("", username, password)
        super().__init__(url=url, *args, **kwargs)

    def metric_source_urls(self, *report_urls: str) -> List[str]:
        checkmarx_report_urls = []

        for project_name in report_urls:
            try:
                json = self.__fetch_last_scan(project_name)
                checkmarx_report_urls.append("{}/CxWebClient/ViewerMain.aspx?scanId={}&ProjectID={}".format(
                    self.url(), str(json["Id"]), str(json["ProjectId"])))
            except (IndexError, KeyError, TypeError) as reason:
                logging.warning("Couldn't load values from json: %s - %s", project_name, reason)
            except url_opener.UrlOpener.url_open_exceptions:
                return [self.url()]

        return checkmarx_report_urls

    def nr_warnings(self, metric_source_ids: Iterable[str], priority: str) -> int:
        """ Return the number of warnings in the reports with the specified priority. """
        nr_alerts = 0
        for project_name in metric_source_ids:
            try:
                json = self.__fetch_last_scan(project_name)
                nr_alerts += json[priority.title()]
            except url_opener.UrlOpener.url_open_exceptions:
                return -1
            except (KeyError, IndexError) as reason:
                logging.error("Couldn't parse alerts for project %s with %s risk level from %s: %s",
                              project_name, priority, self.url(), reason)
                return -1
        return nr_alerts

    def datetime(self, *metric_source_ids: str) -> DateTime:
        """ Return the last date and time the projects were scanned. """
        dates = []
        for project_name in metric_source_ids:
            try:
                json = self.__fetch_last_scan(project_name)
                dates.append(self.__parse_datetime(json))
            except url_opener.UrlOpener.url_open_exceptions:
                return datetime.datetime.min
            except (KeyError, IndexError) as reason:
                logging.error("Couldn't parse date and time for project %s from %s: %s",
                              project_name, self.url(), reason)
                return datetime.datetime.min
        return min(dates, default=datetime.datetime.min)

    @staticmethod
    def __parse_datetime(json: Dict) -> DateTime:
        """ Parse the JSON to get the date and time of the last scan. """
        datetimes = []
        datetime_string = json["ScanCompletedOn"].split('.')[0]
        datetimes.append(dateutil.parser.parse(datetime_string, ignoretz=True))
        comment = json.get("Comment", "")
        comment_sep, prefix, postfix = '; ', 'Attempt to perform scan on ', ' - No code changes were detected'
        if comment_sep in comment:
            for check in comment.strip(comment_sep).split(comment_sep):
                if prefix in check:
                    datetime_string = check.strip(prefix).strip(postfix)
                    datetimes.append(dateutil.parser.parse(datetime_string, dayfirst=False))
        return max(datetimes, default=datetime.datetime.min)

    @functools.lru_cache(maxsize=1024)
    def __fetch_last_scan(self, project_name: str) -> Dict[str, int]:
        """ Create the api URL and fetch the report from it. """
        api_url = "{}/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27{}%27".format(
            self.url(), urllib.parse.quote(project_name))
        return self.__get_json(api_url)["value"][0]["LastScan"]

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
