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

    def __init__(self, project, short_name='',
                 unittests=None, jsf=None, art=None,
                 responsible_teams=None, metric_responsibility=None, 
                 product_branches=None, product_version='', product_branch='',
                 **kwargs):

        ''' responsible_teams: list of teams responsible for this product.
            metric_responsibility: dictionary of metric classes mapped to lists
                of teams responsible for the product/metric combination. '''
        super(Product, self).__init__(**kwargs)
        self.__project = project
        self.__short_name = short_name
        self.__unittests = unittests
        self.__jsf = jsf
        self.__art = art
        self.__product_branches = product_branches or []
        self.__product_version = product_version
        self.__product_branch = product_branch
        self.__product_responsibility = responsible_teams or []
        self.__metric_responsibility = metric_responsibility or {}

    def __eq__(self, other):
        return self.product_label() == other.product_label()

    def sonar_id(self):
        ''' Return the id that identifies the product in Sonar. '''
        from qualitylib import metric_source
        sonar = self.__project.metric_source(metric_source.Sonar)
        sonar_id = self.old_metric_source_id(sonar, self.__product_version)
        if not sonar_id:
            sonar_id = self.metric_source_id(sonar) or ''
        if sonar_id and self.__product_branch:
            sonar_id += ':' + self.__product_branch
        if sonar_id and self.__product_version:
            sonar_id += ':' + self.__product_version
        return sonar_id

    def set_product_version(self, product_version):
        ''' Set the product version of this product. '''
        self.__product_version = product_version

    def product_version(self):
        ''' Return the product version of this product. '''
        return self.__product_version

    def product_branches(self):
        ''' Return the branches of this product that have to be monitored. '''
        return self.__product_branches if \
            self.product_version_type() == 'trunk' else []

    def product_branch(self):
        ''' Return the branch of this product. '''
        return self.__product_branch

    def set_product_branch(self, product_branch):
        ''' Set the product branch of this product. '''
        self.__product_branch = product_branch

    def product_version_type(self):
        ''' Return whether the version of this product is trunk, tagged or 
            release candidate. '''
        if self.is_release_candidate():
            return 'release'
        elif self.product_version():
            return 'tag'
        elif self.product_branch():
            return 'branch'
        else:
            return 'trunk'

    def product_label(self):
        ''' Name, version, branch combination. '''
        return self.name() + ':' + self.branch_version_label()

    def branch_version_label(self):
        ''' Return the branch and version as label. '''
        branch = self.product_branch()
        version = self.product_version()
        if branch and version:
            return branch + ':' + version
        if branch:
            return branch
        if version:
            return version
        return 'trunk'

    def latest_released_product_version(self):
        ''' Return the latest released version of this product. '''
        from qualitylib import metric_source
        subversion = self.__project.metric_source(metric_source.Subversion)
        svn_path = self.metric_source_id(subversion)
        if not svn_path:
            return ''
        if not svn_path.endswith('/'):
            svn_path += '/'
        if not '/trunk/' in svn_path:
            svn_path += 'trunk/'
        return subversion.latest_tagged_product_version(svn_path)

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
        from qualitylib import metric_source
        subversion = self.__project.metric_source(metric_source.Subversion)
        return subversion.last_changed_date(self.svn_path())

    def release_candidate(self):
        ''' Return the version of this product that is the candidate for 
            release to operations. '''
        from qualitylib import metric_source
        release_candidates = self.__project.metric_source(metric_source.ReleaseCandidates)
        release_candidate_id = self.metric_source_id(release_candidates)
        return release_candidates.release_candidate(release_candidate_id)

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

    def short_name(self):
        ''' Return a short (two letter) abbreviation of the product name. '''
        return self.__short_name + \
            self.__product_branch.replace('-', '_').replace('.', '_') + \
            self.__product_version.replace('-', '_').replace('.', '_')

    def art(self):
        ''' Return a product that represents the ART of this product. '''
        return self.__copy_component(self.__art)

    def unittests(self):
        ''' Return a product that represents the unit test of this product. '''
        return self.__copy_component(self.__unittests)

    def jsf(self):
        ''' Return a product that represents the JSF of this product. '''
        return self.__copy_component(self.__jsf)

    def __copy_component(self, component):
        ''' Return a product that represents a component of this product. '''
        if component:
            copy_component = copy.copy(component)
            copy_component.set_product_branch(self.product_branch())
            copy_component.set_product_version(self.product_version())
            return copy_component
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

    def responsible_teams(self, metric_class=None):
        ''' Return the list of teams responsible for this product. '''
        if metric_class in self.__metric_responsibility:
            return self.__metric_responsibility[metric_class]
        elif self.__product_responsibility:
            return self.__product_responsibility
        else:
            return self.__project.responsible_teams()

    def svn_path(self, version=None, branch=None):
        ''' Return the svn path of this product and version. '''
        from qualitylib import metric_source
        subversion = self.__project.metric_source(metric_source.Subversion)
        version = version or self.product_version()
        branch = branch or self.product_branch()
        old_svn_path = self.old_metric_source_id(subversion, version)
        if old_svn_path:
            return old_svn_path
        result = self.metric_source_id(subversion)
        if not result:
            return ''
        if not result.endswith('/'):
            result += '/'
        if not '/trunk/' in result:
            result += 'trunk/'
        if version:
            result = subversion.tags_folder_for_version(result, version)
        elif branch:
            result = subversion.branch_folder_for_branch(result, branch)
        return result

    def check_out(self, folder):
        ''' Check out the source code of the product. '''
        from qualitylib import metric_source
        subversion = self.__project.metric_source(metric_source.Subversion)
        subversion.check_out(self.svn_path(), folder)

    def product_resources(self):
        ''' Return the resources of the product. '''
        from qualitylib import metric_source
        resources = []
        if not self.product_version():
        # Only include these resources for trunk versions:
            for metric_source_class in [metric_source.Emma,
                                        metric_source.JaCoCo]:
                source = self.__project.metric_source(metric_source_class)
                source_id = self.metric_source_id(source)
                if source_id:
                    resources.append(('%s %s' % (source.name(), 
                                                 self.name()), 
                                      source.get_coverage_url(source_id)))
            if self.svn_path():
                resources.append(('Broncode repository %s' % self.name(), 
                                  self.svn_path()))
        return resources

    @utils.memoized
    def dependencies(self, recursive=True, version=None, user=None):
        ''' Return the dependencies of this product and version,
            recursively. '''
        version = version or self.product_version()
        dependencies = self.__get_dependencies(version, user)
        recursive_dependencies = set()
        for dependency_name, dependency_version in dependencies.copy():
            dependency = self.__project.get_product(dependency_name)
            if dependency and dependency.name() != self.name():
                if recursive:
                    recursive_dependencies.update(\
                        dependency.dependencies(version=dependency_version,
                                                user=self))
            else:
                dependencies.remove((dependency_name, dependency_version))
        all_dependencies = dependencies | recursive_dependencies
        logging.debug('Dependencies of %s are: %s', self.product_label(), 
                      all_dependencies)
        return all_dependencies

    @utils.memoized
    def users(self, recursive=True):
        ''' Return the users of this product and version. '''
        logging.info('Retrieving users of %s', self.product_label())
        name, version = self.name(), self.product_version()
        users = set()
        for product in self.__project.products():
            if (name, version) in product.dependencies(recursive):
                users.add(product)
        return users

    def __get_dependencies(self, version, user):
        ''' Get the dependencies from the cached dependencies database if 
            possible or else from the pom file. '''
        from qualitylib import metric_source
        cache = self.__project.metric_source(metric_source.Dependencies)
        if cache and version:
            return self.__get_dependencies_from_cache(version, user, cache)
        else:
            return self.__get_dependencies_from_pom(version, user)

    def __get_dependencies_from_cache(self, version, user, cache):
        ''' Get the dependencies from the cached dependencies database. First
            update cache if necessary. '''
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
        from qualitylib import metric_source
        pom = self.__project.metric_source(metric_source.Pom)
        if not pom:
            logging.warning('No pom retriever defined.')
            return set()
        svn_path = self.svn_path(version)
        try:
            return pom.dependencies(svn_path, self.__project.products())
        except urllib2.HTTPError, reason:
            logging.warn("Couldn't retrieve dependencies for %s: %s",
                          self.product_label(), reason)
            return set()
        except (ValueError, IndexError), reason:
            logging.error("Couldn't parse dependencies for %s: %s",
                          self.product_label(), reason)
            if user:
                logging.error('User of %s is %s', self.product_label(),
                              user.product_label())
            raise
