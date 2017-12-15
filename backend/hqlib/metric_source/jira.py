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


from typing import Optional, Mapping
import urllib.parse

from . import url_opener
from .. import utils


class Jira(object):
    """ Class representing the Jira instance. """

    def __init__(self, url: str, username: str, password: str) -> None:
        self.__url = url + '/' if not url.endswith('/') else url
        self.__url_opener = url_opener.UrlOpener(username=username, password=password)

    def query_total(self, query_id: int) -> int:
        """ Return the number of results of the specified query. """
        results = self.__get_query(query_id)
        return int(results['total']) if results else -1

    def query_sum(self, query_id: int, field: str) -> float:
        """ Return the sum of the fields as returned by the query. """
        results = self.__get_query(query_id)
        if not results:
            return -1
        total = 0.
        for issue in results['issues']:
            try:
                total += float(issue['fields'][field])
            except TypeError:
                pass  # field is null
        return total

    def query_field_empty(self, query_id: int, field: str) -> int:
        """ Return the number of query results with field empty (null). """
        results = self.__get_query(query_id)
        if not results:
            return -1
        total = 0
        for issue in results['issues']:
            try:
                int(issue['fields'][field])
            except TypeError:
                total += 1
        return total

    def __get_query(self, query_id: int) -> Optional[Mapping]:
        """ Get the JSON from the query and evaluate it. """
        query_url = self.get_query_url(query_id)
        if not query_url:
            return None
        # We know that the base url configured for Jira can be used for querying so keep using that for querying
        # whatever Jira returns as scheme and netloc
        config_parts = urllib.parse.urlparse(self.__url)
        query_parts = urllib.parse.urlparse(query_url)
        read_url = config_parts.scheme + '://' + config_parts.netloc + query_parts.path + '?' + query_parts.query
        try:
            return utils.eval_json(self.__url_opener.url_read(read_url))
        except url_opener.UrlOpener.url_open_exceptions:
            return None

    def get_query_url(self, query_id: int, search: bool=True) -> Optional[str]:
        """ Get the query url based on the query id. """
        if not query_id:
            return None
        url = self.__url + 'rest/api/2/filter/{qid}'.format(qid=query_id)
        try:
            json_string = self.__url_opener.url_read(url)
        except url_opener.UrlOpener.url_open_exceptions:
            return None
        url_type = 'searchUrl' if search else 'viewUrl'
        return utils.eval_json(json_string)[url_type]
