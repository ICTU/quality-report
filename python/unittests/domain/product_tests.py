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

from qualitylib import domain, metric_source
import unittest


class FakeSonar(object):  # pylint: disable=too-few-public-methods
    ''' Fake a Sonar instance. '''
    pass


class FakeBirt(object):  # pylint: disable=too-few-public-methods
    ''' Fake Birt so we can return whether a product has a test design. '''
    pass


class FakeSubversion(object):
    ''' Fake a Subversion repository. '''
    @staticmethod
    def latest_tagged_product_version(svn_path):  
        # pylint: disable=unused-argument
        ''' Return the latest tagged product version from Subversion. '''
        return '1.1'

    @staticmethod
    def last_changed_date(svn_path):  # pylint: disable=unused-argument
        ''' Return the date the product was last changed. '''
        return 'yesterday'


class FakePom(object):  # pylint: disable=too-few-public-methods
    ''' Fake a pom file. '''
    @staticmethod  # pylint: disable=unused-argument
    def dependencies(*args):
        ''' Return a set of fake dependencies. '''
        return set([('product', domain.Product(domain.Project()))])


class FakeDependenciesDb(object):
    ''' Fake a dependencies database. '''
    @staticmethod  # pylint: disable=unused-argument
    def has_dependencies(*args):
        ''' Return whether the database has cached dependencies. '''
        return False

    @staticmethod
    def set_dependencies(*args):
        ''' Fake adding new dependencies to the database. '''
        pass

    save = set_dependencies

    @staticmethod  # pylint: disable=unused-argument
    def get_dependencies(*args):
        ''' Fake results. '''
        return set()


class ProductTest(unittest.TestCase):  # pylint: disable=too-many-public-methods
    '''Unit tests for the Product domain class. '''
    def setUp(self):  # pylint: disable=invalid-name
        self.__sonar = FakeSonar()
        self.__project = domain.Project('Organization',
            metric_sources={metric_source.Sonar: self.__sonar})
        self.__product = domain.Product(self.__project, name='Product',
            metric_source_ids={self.__sonar: 'sonar:id'},
            old_metric_source_ids={self.__sonar: {'old.version':
                                                  'old-sonar:id'}})

    def test_product_name(self):
        ''' Test that the name of the product equals given name. '''
        self.assertEqual('Product', self.__product.name())

    def test_sonar_id(self):
        ''' Test that the Sonar id of the product equals the passed id. '''
        self.assertEqual('sonar:id', self.__product.sonar_id())

    def test_sonar_id_with_version(self):
        ''' Test that the Sonar id includes the version for released 
            products. '''
        self.__product.set_product_version('1.2.3')
        self.assertEqual('sonar:id:1.2.3', self.__product.sonar_id())

    def test_sonar_id_with_branch(self):
        ''' Test that the Sonar id includes the branch for branch products. '''
        self.__product.set_product_branch('product-branch')
        self.assertEqual('sonar:id:product-branch', self.__product.sonar_id())

    def test_old_sonar_id(self):
        ''' Test that the Sonar id for an old version can be different. '''
        self.__product.set_product_version('old.version')
        self.assertEqual('old-sonar:id:old.version', self.__product.sonar_id())

    def test_trunk_without_dependencies(self):
        ''' Test that the product dependencies set is empty if the product has
            no dependencies. '''
        self.assertEqual(set(), self.__product.dependencies())

    def test_one_unknown_dependency(self):
        ''' Test that the product has no dependencies when the dependency
            returned by the pom file is not in the project. '''
        project = domain.Project('Organization',
                                 metric_sources={metric_source.Pom: FakePom()})
        product = domain.Product(project)
        self.failIf(product.dependencies())

    def test_version_without_dependencies(self):
        ''' Test a product version without dependencies. '''
        project = domain.Project('Organization',
            metric_sources={metric_source.Dependencies: FakeDependenciesDb()})
        product = domain.Product(project)
        self.failIf(product.dependencies(version='1.1'))

    def test_version_type_trunk(self):
        ''' Test that the product version type of a product without version
            is trunk. '''
        self.assertEqual('trunk', self.__product.product_version_type())

    def test_version_type_tag(self):
        ''' Test that the product version type of a tagged product is tag. '''
        self.__product.set_product_version('1.1')
        self.assertEqual('tag', self.__product.product_version_type())

    def test_version_type_release(self):
        ''' Test that the product version type of a product to be released
            is release. '''
        class FakeReleaseCandidates(object):
            # pylint: disable=too-few-public-methods,incomplete-protocol
            ''' Fake a release candidates metric source. '''
            @staticmethod
            def release_candidate(item):  # pylint: disable=unused-argument
                ''' Return the release candidate version number. '''
                return '1.1'

        release_candidates = FakeReleaseCandidates()
        project = domain.Project('Organization',
            metric_sources={metric_source.ReleaseCandidates:
                            release_candidates})
        product = domain.Product(project,
                                 metric_source_ids={release_candidates: 'P'})
        product.set_product_version('1.1')
        self.assertEqual('release', product.product_version_type())

    def test_latest_released_product_version(self):
        ''' Test that the latest release product version is retrieved from
            Subversion. '''
        subversion = FakeSubversion()
        project = domain.Project('Organization',
            metric_sources={metric_source.Subversion: subversion})
        product = domain.Product(project,
                                 metric_source_ids={subversion: 'http://svn/'})
        self.assertEqual('1.1', product.latest_released_product_version())

    def test_latest_release_product_version_without_svn_path(self):
        ''' Test that a product without Subversion path doesn't have a latest
            released product version. '''
        self.assertEqual('', self.__product.latest_released_product_version())

    def test_trunk_is_not_latest_release(self):
        ''' Test that the trunk version of a product is not the latest 
            release. '''
        self.failIf(self.__product.is_latest_release())

    def test_is_latest_release(self):
        ''' Test that the product is the latest release if its product version
            is the same as the latest release returned by Subversion. '''
        subversion = FakeSubversion()
        project = domain.Project('Organization',
            metric_sources={metric_source.Subversion: subversion})
        product = domain.Product(project,
                                 metric_source_ids={subversion: 'http://svn/'})
        product.set_product_version('1.1')
        self.failUnless(product.is_latest_release())

    def test_last_changed_date(self):
        ''' Test that the date the product was last changed is the date
            reported by Subversion. '''
        subversion = FakeSubversion()
        project = domain.Project('Organization',
            metric_sources={metric_source.Subversion: subversion})
        product = domain.Product(project,
                                 metric_source_ids={subversion: 'http://svn/'})
        self.assertEqual(subversion.last_changed_date('http://svn'),
                         product.last_changed_date())

    def test_responsible_teams(self):
        ''' Test that the product has no responsible teams by default. '''
        self.assertEqual([], self.__product.responsible_teams())

    def test_set_responsible_team(self):
        ''' Test that the responsible teams can be set. '''
        product = domain.Product(domain.Project(), 
                                 responsible_teams=['Team'])
        self.assertEqual(['Team'], product.responsible_teams())

    def test_project_responsible_teams(self):
        ''' Test that the project's responsible teams are used if no
            responsible teams have been set for the product. '''
        project = domain.Project()
        project.add_team('Team', responsible=True)
        product = domain.Product(project)
        self.assertEqual(['Team'], product.responsible_teams())

    def test_default_unittests(self):
        ''' Test that products have no unit test component by default. '''
        self.failIf(self.__product.unittests())

    def test_unittests(self):
        ''' Test that the unit test component can be retrieved. '''
        unittests = domain.Product(self.__project)
        product = domain.Product(self.__project, unittests=unittests)
        self.assertEqual(unittests, product.unittests())

    def test_unittests_have_product_version(self):
        ''' Test that the unit test component has the same version as the
            product it belongs to. '''
        unittests = domain.Product(self.__project)
        product = domain.Product(self.__project, unittests=unittests)
        product.set_product_version('1.1')
        self.assertEqual('1.1', product.unittests().product_version())

    def test_default_jsf(self):
        ''' Test that products have no jsf component by default. '''
        self.failIf(self.__product.jsf())

    def test_jsf(self):
        ''' Test that the jsf component can be retrieved. '''
        jsf = domain.Product(self.__project)
        self.assertEqual(jsf, domain.Product(self.__project, jsf=jsf).jsf())

    def test_jsf_has_product_version(self):
        ''' Test that the jsf has the same version as the product it belongs
            to. '''
        jsf = domain.Product(self.__project)
        product = domain.Product(self.__project, jsf=jsf)
        product.set_product_version('1.1')
        self.assertEqual('1.1', product.jsf().product_version())

    def test_default_art(self):
        ''' Test that products have no automated regression test by default. '''
        self.failIf(self.__product.art())

    def test_art(self):
        ''' Test that the automated regression test can be retrieved. '''
        art = domain.Product(self.__project)
        self.assertEqual(art, domain.Product(self.__project, art=art).art())

    def test_art_has_product_version(self):
        ''' Test that the automated regression test has the same version as the
            product it belongs to. '''
        art = domain.Product(self.__project)
        product = domain.Product(self.__project, art=art)
        product.set_product_version('1.1')
        self.assertEqual('1.1', product.art().product_version())
