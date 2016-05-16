"""
Copyright 2012-2016 Ministerie van Sociale Zaken en Werkgelegenheid

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

from __future__ import absolute_import

from .. import url_opener
from ... import domain


class TestReport(domain.MetricSource):
    """ Abstract class representing a test report. """
    metric_source_name = 'Test report'
    needs_metric_source_id = True

    def __init__(self, url_open=None, **kwargs):
        self._url_open = url_open or url_opener.UrlOpener(**kwargs).url_open
        super(TestReport, self).__init__()

    def passed_tests(self, *report_urls):
        """ Return the number of passed tests. """
        return sum([self._passed_tests(report_url) for report_url in report_urls])

    def failed_tests(self, *report_urls):
        """ Return the number of failed tests. """
        return sum([self._failed_tests(report_url) for report_url in report_urls])

    def skipped_tests(self, *report_urls):
        """ Return the number of skipped tests. """
        return sum([self._skipped_tests(report_url) for report_url in report_urls])

    def _passed_tests(self, report_url):
        """ Return the number of passed tests as reported by the test report. """
        raise NotImplementedError  # pragma: nocover

    def _failed_tests(self, report_url):
        """ Return the number of failed tests as reported by the test report. """
        raise NotImplementedError  # pragma: nocover

    def _skipped_tests(self, report_url):
        """ Return the number of skipped tests as reported by the test report. """
        raise NotImplementedError  # pragma: nocover
