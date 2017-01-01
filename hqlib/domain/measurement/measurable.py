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

from ..base import DomainObject


class MeasurableObject(DomainObject):
    """ An object that has measurable characteristics. Base class for products, teams, etc. """
    def __init__(self, *args, **kwargs):
        self.__metric_source_ids = kwargs.pop('metric_source_ids', dict())
        self.__old_metric_source_ids = kwargs.pop('old_metric_source_ids', dict())
        self.__metric_source_options = kwargs.pop('metric_source_options', dict())
        self.__metric_options = kwargs.pop('metric_options', dict())
        super(MeasurableObject, self).__init__(*args, **kwargs)

    def target(self, metric_class):
        """ Return the target for the specified metric. """
        return self.__metric_options.get(metric_class, dict()).get('target')

    def low_target(self, metric_class):
        """ Return the low target for the specified metric. """
        return self.__metric_options.get(metric_class, dict()).get('low_target')

    def technical_debt_target(self, metric_class):
        """ Return whether a score below target is considered to be accepted technical debt. """
        return self.__metric_options.get(metric_class, dict()).get('debt_target')

    def metric_source_id(self, metric_source):
        """ Return the id of this object in the metric source. """
        if isinstance(metric_source, list):
            for source in metric_source:
                if source in self.__metric_source_ids:
                    return self.__metric_source_ids.get(source)
            return None
        else:
            return self.__metric_source_ids.get(metric_source)

    def old_metric_source_id(self, metric_source, version):
        """ Return the id of this object in the metric source for a specific version of the object. """
        old_metric_source_ids = self.__old_metric_source_ids.get(metric_source, dict())
        return old_metric_source_ids.get(version)

    def metric_source_options(self, metric_source):
        """ Return the options of this object for the metric source. Options can be any information that is needed
            to get information about this object from the metric source. """
        return self.__metric_source_options.get(metric_source)

    def metric_options(self, metric_class):
        """ Return the options of this object for the metric class. Options can be any information that is needed
            for the metric. """
        return self.__metric_options.get(metric_class, dict())
