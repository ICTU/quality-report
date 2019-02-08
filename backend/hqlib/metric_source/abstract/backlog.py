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


from typing import List, Tuple
from hqlib.typing import DateTime
from ... import domain


class Backlog(domain.MetricSource):
    """ Abstract base class for user story metrics. """

    def nr_user_stories(self) -> Tuple[int, List[str]]:
        """ Return the total number of user stories. """
        raise NotImplementedError

    def approved_user_stories(self) -> Tuple[int, List[str]]:
        """ Return the number of user stories that have been approved. """
        raise NotImplementedError

    def reviewed_user_stories(self) -> Tuple[int, List[str]]:
        """ Return the number of user stories that have been reviewed. """
        raise NotImplementedError

    def nr_user_stories_with_sufficient_ltcs(self) -> Tuple[int, List[str]]:
        """ Return the number of user stories that have enough logical test cases. """
        raise NotImplementedError

    def reviewed_ltcs(self) -> Tuple[int, List[str]]:
        """ Return the number of reviewed logical test cases for the product. """
        raise NotImplementedError

    def nr_ltcs(self) -> Tuple[int, List[str]]:
        """ Return the number of logical test cases. """
        raise NotImplementedError

    def approved_ltcs(self) -> Tuple[int, List[str]]:
        """ Return the number of approved logical test casess. """
        raise NotImplementedError

    def nr_automated_ltcs(self) -> Tuple[int, List[str]]:
        """ Return the number of logical test cases that have been implemented as automated tests. """
        raise NotImplementedError

    def nr_ltcs_to_be_automated(self) -> Tuple[int, List[str]]:
        """ Return the number of logical test cases for the product that have to be automated. """
        raise NotImplementedError

    def nr_manual_ltcs(self, version: str = 'trunk') -> Tuple[int, List[str]]:
        """ Return the number of logical test cases for the product that are executed manually. """
        raise NotImplementedError

    def date_of_last_manual_test(self, version: str = 'trunk') -> DateTime:
        """ Return the date when the product/version was last tested manually. """
        raise NotImplementedError

    def manual_test_execution_url(self, version: str = 'trunk') -> str:
        """ Return the url for the manual test execution report. """
        raise NotImplementedError

    def nr_manual_ltcs_too_old(self, version: str, target: int) -> int:
        """ Return the number of manual logical test cases that have not been executed for target amount of days. """
        raise NotImplementedError
