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


class NexusDirectory(release_archive.ReleaseArchive, 
                      beautifulsoup.BeautifulSoupOpener):
    ''' Class representing a specific directory served by Nexus. '''
    metric_source_name = 'Nexus'

    @utils.memoized
    def date_of_most_recent_file(self):
        ''' Return the date and time of the most recent file listed. '''
        soup = self.soup(self.url())
        date_times = []
        for table_row in soup('tr')[2:]:  # Skip header row and parent dir
            columns = table_row('td')
            date_times.append(utils.parse_uk_date_time(columns[1].string))
        return max(date_times)
