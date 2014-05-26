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

from qualitylib.metric_source import beautifulsoup
from qualitylib import utils
import datetime
import logging
import re
import time
import urllib2


class UnknownAge(object):  # pylint: disable=too-few-public-methods
    ''' Fake age that is larger than any concrete age. '''

    def __gt__(self, other):
        return True

    days = '?'


class Jenkins(beautifulsoup.BeautifulSoupOpener):
    ''' Class representing the Jenkins instance. '''

    api_postfix = 'api/python'
    jobs_api_postfix = api_postfix + \
                       '?tree=jobs[name,description,color,url,buildable]'

    def __init__(self, jenkins_url, username, password, job_re=''):
        super(Jenkins, self).__init__(username=username, password=password)
        self.__jenkins_url = jenkins_url
        self.__job_re = re.compile(job_re)
        self.__job_url = jenkins_url + 'job/%s/'
        self.__last_completed_build_url = self.__job_url + 'lastCompletedBuild/'
        self.__last_stable_build_url = self.__job_url + 'lastStableBuild/'
        self.__job_api_url = self.__job_url + self.api_postfix
        self.__jobs_api_url = jenkins_url + self.jobs_api_postfix

    def url(self):
        ''' Return the base url for the Jenkins server. '''
        return self.__jenkins_url

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
        all_jobs = self.__api(self.__jobs_api_url)['jobs']
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
        soup = self.soup(self.__jenkins_url)
        arts = soup('table', id='projectstatus')[0]('a',
                                                    text=re.compile(projects))
        max_age = datetime.timedelta(days=days)
        unstable = dict()
        for art in arts:
            age = self.__build_age(self.__last_stable_build_url % art)
            if age > max_age:
                art_description = art + ' (%s dagen)' % age.days
                unstable[art_description] = self.__job_url % art
        return unstable

    def __age_of_last_completed_build(self, job):
        ''' Return the age of the last completed build of the job. '''
        return self.__build_age(self.__last_completed_build_url % job['name'])

    def __age_of_last_stable_build(self, job):
        ''' Return the age of the last stable build of the job. '''
        return self.__build_age(self.__last_stable_build_url % job['name'])

    def __build_age(self, url):
        ''' Return the age of the build in days. '''
        build_date = self.__build_date(url)
        if build_date > datetime.datetime.min:
            build_age = datetime.datetime.today() - build_date
        else:
            build_age = UnknownAge()
        return build_age

    @utils.memoized
    def __build_date(self, url):
        ''' Return the date and time of the build. '''
        try:
            datetime_text = self.__get_build_date_time(self.soup(url))
            return self.__parse_build_date(datetime_text)
        except urllib2.HTTPError, message:
            logging.warning("Couldn't read %s: %s", url, message)
            return datetime.datetime.min
        except (ValueError, KeyError, IndexError):
            logging.error("Couldn't parse %s", url)
            raise

    @staticmethod
    def __get_build_date_time(soup):
        ''' Get the build date and time from the soup. '''
        title = str(soup('h1')[0])
        return title.split('(')[1].split(')')[0]

    @staticmethod
    def __parse_build_date(datetime_text):
        ''' Parse the build date and time text. '''
        try:
            parsed_datetime = time.strptime(datetime_text,
                                            '%b %d, %Y %H:%M:%S %p')
        except ValueError:
            try:
                parsed_datetime = time.strptime(datetime_text,
                                                '%d-%b-%Y %H:%M:%S')
            except ValueError:
                date_text, time_text = datetime_text.split(' ')
                day, month, year = date_text.split('-')
                month = dict(jan=1, feb=2, mrt=3, mar=3, apr=4, mei=5, may=5,
                             jun=6, jul=7, aug=8, sep=9, okt=10, oct=10,
                             nov=11, dec=12)[month[:3].lower()]
                hour, minute, second = time_text.split(':')
                parsed_datetime = [int(year), month, int(day),
                                   int(hour), int(minute), int(second)]
        return datetime.datetime(*(parsed_datetime[0:6]))

    @utils.memoized
    def __api(self, url):
        ''' Return the result of the API call at the url. '''
        return eval(self.url_open(url).read())

    def url_open(self, url):
        ''' Override to safely quote the url, needed because Jenkins may return
            unquoted urls. '''
        url = urllib2.quote(url, safe="%/:=&?~#+!$,;'@()*[]")
        return super(Jenkins, self).url_open(url)
