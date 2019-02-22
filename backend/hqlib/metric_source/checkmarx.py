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


import json
import time
import datetime
import functools
import logging
import urllib.parse
import xml.etree.cElementTree
from typing import Dict, List, Iterable

import dateutil.parser

from hqlib.typing import DateTime
from hqlib.domain.measurement.metric_source_with_issues import MetricSourceWithIssues
from . import url_opener
from .. import utils


class Checkmarx(MetricSourceWithIssues):
    """ Class representing the Checkmarx API. """
    # pylint: disable=too-many-instance-attributes
    metric_source_name = 'Checkmarx'

    class Issue(MetricSourceWithIssues.Issue):
        """ A dependency in owasp report. """
        # pylint: disable=too-few-public-methods
        # pylint: disable=too-many-arguments
        def __init__(self, group: str, name: str, display_url: str, count: int, status: str) -> None:
            self.group = group.replace('_', ' ')
            self.display_url = display_url
            self.count = count
            self.status = status
            super().__init__(name.replace('_', ' '))

    def __init__(self, url: str, username: str, password: str, *args, **kwargs) -> None:
        self._projects_url = urllib.parse.urljoin(url, 'CxRestAPI/projects')
        self._scan_url = urllib.parse.urljoin(url, '/CxRestAPI/sast/scans?projectId={project_id}&last=1')
        self._statistics_url = urllib.parse.urljoin(url, '/CxRestAPI/sast/scans/{id}/resultsStatistics')

        self._generate_report_post_url = urllib.parse.urljoin(url, '/CxRestAPI/reports/sastScan')
        self._sast_scan_status_url = urllib.parse.urljoin(url, '/CxRestAPI/reports/sastScan/{scan_id}/status')
        self._sast_scan_url = urllib.parse.urljoin(url, '/CxRestAPI/reports/sastScan/{scan_id}')
        self._reference_display_url = urllib.parse.urljoin(
            url, '/CxWebClient/ScanQueryDescription.aspx?'
            'queryID={query_id}&queryVersionCode={query_version_code}&queryTitle={name}')
        self.__avoid_crl_check()

        token_url = urllib.parse.urljoin(url, '/cxrestapi/auth/identity/connect/token')
        token_post_body = \
            'username={username}&password={password}&scope=sast_rest_api&grant_type=password' \
            '&client_id=resource_owner_client&client_secret=014DF517-39D1-4453-B7B3-9930C563627C' \
            .format(username=username, password=password)
        self._url_open = url_opener.UrlOpener(
            authorization_token=self.__retrieve_access_token(token_url, token_post_body))
        super().__init__(url=url, *args, **kwargs)

    @staticmethod
    def __avoid_crl_check():
        """ Function disables certificate revocation check. """
        import ssl
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            # Legacy Python that doesn't verify HTTPS certificates by default
            pass
        else:
            # Handle target environment that doesn't support HTTPS verification
            ssl._create_default_https_context = _create_unverified_https_context

    @staticmethod
    @functools.lru_cache(maxsize=4096)
    def __retrieve_access_token(token_url: str, token_post_body: str) -> str:
        try:
            opener = url_opener.UrlOpener()
            json_string = opener.url_read(token_url, post_body=bytes(token_post_body, 'ascii'))
            return json.loads(json_string)['access_token']
        except url_opener.UrlOpener.url_open_exceptions:
            logging.error("HTTP error during the retrieving of access token!")
        except (KeyError, ValueError) as reason:
            logging.error("Couldn't load access token from json: %s.", reason)
        return ''

    def metric_source_urls(self, *report_urls: str) -> List[str]:
        """ Return the url(s) to the metric source for the metric source id. """
        checkmarx_report_urls = []
        for project_name in report_urls:
            try:
                project_id = self._fetch_project_id(project_name)
                last_scan_id = self._fetch_last_scan(project_id)[0]["id"]
                checkmarx_report_urls.append(urllib.parse.urljoin(
                    self.url(),
                    "/CxWebClient/ViewerMain.aspx?scanId={}&ProjectID={}"
                    .format(str(last_scan_id), str(project_id))))
            except (IndexError, KeyError) as reason:
                logging.error("Couldn't load values from json: %s - %s", project_name, reason)
                return [self.url()]
            except url_opener.UrlOpener.url_open_exceptions:
                return [self.url()]
        return checkmarx_report_urls

    def nr_warnings(self, metric_source_ids: Iterable[str], priority: str) -> int:
        """ Return the number of warnings in the reports with the specified priority. """
        nr_alerts = 0
        for project_name in metric_source_ids:
            try:
                project_id = self._fetch_project_id(project_name)
                last_scan_id = self._fetch_last_scan(project_id)[0]["id"]
                statistics_json = self._fetch_statistics(last_scan_id)
                nr_alerts += statistics_json[priority.lower() + 'Severity']
            except url_opener.UrlOpener.url_open_exceptions:
                return -1
            except StopIteration:
                logging.error("Error: no project id found for project with name '%s'.", project_name)
                return -1
            except (KeyError, IndexError) as reason:
                logging.error("Couldn't parse alerts for project %s with %s risk level from %s: %s",
                              project_name, priority, self.url(), reason)
                return -1
        return nr_alerts

    def _create_report(self, last_scan_id: int) -> int:
        post_request_body = 'reportType=XML&scanId={scan_id}'.format(scan_id=last_scan_id)
        json_string = self._url_open.\
            url_read(self._generate_report_post_url, post_body=bytes(post_request_body, 'ascii'))
        return json.loads(json_string)['reportId']

    class SastReportNotCreated(Exception):
        """ Exception thrown when SAST report is not found in status ready after defined retries. """

    def _get_issues_from_report(self, sast_report_id: int, priority: str) -> List:
        sast_report = self._url_open.url_read(self._sast_scan_url.format(scan_id=sast_report_id))
        root = xml.etree.cElementTree.fromstring(sast_report)
        issues = []
        queries = root.findall(".//Query")
        for query in queries:
            self._append_issues_from_query(query, priority, issues)
        return issues

    def _append_issues_from_query(self, query, priority, issues):
        severity = query.attrib["Severity"]
        if severity == priority.title():
            count, status = self.__get_results(query)
            if count:
                issues.append(self._create_issue(count, query, status))

    def _create_issue(self, count, query, status):
        display_url = self._reference_display_url.format(
            query_id=query.attrib["id"],
            query_version_code=query.attrib["QueryVersionCode"],
            name=query.attrib["name"])
        return self.Issue(query.attrib["group"], query.attrib["name"], display_url, count, status)

    @classmethod
    def __get_results(cls, query_node) -> (int, str):
        statuses = [issue.attrib['Status'] for issue in
                    query_node.findall('Result') if issue.attrib['FalsePositive'] == 'False']
        return len(statuses), 'New' if 'New' in statuses else 'Recurrent'

    def obtain_issues(self, metric_source_ids: Iterable[str], priority: str):
        """ Get detail info about warnings with the specified priority. """
        self._issues = []
        for project_name in metric_source_ids:
            try:
                project_id = self._fetch_project_id(project_name)
                last_scan_id = self._fetch_last_scan(project_id)[0]["id"]
                logging.info("Retrieved last scan id: %s.", last_scan_id)
                sast_report_id = self._create_report(last_scan_id)
                logging.info("Retrieved SAST report id %s for scan with id %s.", sast_report_id, last_scan_id)

                self._wait_for_sast_report(sast_report_id)
                logging.info(
                    "SAST report with id %s for scan with id %s created successfully.", sast_report_id, last_scan_id)
                self._issues = self._get_issues_from_report(sast_report_id, priority)
            except url_opener.UrlOpener.url_open_exceptions:
                pass
            except ValueError as reason:
                logging.error("Error loading json: %s.", reason)
            except KeyError as reason:
                logging.error("Tag %s could not be found.", reason)
            except xml.etree.ElementTree.ParseError as reason:
                logging.error("Error in checkmarx report xml: %s.", reason)
            except self.SastReportNotCreated:
                logging.error('SAST report is not created on the Checkmarx server!')

    def _wait_for_sast_report(self, sast_report_id: int, repeat_nr: int = 10, wait_seconds: int = 5):
        time.sleep(2)
        status_url = self._sast_scan_status_url.format(scan_id=sast_report_id)
        while self.__get_json(status_url)["status"]["value"] != "Created":
            self._url_open.url_read.cache_clear()
            repeat_nr -= 1
            if not repeat_nr:
                raise self.SastReportNotCreated()
            logging.info(
                "SAST report with id %s is still not created. "
                "Next check in %s second(s). There are %s attempts remaining before giving up.",
                sast_report_id, wait_seconds, repeat_nr)
            time.sleep(wait_seconds)

    def datetime(self, *metric_source_ids: str) -> DateTime:
        """ Return the last date and time the projects were scanned. """
        dates = []
        for project_name in metric_source_ids:
            try:
                project_id = self._fetch_project_id(project_name)
                last_scan_json = self._fetch_last_scan(project_id)
                last_scan_date_time = self.__parse_datetime(last_scan_json)
                dates.append(last_scan_date_time)
                logging.info("Last scan date from Checkmarx for project %s, project id %s is: %s. JSON: %s",
                             project_name, project_id, last_scan_date_time, last_scan_json)
            except url_opener.UrlOpener.url_open_exceptions:
                return datetime.datetime.min
            except (KeyError, IndexError, ValueError, AttributeError) as reason:
                logging.error("Couldn't parse date and time for project %s from %s: %s",
                              project_name, self.url(), reason)
                return datetime.datetime.min
        return min(dates, default=datetime.datetime.min)

    @staticmethod
    def __parse_datetime(json_object: Dict) -> DateTime:
        """ Parse the JSON to get the date and time of the last scan. """
        datetime_string = json_object[0]["dateAndTime"]["finishedOn"].split('.')[0]
        return dateutil.parser.parse(datetime_string, ignoretz=True)

    @functools.lru_cache(maxsize=1024)
    def _fetch_project_id(self, project_name: str) -> int:
        projects = self.__get_json(self._projects_url)
        return next(project['id'] for project in projects if project['name'] == project_name)

    def _fetch_statistics(self, scan_id: int) -> Dict[str, int]:
        return self.__get_json(self._statistics_url.format(id=scan_id))

    @functools.lru_cache(maxsize=1024)
    def _fetch_last_scan(self, project_d: int) -> Dict[str, int]:
        """ Create the api URL and fetch the report from it. """
        return self.__get_json(self._scan_url.format(project_id=project_d))

    def __get_json(self, api_url: str) -> Dict:
        """ Return and evaluate the JSON at the url using Basic Authentication. """
        return utils.eval_json(self._url_open.url_read(api_url))
