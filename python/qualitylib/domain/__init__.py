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

# Package for domain objects.


from qualitylib.domain.measurement.metric import Metric, HigherIsBetterMetric, \
    HigherPercentageIsBetterMetric, LowerPercentageIsBetterMetric, \
    LowerIsBetterMetric
from qualitylib.domain.measurement.metric_source import MetricSource, \
    MissingMetricSource
from qualitylib.domain.measurement.metric_mixin import MetaMetricMixin
from qualitylib.domain.measurement.target import TechnicalDebtTarget, \
    DynamicTechnicalDebtTarget

from qualitylib.domain.base import DomainObject
from qualitylib.domain.product import Product
from qualitylib.domain.team import Team
from qualitylib.domain.project import Project
from qualitylib.domain.quality_attribute import QualityAttribute
from qualitylib.domain.street import Street
from qualitylib.domain.document import Document
