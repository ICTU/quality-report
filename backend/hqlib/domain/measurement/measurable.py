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


from typing import Any, Dict, List, Set, Type, Optional, TYPE_CHECKING

from hqlib.typing import MetricValue
from ..base import DomainObject
if TYPE_CHECKING:  # pragma: no cover
    # pylint: disable=unused-import
    from .metric import Metric
    from .metric_source import MetricSource


class MeasurableObject(DomainObject):
    """ An object that has measurable characteristics. Base class for products, teams, etc. """
    def __init__(self, *args, **kwargs) -> None:
        self.__metric_sources: Dict = kwargs.pop('metric_sources', dict())
        self.__metric_source_ids: Dict['MetricSource', str] = kwargs.pop('metric_source_ids', dict())
        self.__metric_options: Dict[Type['Metric'], Dict[str, Any]] = kwargs.pop('metric_options', dict())
        super().__init__(*args, **kwargs)

    def target(self, metric_class: Type['Metric']) -> MetricValue:
        """ Return the target for the specified metric. """
        return self.__metric_options.get(metric_class, dict()).get('target')

    def low_target(self, metric_class: Type['Metric']) -> MetricValue:
        """ Return the low target for the specified metric. """
        return self.__metric_options.get(metric_class, dict()).get('low_target')

    def technical_debt_target(self, metric_class: Type['Metric']):
        """ Return whether a score below target is considered to be accepted technical debt. """
        return self.__metric_options.get(metric_class, dict()).get('debt_target')

    def metric_sources(self, metric_source_class: Type['MetricSource']) -> List['MetricSource']:
        """ Return the metric source instances for the metric source class. """
        metric_sources = self.__metric_sources.get(metric_source_class, [])
        if metric_sources and not isinstance(metric_sources, list):
            metric_sources = [metric_sources]
        return metric_sources

    def metric_source_classes(self) -> List[Type['MetricSource']]:
        """ Return a set of all metric source classes. """
        return list(self.__metric_sources.keys())

    def metric_source_id(self, metric_source: 'MetricSource') -> Optional[str]:
        """ Return the id of this object in the metric source. """
        return self.__metric_source_ids.get(metric_source)

    def metric_options(self, metric_class: Type['Metric']) -> Dict[str, Any]:
        """ Return the options of this object for the metric class. Options can be any information that is needed
            for the metric. """
        return self.__metric_options.get(metric_class, dict())

    def metrics_with_options(self) -> Set[Type['Metric']]:
        """ Return the metrics that have options. """
        return set(self.__metric_options.keys())
