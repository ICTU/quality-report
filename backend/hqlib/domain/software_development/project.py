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

import logging

from typing import cast, List, Set, Sequence, Type, Optional

from .document import Document
from .environment import Environment
from .product import Product
from .process import Process
from .requirement import RequirementSubject, Requirement
from .team import Team
from ..measurement import measurable
from ..base import DomainObject
from ...typing import Dashboard, DashboardColumns, DashboardRows


class Project(RequirementSubject, measurable.MeasurableObject):
    """ Class representing a software development/maintenance project. """

    def __init__(self, organization: str = 'Unnamed organization', *args, **kwargs) -> None:
        self.__short_section_names = {'MM', 'PC', 'PD'}  # Two letter abbreviations used, must be unique
        self.__organization = organization
        self.__processes: List[Process] = []
        self.__products: List[Product] = []
        self.__teams: List[Team] = []
        self.__documents: List[Document] = []
        self.__environments: List[Environment] = []
        self.__dashboard: Dashboard = ([], [])  # rows, columns
        super().__init__(*args, **kwargs)

    @staticmethod
    def optional_requirements() -> Sequence[Type[Requirement]]:
        from ... import requirement  # Run time import to prevent circular dependency.
        return (requirement.TrackActions, requirement.TrackRisks,
                requirement.TrackBugs, requirement.TrackSecurityBugs, requirement.TrackStaticSecurityBugs,
                requirement.TrackSecurityTestDate, requirement.TrackQualityGate, requirement.TrackFindings,
                requirement.TrackTechnicalDebt,
                requirement.TrackReadyUS, requirement.TrackSecurityAndPerformanceRisks,
                requirement.TrackUserStoriesInProgress, requirement.TrackDurationOfUserStories,
                requirement.TrackManualLTCs, requirement.TrustedProductMaintainability)

    def organization(self) -> str:
        """ Return the name of the organization. """
        return self.__organization

    def domain_object_classes(self) -> Set[Type[DomainObject]]:
        """ Return a set of all the domain object classes used. """
        domain_objects = self.processes() + self.products() + self.teams() + self.documents() + self.environments()
        return {cast(Type[DomainObject], domain_object.__class__) for domain_object in domain_objects}

    def add_process(self, process: Process) -> None:
        """ Add a process to the project. """
        self.__check_short_section_name(process.short_name())
        self.__processes.append(process)

    def processes(self) -> List[Process]:
        """ Return the processes of the project. """
        return self.__processes

    def get_process(self, name: str) -> Optional[Process]:
        """ Find a process by name. """
        matches = [process for process in self.__processes if process.name() == name]
        return matches[0] if matches else None

    def add_product(self, product: Product) -> None:
        """ Add a product to the project. """
        self.__check_short_section_name(product.short_name())
        self.__products.append(product)

    def products(self) -> List[Product]:
        """ Return the products of the project. """
        return self.__products

    def get_product(self, name: str) -> Optional[Product]:
        """ Find a product by name. """
        matches = [product for product in self.__products if product.name() == name]
        return matches[0] if matches else None

    def add_team(self, team: Team) -> None:
        """ Add a team to the project. """
        self.__check_short_section_name(team.short_name())
        self.__teams.append(team)

    def teams(self) -> List[Team]:
        """ Return the teams that work on the project. """
        return self.__teams

    def add_document(self, document: Document) -> None:
        """ Add a document to the project. """
        self.__documents.append(document)

    def documents(self) -> List[Document]:
        """ Return the documents of the project. """
        return self.__documents

    def add_environment(self, environment: Environment) -> None:
        """ Add an environment to the project. """
        self.__environments.append(environment)

    def environments(self) -> List[Environment]:
        """ Return the environments of the project """
        return self.__environments

    def set_dashboard(self, dashboard_columns: DashboardColumns, dashboard_rows: DashboardRows):
        """ Set the dashboard layout for the project. """
        self.__dashboard = (dashboard_columns, dashboard_rows)

    def dashboard(self) -> Dashboard:
        """ Return the dashboard layout for the project. """
        return self.__dashboard

    def __check_short_section_name(self, name: str) -> None:
        """ Raise an exception when the short section name is already in use. """
        if name in self.__short_section_names:
            logging.error('Section abbreviation must be unique: %s already used: %s',
                          name, self.__short_section_names)
            raise ValueError('Section abbreviation {0!s} is not unique'.format(name))
        else:
            self.__short_section_names.add(name)
