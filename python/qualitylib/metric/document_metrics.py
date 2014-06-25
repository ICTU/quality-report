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

import datetime
from qualitylib.domain import LowerIsBetterMetric
from qualitylib.metric.metric_source_mixin import SubversionMetricMixin
from qualitylib.metric.quality_attributes import DOC_QUALITY


class DocumentAge(SubversionMetricMixin, LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the progress of a team. '''

    name = 'Document update leeftijd'
    norm_template = 'Dit document wordt minimaal een keer per %(target)d ' \
        'dagen bijgewerkt. Als het document langer dan %(low_target)d dagen ' \
        'geleden is bijgewerkt is deze metriek rood.'
    template = 'Het document "%(name)s" is %(value)d dag(en) geleden ' \
        'bijgewerkt.'
    quality_attribute = DOC_QUALITY
    target_value = 180
    low_target_value = 200

    @classmethod
    def can_be_measured(cls, document, project):
        return super(DocumentAge, cls).can_be_measured(document, project) and \
            document.url()

    def value(self):
        now = datetime.datetime.now()
        changed_date = self._subversion.last_changed_date(self._subject.url())
        return (now - changed_date).days

    def url(self):
        return dict(Subversion=self._subject.url())
