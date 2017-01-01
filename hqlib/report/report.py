"""
Copyright 2012-2017 Ministerie van Sociale Zaken en Werkgelegenheid

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

import datetime

from .section import Section, SectionHeader
from .. import metric, metric_source, metric_info, domain, requirement


class QualityReport(domain.DomainObject):
    """ Quality report on a project. """

    @staticmethod
    def domain_object_classes():
        """ Return a set of all domain object classes that the report can report on. """
        return {domain.Project, domain.Product, domain.Component, domain.Application, domain.Document, domain.Team}

    @classmethod
    def requirement_classes(cls):
        """ Return a list of all requirement classes that the report can report on. """
        return (requirement.UnitTests, requirement.ART, requirement.ARTCoverage, requirement.UserStoriesAndLTCs,
                requirement.CodeQuality, requirement.JSFCodeQuality, requirement.PerformanceLoad,
                requirement.PerformanceEndurance, requirement.PerformanceScalability, requirement.TrackActions,
                requirement.TrackRisks, requirement.TrackBugs, requirement.TrackTechnicalDebt,
                requirement.TrackManualLTCs, requirement.TrackSecurityAndPerformanceRisks,
                requirement.TrackReadyUS, requirement.TrackCIJobs, requirement.TrackJavaConsistency,
                requirement.TrackSonarVersion, requirement.TrackDocumentAge, requirement.ScrumTeam,
                requirement.TrackSpirit, requirement.TrackAbsence,
                requirement.OWASPDependencies, requirement.OWASPZAP, requirement.OpenVAS, requirement.Java,
                requirement.CSharp, requirement.JavaScript, requirement.Web,
                requirement.TrustedProductMaintainability, requirement.TrackBranches)

    @classmethod
    def metric_classes(cls):
        """ Return a list of metric classes that the report can measure. """
        return [metric_class for req_class in cls.requirement_classes() for metric_class in req_class.metric_classes()]

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
        self.__products = sorted(project.products(), key=lambda product: (product.name(), product.short_name()))
        self.__teams = sorted(project.teams(), key=str)
        self.__sections = []
        self.__meta_section = None
        self.__metrics = []
        self.__requirements = set()

    def __str__(self):
        return self.title()

    def title(self):
        """ Return the title of the quality report. """
        return 'Kwaliteitsrapportage {org}/{proj}'.format(org=self.__project.organization(), proj=self.__project.name())

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
            sections = [self.__process_section(), self.__overall_products_section(), self.__environment_section()]
            sections.extend([self.__product_section(product) for product in self.__products])
            sections.extend([self.__team_section(team) for team in self.__teams])
            self.__sections = [section for section in sections if section]
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
        return {section.product().name(): section for section in self.sections() if section.product()}[product.name()]

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

    def included_requirement_classes(self):
        """ Return the requirements included in the report. """
        return self.__requirements.copy()

    def included_metric_source_classes(self):
        """ Return the metric classes actually configured in the project. """
        return self.__project.metric_source_classes()

    def included_domain_object_classes(self):
        """ Return the domain object classes actually configured in the project. """
        return {self.__project.__class__} | self.__project.domain_object_classes()

    def teams(self):
        """ Return the teams we report on. """
        return self.__teams

    def products(self):
        """ Return the products we report on. """
        return self.__products

    def __latest_product_version(self, product):
        """ Return the most recent version of the product. """
        sonar = self.__project.metric_source(metric_source.Sonar)
        return metric_info.SonarProductInfo(sonar, product).latest_version()

    def __process_section(self):
        """ Return the process section. """
        metrics = self.__required_subject_metrics(self.__project, requirement.TrackActions,
                                                  requirement.TrackRisks, requirement.TrackBugs,
                                                  requirement.TrackTechnicalDebt, requirement.TrackManualLTCs,
                                                  requirement.TrackReadyUS,
                                                  requirement.TrackSecurityAndPerformanceRisks)
        self.__metrics.extend(metrics)
        return Section(SectionHeader('PC', 'Proceskwaliteit algemeen'), metrics) if metrics else None

    def __environment_section(self):
        """ Return the environment section. """
        metrics = self.__required_subject_metrics(self.__project, requirement.TrackCIJobs,
                                                  requirement.TrackJavaConsistency,
                                                  requirement.TrackSonarVersion, requirement.Java,
                                                  requirement.CSharp, requirement.JavaScript, requirement.Web,
                                                  requirement.OpenVAS)
        self.__metrics.extend(metrics)
        return Section(SectionHeader('PE', 'Kwaliteit omgevingen'), metrics) if metrics else None

    def __overall_products_section(self):
        """ Return the products overall section. """
        metrics = self.__required_subject_metrics(self.__project, requirement.TrustedProductMaintainability)
        for document in self.__project.documents():
            metrics.extend(self.__required_subject_metrics(document, requirement.TrackDocumentAge))
        self.__metrics.extend(metrics)
        return Section(SectionHeader('PD', 'Productkwaliteit algemeen'), metrics) if metrics else None

    def __product_section(self, product):
        """ Return the section for the product. """
        metrics = self.__required_subject_metrics(product, requirement.UnitTests, requirement.ART,
                                                  requirement.ARTCoverage, requirement.UserStoriesAndLTCs,
                                                  requirement.CodeQuality, requirement.PerformanceLoad,
                                                  requirement.PerformanceEndurance, requirement.PerformanceScalability,
                                                  requirement.OWASPDependencies, requirement.OWASPZAP)
        metrics.extend(self.__art_metrics(product.art()))
        metrics.extend(self.__jsf_metrics(product.jsf()))
        metrics.extend(self.__required_subject_metrics(product, requirement.TrackBranches))
        self.__metrics.extend(metrics)
        return Section(SectionHeader(product.short_name(), product.name(), self.__latest_product_version(product)),
                       metrics, product=product) if metrics else None

    def __team_section(self, team):
        """ Return a report section for the team. """
        metrics = self.__required_subject_metrics(team, requirement.ScrumTeam, requirement.TrackSpirit,
                                                  requirement.TrackAbsence)
        self.__metrics.extend(metrics)
        return Section(SectionHeader(team.short_name(), 'Team ' + team.name()), metrics) if metrics else None

    def __create_meta_section(self, sections):
        """ Create and return the meta section. """
        metrics = []
        for section in sections:
            metrics.extend(section.metrics())
        meta_metrics = [meta_metric_class(metrics, project=self.__project) for
                        meta_metric_class in (metric.GreenMetaMetric, metric.RedMetaMetric, metric.YellowMetaMetric,
                                              metric.GreyMetaMetric, metric.MissingMetaMetric)]
        self.__metrics.extend(meta_metrics)
        return Section(SectionHeader('MM', 'Meta metrieken'), meta_metrics,
                       history=self.__project.metric_source(metric_source.History))

    def __art_metrics(self, art):
        """ Return a list of Automated Regression Test metrics for the (ART) product. """
        return self.__required_subject_metrics(art, requirement.CodeQuality, requirement.ARTCoverage,
                                               requirement.ART, requirement.TrackBranches) if art else []

    def __jsf_metrics(self, jsf):
        """ Return a list of JSF metrics for the (JSF) product. """
        return self.__required_subject_metrics(jsf, requirement.JSFCodeQuality) if jsf else []

    def __required_subject_metrics(self, subject, *requirements):
        """ Return a list of metrics for the subject that should be measured and are applicable. """
        metrics = []
        for req in requirements:
            for metric_class in req.metric_classes():
                if metric_class.should_be_measured(subject) and metric_class.is_applicable(subject):
                    self.__requirements.add(req)
                    metrics.append(metric_class(subject, project=self.__project))
        return metrics
