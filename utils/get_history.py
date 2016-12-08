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
# This script assumes Subversion was used to store the history file.
# The strategy is to get the last line of each revision and append it to the
# complete history file. Three classes do the work:
# - Revisions is a list of all revisions, retrieved using svn log.
# - LastRevisionProcessed is used to get and set the last revision processed, so we can
#   continue where we left off after a restart.
# - RevisionCollector gets the revisions from Subversion one by one and adds the
#   last line of each revision to the full history file.


import argparse
import logging
import os
import sys
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


class RevisionsToCollect(list):
    """ The revisions of the history file still to collect. """

    def __init__(self, url, last_revision):
        filename = 'history.json.log.xml'
        start_revision = last_revision.get() + 1 if last_revision.get() else 0
        logging.info('svn log --xml -r %d:HEAD %s > %s', start_revision, url, filename)
        os.system('svn log --xml -r {}:HEAD {} > {}'.format(start_revision, url, filename))
        tree = xml.etree.ElementTree.parse(filename)
        revisions = sorted([int(log_entry.attrib['revision']) for log_entry in tree.getroot()])
        logging.info('Read %d revisions from %s', len(revisions), filename)
        super(RevisionsToCollect, self).__init__(revisions)


class RevisionCollector(object):
    """ Get individual revisions of the history file from Subversion and collect them in one complete history file. """

    def __init__(self, url, last_revision):
        self.__url = url
        self.__last_revision = last_revision
        self.__filename = 'history.json'

    def collect(self, revisions):
        """ Get the revisions and append the last measurement of each revision to the full history file. """
        nr_revisions = len(revisions)
        for index, revision in enumerate(revisions):
            logging.info('Retrieving revision %s (%s/%s)', revision, index + 1, nr_revisions)
            self.__get_revision(revision)
            self.__last_revision.set(revision)

    def __get_revision(self, revision):
        """ Get the revision and append the measurement to the full history file. """
        if os.system('svn cat -r {} {} | tail -n 1 >> {}'.format(revision, self.__url, self.__filename)):
            sys.exit('Subversion terminated abnormally')


if __name__ == '__main__':
    arguments = parse_args()
    init_logging(arguments.log)
    last = LastRevisionCollected()
    todo = RevisionsToCollect(arguments.url, last)
    RevisionCollector(arguments.url, last).collect(todo)
