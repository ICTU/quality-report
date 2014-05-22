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

import copy
import logging
from qualitylib.metric_source import MissingMetricSource


class Project(object):
    ''' Class representing a software development/maintenance project. '''

    def __init__(self, organization='Unnamed organization', 
                 name='Unnamed project', build_server=None, emma=None, 
                 jacoco=None, sonar=None, birt=None, wiki=None, 
                 history=None, trello_risklog_board=None, 
                 trello_actions_board=None, performance_report=None, 
                 release_candidates=None, release_archives=None,
                 javamelody=None, jira=None, subversion=None, pom=None,
                 maven_binary='mvn', java_home=None, dependencies_db=None,
                 tasks=None, additional_resources=None):
        self.__organization = organization
        self.__name = name
        missing = MissingMetricSource()
        self.__build_server = build_server or missing
        self.__emma = emma or missing
        self.__jacoco = jacoco or missing
        self.__sonar = sonar or missing
        self.__birt = birt or missing
        self.__wiki = wiki or missing
        self.__history = history
        self.__trello_risklog_board = trello_risklog_board or missing
        self.__trello_actions_board = trello_actions_board or missing
        self.__performance_report = performance_report or missing
        self.__release_candidates = release_candidates or missing
        self.__release_archives = release_archives or missing
        self.__javamelody = javamelody or missing
        self.__jira = jira or missing
        self.__tasks = tasks or jira or missing
        self.__subversion = subversion or missing
        self.__pom = pom or missing
        self.__maven_binary = maven_binary
        self.__java_home = java_home
        self.__dependencies_db = dependencies_db
        self.__additional_resources = additional_resources or missing
        self.__products = []
        self.__teams = []
        self.__responsible_teams = []
        self.__streets = []
        self.__documents = []
        self.__dashboard = [], []  # rows, columns

    def organization(self):
        ''' Return the name of the organization. '''
        return self.__organization

    def name(self):
        ''' Return the name of the project. '''
        return self.__name

    def performance_report(self):
        ''' Return the performance report of the project. '''
        return self.__performance_report

    def release_candidates(self):
        ''' Return the release candidates file of the project. '''
        return self.__release_candidates

    def release_archives(self):
        ''' Return the release archives of the project. '''
        return self.__release_archives

    def sonar(self):
        ''' Return the Sonar instance of the project. '''
        return self.__sonar

    def maven_binary(self):
        ''' Return the Maven binary the project uses. '''
        return self.__maven_binary

    def java_home(self):
        ''' Return the JAVA_HOME environment variable the project uses. '''
        return self.__java_home

    def build_server(self):
        ''' Return the build server instance of the project. '''
        return self.__build_server

    def birt(self):
        ''' Return the Birt reporting instance of the project. '''
        return self.__birt

    def history(self):
        ''' Return the history of the project. '''
        return self.__history

    def dependency_db(self):
        ''' Return the database with cached dependencies of the project. '''
        return self.__dependencies_db

    def additional_resources(self):
        ''' Return the additional resources of the project. '''
        return self.__additional_resources

    def wiki(self):
        ''' Return the wiki of the project (for manual metrics). '''
        return self.__wiki

    def emma(self):
        ''' Return the Emma coverage report(s) for the project. '''
        return self.__emma

    def jacoco(self):
        ''' Return the JaCoCo coverage report(s) for the project. '''
        return self.__jacoco

    def trello_risklog_board(self):
        ''' Return the Trello risklog board for the project. '''
        return self.__trello_risklog_board

    def trello_actions_board(self):
        ''' Return the Trello actions board for the project. '''
        return self.__trello_actions_board

    def javamelody(self):
        ''' Return the JavaMelody instance for the project. '''
        return self.__javamelody

    def jira(self):
        ''' Return the Jira instance for the project. '''
        return self.__jira

    def tasks(self):
        ''' Return the task manager for the project. '''
        return self.__tasks

    def subversion(self):
        ''' Return the Subversion repository of the project. '''
        return self.__subversion

    def pom(self):
        ''' Return the Pom retriever for the project. '''
        return self.__pom

    def add_product(self, product):
        ''' Add a product to the project. '''
        self.__products.append(product)

    def add_product_with_version(self, product_name, product_version):
        ''' Add product with the specified version to the project. '''
        base_product = None
        for product in self.products():
            if product.name() == product_name:
                if product.product_version() and \
                   product.product_version() == product_version:
                    return  # Product/version combination already exists
                else:  # Trunk
                    base_product = product  # No break, keep looking
        if base_product:
            product_copy = copy.copy(base_product)
            product_copy.set_product_version(product_version)
            self.add_product(product_copy)
            return product_copy
        else:
            logging.error("Couldn't find %s:%s", product_name, product_version)

    def products(self):
        ''' Return the products of the project. '''
        return self.__products

    def get_product(self, product_name):
        ''' Find a product by name. '''
        for product in self.__products:
            if product_name == product.name():
                return product

    def product_dependencies(self):
        ''' Return a set of all dependencies of all products. '''
        result = set()
        for product in self.products():
            result.update(product.dependencies(recursive=True))
        return result

    def analyse_products(self):
        ''' Make sure all products/versions in the project are analyzed. '''
        if self.sonar():
            self.sonar().analyse_products(self.products())

    def add_team(self, team, responsible=False):
        ''' Add a team to the project. '''
        self.__teams.append(team)
        if responsible:
            self.__responsible_teams.append(team)

    def teams(self):
        ''' Return the teams that work on the project. '''
        return self.__teams

    def responsible_teams(self, metric_class=None):
        # pylint: disable=unused-argument
        ''' Return the teams that are responsible for the products. '''
        # The metric_class argument is used in other domain objects that may 
        # have teams responsible for them. Maybe we should create an explicit 
        # "Responsibility" interface.
        return self.__responsible_teams

    def add_street(self, street):
        ''' Add a development street to the project. '''
        self.__streets.append(street)

    def streets(self):
        ''' Return the development streets of the project. '''
        return self.__streets

    def add_document(self, document):
        ''' Add a document to the project. '''
        self.__documents.append(document)

    def documents(self):
        ''' Return the documents of the project. '''
        return self.__documents

    def set_dashboard(self, dashboard_columns, dashboard_rows):
        ''' Set the dashboard layout for the project. '''
        self.__dashboard = (dashboard_columns, dashboard_rows)

    def dashboard(self):
        ''' Return the dashboard layout for the project. '''
        return self.__dashboard

    def project_resources(self):
        ''' Return all resources of the project. '''
        resources = []
        resources.append(('Jira', self.jira().url()))
        resources.append(('Build server', self.build_server().url()))
        resources.append(('Sonar', self.sonar().url()))
        resources.append(('Birt reports', self.birt().url()))
        self.__add_coverage_resources(resources)
        if self.performance_report():
            resources.append(('Performance reports', 
                              self.performance_report().url()))
        if self.javamelody():
            resources.append(('JavaMelody', self.javamelody().url()))
        resources.append(('Wiki', self.wiki().url() if self.wiki() else None))
        if self.trello_risklog_board():
            resources.append(('Trello risico log', 
                              self.trello_risklog_board().url()))
        if self.trello_actions_board():
            resources.append(('Trello acties', 
                              self.trello_actions_board().url()))
        if self.release_candidates():
            resources.append(('Release kandidaten', 
                              self.release_candidates().url()))
        for release_archive in self.release_archives():
            resources.append(('Release archief', release_archive.url()))
        self.__add_repository_resources(resources)
        for additional_resource in self.additional_resources():
            resources.append((additional_resource['title'], additional_resource['url']))
        return resources

    def __add_coverage_resources(self, resources):
        ''' Add the ART coverage reports to the resources. '''
        for product in self.products():
            # Only include trunk versions that have an ART with coverage
            # measurement:
            if not product.product_version() and product.has_art_coverage():
                if product.art_coverage_emma():
                    resources.append( \
                        ('Emma coverage report %s' % product.name(), 
                         self.emma().get_coverage_url( \
                                                product.art_coverage_emma())))
                if product.art_coverage_jacoco():
                    resources.append( \
                        ('JaCoCo coverage report %s' % product.name(),
                         self.jacoco().get_coverage_url( \
                                                product.art_coverage_jacoco())))

    def __add_repository_resources(self, resources):
        ''' Add the repositories to the resources. '''
        for product in self.products():
            if product.svn_path().endswith('/trunk'):
                resources.append(('Broncode repository %s' % product.name(),
                                  product.svn_path()[:-len('/trunk')]))
