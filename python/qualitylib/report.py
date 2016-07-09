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

import datetime

from . import metric, utils, metric_source, metric_info, domain


class SectionHeader(object):
    """ Header for a section, consisting of two-letter prefix, title and an optional subtitle. """

    def __init__(self, id_prefix, title, subtitle=''):
        self.__id_prefix = id_prefix
        self.__title = title
        self.__subtitle = subtitle

    def title(self):
        """ Return the title of the section. """
        return self.__title

    def subtitle(self):
        """ Return the subtitle of the section. """
        return self.__subtitle

    def id_prefix(self):
        """ Return the id prefix of the section, a two letter string. """
        return self.__id_prefix


# Section implements __getitem__ but not the complete Container protocol

class Section(object):
    """ Section within a report. """

    ORDERED_STATUS_COLORS = ('missing', 'red', 'yellow', 'grey', 'green', 'perfect')

    def __init__(self, header, metrics, history=None, product=None):
        self.__header = header
        self.__metrics = metrics
        self.__history = history
        self.__product = product
        for index, each_metric in enumerate(self.__metrics):
            each_metric.set_id_string('{pref}-{nr}'.format(pref=self.__header.id_prefix(), nr=index + 1))

    def __str__(self):
        return self.title()

    def __getitem__(self, index):
        return self.__metrics[index]

    def title(self):
        """ Return the title of this section. """
        return self.__header.title()

    def subtitle(self):
        """ Return the subtitle of this section. """
        return self.__header.subtitle()

    def id_prefix(self):
        """ Return the id prefix of this section, a two letter string. """
        return self.__header.id_prefix()

    def metrics(self):
        """ Return the metrics in this section. """
        return self.__metrics

    @utils.memoized
    def color(self):
        """ Return the color of this section. """
        metric_statuses = set(each_metric.status() for each_metric in self)
        for status_color in self.ORDERED_STATUS_COLORS:  # pragma: no branch
            if status_color in metric_statuses:
                color = status_color
                break
        else:
            color = 'white'
        if color == 'perfect':
            color = 'green'
        if color == 'missing':
            color = 'red'
        return color

    def has_history(self):
        """ Return whether this section has history collected. """
        return self.id_prefix() == 'MM'

    def history(self):
        """ Return the history file contents. """
        return self.__history.complete_history()

    def product(self):
        """ Return the product this section is about. """
        return self.__product

    def contains_trunk_product(self):
        """ Return whether this section describes a trunk version of a product. """
        return self.product() and self.product().product_version_type() == 'trunk'


class QualityReport(domain.DomainObject):
    """ Quality report on a project. """

    TEST_COVERAGE_METRIC_CLASSES = (metric.FailingUnittests,
                                    metric.UnittestLineCoverage,
                                    metric.UnittestBranchCoverage,
                                    metric.IntegrationtestLineCoverage,
                                    metric.IntegrationtestBranchCoverage,
                                    metric.UnitAndIntegrationTestLineCoverage,
                                    metric.UnitAndIntegrationTestBranchCoverage,
                                    metric.FailingRegressionTests,
                                    metric.RegressionTestAge,
                                    metric.ARTStatementCoverage,
                                    metric.ARTBranchCoverage)
    TEST_DESIGN_METRIC_CLASSES = (metric.UserStoriesNotReviewed,
                                  metric.UserStoriesNotApproved,
                                  metric.LogicalTestCasesNotReviewed,
                                  metric.LogicalTestCasesNotApproved,
                                  metric.UserStoriesWithTooFewLogicalTestCases,
                                  metric.LogicalTestCasesNotAutomated,
                                  metric.ManualLogicalTestCases,
                                  metric.NumberOfManualLogicalTestCases)
    CODE_METRIC_CLASSES = (metric.BlockerViolations, metric.CriticalViolations,
                           metric.MajorViolations, metric.CyclomaticComplexity,
                           metric.CyclicDependencies, metric.JavaDuplication,
                           metric.ProductLOC, metric.LongMethods,
                           metric.ManyParameters, metric.CommentedLOC,
                           metric.NoSonar, metric.FalsePositives,
                           metric.SonarAnalysisAge)
    DEPENDENCY_METRIC_CLASSES = (metric.DependencyQuality,
                                 metric.SnapshotDependencies)
    SECURITY_METRIC_CLASSES = (metric.HighPriorityOWASPDependencyWarnings,
                               metric.NormalPriorityOWASPDependencyWarnings,
                               metric.HighRiskZAPScanAlertsMetric,
                               metric.MediumRiskZAPScanAlertsMetric)
    PERFORMANCE_METRIC_CLASSES = (metric.ResponseTimes,
                                  metric.YmorResponseTimes)
    ENVIRONMENT_METRIC_CLASSES = (metric.FailingCIJobs,
                                  metric.UnusedCIJobs,
                                  metric.JavaVersionConsistency,
                                  metric.SonarVersion)
    DOCUMENT_METRIC_CLASSES = (metric.DocumentAge,)
    TEAM_METRIC_CLASSES = (metric.TeamProgress, metric.TeamSpirit,
                           metric.TeamAbsence)
    META_METRIC_CLASSES = (metric.GreenMetaMetric, metric.RedMetaMetric,
                           metric.YellowMetaMetric, metric.GreyMetaMetric,
                           metric.MissingMetaMetric)
    SONAR_PLUGIN_METRIC_CLASSES = (metric.SonarPluginVersionJava, metric.SonarPluginVersionCheckStyle,
                                   metric.SonarPluginVersionPMD, metric.SonarPluginVersionFindBugs,
                                   metric.SonarPluginVersionCSharp, metric.SonarPluginVersionJS,
                                   metric.SonarPluginVersionReSharper, metric.SonarPluginVersionStyleCop,
                                   metric.SonarPluginVersionWeb)
    SONAR_QUALITY_PROFILE_METRIC_CLASSES = (metric.SonarQualityProfileVersionJava,
                                            metric.SonarQualityProfileVersionCSharp,
                                            metric.SonarQualityProfileVersionWeb, metric.SonarQualityProfileVersionJS)
    MANAGEMENT_METRIC_CLASSES = (metric.ActionActivity, metric.ActionAge,
                                 metric.RiskLog)
    BUGS_METRIC_CLASSES = (metric.OpenBugs, metric.OpenSecurityBugs, metric.TechnicalDebtIssues)
    PROCESS_SECTION_METRIC_CLASSES = MANAGEMENT_METRIC_CLASSES + BUGS_METRIC_CLASSES + \
                                     (metric.DurationOfManualLogicalTestCases,
                                      metric.ManualLogicalTestCasesWithoutDuration,
                                      metric.ReadyUserStoryPoints)
    META_SECTION_METRIC_CLASSES = META_METRIC_CLASSES
    TEAM_SECTION_METRIC_CLASSES = TEAM_METRIC_CLASSES

    @classmethod
    def metric_classes(cls):
        """ Return a list of metric classes that the report can measure. """
        return cls.TEST_COVERAGE_METRIC_CLASSES + cls.TEST_DESIGN_METRIC_CLASSES + cls.CODE_METRIC_CLASSES + \
            cls.PERFORMANCE_METRIC_CLASSES + cls.PROCESS_SECTION_METRIC_CLASSES + cls.ENVIRONMENT_METRIC_CLASSES + \
            cls.DOCUMENT_METRIC_CLASSES + cls.TEAM_METRIC_CLASSES + cls.DEPENDENCY_METRIC_CLASSES + \
            cls.SECURITY_METRIC_CLASSES + cls.SONAR_PLUGIN_METRIC_CLASSES + cls.SONAR_QUALITY_PROFILE_METRIC_CLASSES + \
            (metric.TotalLOC, metric.UnmergedBranches, metric.ARTStability)

    @classmethod
    def metric_source_classes(cls):
        """ Return a list of metric source classes that the report can use. """
        classes = set()
        for metric_class in cls.metric_classes():
            classes.update(set(metric_class.metric_source_classes))
        return classes

    def __init__(self, project):
        # Use None as name to keep the history consistent of metrics that have the report as subject:
        super(QualityReport, self).__init__(name='None')
        self.__project = project
        self.__title = 'Kwaliteitsrapportage {org}/{proj}'.format(org=project.organization(), proj=project.name())
        self.__products = sorted(project.products(), key=lambda product: (product.name(), product.short_name()))
        self.__product_sections = dict()
        self.__teams = sorted(project.teams(), key=str)
        self.__sections = []
        self.__meta_section = None
        self.__metrics = []

    def __str__(self):
        return self.__title

    def title(self):
        """ Return the title of the quality report. """
        return self.__title

    def project(self):
        """ Return the project this report is about. """
        return self.__project

    @staticmethod
    def date():
        """ Return the date and time the quality report was generated. """
        return datetime.datetime.today()

    def sections(self):
        """ Return the sections in the report. """
        if not self.__sections:
            process_section = self.__process_section()
            if process_section:
                self.__sections.append(process_section)
            if self.__products or self.__project.documents():
                self.__sections.append(self.__overall_products_section())
            environment_section = self.__environment_section()
            if environment_section:
                self.__sections.append(environment_section)
            for product in self.__products:
                section = self.__product_section(product)
                self.__product_sections[product.product_label()] = section
                self.__sections.append(section)
            for team in self.__teams:
                self.__sections.append(self.__team_section(team))
            self.__meta_section = self.__create_meta_section(self.__sections)
            self.__sections.append(self.__meta_section)
        return self.__sections

    def get_section(self, section_id):
        """ Return the section with the specified section id. """
        for section in self.sections():
            if section_id == section.id_prefix():
                return section
        return None

    def get_product_section(self, product):
        """ Return the section for a specific product. """
        if product.product_label() not in self.__product_sections:
            self.sections()  # Create the sections
        return self.__product_sections[product.product_label()]

    def get_meta_section(self):
        """ Return the section with the meta metrics. """
        return self.__meta_section

    def dashboard(self):
        """ Return the dashboard layout. """
        return self.__project.dashboard()

    def metrics(self):
        """ Return all metrics we report on. """
        return self.__metrics

    def included_metric_classes(self):
        """ Return the metric classes included in the report. """
        return {each_metric.__class__ for each_metric in self.__metrics}

    def included_metric_source_classes(self):
        """ Return the metric classes actually configured in the project. """
        return self.__project.metric_source_classes()

    def teams(self):
        """ Return the teams we report on. """
        return self.__teams

    def products(self):
        """ Return the products we report on. """
        return self.__products

    def get_product(self, product_name, product_version):
        """ Return the product with the specified name and version. """
        return [product for product in self.products() if product.name() == product_name and
                product.product_version() == product_version][0]

    def __latest_product_version(self, product):
        """ Return the most recent version of the product. """
        sonar = self.__project.metric_source(metric_source.Sonar)
        return metric_info.SonarProductInfo(sonar, product).latest_version()

    def __process_section(self):
        """ Return the process section. """
        metrics = []
        for metric_class in self.PROCESS_SECTION_METRIC_CLASSES:
            if metric_class.can_be_measured(self.__project, self.__project):
                metrics.append(metric_class(self.__project, project=self.__project))
        for street in self.__project.streets():
            metrics.append(metric.ARTStability(street, project=self.__project))
        self.__metrics.extend(metrics)
        return Section(SectionHeader('PC', 'Proceskwaliteit algemeen'), metrics) if metrics else None

    def __environment_section(self):
        """ Return the environment section. """
        metrics = []
        for metric_class in self.ENVIRONMENT_METRIC_CLASSES:
            if metric_class.can_be_measured(self.__project, self.__project):
                metrics.append(metric_class(self.__project, project=self.__project))
        metrics.extend(self.__mandatory_subject_metrics(self.__project, self.SONAR_PLUGIN_METRIC_CLASSES +
                                                        self.SONAR_QUALITY_PROFILE_METRIC_CLASSES))
        self.__metrics.extend(metrics)
        return Section(SectionHeader('PE', 'Kwaliteit omgevingen'), metrics) if metrics else None

    def __overall_products_section(self):
        """ Return the products overall section. """
        metrics = []
        if metric.TotalLOC.should_be_measured(self.__project):
            metrics.append(metric.TotalLOC(subject=self.__project, project=self.__project))
        metrics.append(metric.DependencyQuality(subject=self, project=self.__project))
        for document in self.__project.documents():
            if metric.DocumentAge.can_be_measured(document, self.__project):
                metrics.append(metric.DocumentAge(document, project=self.__project))
        self.__metrics.extend(metrics)
        return Section(SectionHeader('PD', 'Productkwaliteit algemeen'), metrics)

    def __product_section(self, product):
        """ Return the section for the product. """
        metrics = self.__optional_subject_metrics(product, self.TEST_COVERAGE_METRIC_CLASSES)
        metrics.extend(self.__mandatory_subject_metrics(product, self.TEST_DESIGN_METRIC_CLASSES))
        metrics.extend(self.__optional_subject_metrics(product, self.CODE_METRIC_CLASSES +
                                                       self.PERFORMANCE_METRIC_CLASSES))
        metrics.extend(self.__mandatory_subject_metrics(product, self.SECURITY_METRIC_CLASSES))
        if metric.SnapshotDependencies.can_be_measured(product, self.__project):
            metrics.append(metric.SnapshotDependencies(product, report=self, project=self.__project))
        metrics.extend(self.__art_metrics(product.art()))
        metrics.extend(self.__jsf_metrics(product.jsf()))
        if metric.UnmergedBranches.can_be_measured(product, self.__project):
            metrics.append(metric.UnmergedBranches(product, project=self.__project))
        self.__metrics.extend(metrics)
        return Section(SectionHeader(product.short_name(), product.name(), self.__latest_product_version(product)),
                       metrics, product=product)

    def __team_section(self, team):
        """ Return a report section for the team. """
        team_metrics = self.__optional_subject_metrics(team, self.TEAM_SECTION_METRIC_CLASSES)
        self.__metrics.extend(team_metrics)
        return Section(SectionHeader(team.short_name(), 'Team ' + team.name()), team_metrics)

    def __create_meta_section(self, sections):
        """ Create and return the meta section. """
        metrics = []
        for section in sections:
            metrics.extend(section.metrics())
        meta_metrics = [meta_metric_class(metrics, project=self.__project) for
                        meta_metric_class in self.META_SECTION_METRIC_CLASSES]
        self.__metrics.extend(meta_metrics)
        return Section(SectionHeader('MM', 'Meta metrieken'), meta_metrics,
                       history=self.__project.metric_source(metric_source.History))

    def __art_metrics(self, art):
        """ Return a list of Automated Regression Test metrics for the (ART) product. """
        metrics = []
        if art and art.product_version_type() == 'trunk':
            # Only add the ART if we're reporting on the trunk version because we currently can only report on the
            # trunk version of the ART.
            art_metric_classes = self.CODE_METRIC_CLASSES + (metric.ARTStatementCoverage, metric.ARTBranchCoverage,
                                                             metric.FailingRegressionTests, metric.RegressionTestAge)
            metrics.extend(self.__optional_subject_metrics(art, art_metric_classes))
        if metric.UnmergedBranches.can_be_measured(art, self.__project):
            metrics.append(metric.UnmergedBranches(subject=art, project=self.__project))
        return metrics

    def __jsf_metrics(self, jsf):
        """ Return a list of JSF metrics for the (JSF) product. """
        return self.__optional_subject_metrics(jsf, (metric.JsfDuplication, metric.ProductLOC))

    def __optional_subject_metrics(self, subject, metric_classes):
        """ Return a list of metrics for the subject that can be measured. """
        metrics = []
        for metric_class in metric_classes:
            if metric_class.can_be_measured(subject, self.__project):
                metrics.append(metric_class(subject, project=self.__project))
        return metrics

    def __mandatory_subject_metrics(self, subject, metric_classes):
        """ Return a list of metrics for the subject that should be measured. """
        metrics = []
        for metric_class in metric_classes:
            if metric_class.should_be_measured(subject):
                metrics.append(metric_class(subject, project=self.__project))
        return metrics
