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


import functools
import logging
import utils
import urllib

#from . import url_opener
from .. import domain


class Checkmarx(domain.MetricSource):
    """ Class representing the Checkmarx API. """
    metric_source_name = 'Checkmarx'
    needs_metric_source_id = True
    checkmarx_url = ''
    checkmarx_username = ''
    checkmarx_password = ''

    def __init__(self, url, username, password, url_open=None, **kwargs):
        #self._url_open = url_open or url_opener.UrlOpener(**kwargs).url_open
        self.checkmarx_url = url
        self.checkmarx_username = username
        self.checkmarx_password = password
        super().__init__()

    @functools.lru_cache(maxsize=1024)
    def alerts(self, risk_level, *report_urls):
        """ Return the number of alerts of the specified risk level. """
        nr_alerts = 0
        for project_name in report_urls:
            try:
                logging.warning("Checkmarx project_name - %s", project_name)
                nr_alerts += self.__parse_alerts(self.__fetch_report(project_name), risk_level)
            #except url_opener.UrlOpener.url_open_exceptions:
            #    return -1
            except:
                logging.warning("Couldn't parse alerts with %s risk level from %s - %s", risk_level, self.checkmarx_url, project_name)
                return -1
        return nr_alerts

    @staticmethod
    def __parse_alerts(json, risk_level):
        """ Parse the JSON to get the nr of alerts for the risk_level """

        return int(json[risk_level])

    def __fetch_report(self, project_name):
        api_url = "{}/Cxwebinterface/odata/v1/Projects?$expand=LastScan&" \
                  "$filter=LastScan/Results/any(r: r/Severity eq CxDataRepository.Severity'High' or " \
                  "r/Severity eq CxDataRepository.Severity'Medium') and Name eq '{}'".format(self.checkmarx_url, project_name)

        top_level_url = "{}/Cxwebinterface".format(self.checkmarx_url)
        json = self.__get_json(top_level_url, api_url, self.checkmarx_username, self.checkmarx_password)
        logging.warning("Checkmarx fetch - %s", json)
        return json

    def __get_json(self, top_level_url, api_url, username, password):
        """ Return and evaluate the JSON at the url using Basic Authentication. """

        if api_url in self.__json:
            return self.__json[api_url]

        try:
            password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, top_level_url, username, password)
            handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
            opener = urllib.request.build_opener(handler)
            json_string = opener.open(api_url).read()
        except: #url_opener.UrlOpener.url_open_exceptions as reason:
            #logging.warning("Couldn't open %s: %s", api_url, reason)
            logging.warning("Couldn't open %s", api_url)
            raise

        json = self.__json[api_url] = utils.eval_json(json_string)
        return json

