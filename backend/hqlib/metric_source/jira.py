"""
Copyright 2012-2019 Ministerie van Sociale Zaken en Werkgelegenheid

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

import functools
import logging
import urllib.parse
from json import JSONDecodeError
from typing import Optional, Mapping, Union

from . import url_opener
from .. import utils


QueryId = Union[int, str]  # pylint: disable=invalid-name


class Jira(object):
    """ Class representing the Jira instance. """

    def __init__(self, url: str, username: str, password: str) -> None:
        self.__url = url + '/' if not url.endswith('/') else url
        self.__url_opener = url_opener.UrlOpener(username=username, password=password)

    def get_query(self, query_id: QueryId) -> Optional[Mapping]:
        """ Get the JSON from the query and evaluate it. """
        query_url = self.get_query_url(query_id)
        if not query_url:
            return None
        # We know that the base url configured for Jira can be used for querying so keep using that for querying
        # whatever Jira returns as scheme and netloc
        config_parts = urllib.parse.urlparse(self.__url)
        query_parts = urllib.parse.urlparse(query_url)
        read_url = config_parts.scheme + '://' + config_parts.netloc + query_parts.path + \
            '?maxResults=1000&' + query_parts.query
        try:
            return utils.eval_json(self.__url_opener.url_read(read_url))
        except url_opener.UrlOpener.url_open_exceptions:
            return None

    @functools.lru_cache(maxsize=1024)
    def get_field_id(self, filed_name: str) -> Optional[str]:
        """ Retrieves the id of a field for a given name """
        try:
            json_string = self.__url_opener.url_read(self.__url + 'rest/api/2/field')
        except url_opener.UrlOpener.url_open_exceptions:
            return None
        for field in utils.eval_json(json_string):
            if field['name'] == filed_name:
                return field['id']
        logging.error("Error retrieving id for the field with name %s.", filed_name)
        return None

    def get_query_url(self, query_id: QueryId, search: bool = True) -> Optional[str]:
        """ Get the query url based on the query id. """
        if not query_id:
            return None
        if isinstance(query_id, int) or query_id.isdigit():
            return self.__retrieve_issues_url(query_id, search)

        url_part = 'rest/api/2/search?maxResults=1000&' if search else 'issues/?'
        return self.__url + url_part + 'jql={qid}'.format(qid=query_id.replace(' ', '%20'))

    def __retrieve_issues_url(self, query_id, search):
        url = self.__url + 'rest/api/2/filter/{qid}'.format(qid=query_id)

        try:
            json_string = self.__url_opener.url_read(url)
        except url_opener.UrlOpener.url_open_exceptions:
            return None

        url_type = 'searchUrl' if search else 'viewUrl'
        return utils.eval_json(json_string)[url_type]

    def get_issue_details(self, issue_id: str):
        """ Get the JSON with the changelog of the issue. """
        url = self.__url + 'rest/api/2/issue/{issue_id}?maxResults=1000&expand=changelog&fields="*all,-comment"' \
            .format(issue_id=issue_id)
        try:
            json_string = self.__url_opener.url_read(url)
            json = utils.eval_json(json_string)
            return json
        except url_opener.UrlOpener.url_open_exceptions:
            return None
        except JSONDecodeError:
            return None
