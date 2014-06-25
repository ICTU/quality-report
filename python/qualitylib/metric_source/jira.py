'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''


from qualitylib.metric_source import url_opener
from qualitylib.metric_source.tasks import Tasks
from qualitylib import utils
import datetime
import urllib
import logging


class Jira(Tasks, url_opener.UrlOpener):
    ''' Class representing the Jira instance. '''
    metric_source_name = 'Jira'
    TECHNICAL_TASK_ISSUE_TYPE = 8
    ID_PREFIX = 'Metriek '
    ID_TEMPLATE = ID_PREFIX + '%s'

    def __init__(self, url, username, password, jira_project_id=None,
                 jira_parent_task_id=None, open_bug_query_id=None, 
                 open_security_bug_query_id=None,  
                 blocking_test_issues_query_id=None):
        self.__url = url
        self.__new_task_url = self.__create_new_task_url(jira_project_id,
                                                         jira_parent_task_id)
        self.__open_bug_query_id = open_bug_query_id
        self.__open_security_bug_query_id = open_security_bug_query_id
        self.__blocking_test_issues_query_id = blocking_test_issues_query_id
        super(Jira, self).__init__(username=username, password=password)

    def __create_new_task_url(self, jira_project_id, jira_parent_task_id):
        ''' Determine the new task url based on project and 
            a parent task for new tasks. '''
        new_task_url = self.__url
        if jira_project_id and jira_parent_task_id:
            parameters = dict(pid=jira_project_id, 
                              parent_issue_id=jira_parent_task_id, 
                              issuetype=self.TECHNICAL_TASK_ISSUE_TYPE)
            new_task_url += 'secure/CreateSubTaskIssue!default.jspa?' \
                'pid=%(pid)d&issuetype=%(issuetype)d&' \
                'parentIssueId=%(parent_issue_id)d' % parameters
        return new_task_url

    def tasks(self, metric_id, recent_only=False, weeks_recent=3):
        ''' Return a list of open issues that refer to the metric id. '''
        def browse_url(issue):
            ''' Return a url that points to the issue. '''
            return self.__url + 'browse/' + issue['key']

        def match_id(issue, metric_id):
            ''' Return whether the issue refers to the metric. '''
            return self.ID_TEMPLATE % metric_id in \
                issue['fields']['description']

        def match_recent(issue):
            ''' Return whether the issue is recent. '''
            if recent_only:
                date_time_string = issue['fields']['updated']
                updated = utils.parse_iso_date_time(date_time_string)
                age = datetime.datetime.now() - updated
                return age < datetime.timedelta(weeks=weeks_recent)
            else:
                return True

        return [browse_url(issue) for issue in self.__all_tasks() \
                if match_id(issue, metric_id) and match_recent(issue)]

    def new_task_url(self, metric_id):
        ''' Return a url for creating a new issue. '''
        return self.__new_task_url + '&description=%s' % \
            urllib.quote_plus(self.ID_TEMPLATE % metric_id)

    @utils.memoized
    def __all_tasks(self):
        ''' Return all issues from Jira that contain a reference to a 
            metric. '''

        url = self.__url + 'rest/api/2/search?maxResults=1000&jql=' + \
            urllib.quote_plus('status in (Open, "In Progress", Reopened) AND ' \
                              'issuetype = "Technical Task"')
        issues = utils.eval_json(self.url_open(url).read())['issues']
        logging.info('Received %d Jira issues', len(issues))
        logging.debug('Jira issues: %s', issues)
        tasks = [issue for issue in issues if 'description' in issue['fields'] \
                and self.ID_PREFIX in unicode(issue['fields']['description'])]
        return tasks

    @utils.memoized
    def nr_open_bugs(self):
        ''' Return the number of open bugs. '''
        return self.__query_total(self.__open_bug_query_id)

    def has_open_bugs_query(self):
        ''' Return whether Jira has a query for the number of open bugs. '''
        return self.__open_bug_query_id

    @utils.memoized
    def nr_open_security_bugs(self):
        ''' Return the number of open security bugs. '''
        return self.__query_total(self.__open_security_bug_query_id)

    def has_open_security_bugs_query(self):
        ''' Return whether Jira has a query for the number of open security 
            bugs. '''
        return self.__open_security_bug_query_id

    @utils.memoized
    def nr_blocking_test_issues(self):
        ''' Return the number of blocking test issues reported the previous
            month. '''
        return self.__query_total(self.__blocking_test_issues_query_id)

    def has_blocking_test_issues_query(self):
        ''' Return whether Jira has a query for the number of blocking test 
            isuees reported last month. '''
        return self.__blocking_test_issues_query_id

    @utils.memoized
    def __query_total(self, query_id):
        ''' Return the number of results of the specified query. '''
        query_url = self.__get_query_url(query_id)
        json_string = self.url_open(query_url).read()
        return int(utils.eval_json(json_string)['total'])

    @utils.memoized
    def __get_query_url(self, query_id, search=True):
        ''' Get the query url based on the query id. '''
        url = self.__url + 'rest/api/2/filter/%d' % query_id
        json_string = self.url_open(url).read()
        url_type = 'searchUrl' if search else 'viewUrl'
        return utils.eval_json(json_string)[url_type]

    def nr_open_bugs_url(self):
        ''' Return the url for the nr of open bug reports query. '''
        return self.__get_query_url(self.__open_bug_query_id, search=False)

    def nr_open_security_bugs_url(self):
        ''' Return the url for the nr of open security bug reports query. '''
        return self.__get_query_url(self.__open_security_bug_query_id, 
                                    search=False)

    def nr_blocking_test_issues_url(self):
        ''' Return the url for the number of blocking test issues query. '''
        return self.__get_query_url(self.__blocking_test_issues_query_id, 
                                    search=False)

    def url(self):
        ''' Return the url of the Jira instance. '''
        return self.__url
