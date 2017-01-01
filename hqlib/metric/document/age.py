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

import datetime

from ... import metric_source
from ...domain import LowerIsBetterMetric


class DocumentAge(LowerIsBetterMetric):
    """ Metric for measuring the progress of a team. """

    name = 'Document update leeftijd'
    unit = 'dag(en)'
    norm_template = 'Dit document wordt minimaal een keer per {target} {unit} bijgewerkt. Als het document langer ' \
        'dan {low_target} {unit} geleden is bijgewerkt is deze metriek rood.'
    template = 'Het document "{name}" is {value} {unit} geleden bijgewerkt.'
    missing_template = 'Het document "{name}" is niet aangetroffen.'
    target_value = 180
    low_target_value = 200
    metric_source_classes = (metric_source.ArchiveSystem,)

    def value(self):
        """ Return the number of days since the document was last changed. """
        return -1 if self._missing() else (datetime.datetime.now() - self.__changed_date()).days

    def _metric_source_urls(self):
        """ Return the url to the document. """
        return [self._subject.url()]

    def __changed_date(self):
        """ Return the date that the document was last changed. """
        if self._metric_source and self._metric_source_id:
            return self._metric_source.last_changed_date(self._metric_source.normalize_path(self._metric_source_id))
        else:
            return datetime.datetime.min

    def _missing(self):
        """ Return whether the age of the document could be established. """
        return self.__changed_date() in (None, datetime.datetime.min)
