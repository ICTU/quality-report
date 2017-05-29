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


import copy
from typing import Optional, Set, Type

from .requirement import RequirementSubject, Requirement
from ..measurement.measurable import MeasurableObject


class Product(RequirementSubject, MeasurableObject):
    """ Class representing a software product that is developed or maintained. """

    def __init__(self, jsf: 'Product'=None, art: 'Product'=None, is_main: bool=True,
                 has_unittests: bool=True, has_integration_tests: bool=False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.__has_unittests = has_unittests
        self.__has_integration_tests = has_integration_tests
        self.__jsf = jsf
        self.__art = art
        self.__is_main = is_main  # Is this product part of the main system or is it support code?

    @staticmethod
    def optional_requirements() -> Set[Type[Requirement]]:
        from ... import requirement
        return {requirement.ARTCoverage, requirement.ART, requirement.CodeQuality, requirement.JSFCodeQuality,
                requirement.OWASPDependencies, requirement.OWASPZAP, requirement.Checkmarx,
                requirement.PerformanceLoad, requirement.PerformanceEndurance, requirement.PerformanceScalability,
                requirement.TrackBranches, requirement.UnitTests, requirement.UserStoriesAndLTCs}

    def __eq__(self, other):
        return self.name() == other.name()

    def is_main(self) -> bool:
        """ Return whether this product is part of the main system or it is to be considered support code.
            In the latter case it doesn't count towards the total number of lines of code of the whole system. """
        return self.__is_main

    def art(self) -> Optional['Product']:
        """ Return a product that represents the ART of this product. """
        return self.__copy_component(self.__art)

    def has_unittests(self) -> bool:
        """ Return whether the product has unit tests. """
        return self.__has_unittests

    def has_integration_tests(self) -> bool:
        """ Return whether the product has integration tests. """
        return self.__has_integration_tests

    def jsf(self) -> Optional['Product']:
        """ Return a product that represents the JSF of this product. """
        return self.__copy_component(self.__jsf)

    @staticmethod
    def __copy_component(component) -> Optional['Product']:
        """ Return a product that represents a component of this product. """
        return copy.copy(component) if component else None


class Component(Product):
    """ Class representing a software component. """
    @staticmethod
    def default_requirements() -> Set[Type[Requirement]]:
        from ... import requirement
        return {requirement.CodeQuality, requirement.UnitTests, requirement.TrackBranches}

    @staticmethod
    def optional_requirements():
        from ... import requirement
        return super(Component, Component).optional_requirements() - Component.default_requirements() - \
            {requirement.PerformanceLoad, requirement.PerformanceEndurance, requirement.PerformanceScalability}


class Application(Product):
    """ Class representing a software application. """
    @staticmethod
    def default_requirements() -> Set[Type[Requirement]]:
        from ... import requirement
        return {requirement.CodeQuality, requirement.TrackBranches, requirement.ART, requirement.ARTCoverage,
                requirement.PerformanceLoad, requirement.PerformanceEndurance, requirement.OWASPDependencies,
                requirement.OWASPZAP, requirement.Checkmarx}

    @staticmethod
    def optional_requirements():
        return super(Application, Application).optional_requirements() - Application.default_requirements()
