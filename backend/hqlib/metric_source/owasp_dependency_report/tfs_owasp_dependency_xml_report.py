"""
Copyright 2012-2018 Ministerie van Sociale Zaken en Werkgelegenheid

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

import json
import zipfile
import logging
import urllib.error
from io import BytesIO
from ...typing import DateTime

from ... import utils
from .owasp_dependency_xml_report import OWASPDependencyXMLReport


def tfs_metric_source_id_decorator(func):
    """ Provides artifact url for metric source id argument."""
    # pylint: disable=unused-argument
    def _metric_source_id_param(self, metric_source_id: str, *args, **kwargs) -> (str, str):
        """ Return the artifact url as metric_source_id parameter. """
        # pylint: disable=protected-access
        return func(self, self._url_artifact, *args, **kwargs)
    return _metric_source_id_param


class TfsOWASPDependencyXMLReport(OWASPDependencyXMLReport):
    """ Class representing OWASP dependency reports in XML format. """

    # pylint: disable=too-many-arguments
    def __init__(self,
                 base_url: str, organization: str, project: str, definitions: str, pat_token: str, **kwargs) -> None:
        super().__init__(username='', password=pat_token, **kwargs)
        build_url = utils.url_join(
            base_url, 'tfs', organization, project,
            '_apis/build/builds?queryOrder=finishTimeDescending&statusFilter=completed&definitions='
            '{definitions}&$top=1&resultFilter=succeeded&api-version=4.1'.format(definitions=definitions))
        part_1 = self.__get_build_artifacts_url(build_url)
        self._url_artifact = utils.url_join(part_1, 'artifacts?artifactName=OWASP&api-version=4.1&%24format=zip') \
            if part_1 else ''

    def __get_build_artifacts_url(self, url: str) -> str:
        try:
            json_string = self._url_opener.url_read(url)
            return utils.eval_json(json_string)['value'][0]['url']
        except urllib.error.HTTPError:
            logging.error('Error constructing TfsOWASPDependencyXMLReport - could not get list of builds.')
        except json.decoder.JSONDecodeError:
            logging.error('Error constructing TfsOWASPDependencyXMLReport - JSON error.')
        except KeyError as reason:
            logging.error('Error constructing TfsOWASPDependencyXMLReport - JSON error: %s.', reason)
        return ''

    @tfs_metric_source_id_decorator
    def _nr_warnings(self, metric_source_id: str, priority: str) -> int:
        """ Return the number of warnings in the reports with the specified priority. """
        return super()._nr_warnings(metric_source_id, priority)

    @tfs_metric_source_id_decorator
    def get_dependencies_info(self, metric_source_id: str, priority: str) -> list:
        """ Extracts info of dependencies with vulnerabilities of given priority. """
        return super().get_dependencies_info(metric_source_id, priority)

    @tfs_metric_source_id_decorator
    def _report_datetime(self, metric_source_id: str) -> DateTime:
        """ Return the report date and time. """
        return super()._report_datetime(metric_source_id)

    def _get_content(self, report_url) -> str:
        try:
            response = self._url_opener.url_open(report_url)
            zipped_content = zipfile.ZipFile(BytesIO(response.read()))
            return zipped_content.read('OWASP/dependency-check-report.xml')
        except urllib.error.HTTPError:
            logging.error("Error getting content of the OWASP report from %s.", report_url)
        except AttributeError as reason:
            logging.error("Error reading server response of the OWASP report: %s.", reason)
        except TypeError as reason:
            logging.error("Error casting server response for the OWASP report to a byte stream: %s.", reason)
        except (zipfile.BadZipFile, KeyError) as reason:
            logging.error("Archive of the OWASP report is corrupted: %s.", reason)
        return ''
