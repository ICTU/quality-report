"""
Copyright 2012-2016 Ministerie van Sociale Zaken en Werkgelegenheid

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

# Utility to recreate a complete history file from the committed revisions.
#
# This script assumes Subversion was used to store the history file. The strategy is to get the last line of each
#  revision and append it to the complete history file. Four classes do the work:
# - TimeEstimator estimates how more time is needed to collect the revisions still to be collected based on the time
#   it took to collect the revisions so far.
# - LastRevisionProcessed is used to get and set the last revision processed, so we can continue where we left off
#   after a restart.
# - RevisionsToCollect is a list of the revisions still to be collected, retrieved using svn log.
# - RevisionCollector gets the revisions from Subversion one by one and adds the last line of each revision to the
#   full history file.


import argparse
import datetime
import logging
import os
import subprocess
import xml.etree.ElementTree


def parse_args():
    """ Parse the command line arguments. """
    parser = argparse.ArgumentParser(description='Create a full history file for a project.')
    parser.add_argument('url', help='Subversion url of the history file')
    parser.add_argument('--log', default="INFO", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="log level (INFO by default)")
    return parser.parse_args()


def init_logging(log_level):
    """ Initialize logging for the application. """
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=getattr(logging, log_level.upper(), None))


class LastRevisionCollected(object):
    """ Keep track of the last revision collected. """

    def __init__(self):
        self.__filename = 'history.json.last_revision.txt'

    def get(self):
        """ Get the last collected revision. """
        if os.path.exists(self.__filename):
            with open(self.__filename, mode='r') as last_revision_file:
                return int(last_revision_file.read())
        else:
            return None

    def set(self, revision):
        """ Set the last collected revision. """
        with open(self.__filename, mode='w') as last_revision_file:
            last_revision_file.write(bytes(revision))


class TimeEstimator(object):
    """ Class to estimate how much time is needed to do the remaining work. """
    def __init__(self, total_steps):
        super(TimeEstimator, self).__init__()
        self.__total_steps = total_steps
        self.__start_time = datetime.datetime.now()

    def time_remaining(self, steps_done):
        """ Return the estimated amount of time needed to do the work. """
        if steps_done:
            seconds_per_step = (datetime.datetime.now() - self.__start_time).total_seconds() / steps_done
            seconds_remaining = (self.__total_steps - steps_done) * seconds_per_step
            return str(datetime.timedelta(seconds=round(seconds_remaining)))
        else:
            return 'not enough data to estimate'


class RevisionsToCollect(list):
    """ The revisions of the history file still to collect. """

    def __init__(self, url, last_revision):
        start_revision = last_revision.get() + 1 if last_revision.get() else 0
        logging.info('svn log --xml -r %d:HEAD %s', start_revision, url)
        revisions_xml = subprocess.check_output(['svn', 'log', '--xml', '-r', '{}:HEAD'.format(start_revision), url])
        root = xml.etree.ElementTree.fromstring(revisions_xml)
        super(RevisionsToCollect, self).__init__(sorted([int(log_entry.attrib['revision']) for log_entry in root]))
        logging.info('%d revisions to collect from %s', len(self), url)


class RevisionCollector(object):
    """ Get individual revisions of the history file from Subversion and collect them in one complete history file. """

    def __init__(self, url, last_revision):
        self.__url = url
        self.__last_revision = last_revision
        self.__filename = 'history.json'

    def collect(self, revisions):
        """ Get the revisions and append the last measurement of each revision to the full history file. """
        nr_revisions = len(revisions)
        estimate = TimeEstimator(nr_revisions)
        for index, revision_number in enumerate(revisions):
            last_measurement = self.__get_last_measurement(revision_number)
            self.__write_measurement(last_measurement)
            self.__last_revision.set(revision_number)
            logging.info('Revision: %s, %s/%s, measurement date: %s, time remaining: %s', revision_number, index + 1,
                         nr_revisions, self.__get_date(last_measurement), estimate.time_remaining(index))

    def __get_last_measurement(self, revision_number):
        """ Get the revision and extract the last measurement (the measurement that was new to this revision). """
        revision = subprocess.check_output(['svn', 'cat', '-r', str(revision_number), self.__url],
                                           universal_newlines=True).strip()
        return revision.rsplit('\n', 1)[-1] if revision else ''

    def __write_measurement(self, measurement):
        """ Append the measurement to the history file. """
        with open(self.__filename, mode='a') as history_file:
            history_file.write(measurement + '\n')

    @staticmethod
    def __get_date(measurement):
        """ Get the date of the measurement from the JSON. """
        return eval(measurement).get('date') if measurement else 'unknown date'


def main():
    """ Get the history. """
    arguments = parse_args()
    init_logging(arguments.log)
    last = LastRevisionCollected()
    todo = RevisionsToCollect(arguments.url, last)
    RevisionCollector(arguments.url, last).collect(todo)


if __name__ == '__main__':
    main()
