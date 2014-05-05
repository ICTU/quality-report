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

from qualitylib.metric_source import beautifulsoup
from qualitylib import utils
import logging
import urllib2


class Pom(beautifulsoup.BeautifulSoupOpener):
    ''' Class representing Maven pom.xml files. '''

    def __init__(self, *args, **kwargs):
        self.__maven_binary = kwargs.pop('maven_binary', 'mvn')
        super(Pom, self).__init__(*args, **kwargs)

    @utils.memoized
    def dependencies(self, url, products, parent_pom_properties=None):
        ''' Return a set of dependencies defined in the pom file. '''
        if not url:
            return set()
        try:
            pom_soup = self.__get_pom_soup(url)
        except urllib2.HTTPError:
            return set()
        properties = self.__get_properties(pom_soup, parent_pom_properties)
        dependencies = self.__artifacts(pom_soup, url, properties, products)
        dependencies.update(self.__module_dependencies(pom_soup, url, products,
            properties))
        return dependencies

    @utils.memoized
    def modules(self, url):
        ''' Return the modules defined in the pom file, recursively. '''
        if not url:
            return set()
        pom_soup = self.__get_pom_soup(url, log_level=logging.ERROR)
        module_artifacts = set()
        for module in self.__get_modules(pom_soup):
            module_url = url + '/' + module
            artifact_id = self.soup(module_url + '/pom.xml').project.find('artifactid', recursive=False).string
            module_artifacts.add(artifact_id)
            module_artifacts.update(self.modules(module_url))
        return module_artifacts

    @classmethod
    def __artifacts(cls, pom_soup, url, properties, products):
        ''' Return the artifacts from the dependency tag. '''
        dependencies = set()
        for dependency_tag in pom_soup('dependency'):
            try:
                scope = dependency_tag('scope')[0].string
                if scope != 'compiled':
                    continue
            except IndexError:
                pass  # No explicit scope
            artifact = cls.__artifact(dependency_tag, products)
            if not artifact:
                continue
            version = cls.__version(dependency_tag, url, properties)
            if not version:
                continue
            if 'SNAPSHOT' in version:
                continue
            dependencies.add((artifact, version))
        return dependencies

    @staticmethod
    def __artifact(dependency_tag, products):
        ''' Parse the artifact name from the dependency tag. '''
        artifact_name = dependency_tag('artifactid')[0].string
        for product in products:
            if product.has_artifact(artifact_name):
                return product.sonar_id().split(':')[1]

    @staticmethod
    def __version(dependency_tag, url, properties):
        ''' Parse the version from the dependency tag. '''
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
        ''' Return the dependencies of the modules in this pom. '''
        module_dependencies = set()
        for module in self.__get_modules(pom_soup):
            module_url = url + '/' + module
            module_dependencies.update(self.dependencies(module_url, products,
                properties))
        return module_dependencies

    @classmethod
    def __get_properties(cls, pom_soup, parent_pom_properties=None):
        ''' Return a dictionary of properties defined in the pom file. '''
        properties = parent_pom_properties or dict()
        properties_tags = pom_soup('properties')
        if properties_tags:
            for property_tag in properties_tags[0]:
                try:
                    properties[property_tag.name] = property_tag.string.strip()
                except AttributeError:
                    pass  # Whitespace or Comment
        try:
            properties['project.version'] = properties['version'] = \
                pom_soup('version')[0].string.strip()
        except IndexError:
            pass  # Ignore, deprecated way of referring to version
        cls.__resolve_properties(properties)
        return properties

    @staticmethod
    def __resolve_properties(properties):
        ''' Resolve properties that use other properties as value. '''
        resolved_properties = dict()
        for property_tag, value in properties.items():
            if value and '${' in value:
                # Create a python string template
                templated_value = value.replace('${', '%(').replace('}', ')s')
                try:
                    resolved_value = templated_value % properties
                    resolved_properties[property_tag] = resolved_value
                except KeyError:
                    logging.warn("Couldn't resolve property %s: %s", 
                                 property_tag, value)
        properties.update(resolved_properties)

    @staticmethod
    def __get_modules(pom_soup):
        ''' Return a set of modules defined in the pom file. '''
        modules = set()
        for module_tag in pom_soup('module'):
            modules.add(module_tag.string)
        return modules

    def __get_pom_soup(self, url, log_level=logging.WARNING):
        ''' Return the soup version of the pom. '''
        pom_url = url + '/pom.xml'
        try:
            return self.soup(pom_url)
        except urllib2.HTTPError, reason:
            logging.log(log_level, "Couldn't open %s: %s", pom_url, reason)
            raise

        '''
        with file('pom.xml', 'w') as pom_file: 
            pom_file.write(pom_contents)
            pom_file.close()
        os.system('%s help:effective-pom > effective-pom.xml' % self.__maven_binary)
        return BeautifulSoup(file('effective-pom.xml'))
        '''
