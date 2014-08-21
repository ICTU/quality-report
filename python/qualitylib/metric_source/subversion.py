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

from qualitylib import utils, domain
from qualitylib.metric_source import release_archive
from BeautifulSoup import BeautifulSoup
import datetime
import logging
import re
import subprocess


class SubversionFolder(release_archive.ReleaseArchive):
    ''' Class representing a specific directory served by Subversion. '''

    metric_source_name = 'Subversion folder'

    def __init__(self, name, url, run_shell_command=subprocess.check_output):
        self.__run_shell_command = run_shell_command
        super(SubversionFolder, self).__init__(name, url)

    @utils.memoized
    def date_of_most_recent_file(self):
        ''' Return the date and time of the most recent file listed. '''
        output = self.__svn_info()
        regular_expression = 'Last Changed Date: ([^ ]+) ([^ ]+) '
        last_changed_date_time = re.search(regular_expression, output)
        date_text = last_changed_date_time.group(1)
        time_text = last_changed_date_time.group(2)
        year, month, day = date_text.split('-')
        hour, minute, second = time_text.split(':')
        return datetime.datetime(int(year), int(month), int(day), int(hour),
                                 int(minute), int(second))

    def __svn_info(self):
        ''' Run the svn info command and return its output. '''
        return self.__run_shell_command(['svn', 'info', self.url()])


class Subversion(domain.MetricSource):
    ''' Class representing the Subversion repository. '''

    metric_source_name = 'Subversion'

    def __init__(self, username=None, password=None, url=None,
                 run_shell_command=subprocess.check_output):
        self.__username = username
        self.__password = password
        self.__shell_command = run_shell_command
        super(Subversion, self).__init__(url=url)

    def check_out(self, svn_path, folder):
        ''' Check out the subversion path into the folder. '''
        shell_command = ['svn', 'co', svn_path, folder]
        if self.__username and self.__password:
            shell_command.extend(['--no-auth-cache', 
                                  '--username', self.__username, 
                                  '--password', self.__password])
        self.__run_shell_command(shell_command, log_level=logging.ERROR)

    @utils.memoized
    def latest_tagged_product_version(self, product_url):
        ''' Return the latest version as tagged in Subversion. '''
        tags = self.tags(product_url)
        if not tags:
            return
        versions = [self.__parse_version(tag) for tag in tags]
        versions.sort()
        return versions[-1][1]  # Return the text version of the highest number

    def tags_folder_for_version(self, trunk_url, version):
        ''' Return the tags folder for the specified version. '''
        tags = self.tags(trunk_url)
        # Mapping from version numbers to tags:
        folders = dict([(self.__parse_version(tag)[1], tag) for tag in tags])
        # Look up the tag by its version number and return the tag folder
        tags_folder = self.__tags_folder(trunk_url)
        if version in folders:
            return tags_folder + folders[version] + '/' + \
                   trunk_url.split('/trunk/')[1]
        else:
            logging.warn('No tag folder for %s version %s in %s', trunk_url,
                         version, tags_folder)
            return ''

    def branch_folder_for_branch(self, trunk_url, branch):
        ''' Return the branch folder for the specified branch. '''
        return self.__branches_folder(trunk_url) + branch + '/' + \
            trunk_url.split('/trunk/')[1]

    @utils.memoized
    def last_changed_date(self, url):
        ''' Return the date when the url was last changed in Subversion. ''' 
        svn_info_xml = str(self.__run_shell_command(['svn', 'info', '--xml', 
                                                     url]))
        date = BeautifulSoup(svn_info_xml)('date')[0].string
        return datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')

    @utils.memoized
    def unmerged_branches(self, product_url):
        ''' Return a dictionary of branch names and number of unmerged 
            revisions for each branch that has any unmerged revisions. '''
        branches = [(branch, self.__nr_unmerged_revisions(product_url, 
                                                          branch)) \
                    for branch in self.branches(product_url)]
        unmerged_branches = [(branch, nr_revisions) for (branch, nr_revisions) \
                             in branches if nr_revisions > 0]
        return dict(unmerged_branches)

    def __nr_unmerged_revisions(self, product_url, branch_name):
        ''' Return whether the branch has unmerged revisions. '''
        branch_url = self.__branches_folder(product_url) + branch_name
        trunk_url = product_url
        revisions = str(self.__run_shell_command(['svn', 'mergeinfo', 
            '--show-revs', 'eligible', branch_url, trunk_url])).strip()
        logging.debug('Unmerged revisions from %s to %s: "%s"', branch_url, 
                     trunk_url, revisions)
        # Number of revisions is one more than the number of line breaks, if 
        # there is any output:
        nr_revisions = revisions.count('\n') + 1 if revisions else 0
        # If there is a small number of revisions, it may be caused by the Maven
        # release plugin committing to a tag before creating the branch.
        # Check for that and ignore those revisions if that's the case. 
        if 1 <= nr_revisions <= 3:
            # Create a list of revision numbers and remove the initial 'r'
            revisions = [revision[1:].strip() for revision in revisions.split('\n')]
            for revision in revisions:
                if '/tags/' in self.__revision_url(branch_url, revision):
                    nr_revisions -= 1
        return nr_revisions

    def __revision_url(self, branch_url, revision_number):
        ''' Return the url for a specific revision number. '''
        svn_info_xml = str(self.__run_shell_command(['svn', 'info', branch_url,
                                                     '--xml',
                                                     '-r', revision_number]))
        return BeautifulSoup(svn_info_xml)('url')[0].string

    @utils.memoized
    def branches(self, trunk_url):
        ''' Return a list of branch names for the specified trunk url. '''
        return self.__svn_list(self.__branches_folder(trunk_url))

    @utils.memoized
    def tags(self, trunk_url):
        ''' Return a list of tags for the specified trunk url. '''
        return self.__svn_list(self.__tags_folder(trunk_url))

    @staticmethod
    def __tags_folder(trunk_url):
        ''' Return the tags folder for the trunk url. '''
        return trunk_url.split('/trunk/')[0] + '/tags/'

    @staticmethod
    def __branches_folder(trunk_url):
        ''' Return the branches folder for the trunk url. '''
        return trunk_url.split('/trunk/')[0] + '/branches/'

    @staticmethod
    def __parse_version(tag):
        ''' Parse and return the version number from the tag. Returns the 
            version as a two-tuple. The first element of the tuple is the
            version number as tuple of integers (for sorting). The second
            element of the tuple is the version number as text, including
            any postfix elements (e.g. 1.2.3-beta). '''
        versions_in_tag = re.findall(r'[0-9]+(?:\.[0-9]+)+', tag)
        if versions_in_tag and not 'emma' in tag.lower():
            numbers = versions_in_tag[0].split('.')
            version_integer_tuple = tuple(int(number) for number in numbers)
            version_text = re.findall(r'[0-9].*', tag)[0]
        else:
            version_integer_tuple = (0, 0, 0)
            version_text = ''
        return version_integer_tuple, version_text

    def __svn_list(self, url):
        ''' Return a list of sub folder names. '''
        shell_command = ['svn', 'list', '--xml', url]
        svn_info_xml = str(self.__run_shell_command(shell_command))
        return [name.string for name in BeautifulSoup(svn_info_xml)('name')]

    def __run_shell_command(self, shell_command, log_level=logging.WARNING):
        ''' Invoke a shell and run the command. '''
        try:
            return self.__shell_command(shell_command)
        except subprocess.CalledProcessError, reason:
            # No need to include the shell command in the log, because the 
            # reason contains the shell command.
            logging.log(log_level, 'Shell command failed: %s', reason)
            if log_level > logging.WARNING:
                raise
