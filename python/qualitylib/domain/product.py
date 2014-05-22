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

from qualitylib import utils
from qualitylib.domain.measurement.measurable import MeasurableObject
import copy
import logging
import urllib2


class Product(MeasurableObject):
    ''' Class representing a software product that is developed or
        maintained. '''

    def __init__(self, project, short_name='', sonar_id='', 
                 old_sonar_ids=None, jsf=None, 
                 art_coverage_emma_id=None, art_coverage_jacoco_id=None,
                 unittest_sonar_id=None, old_unittest_sonar_ids=None,
                 birt_id=None, svn_path='', old_svn_paths=None,
                 sonar_options=None, maven_binary=None, 
                 maven_options=None, unittest_maven_options=None, 
                 java_home=None, is_art=False, performancetest_id=None,
                 responsible_teams=None, kpi_responsibility=None, targets=None,
                 low_targets=None, technical_debt_targets=None,
                 art=None, release_candidate_id='', pom=None, 
                 branches_to_ignore=None, product_version=''):

        ''' responsible_teams: list of teams responsible for this product.
            kpi_responsibility: dictionary of metric classes mapped to lists
                                of teams responsible for the product/metric
                                combination. '''
        super(Product, self).__init__( \
            targets=targets, low_targets=low_targets,
            technical_debt_targets=technical_debt_targets)
        self.__project = project
        self.__short_name = short_name
        self.__sonar_id = sonar_id
        self.__old_sonar_ids = old_sonar_ids or {}
        self.__jsf = jsf
        self.__art = art
        self.__art_coverage_emma_id = art_coverage_emma_id
        self.__art_coverage_jacoco_id = art_coverage_jacoco_id
        self.__unittest_sonar_id = unittest_sonar_id
        self.__old_unittest_sonar_ids = old_unittest_sonar_ids or {}
        self.__birt_id = birt_id
        if svn_path and not svn_path.endswith('/'):
            svn_path += '/'
        self.__svn_path = svn_path
        self.__old_svn_paths = old_svn_paths or {}
        self.__product_version = product_version
        self.__release_candidate_id = release_candidate_id
        self.__sonar_options = sonar_options or {}
        self.__maven_binary = maven_binary or self.__project.maven_binary()
        self.__maven_options = maven_options or ''
        self.__unittest_maven_options = unittest_maven_options or ''
        self.__java_home = java_home or self.__project.java_home()
        self.__is_art = is_art
        self.__performancetest_id = performancetest_id
        self.__product_responsibility = responsible_teams or []
        self.__kpi_responsibility = kpi_responsibility or {}
        self.__pom = pom
        self.__branches_to_ignore = branches_to_ignore or []
        self.__initialize_targets()

    def __initialize_targets(self):
        ''' Set default targets that depend on the product characteristics,
            e.g. whether the product is an ART or not. '''
        from qualitylib import metric  # Prevent circular import
        for metric_class in [metric.ManyParameters, metric.LongMethods,
                             metric.CyclomaticComplexity]:
            if metric_class not in self._targets and self.is_art():
                self._targets[metric_class] = 1

    def __str__(self):
        return self.sonar_id()

    def __repr__(self):
        return self.sonar_id()

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return str(self) != str(other)

    def __add__(self, other):
        return str(self) + str(other)

    def __radd__(self, other):
        return str(other) + str(self)

    def sonar_id(self):
        ''' Return the id that identifies the product in Sonar. '''
        if self.__product_version in self.__old_sonar_ids:
            sonar_id = self.__old_sonar_ids[self.__product_version]
        else:
            sonar_id = self.__sonar_id
        if self.__product_version:
            sonar_id += ':' + self.__product_version
        return sonar_id

    def all_sonar_ids(self):
        ''' Return all Sonar ids of the product: the Sonar id of the product
            itself and its unit tests if applicable. '''
        sonar_ids = set([self.sonar_id()])
        if self.unittests():
            sonar_ids.add(self.unittests())
        jsf = self.jsf()
        if jsf:
            sonar_ids.add(jsf.sonar_id())
        return sonar_ids

    def set_product_version(self, product_version):
        ''' Set the product version of this product. '''
        self.__product_version = product_version

    def product_version(self):
        ''' Return the product version of this product. '''
        return self.__product_version

    def product_version_type(self):
        ''' Return whether the version of this product is trunk, tagged or 
            release candidate. '''
        if self.is_release_candidate():
            return 'release'
        elif self.product_version():
            return 'tag'
        else:
            return 'trunk'

    def latest_released_product_version(self):
        ''' Return the latest released version of this product. '''
        if not self.__svn_path:
            return ''
        subversion = self.__project.subversion()
        return subversion.latest_tagged_product_version(self.__svn_path)

    def is_latest_release(self):
        ''' Return whether the version of this product is the latest 
            released version. '''
        product_version = self.product_version()
        if product_version:
            return product_version == self.latest_released_product_version()
        else:
            return False
        
    def last_changed_date(self):
        ''' Return the date this product/version was last changed. '''
        subversion = self.__project.subversion()
        return subversion.last_changed_date(self.repository_path())
    
    def release_candidate(self):
        ''' Return the version of this product that is the candidate for 
            release to operations. '''
        if self.__release_candidate_id:
            release_candidates = self.__project.release_candidates()
            try:
                return release_candidates[self.__release_candidate_id]
            except KeyError:
                pass
        return ''

    def is_release_candidate(self):
        ''' Return whether this product/version is a release candidate. '''
        if self.product_version():
            if self.product_version() == self.release_candidate():
                return True
            else:  # Consider this a release candidate when any of its users is
                for user in self.users(recursive=True):
                    if user.is_release_candidate():
                        return True        
        return False

    def name(self):
        ''' Return a human readable name for the product. '''
        try:
            return self.__sonar_id.split(':', 1)[-1]
        except AttributeError:
            logging.error('Product %s has no Sonar id', self.__short_name)
            raise

    def short_name(self):
        ''' Return a short (two letter) abbreviation of the product name. '''
        return self.__short_name + \
            self.__product_version.replace('-', '_').replace('.', '_')

    def art(self):
        ''' Return a product that represents the ART of this product. '''
        if self.__art:
            art = copy.copy(self.__art)
            art.set_product_version(self.product_version())
            return art
        else:
            return None

    def is_art(self):
        ''' Return whether this product is an ART or not. '''
        return self.__is_art

    def has_art_coverage(self):
        ''' Return whether the ART coverage of the product is measured. '''
        return self.art_coverage_emma() is not None or \
               self.art_coverage_jacoco() is not None

    def art_coverage_emma(self):
        ''' Return the Emma id of the coverage project. '''
        return self.__art_coverage_emma_id

    def art_coverage_jacoco(self):
        ''' Return the JaCoCo id of the coverage project. '''
        return self.__art_coverage_jacoco_id

    def unittests(self):
        ''' Return the Sonar id of the unit tests of this product. '''
        if self.__product_version in self.__old_unittest_sonar_ids:
            unittest_sonar_id = \
                self.__old_unittest_sonar_ids[self.__product_version]
        else:
            unittest_sonar_id = self.__unittest_sonar_id
        if unittest_sonar_id and self.__product_version:
            return unittest_sonar_id + ':' + self.__product_version
        else:
            return unittest_sonar_id

    def jsf(self):
        ''' Return a product that represents the JSF of this product. '''
        if self.__jsf:
            jsf = copy.copy(self.__jsf)
            jsf.set_product_version(self.product_version())
            return jsf
        else:
            return None

    def technical_debt_target(self, metric_class):
        ''' Return whether a score below target is considered to be accepted
            technical debt. '''
        # First check for a technical debt target for our version. If there
        # is no technical debt target for our version return the generic
        # technical debt target.
        try:
            return self._technical_debt_targets[(metric_class,
                                                 self.product_version())]
        except KeyError:
            return super(Product, self).technical_debt_target(metric_class)

    def birt_id(self):
        ''' Return the id of this product in Birt. '''
        return self.__birt_id

    def has_test_design(self):
        ''' Return whether this product has test design metrics. '''
        birt = self.__project.birt()
        return birt.has_test_design(self.birt_id()) if birt else False

    def performance_test(self):
        ''' Return the id of this product for the performance test report. '''
        return self.__performancetest_id

    def responsible_teams(self, metric_class=None):
        ''' Return the list of teams responsible for this product. '''
        if metric_class in self.__kpi_responsibility:
            return self.__kpi_responsibility[metric_class]
        elif self.__product_responsibility:
            return self.__product_responsibility
        else:
            return self.__project.responsible_teams()

    def svn_path(self, version=None):
        ''' Return the svn path of this product and version. '''
        version = version or self.product_version()
        if version in self.__old_svn_paths:
            return self.__old_svn_paths[version]
        else:
            result = self.__svn_path
            if not result:
                return ''
            if version:
                name = self.name()
                if name.endswith(':jsf'):
                    name = name[:-len(':jsf')]
                result += 'tags/' + name + '-' + version
            else:
                result += 'trunk'
            return result

    def repository_path(self, version=None):
        ''' Return the source code repository path of this product and 
            version. '''
        if self.__svn_path:
            return self.svn_path(version)
        else:
            return ''
        
    def check_out(self, folder):
        ''' Check out the source code of the product. '''
        self.__project.subversion().check_out(self.svn_path(), folder)
        
    def branches_to_ignore(self):
        ''' Return the list of branch names that shouldn't be checked for
            unmerged code. '''
        return self.__branches_to_ignore

    def sonar_options(self):
        ''' Return options to pass to Sonar for analysing this product. '''
        return self.__sonar_options.copy()

    def maven_binary(self):
        ''' Return the Maven binary to use for building the project. '''
        return self.__maven_binary

    def maven_options(self):
        ''' Return options to pass to Maven for building this product. '''
        return self.__maven_options

    def unittest_maven_options(self):
        ''' Return options to pass to Maven for running the unit tests of this
            product. '''
        return self.__unittest_maven_options
    
    def java_home(self):
        ''' Return the JAVA_HOME environment variable to be used for building
            the product. '''
        return self.__java_home
        
    @utils.memoized
    def dependencies(self, recursive=True, version=None, user=None):
        ''' Return the dependencies of this product and version,
            recursively. '''
        version = version or self.product_version()
        dependencies = self.__get_dependencies(version, user)
        recursive_dependencies = set()
        for dependency_name, dependency_version in dependencies.copy():
            dependency = self.__find_product_by_name(dependency_name)
            if dependency and dependency.name() != self.name():
                if recursive:
                    recursive_dependencies.update(\
                        dependency.dependencies(version=dependency_version,
                                                user=self))
            else:
                dependencies.remove((dependency_name, dependency_version))
        all_dependencies = dependencies | recursive_dependencies
        logging.debug('Dependencies of %s:%s are: %s', self.name(),
                      version or 'trunk', all_dependencies)
        return all_dependencies

    @utils.memoized
    def users(self, recursive=True):
        ''' Return the users of this product and version. '''
        name, version = self.name(), self.product_version()
        logging.info('Retrieving users of %s:%s', name, version or 'trunk')
        users = set()
        for product in self.__project.products():
            if (name, version) in product.dependencies(recursive):
                users.add(product)
        return users
    
    @utils.memoized
    def has_artifact(self, artifact_id):
        ''' Return whether this product has an artifact with artifact id. '''
        own_artifact_id = self.sonar_id().split(':')[1]
        if artifact_id == own_artifact_id:
            return True
        for module in self.__project.pom().modules(self.repository_path()):
            if artifact_id == module:
                return True
        return False

    def __get_dependencies(self, version, user):
        ''' Get the dependencies from the cached dependencies database if 
            possible or else from the pom file. '''
        if self.__project.dependency_db() and version:
            return self.__get_dependencies_from_cache(version, user)
        else:
            return self.__get_dependencies_from_pom(version, user)
        
    def __get_dependencies_from_cache(self, version, user):
        ''' Get the dependencies from the cached dependencies database. First
            update cache if necessary. '''
        cache = self.__project.dependency_db()
        name = self.name()
        if not cache.has_dependencies(name, version):
            # Update the cache
            dependencies = self.__get_dependencies_from_pom(version, user)
            cache.set_dependencies(name, version, dependencies)
            cache.save()
        return cache.get_dependencies(name, version)
    
    @utils.memoized
    def __get_dependencies_from_pom(self, version, user):
        ''' Open the pom file for this product and the specified version
            and retrieve the dependencies from the pom file. '''
        pom = self.__project.pom()
        if not pom:
            logging.warning('No pom retriever defined.')
            return set()
        repository_path = self.repository_path(version)
        try:
            return pom.dependencies(repository_path, self.__project.products())
        except (ValueError, IndexError, urllib2.HTTPError), reason:
            logging.error("Couldn't retrieve dependencies for %s:%s: %s",
                          self.name(), version or 'trunk', reason)
            if user:
                logging.error('User of %s:%s is %s:%s', self.name(), 
                              version or 'trunk', user.name(), 
                              user.product_version() or 'trunk')
            raise

    def __find_product_by_name(self, product_name):
        ''' Lookup a product in the list of products by its name. '''
        for product in self.__project.products():
            if product_name == product.name():
                return product
