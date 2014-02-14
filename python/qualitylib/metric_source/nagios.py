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


class Nagios(beautifulsoup.BeautifulSoupOpener):
    ''' Class representing the Nagios instance. '''

    def __init__(self, nagios_url, username, password, host_groups,
                 availability_via_service=False):
        self.__nagios_url = nagios_url + 'nagios/'
        self.__host_groups = host_groups
        self.__availability_via_service = availability_via_service
        super(Nagios, self).__init__(uri=nagios_url, username=username,
                                     password=password)
        self.__hostgroup_availability_url = self.__nagios_url + '/cgi-bin/avail.cgi?' \
            'show_log_entries=&hostgroup=%(host_group)s&' \
            'timeperiod=%(time_period)s&rpttimeperiod=%(report_time_period)s'
        self.__service_availability_url = self.__nagios_url + '/cgi-bin/avail.cgi?' \
            'show_log_entries=&host=all&service=all' \
            '&timeperiod=%(time_period)s&rpttimeperiod=%(report_time_period)s'
        self.__server_availability_url = self.__nagios_url + '/cgi-bin/avail.cgi?' \
            'show_log_entries=&host=all' \
            '&timeperiod=%(time_period)s&rpttimeperiod=%(report_time_period)s'
            
    def url(self):
        ''' Return the base url for Nagios. '''
        return self.__nagios_url
            
    def service_availability(self, server, time_period='lastmonth', 
                            report_time_period='17x7'):
        ''' Return the availability of an individual service on the specified
            server. This assumes there is just one service for each server. '''
        url = self.service_availability_url(time_period, report_time_period)
        soup = self.soup(url)
        table = soup('table', 'data')[0]
        ok_label = 'serviceOK' if self.__availability_via_service else 'hostUP'
        for row in table('tr')[1:-1]:  # Skip header row and total row
            if row('td')[0]('a')[0].string == server:
                return float(row('td', ok_label)[0].string.split('%')[0])
        return -1
    
    def service_availability_url(self, time_period='lastmonth', 
                                 report_time_period='17x7'):
        ''' Return the url for measuring the availability of a service. '''
        if self.__availability_via_service:
            availability_url = self.__service_availability_url
        else:
            availability_url = self.__server_availability_url
        return availability_url % (dict(time_period=time_period, 
                                    report_time_period=report_time_period))
        
    def average_availability(self, time_period='lastmonth', 
                             report_time_period='17x7'):
        ''' Return the average availability of the host groups. '''
        availabilities = []
        for host_group in self.__host_groups:
            soup = self.soup(self.__hostgroup_availability_url % \
                             (dict(host_group=host_group, 
                                   time_period=time_period,
                                   report_time_period=report_time_period)))
            td_with_average_availability = soup('td', 'hostUP')[-1]
            availability = td_with_average_availability.string.split('%')[0]
            availabilities.append(float(availability))
        if availabilities:
            return sum(availabilities) / len(availabilities)
        else:
            return 100.
        
    def number_of_servers(self):
        ''' Return the number of servers Nagios is monitoring. '''
        return len(self.__servers_and_availability())

    def number_of_servers_per_group(self):
        ''' Return the number of servers Nagios is monitoring ordered by
            server group. '''
        servers_per_group = {}
        for group, _ in self.__servers_and_availability():
            servers_per_group[group] = servers_per_group.get(group, 0) + 1
        return servers_per_group
    
    def availability_url(self, time_period='lastmonth', 
                         report_time_period='17x7'):
        ''' Return the Nagios URL for the availability of the host or host 
            group(s). '''
        url = self.__hostgroup_availability_url if self.__host_groups else \
              self.__service_availability_url
        url_parameters = dict(host_group='all', time_period=time_period, 
                              report_time_period=report_time_period)
        if len(self.__host_groups) == 1:
            url_parameters['host_group'] = self.__host_groups[0]
        elif len(self.__host_groups) > 1:
            url_parameters['time_period'] = 'last7days'
        return url % url_parameters
        
    def number_of_servers_sufficiently_available(self):
        ''' Return the number of servers that have been sufficiently
            available. '''
        availability_numbers = self.__servers_and_availability().values()
        return len([availability for availability in availability_numbers \
                    if availability >= 99.0])

    @utils.memoized
    def __servers_and_availability(self):
        ''' Get the servers and their availability. '''
        servers = {}
        soup = self.soup(self.availability_url(time_period='last7days'))
        table_headers = soup('div', 'dataTitle')
        for header in table_headers:
            for host_group in self.__host_groups:
                if host_group in header.string:
                    current_host_group = host_group
                    break
            else:
                continue  # with next header
            tables = header.findNextSibling('div')('table')
            if tables:
                table = tables[0]
            else:
                continue
            rows = table('tr')
            if not rows:
                continue
            for row in rows:
                columns = row('td')
                if not columns:
                    continue
                link = columns[0]('a')
                if not link:
                    continue
                server_name = link[0].string
                availability = float(columns[1].string.split('(')[1][:-2])
                servers[(current_host_group, server_name)] = availability
        return servers
