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


from typing import List, Iterable
from .. import MetricSource


class MetricSourceWithIssues(MetricSource):  # pylint: disable=too-few-public-methods
    """ Base class for metric sources with a list of issues. """

    class Issue:
        """ Generic class that will be inherited and holds data about the issues of  """
        # pylint: disable=too-few-public-methods

        def __init__(self, title: str):
            self.title = title

    def __init__(self, *args: str, **kwargs: str) -> None:
        self._issues = []
        super().__init__(*args, **kwargs)

    def obtain_issues(self, metric_source_ids: Iterable[str], priority: str):
        """ Abstract: obtains data and fills the list of issues. """
        raise NotImplementedError

    def issues(self) -> List:
        """ Returns the list of issues. """
        return self._issues
