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
import re
from typing import Dict, Optional, List
import gitlab
from gitlab.v4.objects import Project

from hqlib import utils
from hqlib.typing import TimeDelta
from ..abstract import ci_server


class GitLabCI(ci_server.CIServer):
    """ Class representing the GitLab instance. """

    metric_source_name = 'GitLabCI'

    # pylint: disable=too-many-arguments

    def __init__(self, url: str, *projects: str, job_re: str = '', private_token: str = '') -> None:

        self.__gitlab = gitlab.Gitlab(url, private_token=private_token)
        self._job_re = re.compile(job_re) if job_re else ''
        self.__projects = projects

        super().__init__()

    @functools.lru_cache(maxsize=2048)
    def _get_projects(self) -> List[Project]:
        try:
            ret = []
            for project_name in self.__projects:
                ret.append(self.__gitlab.projects.get(project_name))
            return ret
        except (gitlab.GitlabError, TypeError) as reason:
            logging.error('Error retrieving project data. Reason: %s.', reason)
            return []

    def _get_days_since_projects_last_success(self, project: Project) -> TimeDelta:
        last_success_date = self._get_last_successful_pipeline_date(project, 'success')
        return datetime.datetime.now() - utils.parse_iso_datetime(last_success_date)

    def _get_days_since_projects_last_completion(self, project: Project) -> TimeDelta:
        last_completion_date = self._get_last_successful_pipeline_date(project, 'success', 'failure')
        return datetime.datetime.now() - utils.parse_iso_datetime(last_completion_date)

    @classmethod
    @functools.lru_cache(maxsize=2048)
    def _get_last_successful_pipeline_date(cls, project: Project, *statuses: str):
        return max([
            project.pipelines.get(pipe.attributes['id']).attributes['finished_at']
            for pipe in project.pipelines.list() if pipe.attributes['status'] in statuses
        ], default=datetime.datetime.max.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))

    def number_of_failing_jobs(self) -> int:
        """ Return the number of failing CI jobs. """
        return len(self._jobs_urls(self._get_days_since_projects_last_success, 1, 'failed'))

    def number_of_unused_jobs(self) -> int:
        """ Return the number of unused CI jobs. """
        return len(self._jobs_urls(self._get_days_since_projects_last_completion, 180))

    def failing_jobs_url(self) -> Optional[List]:
        """ Return the urls for the failing Jenkins jobs. """
        return self._jobs_urls(self._get_days_since_projects_last_success, 1, 'failed')

    def unused_jobs_url(self) -> Optional[List]:
        """ Return the urls for the unused CI jobs. """
        return self._jobs_urls(self._get_days_since_projects_last_completion, 180)

    def number_of_active_jobs(self) -> int:
        """ Return the total number of active CI jobs. """
        return len(self._all_jobs())

    def _jobs_urls(self, get_age, days_to_tolerate: int, *statuses: str) -> Optional[List]:
        try:
            ret = []
            for project in self._get_projects():
                age = get_age(project)
                if age.days > days_to_tolerate:
                    jobs = self.__get_jobs_list(project, statuses)
                    self.__append_jobs(project, jobs, str(age.days), ret)
            return ret
        except (AttributeError, gitlab.GitlabError) as reason:
            logging.error('Error retrieving pipeline data. Reason: %s.', reason)
        return []

    @classmethod
    def __append_jobs(cls, project, jobs, days, ret):
        if jobs:
            ret.append([(project.attributes['name_with_namespace'] + ' / ' + job.attributes['name'],
                         job.attributes['web_url'], days) for job in jobs])

    def __get_jobs_list(self, project, statuses):
        if statuses:
            jobs = [job for job in self._get_jobs_list(project) if job.attributes['status'] in statuses]
        else:
            jobs = self._get_jobs_list(project)
        return jobs

    @functools.lru_cache(maxsize=2048)
    def _get_jobs_list(self, project: Project):
        if not self._job_re:
            return project.jobs.list()
        return [job for job in project.jobs.list() if self._job_re.match(job.attributes['name'])]

    def _all_jobs(self) -> List[Dict]:
        """ Return the urls for all CI jobs. """
        try:
            ret = []
            for project in self._get_projects():
                ret.extend(self._get_jobs_list(project))
            return ret
        except (AttributeError, gitlab.GitlabError) as reason:
            logging.error('Error retrieving jobs data. Reason: %s.', reason)
        return []
