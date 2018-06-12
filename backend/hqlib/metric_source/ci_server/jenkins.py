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
import functools
import logging
import re
import urllib.parse
from typing import Dict, IO, List, Tuple

from hqlib.typing import DateTime, TimeDelta
from .. import url_opener
from ..abstract import ci_server

Job = Dict[str, str]  # pylint: disable=invalid-name
Jobs = List[Job]  # pylint: disable=invalid-name


class Jenkins(ci_server.CIServer):
    """ Class representing the Jenkins instance. """

    metric_source_name = "Jenkins build server"
    api_postfix = "api/python"
    jobs_api_postfix = api_postfix + "?tree=jobs[name,description,color,url,buildable]"
    builds_api_postfix = api_postfix + "?tree=builds[result,building]&depth=1"

    def __init__(self, url: str, username: str = '', password: str = '', job_re: str = '') -> None:
        super().__init__(url=url)
        self.__url_opener = url_opener.UrlOpener(username=username, password=password)
        self.__job_re = re.compile(job_re)
        self.__job_url = url + 'job/{job}/'
        self.__last_completed_build_url = self.__job_url + 'lastCompletedBuild/'
        self.__last_successful_build_url = self.__job_url + 'lastSuccessfulBuild/'
        self._last_stable_build_url = self.__job_url + 'lastStableBuild/'
        self.__jobs_api_url = url + self.jobs_api_postfix

    def number_of_active_jobs(self) -> int:
        """ Return the total number of active Jenkins jobs. """
        try:
            return len(self.__active_jobs())
        except url_opener.UrlOpener.url_open_exceptions:
            return -1

    def number_of_failing_jobs(self) -> int:
        """ Return the number of failing Jenkins jobs. """
        try:
            return len(self.__failing_jobs())
        except url_opener.UrlOpener.url_open_exceptions:
            return -1

    def number_of_unused_jobs(self) -> int:
        """ Return the number of unused Jenkins jobs. """
        try:
            return len(self.__unused_jobs())
        except url_opener.UrlOpener.url_open_exceptions:
            return -1

    def failing_jobs_url(self) -> List[Tuple[str, str, str]]:
        """ Return the urls for the failing Jenkins jobs. """
        try:
            return self.__job_urls(self.__failing_jobs())
        except url_opener.UrlOpener.url_open_exceptions:
            return []

    def unused_jobs_url(self) -> List[Tuple[str, str, str]]:
        """ Return the urls for the unused Jenkins jobs. """
        try:
            return self.__job_urls(self.__unused_jobs())
        except url_opener.UrlOpener.url_open_exceptions:
            return []

    def __job_urls(self, jobs: Jobs) -> List[Tuple[str, str, str]]:
        """ Return the urls for the Jenkins jobs. """
        def days(job: Job) -> str:
            """ Return the age of the last stable build. """
            age = self.__age_of_last_stable_build(job)
            return '?' if age == datetime.timedelta.max else str(age.days)

        return [(self.__format_job_name(job), job['url'], days(job)) for job in jobs]

    @classmethod
    def __format_job_name(cls, job: Job):
        """ Formats the job name for display. """
        parts = job['url'].split('/')
        length = len(parts)
        if not parts[length - 1]:
            length -= 1
        return parts[length - 3] + '/' + parts[length - 1] \
            if length > 2 and parts[length - 1] == job['name'] and parts[length - 2] == 'job' else job['name']

    def __failing_jobs(self) -> Jobs:
        """ Return the active Jenkins jobs that are failing. """

        def failing(job: Job) -> bool:
            """ Return whether the job is failing. """
            return not job['color'].startswith('blue') if job.get('buildable', False) else False

        def old(job: Job) -> bool:
            """ Return whether the build age of the job is considered to be long ago. """
            return self.__age_of_last_stable_build(job) > datetime.timedelta(days=1)

        return [job for job in self.__active_jobs() if self.__builds(job) and failing(job) and old(job)]

    def __unused_jobs(self) -> Jobs:
        """ Return the active Jenkins jobs that are unused. """
        def grace_time(job: Job, default: int = 180) -> TimeDelta:
            """ Return the grace time for the job. """
            # Don't consider projects to be old until their last successful build was longer ago than the grace time.
            description = job['description'] or ''
            match = re.search(r'\[gracedays=(\d+)\]', description.lower())
            days = int(match.group(1)) if match else default
            return datetime.timedelta(days=days)

        return [job for job in self.__active_jobs() if self.__age_of_last_completed_build(job) > grace_time(job)]

    def __active_jobs(self) -> Jobs:
        """ Return all active Jenkins jobs. """
        return [job for job in self.jobs() if job.get('buildable', False)]

    def jobs(self) -> Jobs:
        """ Return all Jenkins jobs that match our job regular expression. """
        all_jobs: Jobs = []
        jobs = self._api(self.__jobs_api_url)['jobs']
        all_jobs.extend(jobs)
        for job in jobs:
            all_jobs.extend(self.__subjobs(job))
        return [job for job in all_jobs if self.__job_re.match(job['name'])]

    def __subjobs(self, job) -> Jobs:
        """ Return the subjobs of a job. """
        try:
            return self._api(job["url"] + self.jobs_api_postfix)['jobs']
        except KeyError:
            return []

    def __age_of_last_completed_build(self, job: Job) -> TimeDelta:
        """ Return the age of the last completed build of the job. """
        return self.__age_of_build(job, "lastCompletedBuild") \
            if any(self.__builds(job, "SUCCESS", "FAILURE", "UNSTABLE")) else datetime.timedelta.max

    def __age_of_last_stable_build(self, job: Job) -> TimeDelta:
        """ Return the age of the last stable build of the job. """
        return self.__age_of_build(job, "lastStableBuild") \
            if any(self.__builds(job, "SUCCESS")) else datetime.timedelta.max

    def __age_of_build(self, job: Job, result_type: str) -> TimeDelta:
        """ Return the age of the last completed or stable build of the job. """
        build_time = self._job_datetime(job, result_type)
        return datetime.timedelta.max if build_time == datetime.datetime.min else \
            datetime.datetime.utcnow() - build_time

    def _job_datetime(self, job: Job, result_type: str) -> DateTime:
        """ Return the datetime of the last completed or stable build of the job. """
        builds_url = job["url"].strip("/") + "/" + result_type + "/" + self.api_postfix
        try:
            job = self._api(builds_url)
        except url_opener.UrlOpener.url_open_exceptions:
            return datetime.datetime.min
        try:
            return datetime.datetime.utcfromtimestamp(float(job['timestamp']) / 1000)
        except (KeyError, ValueError) as reason:
            logging.warning("Couldn't get timestamp from %s: %s.", builds_url, reason)
            return datetime.datetime.min

    def __builds(self, job: Job, *results: str) -> List[Dict]:
        """ Return the builds of the job with the given status, if any. """
        builds = self._api(job["url"] + self.builds_api_postfix).get("builds", [])
        builds = [build for build in builds if not build.get("building")]
        return [build for build in builds if build.get("result") in results] if results else builds

    @functools.lru_cache(maxsize=1024)
    def _api(self, url: str) -> Dict:
        """ Return the result of the API call at the url. """
        data = self.__url_opener.url_read(url)
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        try:
            return ast.literal_eval(data)
        except Exception as reason:
            logging.error("Couldn't evaluate %s from %s: %s", data, url, reason)
            raise

    def url_open(self, url: str, log_error: bool = True) -> IO:
        """ Override to safely quote the url, needed because Jenkins may return unquoted urls. """
        return self.__url_opener.url_open(urllib.parse.quote(url, safe="%/:=&?~#+!$,;'@()*[]"), log_error=log_error)
