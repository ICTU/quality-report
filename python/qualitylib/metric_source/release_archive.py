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


class ReleaseArchive(object):  # pylint: disable=abstract-class-not-used
    ''' Abstract base class for release archives. '''
    def __init__(self, name, url, *args, **kwargs):
        self.__name = name
        self.__url = url
        super(ReleaseArchive, self).__init__(*args, **kwargs)
        
    def name(self):
        ''' Return the name of the release archive. '''
        return self.__name
    
    def url(self):
        ''' Return the url of the release archive. '''
        return self.__url

    def date_of_most_recent_file(self):
        ''' Return the date and time of the most recent file in the release
            archive. '''
        raise NotImplementedError  # pragma: no cover
