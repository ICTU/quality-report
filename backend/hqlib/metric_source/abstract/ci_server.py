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


from typing import Dict, Optional

from ... import domain


class CIServer(domain.MetricSource):
    """ Abstract base class for continuous integration servers, also known as build servers. """
    metric_source_name = 'Continuous Integration (CI) server'

    def number_of_active_jobs(self) -> int:
        """ Return the total number of active CI jobs. """
        raise NotImplementedError

    def failing_jobs_url(self) -> Optional[Dict[str, str]]:
        """ Return the urls for the failing Jenkins jobs. """
        raise NotImplementedError

    def unused_jobs_url(self) -> Optional[Dict[str, str]]:
        """ Return the urls for the unused Jenkins jobs. """
        raise NotImplementedError
