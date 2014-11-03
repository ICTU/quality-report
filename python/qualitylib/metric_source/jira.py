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
from qualitylib import utils, domain


class Jira(domain.MetricSource, url_opener.UrlOpener):
    ''' Class representing the Jira instance. '''
    metric_source_name = 'Jira'

    def __init__(self, url, username, password, open_bug_query_id=None, 
                 open_security_bug_query_id=None,
                 blocking_test_issues_query_id=None):
        self.__url = url
        self.__open_bug_query_id = open_bug_query_id
        self.__open_security_bug_query_id = open_security_bug_query_id
        self.__blocking_test_issues_query_id = blocking_test_issues_query_id
        super(Jira, self).__init__(username=username, password=password)

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
