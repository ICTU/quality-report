"""
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
"""
from __future__ import absolute_import

import datetime

from qualitylib.domain import LowerIsBetterMetric
from qualitylib.metric.metric_source_mixin import VersionControlSystemMetricMixin
from qualitylib.metric.quality_attributes import DOC_QUALITY


class DocumentAge(VersionControlSystemMetricMixin, LowerIsBetterMetric):
    """ Metric for measuring the progress of a team. """

    name = 'Document update leeftijd'
    unit = 'dag(en)'
    norm_template = 'Dit document wordt minimaal een keer per {target} {unit} bijgewerkt. Als het document langer ' \
        'dan {low_target} {unit} geleden is bijgewerkt is deze metriek rood.'
    template = 'Het document "{name}" is {value} {unit} geleden bijgewerkt.'
    missing_template = 'Het document "{name}" is niet aangetroffen.'
    quality_attribute = DOC_QUALITY
    target_value = 180
    low_target_value = 200

    @classmethod
    def can_be_measured(cls, document, project):
        """ Return whether the document age can be measured. """
        return super(DocumentAge, cls).can_be_measured(document, project) and document.url()

    def value(self):
        """ Return the number of days since the document was last changed. """
        return -1 if self._missing() else (datetime.datetime.now() - self.__changed_date()).days

    def url(self):
        """ Return the url to the document. """
        return {self._vcs_product_info.metric_source_name: self._subject.url()}

    def __changed_date(self):
        """ Return the date that the document was last changed. """
        return self._vcs_product_info.last_changed_date(self._vcs_path())

    def _missing(self):
        """ Return whether the age of the document could be established. """
        return self.__changed_date() == datetime.datetime.min
