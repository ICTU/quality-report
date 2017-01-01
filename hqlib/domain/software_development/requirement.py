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


class RequirementSubject(DomainObject):
    """ Measurable objects that have requirements. """
    def __init__(self, *args, **kwargs):
        self.__requirements = kwargs.pop('requirements', set())
        if not self.__requirements:
            added_requirements = set(kwargs.pop('added_requirements', []))
            assert added_requirements.issubset(self.optional_requirements())
            removed_requirements = set(kwargs.pop('removed_requirements', []))
            self.__requirements = (self.default_requirements() | added_requirements) - removed_requirements
        super(RequirementSubject, self).__init__(*args, **kwargs)

    @staticmethod
    def default_requirements():
        """ Return the default requirements of the subject. """
        return set()

    @staticmethod
    def optional_requirements():
        """ Return the optional requirements of the subject. """
        return set()

    def requirements(self):
        """ Return the requirements of the subject. """
        return self.__requirements

    def required_metric_classes(self):
        """ Return the metrics that need to be measured as a consequence of the requirements. """
        classes = set()
        for requirement in self.__requirements:
            classes.update(set(requirement.metric_classes()))
        return classes
