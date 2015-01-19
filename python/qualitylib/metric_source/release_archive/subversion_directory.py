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
from __future__ import absolute_import


import datetime
import subprocess
import re


from ..abstract import release_archive
from ... import utils


class SubversionDirectory(release_archive.ReleaseArchive):
    ''' Class representing a specific directory served by Subversion. '''

    metric_source_name = 'Subversion folder'

    def __init__(self, name, url, run_shell_command=subprocess.check_output):
        self.__run_shell_command = run_shell_command
        super(SubversionDirectory, self).__init__(name, url)

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

