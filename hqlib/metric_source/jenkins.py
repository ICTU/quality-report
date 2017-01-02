"""
Copyright 2012-2017 Ministerie van Sociale Zaken en Werkgelegenheid

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
from __future__ import absolute_import

import ast
import datetime
import logging
import re
import urllib2

from . import url_opener
from .. import utils, domain


class UnknownAge(object):  # pylint: disable=too-few-public-methods
    """ Fake age that is larger than any concrete age. """

    def __gt__(self, other):  # pylint: disable=unused-argument
        return True

    days = '?'


class Jenkins(domain.MetricSource, url_opener.UrlOpener):
    """ Class representing the Jenkins instance. """

    metric_source_name = 'Jenkins build server'
    api_postfix = 'api/python'
    jobs_api_postfix = api_postfix + '?tree=jobs[name,description,color,url,buildable]'

    def __init__(self, url, username='', password='', job_re=''):
        super(Jenkins, self).__init__(url=url, username=username, password=password)
        self.__job_re = re.compile(job_re)
        self.__job_url = url + 'job/{job}/'
        self.__last_completed_build_url = self.__job_url + 'lastCompletedBuild/'
        self._last_successful_build_url = self.__job_url + 'lastSuccessfulBuild/'
        self.__last_stable_build_url = self.__job_url + 'lastStableBuild/'
        self.__job_api_url = self.__job_url + self.api_postfix
        self._jobs_api_url = url + self.jobs_api_postfix
        self.__builds_api_url = self.__job_url + self.api_postfix + '?tree=builds'

    @utils.memoized
    def number_of_active_jobs(self):
        """ Return the total number of active Jenkins jobs. """
        return len(self.__active_jobs())

    def failing_jobs_url(self):
        """ Return the urls for the failing Jenkins jobs. """
        try:
            return self.__job_urls(self.__failing_jobs())
        except url_opener.UrlOpener.url_open_exceptions:
            return None

    def unused_jobs_url(self):
        """ Return the urls for the unused Jenkins jobs. """
        try:
            return self.__job_urls(self.__unused_jobs())
        except url_opener.UrlOpener.url_open_exceptions:
            return None

    def __job_urls(self, jobs):
        """ Return the urls for the Jenkins jobs. """
        return {'{0} ({1} dagen)'.format(job['name'], self.__age_of_last_stable_build(job).days): job['url']
                for job in jobs}

    @utils.memoized
    def __failing_jobs(self):
        """ Return the active Jenkins jobs that are failing. """

        def failing(job):
            """ Return whether the job is failing. """
            return not job['color'].startswith('blue') if job.get('buildable', False) else False

        def old(job):
            """ Return whether the build age of the job is considered to be long ago. """
            return self.__age_of_last_stable_build(job) > datetime.timedelta(days=1)

        return [job for job in self.__active_jobs() if self.__has_builds(job) and failing(job) and old(job)]

    @utils.memoized
    def __unused_jobs(self):
        """ Return the active Jenkins jobs that are unused. """
        def grace_time(job, default=180):
            """ Return the grace time for the job. """
            # Don't consider projects to be old until their last successful build was longer ago than the grace time.
            description = job['description'] or ''
            match = re.search(r'\[gracedays=(\d+)\]', description.lower())
            days = int(match.group(1)) if match else default
            return datetime.timedelta(days=days)

        return [job for job in self.__active_jobs() if self.__age_of_last_completed_build(job) > grace_time(job)]

    def __active_jobs(self):
        """ Return all active Jenkins jobs. """
        return [job for job in self.__jobs() if job.get('buildable', False)]

    @utils.memoized
    def __jobs(self):
        """ Return all Jenkins jobs that match our job regular expression. """
        all_jobs = self._api(self._jobs_api_url)['jobs']
        return [job for job in all_jobs if self.__job_re.match(job['name'])]

    @utils.memoized
    def unstable_arts_url(self, projects, days):
        """ Return the urls for the ARTs that have been unstable for the specified number of days. """
        projects_re = re.compile(projects)
        all_jobs = self._api(self._jobs_api_url)['jobs']
        arts = [job for job in all_jobs if projects_re.match(job['name'])]
        max_age = datetime.timedelta(days=days)
        unstable = dict()
        for art in arts:
            age = self.__age_of_last_stable_build(art)
            if age > max_age:
                art_description = art['name'] + ' ({days} dagen)'.format(days=age.days)
                unstable[art_description] = self.__job_url.format(job=art['name'])
        return unstable

    def __age_of_last_completed_build(self, job):
        """ Return the age of the last completed build of the job. """
        return self.__age_of_build(job, self.__last_completed_build_url)

    def __age_of_last_stable_build(self, job):
        """ Return the age of the last stable build of the job. """
        return self.__age_of_build(job, self.__last_stable_build_url)

    def __age_of_build(self, job, url):
        """ Return the age of the last completed or stable build of the job. """
        builds_url = url.format(job=job['name']) + self.api_postfix
        try:
            timestamp = self._api(builds_url)['timestamp']
        except (KeyError, urllib2.HTTPError):
            return UnknownAge()
        try:
            build_time = datetime.datetime.utcfromtimestamp(float(timestamp)/1000)
        except ValueError:
            logging.warning("Couldn't convert timestamp %s from %s to datetime.", timestamp, builds_url)
            return UnknownAge()
        return datetime.datetime.utcnow() - build_time

    def __has_builds(self, job):
        """ Return whether the job has builds or not. """
        return len(self._api(self.__builds_api_url.format(job=job['name']))['builds'])

    @utils.memoized
    def _api(self, url):
        """ Return the result of the API call at the url. """
        data = self.url_open(url).read()
        try:
            return ast.literal_eval(data)
        except:
            logging.warning("Couldn't evaluate %s from %s", data, url)
            raise

    def url_open(self, url):
        """ Override to safely quote the url, needed because Jenkins may return unquoted urls. """
        url = urllib2.quote(url, safe="%/:=&?~#+!$,;'@()*[]")
        return super(Jenkins, self).url_open(url)

    def resolve_job_name(self, job_name):
        """ If the job name is a regular expression, resolve it to a concrete job name.
            Assumes there is exactly one result. """
        if job_name and ('\\' in job_name or '.*' in job_name or '[' in job_name):
            if not job_name.endswith('$'):
                job_name += '$'
            jobs_re = re.compile(job_name)
            all_jobs = self._api(self._jobs_api_url)['jobs']
            jobs = [job for job in all_jobs if jobs_re.match(job['name'])]
            assert len(jobs) == 1
            job_name = jobs[0]['name']
        return job_name
