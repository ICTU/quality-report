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


from typing import Set, Type, Sequence

from hqlib import domain


class Requirement(domain.DomainObject):
    """ Domain object representing a requirement. """
    _name: str = 'Subclass responsibility'
    _url: str = 'Subclass responsibility'
    _metric_classes: Sequence[Type[domain.Metric]] = []  # Subclass responsibility

    @classmethod
    def metric_classes(cls) -> Sequence[Type[domain.Metric]]:
        """ Return the metrics that have to be measured to satisfy this requirement. """
        return cls._metric_classes

    @classmethod
    def name(cls) -> str:
        """ Return the name of the requirement. """
        return cls._name

    @classmethod
    def url(cls) -> str:
        """ Return the url. """
        return cls._url


class RequirementSubject(domain.DomainObject):
    """ Measurable objects that have requirements. """
    def __init__(self, *args, **kwargs) -> None:
        self.__requirements: Set[Type[Requirement]] = set(kwargs.pop('requirements', []))
        if not self.__requirements:
            added_requirements = set(kwargs.pop('added_requirements', []))
            if not added_requirements.issubset(self.optional_requirements()):
                raise ValueError("Added requirements should be a subset of the optional requirements")
            removed_requirements = set(kwargs.pop('removed_requirements', []))
            self.__requirements = (self.default_requirements() | added_requirements) - removed_requirements
        super().__init__(*args, **kwargs)

    @staticmethod
    def default_requirements() -> Set[Type[Requirement]]:
        """ Return the default requirements of the subject. """
        return set()

    @staticmethod
    def optional_requirements() -> Set[Type[Requirement]]:
        """ Return the optional requirements of the subject. """
        return set()

    def requirements(self) -> Set[Type[Requirement]]:
        """ Return the actual requirements of the subject. """
        return self.__requirements

    def should_be_measured_by(self, metric_class: Type[domain.Metric]) -> bool:
        """ Return whether this subject should be measured by the metric. """
        for requirement in self.__requirements:
            if metric_class in requirement.metric_classes():
                return True
        return False
