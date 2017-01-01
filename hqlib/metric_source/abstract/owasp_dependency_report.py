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


class OWASPDependencyReport(domain.MetricSource):
    """ Abstract class representing a OWASP dependency report. """
    metric_source_name = 'OWASP dependency rapport'
    needs_metric_source_id = True

    def nr_warnings(self, metric_source_id, priority):
        """ Return the number of warnings in the report with the specified priority. """
        raise NotImplementedError  # pragma: no cover
