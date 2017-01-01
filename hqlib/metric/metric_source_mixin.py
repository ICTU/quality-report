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
from __future__ import absolute_import

from .. import metric_source, metric_info


class SonarMetricMixin(object):
    """ Mixin class for metrics that use Sonar. """
    metric_source_classes = (metric_source.Sonar,)

    def __init__(self, *args, **kwargs):
        super(SonarMetricMixin, self).__init__(*args, **kwargs)
        self.__sonar_product_info = metric_info.SonarProductInfo(self._metric_source, self._subject)

    def _metric_source_urls(self):
        """ Return the url to Sonar. """
        return [self._metric_source.url()]

    def _sonar_id(self):
        """ Return the id of the subject in Sonar. """
        return self.__sonar_product_info.sonar_id()


class SonarDashboardMetricMixin(SonarMetricMixin):
    """ Mixin class for metrics that use the Sonar dashboard. """
    def _metric_source_urls(self):
        """ Return the url to the Sonar dashboard. """
        return [self._metric_source.dashboard_url(self._sonar_id())]


class SonarViolationsMetricMixin(SonarMetricMixin):
    """ Mixin class for metrics that use the Sonar violations. """
    def _metric_source_urls(self):
        """ Return the url to the Sonar violations. """
        return [self._metric_source.violations_url(self._sonar_id())]


class BirtTestDesignMetricMixin(object):
    """ Mixin class for metrics that use the Birt test design report. """
    # pylint: disable=too-few-public-methods

    metric_source_classes = (metric_source.Birt,)

    def _metric_source_urls(self):
        """ Return the url for the What's Missing report instead of the Birt test design report since the
            What's Missing report allows users to click to the user stories and test cases in Jira. """
        return [self._metric_source.whats_missing_url()]


class VersionControlSystemMetricMixin(object):  # pylint: disable=too-few-public-methods
    """ Mixin class for metrics that use a version control system. """

    metric_source_classes = (metric_source.VersionControlSystem,)

    def __init__(self, *args, **kwargs):
        super(VersionControlSystemMetricMixin, self).__init__(*args, **kwargs)
        self.__vcs = self._project.metric_source(metric_source.VersionControlSystem)
        self._vcs_product_info = metric_info.VersionControlSystemProductInfo(self.__vcs, self._subject)

    def _vcs_path(self):
        """ Return the version control system path for the product. """
        return self._vcs_product_info.vcs_path()
