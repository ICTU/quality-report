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

from qualitylib import metric, utils, metric_source
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

    ORDERED_STATUS_COLORS = ('red', 'yellow', 'grey', 'green', 'perfect')

    def __init__(self, header, metrics, history=None, product=None):
        self.__header = header
        self.__metrics = metrics
        self.__history = history
        self.__product = product
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
        for status_color in self.ORDERED_STATUS_COLORS:  # pragma: no branch
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


class QualityReport(object):
    ''' Quality report on a project. '''

    TEST_COVERAGE_METRIC_CLASSES = (metric.FailingUnittests, 
                                    metric.UnittestCoverage, 
                                    metric.FailingRegressionTests,
                                    metric.ARTCoverage)
    TEST_DESIGN_METRIC_CLASSES = (metric.UserStoriesNotReviewedAndApproved,
                                  metric.LogicalTestCasesNotReviewedAndApproved,
                                  metric.UserStoriesWithTooFewLogicalTestCases,
                                  metric.LogicalTestCasesNotAutomated,
                                  metric.ManualLogicalTestCases)
    JAVA_METRIC_CLASSES = (metric.CriticalViolations, metric.MajorViolations,
                           metric.CyclomaticComplexity, 
                           metric.CyclicDependencies, metric.JavaDuplication,
                           metric.ProductLOC, metric.LongMethods,
                           metric.ManyParameters, metric.CommentedLOC)
    PERFORMANCE_METRIC_CLASSES = (metric.ResponseTimes,
                                  metric.RelativeARTPerformance)
    MANAGEMENT_METRIC_CLASSES = (metric.ActionActivity, metric.ActionAge, 
                                 metric.RiskLog)
    BUILD_SERVER_METRIC_CLASSES = (metric.ProjectFailingCIJobs,
                                   metric.ProjectUnusedCIJobs,
                                   metric.AssignedCIJobs)
    BUGS_METRIC_CLASSES = (metric.OpenBugs, metric.OpenSecurityBugs,
                           metric.BlockingTestIssues)
    DOCUMENT_METRIC_CLASSES = (metric.DocumentAge,)
    META_METRIC_CLASSES = (metric.GreenMetaMetric, metric.RedMetaMetric,
                           metric.YellowMetaMetric, metric.GreyMetaMetric)

    PROCESS_SECTION_METRIC_CLASSES = MANAGEMENT_METRIC_CLASSES + \
        BUILD_SERVER_METRIC_CLASSES + BUGS_METRIC_CLASSES
    META_SECTION_METRIC_CLASSES = META_METRIC_CLASSES
    TEAM_SECTION_METRIC_CLASSES = (metric.ReleaseAge, metric.TeamProgress,
                                   metric.TeamSpirit, metric.TeamFailingCIJobs,
                                   metric.TeamUnusedCIJobs)

    @classmethod
    def metric_classes(cls):
        ''' Return a list of metric classes that the report can measure. '''
        return cls.TEST_COVERAGE_METRIC_CLASSES + \
            cls.TEST_DESIGN_METRIC_CLASSES + cls.JAVA_METRIC_CLASSES + \
            cls.PERFORMANCE_METRIC_CLASSES + cls.MANAGEMENT_METRIC_CLASSES + \
            cls.BUILD_SERVER_METRIC_CLASSES + cls.BUGS_METRIC_CLASSES + \
            cls.DOCUMENT_METRIC_CLASSES + \
            (metric.TotalLOC, metric.DependencyQuality, 
             metric.SnapshotDependencies, metric.UnmergedBranches,
             metric.TeamProgress, metric.ReleaseAge, metric.ARTStability,
             metric.TeamSpirit, metric.TeamFailingCIJobs, 
             metric.TeamUnusedCIJobs)

    def __init__(self, project):
        self.__project = project
        self.__title = 'Kwaliteitsrapportage %s/%s' % (project.organization(), 
                                                       project.name())
        self.__products = sorted(project.products(),
                                 key=lambda product: (product.name(),
                                                      product.short_name()))
        self.__product_sections = dict()
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
            if self.__products or self.__project.documents():
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

    def get_section(self, section_id):
        ''' Return the section with the specified section id. '''
        for section in self.sections():
            if section_id == section.id_prefix():
                return section

    def get_product_section(self, product_name, product_version):
        ''' Return the section for a specific product. '''
        product_key = (product_name, product_version)
        if product_key not in self.__product_sections:
            self.sections()  # Create the sections
        return self.__product_sections[product_key]

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
            sonar = self.__project.metric_source(metric_source.Sonar)
            return sonar.version(product.sonar_id())
        else:
            return ''

    def __process_section(self):
        ''' Return the process section. '''
        metrics = []
        for metric_class in self.PROCESS_SECTION_METRIC_CLASSES:
            if metric_class.can_be_measured(self.__project, self.__project):
                metrics.append(metric_class(project=self.__project))
        for street in self.__project.streets():
            metrics.append(metric.ARTStability(street, project=self.__project))
        self.__metrics.extend(metrics)
        return Section(SectionHeader('PC', 'Proceskwaliteit algemeen'),
                       metrics) if metrics else None

    def __overall_products_section(self):
        ''' Return the products overall section. '''
        metrics = [metric.TotalLOC([product for product in self.__products \
                                     if not product.product_version() and \
                                     product.sonar_id()],
                                    project=self.__project)]
        metrics.append(metric.DependencyQuality(report=self,
                                                project=self.__project))
        for document in self.__project.documents():
            if metric.DocumentAge.can_be_measured(document, self.__project):
                metrics.append(metric.DocumentAge(document, 
                                                  project=self.__project))
        self.__metrics.extend(metrics)
        return Section(SectionHeader('PD', 'Productkwaliteit algemeen'),
                       metrics)

    def __product_section(self, product):
        ''' Return the section for the product. '''
        metrics = []
        for metric_class in self.TEST_COVERAGE_METRIC_CLASSES + \
                            self.TEST_DESIGN_METRIC_CLASSES + \
                            self.JAVA_METRIC_CLASSES + \
                            self.PERFORMANCE_METRIC_CLASSES:
            if metric_class.can_be_measured(product, self.__project):
                metrics.append(metric_class(product, project=self.__project))
        if metric.SnapshotDependencies.can_be_measured(product, self.__project):
            metrics.append(metric.SnapshotDependencies(product, report=self,
                                                       project=self.__project))
        art = product.art()
        if art and not art.product_version():
            # Only add the ART if we're reporting on the trunk version
            # because we currently can only report on the trunk version of the
            # ART.
            metrics.extend(self.__java_metrics(art))
            for art_metric_class in (metric.ARTCoverage,
                                     metric.FailingRegressionTests,
                                     metric.RelativeARTPerformance):
                if art_metric_class.can_be_measured(art, self.__project):
                    metrics.append(art_metric_class(art,
                                                    project=self.__project))
        if metric.UnmergedBranches.can_be_measured(art, self.__project):
            metrics.append(metric.UnmergedBranches(subject=art,
                                                   project=self.__project))
        metrics.extend(self.__jsf_metrics(product))
        if metric.UnmergedBranches.can_be_measured(product, self.__project):
            metrics.append(metric.UnmergedBranches(product,
                                                   project=self.__project))
        self.__metrics.extend(metrics)
        return Section(SectionHeader(product.short_name(),
                                     'Product ' + product.name(),
                                     self.latest_product_version(product)),
                       metrics, product=product)

    def __team_section(self, team):
        ''' Return a report section for the team. '''
        metrics = []
        for metric_class in self.TEAM_SECTION_METRIC_CLASSES:
            if metric_class.can_be_measured(team, self.__project):
                metrics.append(metric_class(team, project=self.__project))
        self.__metrics.extend(metrics)
        return Section(SectionHeader(team.short_name(), 'Team ' + team.name()),
                       metrics)

    def __create_meta_section(self, sections):
        ''' Create and return the meta section. '''
        metrics = []
        for section in sections:
            metrics.extend(section.metrics())
        meta_metrics = [meta_metric_class(metrics, project=self.__project) for \
                        meta_metric_class in self.META_SECTION_METRIC_CLASSES]
        self.__metrics.extend(meta_metrics)
        return Section(SectionHeader('MM', 'Meta metrieken'), meta_metrics,
            history=self.__project.metric_source(metric_source.History))

    def __jsf_metrics(self, product):
        ''' Return a list of JSF metrics for the (JSF) product. '''
        metrics = []
        if metric.JsfDuplication.can_be_measured(product, self.__project):
            metrics.append(metric.JsfDuplication(product.jsf(), 
                                                 project=self.__project))
        if metric.ProductLOC.can_be_measured(product.jsf(), self.__project):
            metrics.append(metric.ProductLOC(product.jsf(), 
                                             project=self.__project))
        return metrics

    def __java_metrics(self, product):
        ''' Return a list of Java metrics for the (Java) product. '''
        metrics = []
        for metric_class in self.JAVA_METRIC_CLASSES:
            if metric_class.can_be_measured(product, self.__project):
                metrics.append(metric_class(product, project=self.__project))
        return metrics
