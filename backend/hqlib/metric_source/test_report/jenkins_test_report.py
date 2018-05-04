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


import ast
import datetime
import logging
import re
from typing import Dict, List, Optional, Sequence, Set, Union

from hqlib import utils

from ..abstract import test_report
from ..url_opener import UrlOpener
from ...typing import DateTime
from .. import Jenkins


class JenkinsTestReport(test_report.TestReport):
    """ Class representing Jenkins test reports. """
    metric_source_name = 'Jenkins testreport'

    def _expand_metric_source_id_reg_exps(self, *metric_source_ids: str) -> Sequence[str]:
        """ Expand regular expressions. """
        try:
            job_names = [job["name"] for job in Jenkins(self.url(), self._username, self._password).jobs()]
        except UrlOpener.url_open_exceptions:
            return metric_source_ids
        matching_job_names = set()
        for metric_source_id in metric_source_ids:
            matching_job_names |= self.__expand_metric_source_id(metric_source_id, job_names)
        return sorted(list(matching_job_names))

    def __expand_metric_source_id(self, metric_source_id: str, job_names: List[str]) -> Set[str]:
        """ Expand the metric source id if it is a regular expression. """
        if "/" in metric_source_id:
            return {metric_source_id}  # pipeline job
        reg_exp = re.compile(metric_source_id)
        matching_job_names = set(filter(reg_exp.match, job_names))
        if matching_job_names:
            return matching_job_names
        logging.warning("No Jenkins jobs match metric source id %s.", metric_source_id)
        logging.warning("Jenkins jobs found at %s: %s", self.url(), ", ".join(job_names))
        return {metric_source_id}

    def metric_source_urls(self, *metric_source_ids: str) -> List[str]:
        """ Return the url(s) to the metric source for the metric source id. """
        metric_source_ids = self._expand_metric_source_id_reg_exps(*metric_source_ids)
        return sorted([utils.url_join(self.url(), "job", metric_source_id) for metric_source_id in metric_source_ids])

    def _passed_tests(self, metric_source_id: str) -> int:
        """ Return the number of passed tests. """
        try:
            return self.__test_count(metric_source_id, 'passCount')
        except KeyError:
            # Surefire reports don't have a pass count, calculate it:
            total = self.__test_count(metric_source_id, 'totalCount')
            skipped = self._skipped_tests(metric_source_id)
            failed = self._failed_tests(metric_source_id)
            return total - skipped - failed

    def _failed_tests(self, metric_source_id: str) -> int:
        """ Return the number of failed tests. """
        return self.__test_count(metric_source_id, 'failCount')

    def _skipped_tests(self, metric_source_id: str) -> int:
        """ Return the number of skipped tests. """
        return self.__test_count(metric_source_id, 'skipCount')

    def __test_count(self, metric_source_id: str, result_type: str) -> int:
        """ Return the number of tests with the specified result in the test report. """
        json = self.__read_json(metric_source_id, "lastCompletedBuild/api/python")
        if not json:
            # Last completed build doesn't have the requested information, e.g. because it's aborted.
            # Fall back to last successful build.
            json = self.__read_json(metric_source_id, "lastSuccessfulBuild/api/python")
        return int(json[result_type]) if json else -1

    def _report_datetime(self, metric_source_id: str) -> DateTime:
        """ Return the date and time of the specified report. """
        json = self.__read_json(metric_source_id, "lastCompletedBuild/api/python")
        if not json:
            # Last completed build doesn't have the requested information, e.g. because it's aborted.
            # Fall back to last successful build.
            json = self.__read_json(metric_source_id, "lastSuccessfulBuild/api/python")
        return datetime.datetime.fromtimestamp(float(json["timestamp"]) / 1000.) if json else datetime.datetime.min

    def __read_json(self, job_name: str, api_postfix: str) -> Optional[Dict[str, Union[int, str]]]:
        """ Return the test results and the timestamp from the url, or None when something goes wrong. """
        api_url = utils.url_join(self.url(), "job", job_name, api_postfix)
        try:
            contents = self._url_read(api_url)
        except UrlOpener.url_open_exceptions:
            return None
        try:
            build = ast.literal_eval(contents)
        except (SyntaxError, NameError, TypeError) as reason:
            logging.error("Couldn't eval %s: %s\nData received: %s", api_url, reason, contents)
            return None
        return self.__test_data(build)

    @staticmethod
    def __test_data(build: Dict) -> Optional[Dict[str, Union[int, str]]]:
        """ Return the test data from the build json. """
        actions = build.get("actions", [])
        for action in actions:
            if "totalCount" in action and "failCount" in action:
                # Assume this is the test action dictionary. Include the timestamp of the build in the dictionary.
                action["timestamp"] = build["timestamp"]
                return action
        return None
