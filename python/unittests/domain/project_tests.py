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


class FakeProduct(object):
    ''' Fake the product class for unit test purposes. '''
    def __init__(self):
        self.__version = None
        self.__branch = None

    @staticmethod
    def name():
        ''' Return the name of the product. '''
        return 'FakeProduct'

    def product_version(self):
        ''' Return the product version. '''
        return self.__version

    def product_branch(self):
        ''' Return the product branch. '''
        return self.__branch

    def set_product_branch(self, branch):
        ''' Set the product branch. '''
        self.__branch = branch

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
        self.__project = domain.Project('Organization', name='Project Name')

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

    def test_add_trunk_product(self):
        ''' Test that a product without a specific version won't be added to the
            project. '''
        product = FakeProduct()
        self.__project.add_product(product)
        self.failIf(self.__project.add_product_with_version('FakeProduct', ''))
        self.assertEqual([product], self.__project.products())

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

    def test_add_branch_without_branch(self):
        ''' Test that a product without a specific branch won't be added to the
            project. '''
        product = FakeProduct()
        self.__project.add_product(product)
        self.failIf(self.__project.add_product_with_branch('FakeProduct', ''))
        self.assertEqual([product], self.__project.products())

    def test_add_branch_to_missing_product(self):
        # pylint: disable=invalid-name
        ''' Test that adding a branch for a missing product fails silently. '''
        self.__project.add_product(FakeProduct())
        self.__project.add_product_with_branch('Missing product', 'branch')

    def test_add_branch(self):
        ''' Test that adding a branch for an existing product works. '''
        trunk = self.__project.add_product(FakeProduct())
        branch = self.__project.add_product_with_branch('FakeProduct', 'branch')
        self.assertEqual([trunk, branch], self.__project.products())

    def test_add_existing_branch(self):
        ''' Test that adding an existing branch does nothing. '''
        trunk = self.__project.add_product(FakeProduct())
        branch = self.__project.add_product_with_branch('FakeProduct', 'branch')
        self.failIf(self.__project.add_product_with_branch('FakeProduct',
                                                           'branch'))
        self.assertEqual([trunk, branch], self.__project.products())

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

    def test_add_document(self):
        ''' Test that a document can be added to the project. '''
        document = domain.Document(name='Title')
        self.__project.add_document(document)
        self.failUnless(document in self.__project.documents())

    def test_streets(self):
        ''' Test that a project has development streets. '''
        self.__project.add_street(domain.Street('A.*', name='A'))
        self.__project.add_street(domain.Street('B.*', name='B'))
        self.assertEqual([domain.Street('A.*', name='A'),
                          domain.Street('B.*', name='B')],
                         self.__project.streets())

    def test_unknown_metric_source(self):
        ''' Test that the project returns None for an unknown metric source
            class. '''
        self.failIf(self.__project.metric_source(self.__class__))

    def test_known_metric_source(self):
        ''' Test that the project returns the instance of a known metric
            source class. '''
        project = domain.Project(metric_sources={''.__class__: 'metric_source'})
        self.assertEqual('metric_source', project.metric_source(''.__class__))


class FakeResource(object):
    ''' Class to fake resources such as metric sources. '''
    def __init__(self, name='FakeResource'):
        self.__name = name

    @staticmethod
    def url():
        ''' Return a fake url. '''
        return 'http://resource'

    def name(self):
        ''' Return the name of the resource. '''
        return self.__name


class ProjectResourcesTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Test case for the Project.project_resources() method. '''

    @staticmethod
    def project(**kwargs):
        ''' Create a project with a default organization and project name and
            the passed keyword arguments. '''
        return domain.Project('Organization', name='Project', **kwargs)

    def test_default_resources(self):
        ''' Test that the project has no resources by default. '''
        self.failIf(self.project().project_resources())

    def test_wiki(self):
        ''' Test that the wiki is in the project resources. '''
        wiki = FakeResource('Wiki')
        project = self.project(metric_sources={metric_source.Wiki: wiki})
        self.failUnless((wiki.name(), wiki.url()) in \
                        project.project_resources())

    def test_jira(self):
        ''' Test that Jira is in the project resources. '''
        jira = metric_source.Jira('url', '', '')
        project = self.project(metric_sources={metric_source.Jira: jira})
        self.failUnless(('Jira', 'url') in project.project_resources())

    def test_build_server(self):
        ''' Test that build server is in the project resources. '''
        jenkins = metric_source.Jenkins('url', '', '')
        project = self.project(metric_sources={metric_source.Jenkins: jenkins})
        self.failUnless(('Jenkins build server', 'url') in \
                        project.project_resources())

    def test_sonar(self):
        ''' Test that Sonar is in the project resources. '''
        sonar = metric_source.Sonar('url')
        project = domain.Project('', name='', 
            metric_sources={metric_source.Sonar: sonar})
        self.failUnless(('SonarQube', 'url') in project.project_resources())

    def test_birt(self):
        ''' Test that Birt is in the project resources. '''
        birt = FakeResource('Birt reports')
        project = self.project(metric_sources={metric_source.Birt: birt})
        self.failUnless(('Birt reports', birt.url()) in 
                        project.project_resources())

    def test_trello_risk_log(self):
        ''' Test that the Trello risk log board is in the project resources. '''
        trello_risk_board = FakeResource('Trello risico log')
        project = self.project(
            metric_sources={metric_source.TrelloRiskBoard: trello_risk_board})
        self.failUnless((trello_risk_board.name(), trello_risk_board.url()) in
                        project.project_resources())

    def test_trello_actions(self):
        ''' Test that the Trello actions board is in the project resources. '''
        actions = FakeResource('Trello acties')
        project = self.project(
            metric_sources={metric_source.TrelloActionsBoard: actions})
        self.failUnless((actions.name(), actions.url()) in
                        project.project_resources())

    def test_performance_report(self):
        ''' Test that the performance report is in the project resources. '''
        performance_report = FakeResource('Performance reports')
        project = self.project(metric_sources={metric_source.PerformanceReport:
                                               performance_report})
        self.failUnless((performance_report.name(), performance_report.url()) in
                         project.project_resources())

    def test_emma(self):
        ''' Test that the Emma reports are in the project resources. '''
        emma = metric_source.Emma('http://emma/%s', '', '')
        project = self.project(metric_sources={metric_source.Emma: emma})
        product = domain.Product(project, 'Short name',
                                 metric_source_ids={emma: 'emma_id'})
        project.add_product(product)
        url = emma.get_coverage_url('emma_id')
        self.failUnless(('Emma coverage report %s' % product.name(), url) in
                         project.project_resources())

    def test_emma_only_for_trunk(self):
        ''' Test that only the Emma reports for trunk versions of products
            are included. '''
        emma = metric_source.Emma('http://emma/%s', '', '')
        project = self.project(metric_sources={metric_source.Emma: emma})
        product = domain.Product(project, 'Short name',
                                 metric_source_ids={emma: 'emma_id'})
        project.add_product(product)
        project.add_product_with_version(product.name(), '1.1')
        url = emma.get_coverage_url('emma_id')
        self.failUnless(('Emma coverage report %s' % product.name(), url) in
                         project.project_resources())

    def test_jacoco(self):
        ''' Test that the JacCoCo reports are in the project resources. '''
        jacoco = metric_source.JaCoCo('http://jacoco/%s', '', '')
        project = self.project(metric_sources={metric_source.JaCoCo: jacoco})
        product = domain.Product(project, 'Short name',
                                 metric_source_ids={jacoco: 'jacoco_id'})
        project.add_product(product)
        url = jacoco.get_coverage_url('jacoco_id')
        self.failUnless(('JaCoCo coverage report %s' % product.name(), url) in 
                         project.project_resources())

    def test_jacoco_only_for_trunk(self):
        ''' Test that only the JaCoCo reports for trunk versions of products
            are included. '''
        jacoco = metric_source.JaCoCo('http://jacoco/%s', '', '')
        project = self.project(metric_sources={metric_source.JaCoCo: jacoco})
        product = domain.Product(project, 'Short name',
                                 metric_source_ids={jacoco: 'jacoco_id'})
        project.add_product(product)
        project.add_product_with_version(product.name(), '1.1')
        url = jacoco.get_coverage_url('jacoco_id')
        self.failUnless(('JaCoCo coverage report %s' % product.name(), url) in 
                         project.project_resources())

    def test_release_candidates(self):
        ''' Test that the release candidates file is in the project 
            resources. '''
        release_candidates = FakeResource('Release kandidaten')
        project = self.project(metric_sources={metric_source.ReleaseCandidates:
                                               release_candidates})
        self.failUnless((release_candidates.name(), release_candidates.url()) in
                         project.project_resources())

    def test_release_archive(self):
        ''' Test that the release archive is in the project resources. '''
        project = self.project()
        team = domain.Team(name='A', release_archives=[FakeResource()])
        project.add_team(team)
        self.failUnless(('Release archief team A', FakeResource().url()) in
                         project.project_resources())

    def test_repository(self):
        ''' Test that the source code repository is in the project 
            resources. '''
        subversion = metric_source.Subversion()
        project = self.project(metric_sources={
                                   metric_source.Subversion: subversion})
        svn_url = 'http://svn/product/trunk/'
        product = domain.Product(project, name='Name',
                                 metric_source_ids={subversion: svn_url})
        project.add_product(product)
        self.failUnless(('Broncode repository Name', 
                         svn_url) in project.project_resources())

    def test_repositories(self):
        ''' Test that the source code repositories are in the project 
            resources. '''
        subversion = metric_source.Subversion()
        project = self.project(metric_sources={
                                   metric_source.Subversion: subversion})
        for index in range(1, 4):
            product = domain.Product(project, name='Product %d' % index, 
                metric_source_ids={subversion: 
                                   'https://svn/product%d/trunk/' % index})
            if index == 3:
                product.set_product_version('1.1')
            project.add_product(product)
        resources = project.project_resources()
        self.failUnless(('Broncode repository Product 1', 
                         'https://svn/product1/trunk/') in resources)
        self.failUnless(('Broncode repository Product 2',
                         'https://svn/product2/trunk/') in resources)

    def test_additional_resources(self):
        ''' Test that additional resources can be added to the project
            resources. '''
        project = self.project(additional_resources=[
            domain.MetricSource(name='Resource', url='http://url')])
        resources = project.project_resources()
        self.failUnless(('Resource', 'http://url') in resources)
