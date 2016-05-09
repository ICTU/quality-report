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

import logging
import urllib2

from . import beautifulsoup
from .. import utils, domain, metric_info


class Pom(domain.MetricSource, beautifulsoup.BeautifulSoupOpener):
    """ Class representing Maven pom.xml files. """

    metric_source_name = 'Maven pom file'

    def __init__(self, *args, **kwargs):
        self.__sonar = kwargs.pop('sonar')
        self.__vcs = kwargs.pop('version_control_system')
        super(Pom, self).__init__(*args, **kwargs)

    @utils.memoized
    def dependencies(self, url, products, parent_pom_properties=None):
        """ Return a set of dependencies defined in the pom file. """
        if not url:
            return set()
        try:
            pom_soup = self.__get_pom_soup(url)
        except urllib2.HTTPError:
            return set()
        properties = self.__get_properties(pom_soup, parent_pom_properties)
        dependencies = self.__artifacts(pom_soup, url, properties, products)
        dependencies.update(self.__module_dependencies(pom_soup, url, products, properties))
        return dependencies

    @utils.memoized
    def modules(self, url):
        """ Return the modules defined in the pom file, recursively. """
        try:
            pom_soup = self.__get_pom_soup(url)
        except urllib2.HTTPError:
            return set()
        module_artifacts = set()
        for module in self.__get_modules(pom_soup):
            module_url = url + '/' + module + '/'
            try:
                module_pom_soup = self.__get_pom_soup(module_url)
            except urllib2.HTTPError:
                continue
            artifact_id = module_pom_soup.project.find('artifactid', recursive=False).string
            module_artifacts.add(artifact_id)
            module_artifacts.update(self.modules(module_url))
        return module_artifacts

    def __artifacts(self, pom_soup, url, properties, products):
        """ Return the artifacts from the dependency tag. """
        dependencies = set()
        for dependency_tag in pom_soup('dependency'):
            try:
                scope = dependency_tag('scope')[0].string
                if scope != 'compiled':
                    continue
            except IndexError:
                pass  # No explicit scope
            artifact = self.__artifact(dependency_tag, products)
            if not artifact:
                continue
            version = self.__version(dependency_tag, url, properties)
            if not version:
                continue
            if 'SNAPSHOT' in version:
                version = ''
            dependencies.add((artifact, version))
        return dependencies

    def __artifact(self, dependency_tag, products):
        """ Parse the artifact name from the dependency tag. """
        artifact_name = dependency_tag('artifactid')[0].string
        for product in products:
            if self.__product_has_artifact(product, artifact_name):
                return self.__product_sonar_id(product).split(':')[1]

    @utils.memoized
    def __product_has_artifact(self, product, artifact_id):
        """ Return whether the product has an artifact with artifact id. """
        sonar_id = self.__product_sonar_id(product)
        if not sonar_id:
            return False
        product_artifact_id = sonar_id.split(':')[1]
        if artifact_id == product_artifact_id:
            return True
        svn_path = self.__product_svn_path(product)
        if svn_path:
            for module in self.modules(svn_path):
                if artifact_id == module:
                    return True
        return False

    @staticmethod
    def __version(dependency_tag, url, properties):
        """ Parse the version from the dependency tag. """
        try:
            version = dependency_tag('version')[0].string
        except IndexError:
            version = ''
        if version.startswith('${'):  # Resolve properties
            try:
                version = properties[version[2:-1]]
            except KeyError:
                logging.warn("Couldn't resolve %s in %s", version, url)
                version = ''
        return version

    def __module_dependencies(self, pom_soup, url, products, properties):
        """ Return the dependencies of the modules in this pom. """
        module_dependencies = set()
        for module in self.__get_modules(pom_soup):
            module_url = url + '/' + module
            module_dependencies.update(self.dependencies(module_url, products, properties))
        return module_dependencies

    @classmethod
    def __get_properties(cls, pom_soup, parent_pom_properties=None):
        """ Return a dictionary of properties defined in the pom file. """
        properties = parent_pom_properties or dict()
        properties_tags = pom_soup('properties')
        if properties_tags:
            for property_tag in properties_tags[0]:
                try:
                    properties[property_tag.name] = property_tag.string.strip()
                except AttributeError:
                    pass  # Whitespace or Comment
        try:
            properties['project.version'] = properties['version'] = pom_soup('version')[0].string.strip()
        except IndexError:
            pass  # Ignore, deprecated way of referring to version
        cls.__resolve_properties(properties)
        return properties

    @staticmethod
    def __resolve_properties(properties):
        """ Resolve properties that use other properties as value. """
        resolved_properties = dict()
        for property_tag, value in properties.items():
            if value and '${' in value:
                # Create a python string template
                templated_value = value.replace('${', '%(').replace('}', ')s')
                try:
                    resolved_value = templated_value % properties
                    resolved_properties[property_tag] = resolved_value
                except KeyError:
                    logging.warn("Couldn't resolve property %s: %s", property_tag, value)
        properties.update(resolved_properties)

    @staticmethod
    def __get_modules(pom_soup):
        """ Return a set of modules defined in the pom file. """
        modules = set()
        for module_tag in pom_soup('module'):
            modules.add(module_tag.string)
        return modules

    def __get_pom_soup(self, url):
        """ Return the soup version of the pom. """
        pom_url = url + '/pom.xml'
        try:
            return self.soup(pom_url)
        except urllib2.HTTPError as reason:
            logging.warn("Couldn't open %s: %s", pom_url, reason)
            raise

    def __product_sonar_id(self, product):
        """ Return the product's Sonar id. """
        sonar_product_info = metric_info.SonarProductInfo(self.__sonar, product)
        return sonar_product_info.sonar_id()

    def __product_svn_path(self, product):
        """ Return the product's version control system path. """
        vcs_product_info = metric_info.VersionControlSystemProductInfo(
            self.__vcs if isinstance(self.__vcs, list) else [self.__vcs], product)
        return vcs_product_info.vcs_path()
