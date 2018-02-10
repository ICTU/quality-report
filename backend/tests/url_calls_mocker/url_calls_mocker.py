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

import os
from hqlib.metric_source.url_opener import UrlOpener


class UrlOpenerMock(UrlOpener):
    """" The class is used to mock UrlOpener class, to avoid real http calls to the urls given in example
    project definition file and to provide example report with example metric sources data.
    Usage:
            import hqlib.metric_source.url_opener
            from tests.url_calls_mocker.url_calls_mocker import UrlOpenerMock
            hqlib.metric_source.url_opener.UrlOpener = UrlOpenerMock
    """

    def __init__(self, uri: str = None, username: str = None, password: str = None) -> None:
        self._dir_path = os.getcwd()
        self._map = {
            # begin UserStoriesInProgress
            'https://jira.myorg.nl/jira/rest/api/2/filter/15208': self._get_file_content(
                os.path.join(self._dir_path,
                             'docs/examples/example_metric_sources/jira_filter_stories_in_progress.json')),

            'https://jira.myorg.nl/jira/rest/api/2/search?filter_parameters': self._get_file_content(
                os.path.join(self._dir_path,
                             'docs/examples/example_metric_sources/jira_filter_search_stories_in_progress.json')),
            # end UserStoriesInProgress

            # begin UserStoriesDuration
            'https://jira.myorg.nl/jira/rest/api/2/filter/15225': self._get_file_content(
                os.path.join(self._dir_path,
                             'docs/examples/example_metric_sources/jira_filter_stories_duration.json')),

            'https://jira.myorg.nl/jira/rest/api/2/search?filter_parameters_duration': self._get_file_content(
                os.path.join(self._dir_path,
                             'docs/examples/example_metric_sources/jira_filter_search_stories_duration.json')),

            'https://jira.myorg.nl/jira/rest/api/2/issue/ISS-1?expand=changelog&fields="*all,-comment"':
                self._get_file_content(
                    os.path.join(self._dir_path,
                                 'docs/examples/example_metric_sources/jira_changelog_stories_duration.json')),
            # end UserStoriesDuration

            # begin FailingCIJobs and UnusedCIJobs

            'http://www.jenkins.proj.org:8080/api/python?tree=jobs[name,description,color,url,buildable]':
                self._get_file_content(os.path.join(self._dir_path,
                                                    'docs/examples/example_metric_sources/jenkins_get_jobs_1.json')),

            'http://www.jenkins.proj.org:8080/job/proj-pipeline/api/python?tree=jobs'
            '[name,description,color,url,buildable]': self._get_file_content(
                os.path.join(self._dir_path, 'docs/examples/example_metric_sources/jenkins_ci_jobs.json')),

            'http://www.jenkins.proj.org:8080/job/proj-pipeline/job/1029_Environemnt_van_elkaar_en_tekst/'
            'api/python?tree=builds[result]&depth=1': self._get_file_content(
                os.path.join(self._dir_path,
                             'docs/examples/example_metric_sources/jenkins_build_result.json')),

            'http://www.jenkins.proj.org:8080/job/proj-pipeline/job/5553_Iets_anders/api/python?tree=builds[result]'
            '&depth=1': self._get_file_content(
                os.path.join(self._dir_path,
                             'docs/examples/example_metric_sources/jenkins_build_result.json')),

            'http://www.jenkins.proj.org:8080/job/proj-pipeline/job/1029_Environemnt_van_elkaar_en_tekst/'
            'lastStableBuild/api/python': self._get_file_content(
                os.path.join(self._dir_path,
                             'docs/examples/example_metric_sources/jenkins_unused_job_1029_last_stable.json')),

            'http://www.jenkins.proj.org:8080/job/proj-pipeline/job/1029_Environemnt_van_elkaar_en_tekst/'
            'lastCompletedBuild/api/python': self._get_file_content(
                os.path.join(self._dir_path,
                             'docs/examples/example_metric_sources/jenkins_unused_job_1029_last_complete.json')),

            'http://www.jenkins.proj.org:8080/job/proj-pipeline/job/5553_Iets_anders/lastCompletedBuild/api/python':
                self._get_file_content(os.path.join(self._dir_path,
                                                    'docs/examples/example_metric_sources/'
                                                    'jenkins_failing_job_5553_last_complete.json')),
            # begin FailingCIJobs and UnusedCIJobs

            'https://last_security_date_url': self._get_file_content(
                os.path.join(self._dir_path, 'docs/examples/example_metric_sources/file_with_date.json'))
        }
        super().__init__()

    def url_read(self, url: str, *args, encoding: str = 'utf-8', **kwargs) -> str:  # pylint: disable=unused-argument
        return self._map[url] if url in self._map.keys() else ""

    @staticmethod
    def _get_file_content(file_name: str) -> str:
        with open(file_name) as file:
            return file.read()
