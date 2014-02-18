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

# JavaMelody https://code.google.com/p/javamelody '''

from qualitylib.metric_source import beautifulsoup
from qualitylib import utils
import urllib


class JavaMelody(beautifulsoup.BeautifulSoupOpener):
    ''' Class representing a JavaMelody instance. '''
    def __init__(self, javamelody_url):
        self.__javamelody_url = javamelody_url
        super(JavaMelody, self).__init__()
        
    def url(self, product_id=None, start=None, end=None, sep='-'):
        ''' Return the JavaMelody url of the product and period. '''
        if product_id and start and end:
            return self.__javamelody_url + \
                '?application=' + urllib.quote(product_id) + \
                '&startDate=' + self.__format_date(start, sep) + \
                '&endDate=' + self.__format_date(end, sep) + \
                '&period=' + self.__format_period(start, end, sep)
        else:
            return self.__javamelody_url
     
    @utils.memoized
    def mean_request_times(self, product_id, start, end):
        ''' Return a list of the mean request times of the specified product
            in the specified period. '''
        soup = self.soup(self.url(product_id, start, end, sep='/'))
        mean_request_times = []
        # Note: using the dictionary to pass the id attribute works, but 
        # passing the id as keyword argument does not. Don't know why. 
        details_divs = soup('div', {'id': 'detailshttp'})
        if not details_divs:
            details_divs = soup('div', {'id': 'detailsejb'})
        if details_divs:
            for table_row in details_divs[0]('tr')[1:]:
                inner_string = ''.join(table_row('td')[3].findAll(text=True))
                mean_request_time = int(inner_string.replace(',', '').
                                                     replace('.', ''))
                mean_request_times.append(mean_request_time)
        return mean_request_times

    @staticmethod
    def __format_date(date, sep):
        ''' Return the date in the right format for JavaMelody. '''
        # Use US date order when the separator is a /
        if sep == '/':
            date_format = '%(month)d%(sep)s%(day)d%(sep)s%(year)d'
        else:
            date_format = '%(day)d%(sep)s%(month)d%(sep)s%(year)d'
        return date_format % dict(day=date.day, month=date.month, 
                                  year=int(str(date.year)[-2:]), sep=sep)

    @classmethod
    def __format_period(cls, start, end, sep):
        ''' Return the period in the right format for JavaMelody. '''
        return urllib.quote('|'.join([cls.__format_date(start, sep), 
                                      cls.__format_date(end, sep)]))
