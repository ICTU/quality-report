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

from qualitylib.metric_source import beautifulsoup, release_archive
from qualitylib import utils
import datetime


class ApacheDirectory(release_archive.ReleaseArchive, 
                      beautifulsoup.BeautifulSoupOpener):
    ''' Class representing a specific directory served by Apache. '''
    metric_source_name = 'Apache directory'

    @utils.memoized
    def date_of_most_recent_file(self):
        ''' Return the date and time of the most recent file listed. '''
        soup = self.soup(self.url())
        date_times = []
        for table_row in soup('tr')[1:]:  # Skip header row
            columns = table_row('td')
            if len(columns) < 3:
                continue  # Skip separators
            date_time_text = columns[2].string.strip()
            date_text, time_text = date_time_text.split(' ')
            day, month, year = date_text.split('-')
            hour, minute = time_text.split(':')
            month = utils.ABBREVIATED_MONTHS[month.lower()]
            date_times.append(datetime.datetime(int(year), month, int(day), 
                                                int(hour), int(minute)))
        return max(date_times)
