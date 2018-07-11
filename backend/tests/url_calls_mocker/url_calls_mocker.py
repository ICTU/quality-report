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

import pathlib
import logging
from hqlib.metric_source.url_opener import UrlOpener


class UrlOpenerMock(UrlOpener):
    """ The class is used to mock UrlOpener class, to avoid real http calls to the urls given in example
    project definition file and to provide example report with example metric sources data.
    Usage:
            import hqlib.metric_source.url_opener
            from tests.url_calls_mocker.url_calls_mocker import UrlOpenerMock
            hqlib.metric_source.url_opener.UrlOpener = UrlOpenerMock
    """

    def __init__(self, uri: str = None, username: str = None, password: str = None) -> None:
        self._dir_path = pathlib.Path(__file__).parent.parent.parent.parent
        examples_metric_sources_path = self._dir_path / 'docs' / 'examples' / 'example_metric_sources'
        self._map = {
            # begin UserStoriesInProgress
            'https://jira.myorg.nl/jira/rest/api/2/filter/15208':
                self._get_file_content(
                    examples_metric_sources_path / 'jira_filter_stories_in_progress.json'
                ),

            'https://jira.myorg.nl/jira/rest/api/2/search?filter_parameters':
                self._get_file_content(
                    examples_metric_sources_path / 'jira_filter_search_stories_in_progress.json'
                ),
            # end UserStoriesInProgress

            # begin DurationOfManualLogicalTestCases
            'https://jira.myorg.nl/jira/rest/api/2/filter/15999':
                self._get_file_content(
                    examples_metric_sources_path / 'jira_filter_manual_tests.json'
                ),

            'https://jira.myorg.nl/jira/rest/api/2/search?filter_manual_tests':
                self._get_file_content(
                    examples_metric_sources_path / 'jira_filter_search_manual_tests.json'
                ),
            # end DurationOfManualLogicalTestCases

            # begin UserStoriesDuration
            'https://jira.myorg.nl/jira/rest/api/2/filter/15225':
                self._get_file_content(
                    examples_metric_sources_path / 'jira_filter_stories_duration.json'
                ),

            'https://jira.myorg.nl/jira/rest/api/2/search?filter_parameters_duration':
                self._get_file_content(
                    examples_metric_sources_path / 'jira_filter_search_stories_duration.json'
                ),

            'https://jira.myorg.nl/jira/rest/api/2/issue/ISS-1?expand=changelog&fields="*all,-comment"':
                self._get_file_content(
                    examples_metric_sources_path / 'jira_changelog_stories_duration.json'
                ),
            # end UserStoriesDuration

            # begin FailingCIJobs and UnusedCIJobs

            'http://www.jenkins.proj.org:8080/api/python?tree=jobs[name,description,color,url,buildable]':
                self._get_file_content(
                    examples_metric_sources_path / 'jenkins_get_jobs_1.json'
                ),

            'http://www.jenkins.proj.org:8080/job/proj-pipeline/api/python?tree=jobs'
            '[name,description,color,url,buildable]':
                self._get_file_content(
                    examples_metric_sources_path / 'jenkins_ci_jobs.json'
                ),

            'http://www.jenkins.proj.org:8080/job/proj-pipeline/job/1029_Environemnt_van_elkaar_en_tekst/'
            'api/python?tree=builds[result,building]&depth=1':
                self._get_file_content(
                    examples_metric_sources_path / 'jenkins_build_result.json'
                ),

            'http://www.jenkins.proj.org:8080/job/proj-pipeline/job/5553_Iets_anders/api/python?tree='
            'builds[result,building]&depth=1':
                self._get_file_content(
                    examples_metric_sources_path / 'jenkins_build_result.json'
                ),

            'http://www.jenkins.proj.org:8080/job/proj-pipeline/job/1029_Environemnt_van_elkaar_en_tekst/'
            'lastStableBuild/api/python':
                self._get_file_content(
                    examples_metric_sources_path / 'jenkins_unused_job_1029_last_stable.json'
                ),

            'http://www.jenkins.proj.org:8080/job/proj-pipeline/job/1029_Environemnt_van_elkaar_en_tekst/'
            'lastCompletedBuild/api/python':
                self._get_file_content(
                    examples_metric_sources_path / 'jenkins_unused_job_1029_last_complete.json'
                ),

            'http://www.jenkins.proj.org:8080/job/proj-pipeline/job/5553_Iets_anders/lastCompletedBuild/api/python':
                self._get_file_content(
                    examples_metric_sources_path / 'jenkins_failing_job_5553_last_complete.json'
                ),
            # end FailingCIJobs and UnusedCIJobs

            # begin Sonar
            'https://my.sonarqube.com/api/server/version':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_version.txt'
                ),

            'https://my.sonarqube.com/api/updatecenter/installed_plugins?format=json':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_plugins.json'
                ),

            'https://my.sonarqube.com/api/project_analyses/search?'
            'project=nl.comp:my_project&format=json&ps=1&category=VERSION':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search.json'
                ),

            'https://my.sonarqube.com/api/projects/index?subprojects=true':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_projects.json'
                ),

            'https://my.sonarqube.com/api/components/show?component=nl.comp:my_project':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_component.json'
                ),

            'https://my.sonarqube.com/api/qualityprofiles/search?format=json':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_qualityprofiles.json'
                ),

            'https://my.sonarqube.com/api/components/search?qualifiers=BRC,TRK&q=nl.comp:my_project':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_component_search.json'
                ),

            'https://my.sonarqube.com/api/measures/component?'
            'componentKey=nl.comp:my_project&metricKeys=blocker_violations':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_blocker_violations.json'
                ),

            'https://my.sonarqube.com/api/measures/component?'
            'componentKey=nl.comp:my_project&metricKeys=critical_violations':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_critical_violations.json'
                ),

            'https://my.sonarqube.com/api/measures/component?'
            'componentKey=nl.comp:my_project&metricKeys=major_violations':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_major_violations.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&'
            'resolved=false&rules=checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.CyclomaticComplexityCheck':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&'
            'resolved=false&rules=pmd:CyclomaticComplexity':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&resolved=false&'
            'rules=squid:MethodCyclomaticComplexity':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&'
            'resolved=false&rules=csharpsquid:S1541':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&'
            'resolved=false&rules=csharpsquid:FunctionComplexity':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&'
            'resolved=false&rules=javascript:FunctionComplexity':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&'
            'resolved=false&rules=Web:ComplexityCheck':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&'
            'resolved=false&rules=python:FunctionComplexity':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&'
            'resolved=false&rules=vbnet:S1541':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&'
            'resolved=false&rules=tslint:cyclomatic-complexity':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/measures/component?componentKey=nl.comp:my_project&metricKeys=functions':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_measures.json'
                ),

            'https://my.sonarqube.com/api/measures/component?componentKey=nl.comp:my_project&'
            'metricKeys=duplicated_lines':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_duplicated_lines.json'
                ),

            'https://my.sonarqube.com/api/measures/component?componentKey=nl.comp:my_project&metricKeys=lines':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_lines.json'
                ),

            'https://my.sonarqube.com/api/measures/component?componentKey=nl.comp:my_project&metricKeys=ncloc':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_ncloc.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&resolved=false&'
            'rules=squid:S138':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&resolved=false&'
            'rules=checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.JavaNCSSCheck':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&resolved=false&'
            'rules=Pylint:R0915':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&resolved=false&'
            'rules=Web:LongJavaScriptCheck':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&resolved=false&'
            'rules=checkstyle:com.puppycrawl.tools.checkstyle.checks.metrics.ParameterNumberCheck':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&resolved=false&'
            'rules=pmd:ExcessiveParameterList':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&resolved=false&'
            'rules=csharpsquid:S107':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&resolved=false&'
            'rules=squid:S00107':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&resolved=false&'
            'rules=javascript:ExcessiveParameterList':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&resolved=false&'
            'rules=python:S107':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&resolved=false&'
            'rules=csharpsquid:S125':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&resolved=false&'
            'rules=csharpsquid:CommentedCode':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&resolved=false&'
            'rules=squid:CommentedOutCodeLine':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&resolved=false&'
            'rules=javascript:CommentedCode':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&resolved=false&'
            'rules=python:S125':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&resolved=false&'
            'rules=Web:AvoidCommentedOutCodeCheck':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&resolved=false&'
            'rules=squid:NoSonar':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?componentRoots=nl.comp:my_project&resolved=false&'
            'rules=Pylint:I0011':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),

            'https://my.sonarqube.com/api/issues/search?resolutions=FALSE-POSITIVE&componentRoots=nl.comp:my_project':
                self._get_file_content(
                    examples_metric_sources_path / 'sonar_search_0_found.json'
                ),
            # end Sonar

            # begin trello
            'https://api.trello.com/1/boards/5fe/?fields=id,url,dateLastActivity&lists=open&list_fields=name'
            '&cards=visible&card_fields=shortUrl,dateLastActivity,due,idList,name&key=2d3&token=57b':
                self._get_file_content(
                    examples_metric_sources_path / 'trello_board.json'
                ),
            # end trello

            # begin junit
            'http://www.junit.report.url/junit.xml':
                self._get_file_content(
                    examples_metric_sources_path / 'junit_report.xml'
                ),
            # end junit

            # begin zap scan
            'http://jenkins/job/zap_scan/ws/report.html':
                self._get_file_content(
                    examples_metric_sources_path / 'ZAPScanningReport.html'
                ),
            # end zap scan

            'https://last_security_date_url':
                self._get_file_content(
                    examples_metric_sources_path / 'file_with_date.json'
                ),
        }
        super().__init__()

    def url_read(self, url: str, *args, encoding: str = 'utf-8', **kwargs) -> str:  # pylint: disable=unused-argument
        if url in self._map.keys():
            return self._map[url]
        logging.info("URL %s is still not mocked for example report!", url)
        return ''

    @staticmethod
    def _get_file_content(file_name: pathlib.Path) -> str:
        return pathlib.Path(file_name).read_text()
