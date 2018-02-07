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

from datetime import datetime

from ... import domain


class ArchiveSystem(domain.MetricSource):
    """ Abstract base class for systems that archive files, such as Nexus, and version control systems. """
    metric_source_name = 'Archive system'

    def last_changed_date(self, path: str) -> datetime:
        """ Return the date when the url was last changed. """
        raise NotImplementedError

    @staticmethod
    def normalize_path(path: str) -> str:
        """ Return a normalized version of the path. """
        return path
