'''
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
'''
from __future__ import absolute_import


from ..domain import LowerIsBetterMetric
from .. import metric_source


class LifeUniverseAndEverything(LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the progress of a team. '''

    name = "Hitchiker's Guide to the Galaxy"
    norm_template = 'Time is an illusion'
    template = 'Het antwoord is {value}, de vraag onbekend.'
    target_value = 42
    low_target_value = 40
    metric_source_classes = [metric_source.NoMetricSourceYet]
    
    def __init__(self, *args, **kwargs):
        super(LifeUniverseAndEverything, self).__init__(*args, **kwargs)
        self.__oracle = self._project.metric_source(metric_source.NoMetricSourceYet)

    def value(self):
        return self.__oracle.ultimate_answer(self._subject.metric_source_id(self.__oracle))

    def url(self):
        return {'Deep Thought': 'http://google.com/'}

    def status(self):
        return 'red'