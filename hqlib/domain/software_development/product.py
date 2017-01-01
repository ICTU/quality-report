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

import copy

from .requirement import RequirementSubject
from ..measurement.measurable import MeasurableObject


class Product(RequirementSubject, MeasurableObject):
    """ Class representing a software product that is developed or maintained. """

    def __init__(self, project, short_name='', unittests=None, integration_tests=None, jsf=None, art=None,
                 is_main=True, **kwargs):
        super(Product, self).__init__(**kwargs)
        self.__project = project
        self.__short_name = short_name
        self.__unittests = unittests
        self.__integration_tests = integration_tests
        self.__jsf = jsf
        self.__art = art
        self.__is_main = is_main  # Is this product part of the main system or is it support code?

    @staticmethod
    def optional_requirements():
        from ... import requirement
        return {requirement.ARTCoverage, requirement.ART, requirement.CodeQuality, requirement.JSFCodeQuality,
                requirement.OWASPDependencies, requirement.OWASPZAP, requirement.PerformanceLoad,
                requirement.PerformanceEndurance, requirement.PerformanceScalability,
                requirement.TrackBranches, requirement.UnitTests, requirement.UserStoriesAndLTCs}

    def __eq__(self, other):
        return self.name() == other.name()

    def is_main(self):
        """ Return whether this product is part of the main system or it is to be considered support code.
            In the latter case it doesn't count towards the total number of lines of code of the whole system. """
        return self.__is_main

    def short_name(self):
        """ Return a short (two letter) abbreviation of the product name. """
        return self.__short_name

    def art(self):
        """ Return a product that represents the ART of this product. """
        return self.__copy_component(self.__art)

    def unittests(self):
        """ Return a product that represents the unit test of this product. """
        return self.__copy_component(self.__unittests)

    def integration_tests(self):
        """ Return a product that represents the integration test of this product. """
        return self.__copy_component(self.__integration_tests)

    def jsf(self):
        """ Return a product that represents the JSF of this product. """
        return self.__copy_component(self.__jsf)

    @staticmethod
    def __copy_component(component):
        """ Return a product that represents a component of this product. """
        return copy.copy(component) if component else None


class Component(Product):
    """ Class representing a software component. """
    @staticmethod
    def default_requirements():
        from ... import requirement
        return {requirement.CodeQuality, requirement.TrackBranches, requirement.UnitTests}

    @staticmethod
    def optional_requirements():
        return super(Component, Component).optional_requirements() - Component.default_requirements()


class Application(Product):
    """ Class representing a software application. """
    @staticmethod
    def default_requirements():
        from ... import requirement
        return {requirement.CodeQuality, requirement.TrackBranches, requirement.ART, requirement.ARTCoverage,
                requirement.PerformanceLoad, requirement.PerformanceEndurance, requirement.OWASPDependencies,
                requirement.OWASPZAP}

    @staticmethod
    def optional_requirements():
        return super(Application, Application).optional_requirements() - Application.default_requirements()
