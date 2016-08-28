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

from ..base import DomainObject


class RequirementOld(DomainObject):
    """ Domain object representing a project requirement. """
    default_metric_classes = tuple()  # Subclass responsibility

    def __init__(self, *args, **kwargs):
        self.__metric_classes = kwargs.pop('metric_classes', tuple())
        self.__id = kwargs.pop('identifier', None)
        super(RequirementOld, self).__init__(*args, **kwargs)

    def metric_classes(self):
        """ Return the metrics that have to be measured to satisfy this requirement. """
        return self.__metric_classes or self.default_metric_classes

    def id(self):
        """ Return the identifier of the requirement instance that can be used in the project definition. """
        return self.__id or self.__class__.__name__


class Requirement(DomainObject):
    """ Domain object representing a requirement. """
    _name = 'Subclass responsibility'
    _metric_classes = tuple()  # Subclass responsibility

    @classmethod
    def metric_classes(cls):
        """ Return the metrics that have to be measured to satisfy this requirement. """
        return cls._metric_classes

    @classmethod
    def name(cls):
        """ Return the name of the requirement. """
        return cls._name

    @classmethod
    def id(cls):
        """ Return the identifier of the requirement instance that can be used in the project definition. """
        return cls.__name__


class RequirementSubject(DomainObject):
    """ Measurable objects that have requirements. """
    def __init__(self, *args, **kwargs):
        self.__requirements = kwargs.pop('requirements', set())
        super(RequirementSubject, self).__init__(*args, **kwargs)

    def requirements(self):
        """ Return the requirements of the object. """
        return self.__requirements

    def required_metric_classes(self):
        """ Return the metrics that need to be measured as a consequence of the requirements. """
        classes = set()
        for requirement in self.__requirements:
            classes.update(set(requirement.metric_classes()))
        return classes
