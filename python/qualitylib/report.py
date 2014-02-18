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

from qualitylib import metric, utils
import datetime


class SectionHeader(object):
    ''' Header for a section, consisting of two-letter prefix, title and an
        optional subtitle. '''
    def __init__(self, id_prefix, title, subtitle=''):
        self.__id_prefix = id_prefix
        self.__title = title
        self.__subtitle = subtitle

    def title(self):
        ''' Return the title of the section. '''
        return self.__title

    def subtitle(self):
        ''' Return the subtitle of the section. '''
        return self.__subtitle

    def id_prefix(self):
        ''' Return the id prefix of the section, a two letter string. '''
        return self.__id_prefix


# Section implements __getitem__ but not the complete Container protocol
# pylint: disable=incomplete-protocol

class Section(object):
    ''' Section within a report. '''

    def __init__(self, header, metrics, history=None, product=None, 
                 service=None):
        self.__header = header
        self.__metrics = metrics
        self.__history = history
        self.__product = product
        self.__service = service
        for index, each_metric in enumerate(self.__metrics):
            each_metric.set_id_string('%s-%d' % (self.__header.id_prefix(),
                                                 index + 1))

    def __str__(self):
        return self.title()

    def __getitem__(self, index):
        return self.__metrics[index]

    def title(self):
        ''' Return the title of this section. '''
        return self.__header.title()

    def subtitle(self):
        ''' Return the subtitle of this section. '''
        return self.__header.subtitle()

    def id_prefix(self):
        ''' Return the id prefix of this section, a two letter string. '''
        return self.__header.id_prefix()

    def metrics(self):
        ''' Return the metrics in this section. '''
        return self.__metrics

    @utils.memoized
    def color(self):
        ''' Return the color of this section. '''
        metric_statuses = set(each_metric.status() for each_metric in self)
        for status_color in ('red', 'yellow', 'grey', 'green', 'perfect'):
            if status_color in metric_statuses:
                color = status_color
                break
        else:
            color = 'white'
        if color == 'perfect':
            color = 'green'
        return color
         
    def has_history(self):
        ''' Return whether this section has history collected. '''
        return self.id_prefix() == 'MM'

    def history(self):
        ''' Return the history file contents. '''
        return self.__history.complete_history()

    def product(self):
        ''' Return the product this section is about. '''
        return self.__product

    def contains_trunk_product(self):
        ''' Return whether this section describes a trunk version of a
            product. '''
        return self.product() and not self.product().product_version()
    
    def service(self):
        ''' Return the service this section is about. '''
        return self.__service


class QualityReport(object):
    ''' Quality report on a project. '''

    def __init__(self, project):
        self.__project = project
        # All metrics need these sources:
        self.__metric_sources = dict(history=project.history(),
                                     wiki=project.wiki(),
                                     tasks=project.jira())
        self.__title = 'Kwaliteitsrapportage %s/%s' % (project.organization(), 
                                                       project.name())
        self.__products = sorted(project.products(),
                                 key=lambda product: (product.name(),
                                                      product.short_name()))
        self.__services = sorted(project.services(), 
                                 key=lambda service: service.name())
        self.__product_sections = dict()
        self.__service_sections = dict()
        self.__teams = sorted(project.teams(), key=str)
        self.__sections = []
        self.__meta_section = None
        self.__metrics = []

    def __str__(self):
        return self.__title

    def title(self):
        ''' Return the title of the quality report. '''
        return self.__title

    def project_resources(self):
        ''' Return the project resources. '''
        return self.__project.project_resources()
    
    @staticmethod
    def date():
        ''' Return the date and time the quality report was generated. '''
        return datetime.datetime.today()

    def sections(self):
        ''' Return the sections in the report. '''
        if not self.__sections:
            process_section = self.__process_section()
            if process_section:
                self.__sections.append(process_section)
            for service in self.__services:
                section = self.__service_section(service)
                self.__service_sections[service] = section
                self.__sections.append(section)
            if self.__products:
                self.__sections.append(self.__overall_products_section())
            for product in self.__products:
                section = self.__product_section(product)
                self.__product_sections[(product.name(),
                                         product.product_version())] = section
                self.__sections.append(section)
            for team in self.__teams:
                self.__sections.append(self.__team_section(team))
            self.__meta_section = self.__create_meta_section(self.__sections)
            self.__sections.append(self.__meta_section)
        return self.__sections

    def get_product_section(self, product_name, product_version):
        ''' Return the section for a specific product. '''
        product_key = (product_name, product_version)
        if product_key not in self.__product_sections:
            self.sections()  # Create the sections
        return self.__product_sections[product_key]
    
    def get_service_section(self, service):
        ''' Return the section for a specific service. '''
        if service not in self.__service_sections:
            self.sections()  # Create the sections
        return self.__service_sections[service]
    
    def get_meta_section(self):
        ''' Return the section with the meta metrics. '''
        return self.__meta_section

    def dashboard(self):
        ''' Return the dashboard layout. '''
        return self.__project.dashboard()

    def metrics(self):
        ''' Return all metrics we report on. '''
        return self.__metrics

    def teams(self):
        ''' Return the teams we report on. '''
        return self.__teams

    def products(self):
        ''' Return the products we report on. '''
        return self.__products
    
    def services(self):
        ''' Return the services we report on. '''
        return self.__services

    def get_product(self, product_name, product_version):
        ''' Return the product with the specified name and version. '''
        return [product for product in self.products() \
                if product.name() == product_name and \
                product.product_version() == product_version][0]

    def latest_product_version(self, product):
        ''' Return the most recent version of the product. '''
        version = product.product_version()
        if version:
            return version
        elif product.sonar_id():
            # Product is a trunk version, get the SNAPSHOT version number 
            # from Sonar
            return self.__project.sonar().version(product.sonar_id())
        else:
            return ''
        
    def __process_section(self):
        ''' Return the process section. '''
        metrics = self.__management_metrics() + \
                  self.__build_server_metrics() + \
                  self.__bugs_metrics()
        self.__metrics.extend(metrics)
        return Section(SectionHeader('PC', 'Proceskwaliteit algemeen'),
                       metrics) if metrics else None

    def __overall_products_section(self):
        ''' Return the products overall section. '''
        metrics = [metric.TotalLOC([product for product in self.__products \
                                     if not product.product_version() and \
                                     product.sonar_id()],
                                    sonar=self.__project.sonar(),
                                    **self.__metric_sources)]
        metrics.append(metric.DependencyQuality(report=self,
                                                **self.__metric_sources))
        self.__metrics.extend(metrics)
        return Section(SectionHeader('PD', 'Productkwaliteit algemeen'),
                       metrics)

    def __product_section(self, product):
        ''' Return the section for the product. '''
        metrics = []
        metrics.extend(self.__test_coverage_metrics(product))
        if product.has_test_design():
            metrics.extend(self.__testdesign_metrics(product))
        if product.sonar_id():
            metrics.extend(self.__java_metrics(product))
        if product.performance_test():
            metrics.extend(self.__performance_metrics(product))
        art = product.art()
        if art and not product.product_version():
            # Only add the ART if we're reporting on the trunk version
            # because we currently can only report on the trunk version of the
            # ART.
            metrics.extend(self.__java_metrics(art))
            if art.has_art_coverage():
                metrics.append(metric.ARTCoverage(art,
                    emma=self.__project.emma(), jacoco=self.__project.jacoco(),
                    **self.__metric_sources))
            if art.svn_path():
                metrics.append(metric.UnmergedBranches(subject=art,
                    subversion=self.__project.subversion(), 
                    **self.__metric_sources))
        if product.jsf():
            metrics.extend(self.__jsf_metrics(product.jsf()))
        if product.svn_path() and not product.product_version():
            # Only report on unmerged branches for the trunk version.
            metrics.append(metric.UnmergedBranches(subject=product,
                subversion=self.__project.subversion(), 
                **self.__metric_sources))
        self.__metrics.extend(metrics)
        return Section(SectionHeader(product.short_name(),
                                     'Product ' + product.name(),
                                     self.latest_product_version(product)),
                       metrics, product=product)
        
    def __service_section(self, service):
        ''' Return the section for the service. '''
        metrics = []
        nagios = service.nagios() or self.__project.nagios()
        if nagios:
            metrics.append(metric.ServiceAvailabilityLastMonth(subject=service,
                           nagios=nagios, **self.__metric_sources))
            metrics.append(metric.ServiceAvailabilityThisMonth(subject=service,
                           nagios=nagios, **self.__metric_sources))
        javamelody = self.__project.javamelody()
        if javamelody:
            metrics.append(metric.ServiceResponseTimesLastMonth(subject=service,
                               javamelody=javamelody, **self.__metric_sources))
            metrics.append(metric.ServiceResponseTimesThisMonth(subject=service,
                               javamelody=javamelody, **self.__metric_sources))
        self.__metrics.extend(metrics)
        return Section(SectionHeader(service.short_name(), 
                                     'Dienst ' + service.name()),
                       metrics, service=service)

    def __team_section(self, team):
        ''' Return a report section for the team. '''
        metrics = []
        if team.birt_id():
            metrics.append(metric.TeamProgress(team, responsible_teams=[team],
                                               birt=self.__project.birt(),
                                               **self.__metric_sources))
        for release_archive in team.release_archives():
            metrics.append(metric.ReleaseAge(team, responsible_teams=[team],
                                             release_archive=release_archive,
                                             **self.__metric_sources))
        jenkins = self.__project.build_server()
        for street in team.streets():
            metrics.append(metric.ARTStability(street,
                                               responsible_teams=[team],
                                               jenkins=jenkins,
                                               **self.__metric_sources))
        nagios = self.__project.nagios()
        if team.is_support_team() and nagios:
            metrics.append(metric.ServerAvailability(responsible_teams=[team],
                nagios=nagios, **self.__metric_sources))
        if self.__project.wiki():
            metrics.append(metric.TeamSpirit(team, responsible_teams=[team],
                                             **self.__metric_sources))
        if len(self.__teams) > 1:
            metrics.append(metric.FailingCIJobs(team, responsible_teams=[team],
                                                jenkins=jenkins,
                                                **self.__metric_sources))
            metrics.append(metric.UnusedCIJobs(team, responsible_teams=[team],
                                               jenkins=jenkins,
                                               **self.__metric_sources))
        self.__metrics.extend(metrics)
        return Section(SectionHeader(team.short_name(), 'Team ' + str(team)),
                       metrics)

    def __create_meta_section(self, sections):
        ''' Create and return the meta section. '''
        metrics = []
        for section in sections:
            metrics.extend(section.metrics())
        meta_metric_classes = (metric.GreenMetaMetric, metric.RedMetaMetric,
                               metric.YellowMetaMetric, metric.GreyMetaMetric)
        meta_metrics = [meta_metric_class(metrics, **self.__metric_sources) \
                        for meta_metric_class in meta_metric_classes]
        self.__metrics.extend(meta_metrics)
        return Section(SectionHeader('MM', 'Meta metrieken'), meta_metrics,
                       history=self.__project.history())

    def __test_coverage_metrics(self, product):
        ''' Return a list of test coverage metrics for the product. '''
        metrics = []
        if product.unittests():
            sonar = self.__project.sonar()
            metrics.append(metric.FailingUnittests(product, sonar=sonar,
                                                   **self.__metric_sources))
            metrics.append(metric.UnittestCoverage(product, sonar=sonar,
                                                   **self.__metric_sources))
        if product.has_art_coverage():
            metrics.append(metric.ARTCoverage(product,
                                              emma=self.__project.emma(),
                                              jacoco=self.__project.jacoco(),
                                              **self.__metric_sources))
        return metrics

    def __testdesign_metrics(self, product):
        ''' Return a list of test design metrics for the product. '''
        metric_classes = []
        if not product.product_version():
            metric_classes.extend(\
                [metric.ReviewedAndApprovedUserStories,
                 metric.ReviewedAndApprovedLogicalTestCases,
                 metric.UserStoriesWithEnoughLogicalTestCases,
                 metric.AutomatedLogicalTestCases])
        metric_classes.append(metric.ManualLogicalTestCases)
        metrics = []
        for metric_class in metric_classes:
            metrics.append(metric_class(product, birt=self.__project.birt(),
                                        **self.__metric_sources))
        return metrics

    def __jsf_metrics(self, product):
        ''' Return a list of JSF metrics for the (JSF) product. '''
        metrics = []
        for metric_class in (metric.JsfDuplication, metric.ProductLOC):
            metrics.append(metric_class(product, sonar=self.__project.sonar(),
                                        **self.__metric_sources))
        return metrics

    def __java_metrics(self, product):
        ''' Return a list of Java metrics for the (Java) product. '''
        metrics = []
        for metric_class in (metric.CriticalViolations, metric.MajorViolations,
                             metric.CyclomaticComplexity, 
                             metric.CyclicDependencies, metric.JavaDuplication,
                             metric.ProductLOC, metric.LongMethods,
                             metric.ManyParameters, metric.CommentedLOC):
            metrics.append(metric_class(product, sonar=self.__project.sonar(), 
                                        **self.__metric_sources))
        return metrics

    def __performance_metrics(self, product):
        ''' Return a list of performance metrics for the product. '''
        return [metric.ResponseTimes(product, 
                performance_report=self.__project.performance_report(),
                **self.__metric_sources)]
        
    def __management_metrics(self):
        ''' Return a list of management metrics for the project. '''
        metrics = []
        actions = self.__project.trello_actions_board()
        if actions:
            for action_metric_class in (metric.ActionActivity,
                                        metric.ActionAge):
                metrics.append(action_metric_class(responsible_teams=[],
                                                   trello_actions_board=actions,
                                                   **self.__metric_sources))
        risklog = self.__project.trello_risklog_board()
        if risklog:
            metrics.append(metric.RiskLog(responsible_teams=[],
                                          trello_risklog_board=risklog,
                                          **self.__metric_sources))
        return metrics
    
    def __build_server_metrics(self):
        ''' Return a list of build server hygiene related metrics. '''
        metrics = []
        jenkins = self.__project.build_server()
        if jenkins:
            metrics.append(metric.FailingCIJobs(responsible_teams=self.__teams,
                                                jenkins=jenkins,
                                                **self.__metric_sources))
            metrics.append(metric.UnusedCIJobs(responsible_teams=self.__teams,
                                               jenkins=jenkins,
                                               **self.__metric_sources))
            if len(self.__teams) > 1:
                metrics.append(metric.AssignedCIJobs(responsible_teams=[],
                                                     jenkins=jenkins,
                                                     **self.__metric_sources))
        return metrics
    
    def __bugs_metrics(self):
        ''' Return a list of bug related metrics for the project. '''
        metrics = []
        jira = self.__project.jira()
        if jira:
            if jira.has_open_bugs_query():
                metrics.append(metric.OpenBugs(responsible_teams=[],
                                               jira=jira, 
                                               **self.__metric_sources))
            if jira.has_open_security_bugs_query():
                metrics.append(metric.OpenSecurityBugs(responsible_teams=[],
                                                       jira=jira,
                                                       **self.__metric_sources))
            if jira.has_blocking_test_issues_query():
                metrics.append(metric.BlockingTestIssues(responsible_teams=[],
                               jira=jira, **self.__metric_sources))
        return metrics
