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

from qualitylib import domain
import unittest


class FakeProduct(object):
    ''' Fake the product class for unit test purposes. '''
    def __init__(self):
        self.__version = None

    @staticmethod
    def name():
        ''' Return the name of the product. '''
        return 'FakeProduct'

    def product_version(self):
        ''' Return the product version. '''
        return self.__version

    def set_product_version(self, version):
        ''' Set the product version. '''
        self.__version = version

    @staticmethod
    def dependencies(recursive=False):  # pylint: disable=unused-argument
        ''' Return a set of dependent products. '''
        return set([FakeProduct()])


class ProjectTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Test case for the Project domain class. '''

    def setUp(self):  # pylint: disable=C0103
        self.__project = domain.Project('Organization', 'Project Name')

    def test_name(self):
        ''' Test that the project has the correct name. '''
        self.assertEqual('Project Name', self.__project.name())

    def test_organization(self):
        ''' Test that the project has the correct organization. '''
        self.assertEqual('Organization', self.__project.organization())

    def test_products(self):
        ''' Test that a newly created project has no products. '''
        self.failIf(self.__project.products())

    def test_add_product(self):
        ''' Test that a product can be added to the project. '''
        product = FakeProduct()
        self.__project.add_product(product)
        self.assertEqual([product], self.__project.products())

    def test_add_product_with_version(self):
        ''' Test that a product with a specific version can be added to the 
            project. '''
        product = FakeProduct()
        self.__project.add_product(product)
        product1_1 = self.__project.add_product_with_version('FakeProduct', 
                                                             '1.1')
        self.assertEqual([product, product1_1], self.__project.products())

    def test_add_product_with_version_twice(self): 
        # pylint: disable=invalid-name
        ''' Test that adding a product/version twice is not possible. '''
        product = FakeProduct()
        self.__project.add_product(product)
        product1_1 = self.__project.add_product_with_version('FakeProduct', 
                                                             '1.1')
        self.__project.add_product_with_version('FakeProduct', '1.1')
        self.assertEqual([product, product1_1], self.__project.products())

    def test_add_version_to_missing_product(self):
        # pylint: disable=invalid-name
        ''' Test that adding a version for a missing product fails silently. '''
        self.__project.add_product(FakeProduct())
        self.__project.add_product_with_version('Missing product', '1.1')

    def test_get_product(self):
        ''' Test that an added product can be found. '''
        product = FakeProduct()
        self.__project.add_product(product)
        self.assertEqual(product, self.__project.get_product('FakeProduct'))

    def test_get_missing_product(self):
        ''' Test that a product that hasn't been added can't be found. '''
        self.__project.add_product(FakeProduct())
        self.failIf(self.__project.get_product('Missing product'))

    def test_product_dependencies(self):
        ''' Test collecting the dependencies of products. '''
        self.__project.add_product(FakeProduct())
        self.assertEqual(1, len(self.__project.product_dependencies()))

    def test_teams(self):
        ''' Test that a newly created project has no teams. '''
        self.failIf(self.__project.teams())

    def test_add_team(self):
        ''' Test that a team can be added to the project. '''
        self.__project.add_team('Team')
        self.assertEqual(['Team'], self.__project.teams())

    def test_add_responsible_team(self):
        ''' Test that a team can be added to the project as responsible 
            team. '''
        self.__project.add_team('Responsible team', responsible=True)
        self.assertEqual(['Responsible team'], 
                         self.__project.responsible_teams())

    def test_dashboard(self):
        ''' Test that a dashboard can be set. '''
        self.__project.set_dashboard([1, 2], [3, 4])
        self.assertEqual(([1, 2], [3, 4]), self.__project.dashboard())

    def test_analyse_products_without_sonar(self):
        # pylint: disable=invalid-name
        ''' Test that analyse products doesn't do anything when no Sonar is
            present. '''
        self.__project.analyse_products()

    def test_analyse_products_with_sonar(self):
        # pylint: disable=invalid-name
        ''' Test that the project delegates analysing products to Sonar. '''

        class FakeSonar(object):  # pylint: disable=too-few-public-methods
            ''' Fake Sonar for this unit test. '''
            def __init__(self):
                self.products_analysed = []

            def analyse_products(self, products):
                ''' Keep a reference to the products to analyse. '''
                self.products_analysed = products

        sonar = FakeSonar()
        project = domain.Project('Organization', 'Project name', sonar=sonar)
        project.add_product(FakeProduct())
        project.analyse_products()
        self.failUnless(sonar.products_analysed)

    def test_add_document(self):
        ''' Test that a document can be added to the project. '''
        document = domain.Document('Title')
        self.__project.add_document(document)
        self.failUnless(document in self.__project.documents())

    def test_streets(self):
        ''' Test that a project has development streets. '''
        self.__project.add_street(domain.Street('A', 'A.*'))
        self.__project.add_street(domain.Street('B', 'B.*'))
        self.assertEqual([domain.Street('A', 'A.*'), domain.Street('B', 'B.*')],
                         self.__project.streets())


class FakeResource(object):
    ''' Class to fake resources such as metric sources. '''
    @staticmethod
    def url():
        ''' Return a fake url. '''
        return 'http://resource'

    @staticmethod
    def get_coverage_url(product):
        ''' Return a fake coverage url. '''
        return 'http://cov/%s' % product


class ProjectResourcesTest(unittest.TestCase):  
    # pylint: disable=too-many-public-methods
    ''' Test case for the Project.project_resources() method. '''

    @staticmethod
    def project(**kwargs):
        ''' Create a project with a default organization and project name and
            the passed keyword arguments. '''
        return domain.Project('Organization', 'Project', **kwargs)

    def test_default_resources(self):
        ''' Test that the project has only missing resources by default. '''
        for resource in self.project().project_resources():
            self.assertEqual(None, resource[1])

    def test_wiki(self):
        ''' Test that the wiki is in the project resources. '''
        self.failUnless(('Wiki', FakeResource().url()) in
            self.project(wiki=FakeResource()).project_resources())

    def test_jira(self):
        ''' Test that Jira is in the project resources. '''
        self.failUnless(('Jira', FakeResource().url()) in
            domain.Project('Organization', 'Project name', 
                           jira=FakeResource()).project_resources())

    def test_build_server(self):
        ''' Test that build server is in the project resources. '''
        self.failUnless(('Build server', FakeResource().url()) in 
            domain.Project('Organization', 'Project name',
                           build_server=FakeResource()).project_resources())

    def test_sonar(self):
        ''' Test that Sonar is in the project resources. '''
        self.failUnless(('Sonar', FakeResource().url()) in
            domain.Project('', '', sonar=FakeResource()).project_resources())

    def test_birt(self):
        ''' Test that Birt is in the project resources. '''
        self.failUnless(('Birt reports', FakeResource().url()) in 
            self.project(birt=FakeResource()).project_resources())

    def test_trello_risk_log(self):
        ''' Test that the Trello risk log board is in the project resources. '''
        project = self.project(trello_risklog_board=FakeResource())
        self.failUnless(('Trello risico log', FakeResource().url()) in
                         project.project_resources())

    def test_trello_actions(self):
        ''' Test that the Trello actions board is in the project resources. '''
        project = self.project(trello_actions_board=FakeResource())
        self.failUnless(('Trello acties', FakeResource().url()) in
                         project.project_resources())

    def test_performance_report(self):
        ''' Test that the performance report is in the project resources. '''
        project = self.project(performance_report=FakeResource())
        self.failUnless(('Performance reports', FakeResource().url()) in
                         project.project_resources())

    def test_emma(self):
        ''' Test that the Emma reports are in the project resources. '''
        project = self.project(emma=FakeResource())
        product = domain.Product(project, 'Short name', 'Sonar id', 
                                 art_coverage_emma_id='emma_id')
        project.add_product(product)
        url = FakeResource.get_coverage_url(product.art_coverage_emma())
        self.failUnless(('Emma coverage report %s' % product.name(), url) in
                         project.project_resources())

    def test_emma_only_for_trunk(self):
        ''' Test that only the Emma reports for trunk versions of products
            are included. '''
        project = self.project(emma=FakeResource())
        product = domain.Product(project, 'Short name', 'Sonar id', 
                                 art_coverage_emma_id='emma_id')
        project.add_product(product)
        project.add_product_with_version(product.name(), '1.1')
        url = FakeResource.get_coverage_url(product.art_coverage_emma())
        self.failUnless(('Emma coverage report %s' % product.name(), url) in
                         project.project_resources())

    def test_jacoco(self):
        ''' Test that the JacCoCo reports are in the project resources. '''
        project = self.project(jacoco=FakeResource())
        product = domain.Product(project, 'Short name', 'Sonar id', 
                                 art_coverage_jacoco_id='jacoco_id')
        project.add_product(product)
        url = FakeResource.get_coverage_url(product.art_coverage_jacoco())
        self.failUnless(('JaCoCo coverage report %s' % product.name(), url) in 
                         project.project_resources())

    def test_jacoco_only_for_trunk(self):
        ''' Test that only the JaCoCo reports for trunk versions of products
            are included. '''
        project = self.project(jacoco=FakeResource())
        product = domain.Product(project, 'Short name', 'Sonar id', 
                                 art_coverage_jacoco_id='jacoco_id')
        project.add_product(product)
        project.add_product_with_version(product.name(), '1.1')
        url = FakeResource.get_coverage_url(product.art_coverage_jacoco())
        self.failUnless(('JaCoCo coverage report %s' % product.name(), url) in 
                         project.project_resources())

    def test_javamelody(self):
        ''' Test that JavaMelody is in the project resources. '''
        project = self.project(javamelody=FakeResource())
        self.failUnless(('JavaMelody', FakeResource().url()) in
                         project.project_resources())

    def test_release_candidates(self):
        ''' Test that the release candidates file is in the project 
            resources. '''
        project = self.project(release_candidates=FakeResource())
        self.failUnless(('Release kandidaten', FakeResource().url()) in
                         project.project_resources())

    def test_release_archive(self):
        ''' Test that the release archive is in the project resources. '''
        project = self.project(release_archives=[FakeResource()])
        self.failUnless(('Release archief', FakeResource().url()) in
                         project.project_resources())

    def test_repository(self):
        ''' Test that the source code repository is in the project 
            resources. '''
        project = self.project()
        product = domain.Product(project, 'Short name', 'Sonar id',
                                 svn_path='https://svn/product')
        project.add_product(product)
        self.failUnless(('Broncode repository Sonar id', 
                         'https://svn/product') in project.project_resources())

    def test_repositories(self):
        ''' Test that the source code repositories are in the project 
            resources. '''
        project = self.project()
        for index in range(1, 4):
            product = domain.Product(project, 'Short name', 
                                     'Sonar id %d' % index,
                                     svn_path='https://svn/product%d' % index)
            if index == 3:
                product.set_product_version('1.1')
            project.add_product(product)
        resources = project.project_resources()
        self.failUnless(('Broncode repository Sonar id 1', 
                         'https://svn/product1') in resources)
        self.failUnless(('Broncode repository Sonar id 2',
                         'https://svn/product2') in resources)

    def test_additional_resources(self):
        ''' Test that additional resources can be added to the project
            resources. '''
        project = self.project(additional_resources=[dict(title='Resource', 
                                                          url='http://url')])
        resources = project.project_resources()
        self.failUnless(('Resource', 'http://url') in resources)
