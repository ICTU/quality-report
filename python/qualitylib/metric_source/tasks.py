'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''


from qualitylib import domain


class Tasks(domain.MetricSource):
    # pylint: disable=too-few-public-methods,abstract-class-not-used
    ''' Class representing a task manager. '''

    metric_source_name = 'Task manager'

    def tasks(self, metric_id, recent_only=False, weeks_recent=3):
        ''' Return a lists of tasks for the specified metric. '''
        raise NotImplementedError  # pragma: nocover
