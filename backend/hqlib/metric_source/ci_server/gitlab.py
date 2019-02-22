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

import datetime
import functools
import logging
import re
from typing import Dict, Optional, List
import gitlab
from gitlab.v4.objects import Project
from dateutil.tz import tzlocal

from hqlib import utils
from hqlib.typing import TimeDelta
from ..abstract import ci_server


class GitLabCI(ci_server.CIServer):
    """ Class representing the GitLab instance. """

    metric_source_name = 'GitLabCI'

    # pylint: disable=too-many-arguments

    def __init__(self, url: str, *projects: str, branch_re: str = '', private_token: str = '') -> None:

        self.__gitlab = gitlab.Gitlab(url, private_token=private_token)
        self.__private_token = private_token
        self.__branch_re = re.compile(branch_re) if branch_re else ''
        self.__projects = projects
        self.__url = url
        self.__commit_display_url = utils.url_join(self.__url, '{project_name}/commit/{commit_id}')
        self.__days_to_tolerate = 180

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

    @classmethod
    def _get_time_since(cls, date: str) -> TimeDelta:
        return datetime.datetime.now().astimezone(tz=tzlocal()) - utils.parse_iso_datetime(date)

    def number_of_failing_jobs(self) -> int:
        """ Return the number of failing CI jobs. """
        return len(self._builds_urls(True))

    def number_of_unused_jobs(self) -> int:
        """ Return the number of unused CI jobs. """
        return len(self._builds_urls())

    def failing_jobs_url(self) -> Optional[List]:
        """ Return the urls for the failing Jenkins jobs. """
        return self._builds_urls(True)

    def unused_jobs_url(self) -> Optional[List]:
        """ Return the urls for the unused CI jobs. """
        return self._builds_urls()

    def number_of_active_jobs(self) -> int:
        """ Return the total number of active CI jobs. """
        return len(self._all_builds())

    @functools.lru_cache(maxsize=2048)
    def _builds_urls(self, only_failed: bool = False) -> Optional[List]:
        try:
            ret = []
            for project in self._get_projects():
                self._add_projects_builds(only_failed, project, ret)
            return ret
        except (gitlab.GitlabError, KeyError, TypeError) as reason:
            logging.error('Error retrieving build data. Reason: %s.', reason)
        return []

    def _add_projects_builds(self, only_failed, project, ret):
        build_pairs = self._get_builds_list(project, only_failed)
        if build_pairs:
            for commits_pair in build_pairs:
                self.__add_build_if_applicable(commits_pair, only_failed, project, ret)

    def __add_build_if_applicable(self, commits_pair, only_failed, project, ret):
        do_append, days_to_report = self.__get_build_criteria(commits_pair, only_failed)
        if do_append:
            ret.append(
                (project.attributes['name'] + '/' + commits_pair[0].branch_name + ' - ' + commits_pair[0].comment,
                 self.__commit_display_url.format(
                     project_name=project.attributes['path_with_namespace'],
                     commit_id=commits_pair[0].attributes['commit_id']),
                 days_to_report))

    def __get_build_criteria(self, commits_pair, failed):
        age_completed = self._get_time_since(commits_pair[0].attributes['created_at'])
        age_succeeded = self._get_time_since(commits_pair[1].attributes['created_at'])\
            if failed and commits_pair[1] else age_completed
        return self.__should_be_appended(age_completed, age_succeeded, failed), \
            age_succeeded.days if failed else age_completed.days

    def __should_be_appended(self, age_completed, age_succeeded, failed):
        return failed and age_succeeded.days > 0 or not failed and age_completed.days > self.__days_to_tolerate

    def _get_builds_list(self, project, only_failed: bool) -> List:
        built_commits = self._get_built_commits(project)
        return [cmt_pair for cmt_pair in built_commits if cmt_pair[0].attributes['status'] == 'failed']\
            if only_failed else built_commits

    @functools.lru_cache(maxsize=2048)
    def _get_built_commits(self, project: Project):
        last_finished_commits = \
            [self.__get_last_finished_commit(project, br) for br in self.__get_applicable_branches(project)]
        return [commits_pair for commits_pair in last_finished_commits if commits_pair[0]]

    def __get_applicable_branches(self, project):
        branches = project.branches.list()
        if self.__branch_re:
            branches = [br for br in branches if self.__branch_re.match(br.attributes['name'])]
        return branches

    def __get_last_finished_commit(self, project, branch):
        commits = sorted(
            project.commits.list(ref_name=branch.attributes['name']),
            key=lambda cmt: cmt.attributes['created_at'], reverse=True)
        last_completed = self.__get_status(commits, branch.attributes['name'], 'success', 'failed')
        last_succeeded = self.__get_status(commits, branch.attributes['name'], 'success')
        return last_completed, last_succeeded

    @classmethod
    def __get_status(cls, commits, branch_name: str, *statuses: str):
        try:
            for cmt in commits:
                stat = cmt.statuses.list(ref=branch_name)
                if stat and stat[0].attributes['status'] in statuses:
                    stat[0].branch_name = branch_name
                    stat[0].comment = cmt.attributes['title']
                    return stat[0]
        except KeyError as reason:
            logging.error('Error retrieving commit status data. Reason: %s.', reason)
        return None

    def _all_builds(self) -> List[Dict]:
        """ Return the urls for all CI jobs. """
        try:
            ret = []
            for project in self._get_projects():
                ret.extend(self._get_built_commits(project))
            return ret
        except (AttributeError, gitlab.GitlabError) as reason:
            logging.error('Error retrieving builds data. Reason: %s.', reason)
        return []

    def metric_source_urls(self, *metric_source_ids: str) -> List[str]:  # pylint: disable=no-self-use
        """ Return the url(s) to the metric source for the metric source id. """
        return [project.attributes['web_url'] for project in self._get_projects()]
