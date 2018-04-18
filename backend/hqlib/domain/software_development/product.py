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


import copy
from typing import Optional, Type, Sequence

from .requirement import RequirementSubject, Requirement
from ..measurement.measurable import MeasurableObject


class Product(RequirementSubject, MeasurableObject):
    """ Class representing a software product that is developed or maintained. """

    def __init__(self, art: 'Product' = None, is_main: bool = True, **kwargs) -> None:
        super().__init__(**kwargs)
        self.__art = art
        self.__is_main = is_main  # Is this product part of the main system or is it support code?

    @staticmethod
    def optional_requirements() -> Sequence[Type[Requirement]]:
        from ... import requirement
        return (requirement.UserStoriesAndLTCs, requirement.TrackReadyUS, requirement.TrackUserStoriesInProgress,
                requirement.TrackDurationOfUserStories, requirement.TrackSecurityAndPerformanceRisks,
                requirement.ARTCoverage, requirement.ART, requirement.UnitTests, requirement.UnitTestCoverage,
                requirement.AggregatedTestCoverage, requirement.CodeQuality, requirement.TrackBranches,
                requirement.OWASPDependencies, requirement.OWASPZAP, requirement.Checkmarx,
                requirement.PerformanceLoad, requirement.PerformanceEndurance, requirement.PerformanceScalability,
                requirement.TrackBugs, requirement.TrackSecurityBugs, requirement.TrackStaticSecurityBugs,
                requirement.TrackSecurityTestDate,
                requirement.TrackTechnicalDebt, requirement.TrackFindings, requirement.TrackQualityGate)

    def __eq__(self, other):
        return self.name() == other.name()

    def is_main(self) -> bool:
        """ Return whether this product is part of the main system or it is to be considered support code.
            In the latter case it doesn't count towards the total number of lines of code of the whole system. """
        return self.__is_main

    def art(self) -> Optional['Product']:
        """ Return a product that represents the ART of this product. """
        return self.__copy_component(self.__art)

    @staticmethod
    def __copy_component(component) -> Optional['Product']:
        """ Return a product that represents a component of this product. """
        return copy.copy(component) if component else None


class Component(Product):
    """ Class representing a software component. """
    @staticmethod
    def default_requirements() -> Sequence[Type[Requirement]]:
        from ... import requirement
        return requirement.CodeQuality, requirement.UnitTests, requirement.UnitTestCoverage, requirement.TrackBranches

    @staticmethod
    def optional_requirements() -> Sequence[Type[Requirement]]:
        from ... import requirement
        return tuple([r for r in super(Component, Component).optional_requirements()
                      if r not in Component.default_requirements() and r not in (requirement.PerformanceLoad,
                                                                                 requirement.PerformanceEndurance,
                                                                                 requirement.PerformanceScalability)])


class Application(Product):
    """ Class representing a software application. """
    @staticmethod
    def default_requirements() -> Sequence[Type[Requirement]]:
        from ... import requirement
        return (requirement.CodeQuality, requirement.ART, requirement.ARTCoverage, requirement.TrackBranches,
                requirement.PerformanceLoad, requirement.PerformanceEndurance, requirement.OWASPDependencies,
                requirement.OWASPZAP, requirement.Checkmarx)

    @staticmethod
    def optional_requirements() -> Sequence[Type[Requirement]]:
        return tuple([r for r in super(Application, Application).optional_requirements()
                      if r not in Application.default_requirements()])
