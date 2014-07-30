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
import datetime
import re
import urllib2


class UnknownAge(object):  # pylint: disable=too-few-public-methods
    ''' Fake age that is larger than any concrete age. '''

    def __gt__(self, other):
        return True

    days = '?'


class Jenkins(domain.MetricSource, url_opener.UrlOpener):
    ''' Class representing the Jenkins instance. '''

    metric_source_name = 'Jenkins build server'
    api_postfix = 'api/python'
    jobs_api_postfix = api_postfix + \
                       '?tree=jobs[name,description,color,url,buildable]'

    def __init__(self, jenkins_url, username, password, job_re=''):
        super(Jenkins, self).__init__(url=jenkins_url, username=username, 
                                      password=password)
        self.__job_re = re.compile(job_re)
        self.__job_url = jenkins_url + 'job/%s/'
        self.__last_completed_build_url = self.__job_url + 'lastCompletedBuild/'
        self._last_successful_build_url = self.__job_url + 'lastSuccessfulBuild/'
        self.__last_stable_build_url = self.__job_url + 'lastStableBuild/'
        self.__job_api_url = self.__job_url + self.api_postfix
        self.__jobs_api_url = jenkins_url + self.jobs_api_postfix

    def number_of_assigned_jobs(self):
        ''' Return the number of Jenkins jobs that has been assigned to one or
            more teams. '''
        return len(self.__assigned_jobs())

    @utils.memoized
    def number_of_jobs(self, *teams):
        ''' Return the total number of Jenkins jobs the specified team is
            responsible for, or the total number of jobs if no team is
            specified. '''
        return len(self.__jobs(*teams))

    def failing_jobs_url(self, *teams):
        ''' Return the urls for the failing Jenkins jobs. '''
        urls = {}
        for failing_job in self.__failing_jobs(*teams):
            failing_job_description = failing_job['name']
            age = self.__age_of_last_stable_build(failing_job)
            failing_job_description += ' (%s dagen)' % age.days
            urls[failing_job_description] = failing_job['url']
        return urls

    def unused_jobs_url(self, *teams):
        ''' Return the urls for the unused Jenkin jobs. '''
        urls = {}
        for unused_job in self.__unused_jobs(*teams):
            unused_job_description = unused_job['name']
            age = self.__age_of_last_stable_build(unused_job)
            unused_job_description += ' (%s dagen)' % age.days
            urls[unused_job_description] = unused_job['url']
        return urls

    def unassigned_jobs_url(self):
        ''' Return the urls for the unassigned Jenkins jobs. '''
        return dict([(job['name'], job['url']) \
                     for job in self.__unassigned_jobs()])

    @utils.memoized
    def __failing_jobs(self, *teams):
        ''' Return the Jenkins jobs that are failing. '''

        def grace_time(job):
            ''' Return the grace time for the job. '''
            # Don't consider projects to have failed until their last successful
            # build was longer ago than the grace time.
            description = job['description'] or ''
            match = re.search(r'\[gracedays=(\d+)\]', description.lower())
            days = int(match.group(1)) if match else 1
            return datetime.timedelta(days=days)

        def failing(job):
            ''' Return whether the job is failing. '''
            return not job['color'].startswith('blue') if job['buildable'] \
                else False

        def old(job):
            ''' Return whether the build age of the job is considered to be
                long ago. '''
            return self.__age_of_last_stable_build(job) > grace_time(job)

        return [job for job in self.__jobs(*teams) if failing(job) and old(job)]

    @utils.memoized
    def __unused_jobs(self, *teams):
        ''' Return the Jenkins jobs that are unused. '''
        old = datetime.timedelta(days=180)
        return [job for job in self.__jobs(*teams) if \
                self.__age_of_last_completed_build(job) > old]

    @utils.memoized
    def __assigned_jobs(self):
        ''' Return the Jenkins jobs that have been assigned to one or more
            teams. '''
        jobs = self.__jobs()
        return [job for job in jobs if job['description'] \
                and "[responsible=" in job['description'].lower()]

    @utils.memoized
    def __unassigned_jobs(self):
        ''' Return the Jenkins jobs that have not been assigned to one or more
            teams. '''
        jobs = self.__jobs()
        return [job for job in jobs if not(job['description'] \
                and "[responsible=" in job['description'].lower())]

    @utils.memoized
    def __jobs(self, *teams):
        ''' Return the Jenkins jobs the specified teams are responsible for, or
            all jobs if no teams are specified. '''
        all_jobs = self._api(self.__jobs_api_url)['jobs']
        all_jobs = [job for job in all_jobs if self.__job_re.match(job['name'])]
        if teams:
            jobs = list()
            for team in teams:
                name = team.name().lower()
                jobs.extend([job for job in all_jobs if job['description'] and \
                             name in job['description'].lower()])
        else:
            jobs = all_jobs
        return jobs

    @utils.memoized
    def unstable_arts_url(self, projects, days):
        ''' Return the urls for the ARTs that have been unstable for the
            specified number of days. '''
        projects_re = re.compile(projects)
        all_jobs = self._api(self.__jobs_api_url)['jobs']
        arts = [job for job in all_jobs if projects_re.match(job['name'])]
        max_age = datetime.timedelta(days=days)
        unstable = dict()
        for art in arts:
            age = self.__age_of_last_stable_build(art)
            if age > max_age:
                art_description = art['name'] + ' (%s dagen)' % age.days
                unstable[art_description] = self.__job_url % art['name']
        return unstable

    def __age_of_last_completed_build(self, job):
        ''' Return the age of the last completed build of the job. '''
        return self.__age_of_build(job, self.__last_completed_build_url)

    def __age_of_last_stable_build(self, job):
        ''' Return the age of the last stable build of the job. '''
        return self.__age_of_build(job, self.__last_stable_build_url)

    def __age_of_build(self, job, url):
        ''' Return the age of the last completed or stable build of the job. '''
        builds_api_postfix = self.api_postfix + '?tree=id'
        try:
            timestamp = self._api(url % job['name'] + builds_api_postfix)['id']
        except (KeyError, urllib2.HTTPError):
            return UnknownAge()
        date_text, time_text = timestamp.split('_')
        year, month, day = date_text.split('-')
        hour, minute, second = time_text.split('-')
        return datetime.datetime.today() - \
            datetime.datetime(int(year), int(month), int(day), 
                              int(hour), int(minute), int(second))

    @utils.memoized
    def _api(self, url):
        ''' Return the result of the API call at the url. '''
        return eval(self.url_open(url).read())

    def url_open(self, url):
        ''' Override to safely quote the url, needed because Jenkins may return
            unquoted urls. '''
        url = urllib2.quote(url, safe="%/:=&?~#+!$,;'@()*[]")
        return super(Jenkins, self).url_open(url)


class JenkinsTestReport(Jenkins):
    ''' Class representing test reports in Jenkins jobs. '''
    def __init__(self, *args, **kwargs):
        super(JenkinsTestReport, self).__init__(*args, **kwargs)
        self.__test_report_url = self._last_successful_build_url + 'testReport/'
        self.__test_report_api_url = self.__test_report_url + self.api_postfix

    def passed_tests(self, job_names):
        ''' Return the number of passed tests as reported by the test report
            of a job. '''
        return sum([self.__passed_tests(job_name) for job_name in job_names])

    def failed_tests(self, job_names):
        ''' Return the number of failed tests as reported by the test report 
            of a job. '''
        return sum([self.__failed_tests(job_name) for job_name in job_names])

    def skipped_tests(self, job_names):
        ''' Return the number of skipped tests as reported by the test report
            of a job. '''
        return sum([self.__skipped_tests(job_name) for job_name in job_names])

    def __passed_tests(self, job_name):
        ''' Return the number of passed tests reported by the test report of
            one Jenkins job. '''
        try:
            return self.__test_count(job_name, 'passCount')
        except KeyError:
            # Surefire reports don't have a pass count, calculate it:
            total = self.__test_count(job_name, 'totalCount')
            skipped = self.__skipped_tests(job_name)
            failed = self.__failed_tests(job_name)
            return total - skipped - failed

    def __failed_tests(self, job_name):
        ''' Return the number of failed tests reported by the test report of
            one Jenkins job. '''
        return self.__test_count(job_name, 'failCount')

    def __skipped_tests(self, job_name):
        ''' Return the number of skipped tests reported by the test report of
            one Jenkins job. '''
        return self.__test_count(job_name, 'skipCount')

    @utils.memoized
    def __test_count(self, job_name, result_type):
        ''' Return the number of tests with the specified result in the test
            report of a job. '''
        report_dict = self._api(self.__test_report_api_url % job_name)
        return int(report_dict[result_type])

    def test_report_url(self, job_name):
        ''' Return the url of the job. '''
        return self.__test_report_url % job_name
