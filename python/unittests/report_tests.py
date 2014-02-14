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

import unittest
from qualitylib import report, domain


class FakeMetric(object):
    ''' Fake metric to use in the tests below. '''
    def __init__(self, status=''):
        self.__status = status
        
    def set_id_string(self, id_string):
        ''' Ignore. '''
        pass
    
    def status(self):
        ''' Return the preset status. '''
        return self.__status


class SectionHeaderTest(unittest.TestCase):  
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the section header class. '''
    
    def setUp(self):  # pylint: disable=invalid-name
        self.__header = report.SectionHeader('TE', 'title', 'subtitle')
        
    def test_title(self):
        ''' Test that the title is correct. '''
        self.assertEqual('title', self.__header.title())
        
    def test_subtitle(self):
        ''' Test that the subtitle is correct. '''
        self.assertEqual('subtitle', self.__header.subtitle())
        
    def test_id_prefix(self):
        ''' Test that the id prefix is correct. '''
        self.assertEqual('TE', self.__header.id_prefix())


class SectionTest(unittest.TestCase):    
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the section class. '''
    
    def setUp(self):  # pylint: disable=invalid-name
        self.__header = report.SectionHeader('TE', 'title', 'subtitle')
        self.__metrics = [FakeMetric('green'), FakeMetric('perfect'), 
                          FakeMetric('yellow'), FakeMetric('grey'),
                          FakeMetric('red')]
        self.__section = report.Section(self.__header, self.__metrics)
        
    def test_title(self):
        ''' Test that the title of the section is the title of the header. '''
        self.assertEqual(self.__header.title(), self.__section.title())
        
    def test_subtitle(self):
        ''' Test that the subtitle of the section is the subtitle of the 
            header. '''
        self.assertEqual(self.__header.subtitle(), self.__section.subtitle())
        
    def test_id_prefix(self):
        ''' Test that the id prefix of the section is the id prefix of the 
            header. '''
        self.assertEqual(self.__header.id_prefix(), self.__section.id_prefix())
        
    def test_str(self):
        ''' Test that str(section) returns the title of the section. '''
        self.assertEqual(self.__section.title(), str(self.__section))
        
    def test_get_metric(self):
        ''' Test that the section is a list of metrics. '''
        self.assertEqual(self.__metrics[0], self.__section[0])
        
    def test_get_all_metrics(self):
        ''' Test that the section has a list of all metrics. '''
        self.assertEqual(self.__metrics, self.__section.metrics())

    def test_color_red(self):
        ''' Test that the section is red when one metric is red. '''
        self.assertEqual('red', self.__section.color())

    def test_color_yellow(self):
        ''' Test that the section is yellow when no metrics are red and at
            least one is yellow. '''
        metrics = [FakeMetric('green'), FakeMetric('perfect'), 
                   FakeMetric('yellow'), FakeMetric('grey')]
        # Using self.__header makes this unit test fail occasionally in the
        # IDE. Don't understand why. 
        header = report.SectionHeader('TE', 'another title', 'subtitle')
        section = report.Section(header, metrics)
        self.assertEqual('yellow', section.color())
        
    def test_color_grey(self):
        ''' Test that the section is grey when no metrics are red or yellow and
            at least one is grey. '''
        metrics = [FakeMetric('green'), FakeMetric('perfect'), 
                   FakeMetric('grey')]
        section = report.Section(self.__header, metrics)
        self.assertEqual('grey', section.color())

    def test_color_green(self):
        ''' Test that the section is green when no metrics are red, yellow or
            grey. '''
        metrics = [FakeMetric('green'), FakeMetric('perfect')]
        section = report.Section(self.__header, metrics)
        self.assertEqual('green', section.color())
        
    def test_color_perfect(self):
        ''' Test that the section is green when all metrics are perfect. '''
        metrics = [FakeMetric('perfect')]
        section = report.Section(self.__header, metrics)
        self.assertEqual('green', section.color())

    def test_color_white(self):
        ''' Test that the section is white when it contains no metrics. '''
        section = report.Section(self.__header, [])
        self.assertEqual('white', section.color())

    def test_has_no_history(self):
        ''' Test that the section has no history unless its id prefix is MM
            (for Meta Metrics). '''
        self.failIf(self.__section.has_history())
        
    def test_has_history(self):
        ''' Test that the section has history when its id prefix is MM (for
            Meta Metrics). '''
        section = report.Section(report.SectionHeader('MM', 'title', 
                                                      'subtitle'), [])
        self.failUnless(section.has_history())
        
    def test_history(self):
        ''' Test that the section returns the history from the history metric 
            source. '''
        
        class FakeHistory(object):  # pylint: disable=too-few-public-methods
            ''' Fake the history metric source. '''
            @staticmethod
            def complete_history():
                ''' Return a fake history. '''
                return 'History'
            
        section = report.Section(None, [], history=FakeHistory())
        self.assertEqual('History', section.history())
        
    def test_product(self):
        ''' Test that the section returns the product. '''
        section = report.Section(None, [], product='Product')
        self.assertEqual('Product', section.product())
        
    def test_trunk_product(self):
        ''' Test that the section returns whether the product is a trunk 
            version. '''
        
        class FakeProduct(object):  # pylint: disable=too-few-public-methods
            ''' Fake a trunk product. '''
            @staticmethod
            def product_version():
                ''' Fake a trunk version. '''
                return
            
        section = report.Section(None, [], product=FakeProduct())
        self.failUnless(section.contains_trunk_product())
        
    def test_service(self):
        ''' Test that the section returns the service. '''
        section = report.Section(None, [], service='Service')
        self.assertEqual('Service', section.service())


class FakeSonar(object):  # pylint: disable=too-few-public-methods
    ''' Fake a Sonar instance. '''
    @staticmethod  # pylint: disable=unused-argument
    def version(*args):
        ''' Return the version number of the product. '''
        return '1'

    @staticmethod
    def url():
        ''' Return the Sonar url. '''
        return 'http://sonar'
    
    
class QualityReportTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the quality report class. '''
    
    def setUp(self):  # pylint: disable=invalid-name
        self.__project = domain.Project('organization', 'project title',
                                        sonar=FakeSonar())
        self.__report = report.QualityReport(self.__project)
        
    def test_title(self):
        ''' Test that the title of the report is equal to the title of the
            project. '''
        self.failUnless(self.__project.name() in self.__report.title())
        
    def test_sections(self):
        ''' Test that the report has one section, the meta metrics, by 
            default. '''
        self.assertEqual(1, len(self.__report.sections()))
        
    def test_product(self):
        ''' Test that the report has three sections when we add a product:
            one for overall product quality, one for the product itself and
            one for meta metrics. '''
        self.__project.add_product(domain.Product(self.__project, 'FP', 
                                                  'sonar.id'))
        self.assertEqual(3, 
                         len(report.QualityReport(self.__project).sections()))
        
    def test_get_product_section(self):
        ''' Test that the section for the product can be found. '''
        product = domain.Product(self.__project, 'FP', 'sonar.id')
        self.__project.add_product(product)
        quality_report = report.QualityReport(self.__project)
        section = quality_report.get_product_section(product.name(), 
                                                     product.product_version())
        self.assertEqual(product, section.product()) 
                         
    def test_service(self):
        ''' Test that the report has two sections when we add a service:
            one for the service itself and one for meta metrics. '''
        self.__project.add_service(domain.Service(self.__project, 'S1', 
                                                  'Service 1'))
        self.assertEqual(2, 
                         len(report.QualityReport(self.__project).sections()))

    def test_get_service_section(self):
        ''' Test that the section for the service can be found. '''
        service = domain.Service(self.__project, 'S1', 'Service 1')
        self.__project.add_service(service)
        quality_report = report.QualityReport(self.__project)
        section = quality_report.get_service_section(service)
        self.assertEqual(service, section.service())
        
    def test_team(self):
        ''' Test that the report has 2 sections when we add a team. '''
        team = domain.Team('Team')
        self.__project.add_team(team)
        quality_report = report.QualityReport(self.__project)
        self.assertEqual(2, len(quality_report.sections()))

    def test_resources(self):
        ''' Test that the report has project resources. '''
        quality_report = report.QualityReport(self.__project)
        self.failUnless(('Sonar', FakeSonar.url()) in 
                         quality_report.project_resources())
