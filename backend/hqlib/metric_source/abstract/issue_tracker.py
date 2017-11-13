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


from ... import domain


class BugTracker(domain.MetricSource):
    """ Abstract base class for bug trackers, such as Jira. """
    metric_source_name = 'Bug tracker'
    needs_metric_source_id = True

    def nr_issues(self, *metric_source_ids: str) -> str:
        """ Return the number of issues for the metric source ids. """
        raise NotImplementedError


class SecurityBugTracker(BugTracker):
    """ Abstract base class for security bug trackers. """
    metric_source_name = 'Security bug tracker'

    def nr_issues(self, *metric_source_ids: str) -> str:
        """ Return the number of issues for the metric source ids. """
        raise NotImplementedError


class StaticSecurityBugTracker(BugTracker):
    """ Abstract base class for static security bug trackers. """
    metric_source_name = 'Static security bug tracker'

    def nr_issues(self, *metric_source_ids: str) -> str:
        """ Return the number of issues for the metric source ids. """
        raise NotImplementedError


class FindingTracker(BugTracker):
    """ Abstract base class for finding strackers. """
    metric_source_name = 'Finding tracker'

    def nr_issues(self, *metric_source_ids: str) -> str:
        """ Return the number of issues for the metric source ids. """
        raise NotImplementedError


class TechnicalDebtTracker(BugTracker):
    """ Abstract base class for finding trackers. """
    metric_source_name = 'Technische schuld tracker'

    def nr_issues(self, *metric_source_ids: str) -> str:
        """ Return the number of issues for the metric source ids. """
        raise NotImplementedError


class QualityGateTracker(BugTracker):
    """ Abstract base class for quality gate trackers. """
    metric_source_name = 'Quality gate tracker'

    def nr_issues(self, *metric_source_ids: str) -> str:
        """ Return the number of issues for the metric source ids. """
        raise NotImplementedError
