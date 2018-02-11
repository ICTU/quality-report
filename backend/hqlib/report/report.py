"""
Copyright 2012-2018 Ministerie van Sociale Zaken en Werkgelegenheid

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
from typing import cast, Set, Tuple, Type, Sequence, Optional, List

from .section import Section, SectionHeader
from .. import metric, metric_source, domain, requirement
from ..typing import Dashboard, DateTime


class QualityReport(domain.DomainObject):
    """ Quality report on a project. """

    @staticmethod
    def domain_object_classes() -> Set[Type[domain.RequirementSubject]]:
        """ Return a set of all domain object classes that the report can report on. """
        return {domain.Project, domain.Environment, domain.Process, domain.Product, domain.Component,
                domain.Application, domain.Document, domain.Team}

    @classmethod
    def requirement_classes(cls) -> Sequence[Type[domain.Requirement]]:
        """ Return a list of all requirement classes that the report can report on. """
        return (requirement.UnitTests, requirement.UnitTestCoverage, requirement.ART, requirement.ARTCoverage,
                requirement.UserStoriesAndLTCs, requirement.CodeQuality, requirement.PerformanceLoad,
                requirement.PerformanceEndurance, requirement.PerformanceScalability, requirement.TrackActions,
                requirement.TrackRisks, requirement.TrackBugs, requirement.TrackSecurityBugs,
                requirement.TrackStaticSecurityBugs, requirement.TrackSecurityTestDate, requirement.TrackFindings,
                requirement.TrackTechnicalDebt, requirement.TrackQualityGate, requirement.TrackManualLTCs,
                requirement.TrackSecurityAndPerformanceRisks, requirement.TrackReadyUS, requirement.TrackCIJobs,
                requirement.TrackSonarVersion, requirement.TrackDocumentAge, requirement.TrackSpirit,
                requirement.TrackAbsence, requirement.TrackUserStoriesInProgress,
                requirement.TrackDurationOfUserStories, requirement.OWASPDependencies, requirement.OWASPZAP,
                requirement.Checkmarx, requirement.OpenVAS, requirement.Java, requirement.CSharp,
                requirement.JavaScript, requirement.Web, requirement.VisualBasic, requirement.Python,
                requirement.TypeScript, requirement.TrustedProductMaintainability, requirement.TrackBranches)

    @classmethod
    def metric_classes(cls) -> Set[Type[domain.Metric]]:
        """ Return a list of metric classes that the report can measure. """
        return set([metric_class for req_class in cls.requirement_classes()
                    for metric_class in req_class.metric_classes()])

    @classmethod
    def metric_source_classes(cls) -> Set[Type[domain.MetricSource]]:
        """ Return a list of metric source classes that the report can use. """
        classes = set()
        for metric_class in cls.metric_classes():
            if metric_class.metric_source_class:  # pragma: no branch
                classes.add(metric_class.metric_source_class)
        return classes

    def __init__(self, project: domain.Project) -> None:
        # Use None as name to keep the history consistent of metrics that have the report as subject:
        super().__init__(name='None')
        self.__project = project
        self.__products = sorted(project.products(), key=lambda product: (product.name(), product.short_name()))
        self.__sections: Sequence[Section] = []
        self.__metrics: List[domain.Metric] = []
        self.__requirements: Set[Type[domain.Requirement]] = set()

    def __str__(self) -> str:
        return self.title()

    def title(self) -> str:
        """ Return the title of the quality report. """
        return 'Kwaliteitsrapportage {org}/{proj}'.format(org=self.__project.organization(), proj=self.__project.name())

    def project(self) -> domain.Project:
        """ Return the project this report is about. """
        return self.__project

    @staticmethod
    def date() -> DateTime:
        """ Return the date and time the quality report was generated. """
        return datetime.datetime.today()

    def sections(self) -> Sequence[Section]:
        """ Return the sections in the report. """
        if not self.__sections:
            sections = [self.__create_section(self.__project,
                                              short_name="PC", name="Proceskwaliteit algemeen",
                                              requirements_to_ignore=[requirement.TrustedProductMaintainability]),
                        self.__overall_products_section()]
            processes = sorted(self.__project.processes(), key=lambda process: (process.name(), process.short_name()))
            sections.extend([self.__create_section(process) for process in processes])
            environments = sorted(self.__project.environments(),
                                  key=lambda environment: (environment.name(), environment.short_name()))
            sections.extend([self.__create_section(environment) for environment in environments])
            sections.extend([self.__product_section(product) for product in self.__products])
            teams = sorted(self.__project.teams(), key=lambda team: (team.name(), team.short_name()))
            sections.extend([self.__create_section(team, name_prefix="Team ") for team in teams])
            self.__sections = [section for section in sections if section]
            self.__sections.append(self.__create_meta_section(self.__sections))
        return self.__sections

    def get_section(self, section_id: str) -> Optional[Section]:
        """ Return the section with the specified section id. """
        for section in self.sections():
            if section_id == section.id_prefix():
                return section
        return None

    def dashboard(self) -> Dashboard:
        """ Return the dashboard layout. """
        return self.__project.dashboard()

    def metrics(self) -> Sequence[domain.Metric]:
        """ Return all metrics we report on. """
        self.sections()
        return self.__metrics

    def included_metric_classes(self):
        """ Return the metric classes included in the report. """
        return {each_metric.__class__ for each_metric in self.__metrics}

    def included_requirement_classes(self) -> Set[Type[domain.Requirement]]:
        """ Return the requirements included in the report. """
        return self.__requirements.copy()

    def included_metric_source_classes(self):
        """ Return the metric classes actually configured in the project. """
        return self.__project.metric_source_classes()

    def included_domain_object_classes(self) -> Set[Type[domain.DomainObject]]:
        """ Return the domain object classes actually configured in the project. """
        return self.__project.domain_object_classes() | {cast(Type[domain.DomainObject], self.__project.__class__)}

    def products(self) -> Sequence[domain.Product]:
        """ Return the products we report on. """
        return self.__products

    def direct_action_needed(self) -> bool:
        """ Return whether any of the metrics in the report are red so that direct action is needed. """
        if self.__metrics:
            return any(each_metric.status() in ('red', 'missing', 'missing_source') for each_metric in self.__metrics)
        return True  # No metrics, so direct action is needed to add metrics

    def latest_product_version(self, product: domain.Product) -> str:
        """ Return the most recent version of the product. """
        sonar, sonar_id = self.sonar_id(product)
        return sonar.version(sonar_id) if sonar_id else ''

    def latest_product_change_date(self, product: domain.Product) -> DateTime:
        """Return the latest change date of the product. """
        vcs, vcs_id = self.vcs_id(product)
        return vcs.last_changed_date(vcs_id) if vcs_id else datetime.datetime.min

    def vcs_id(self, product: domain.Product) -> Tuple[Optional[domain.MetricSource], str]:
        """ Return the version control system of the product and the id of the product in the version control
            system. """
        if not product:
            return None, ''
        for vcs in self.__project.metric_sources(metric_source.VersionControlSystem):
            vcs_id = product.metric_source_id(vcs)
            if vcs_id:
                return vcs, vcs_id
        return None, ''

    def sonar_id(self, product: domain.Product) -> Tuple[Optional[domain.MetricSource], str]:
        """ Return the Sonar id of the product. """
        for sonar in self.__project.metric_sources(metric_source.Sonar):
            sonar_id = product.metric_source_id(sonar)
            if sonar_id:
                return sonar, sonar_id
        return None, ''

    def __create_section(self, subject: domain.RequirementSubject,
                         short_name: str = '', name: str = '', name_prefix: str = '',
                         requirements_to_ignore: List[Type[domain.Requirement]] = None) -> Optional[Section]:
        """ Return a section for the subject. """
        requirements_to_ignore = requirements_to_ignore or []
        requirements = [r for r in subject.default_requirements() if r not in requirements_to_ignore]
        requirements.extend([r for r in subject.optional_requirements() if r not in requirements_to_ignore])
        metrics = self.__required_subject_metrics(subject, *requirements)
        self.__metrics.extend(metrics)
        header = SectionHeader(short_name or subject.short_name(), name or name_prefix + subject.name())
        return Section(header, metrics) if metrics else None

    def __overall_products_section(self) -> Optional[Section]:
        """ Return the products overall section. """
        metrics = self.__required_subject_metrics(self.__project, requirement.TrustedProductMaintainability)
        for document in self.__project.documents():
            metrics.extend(self.__required_subject_metrics(document,
                                                           *document.default_requirements(),
                                                           *document.optional_requirements()))
        self.__metrics.extend(metrics)
        return Section(SectionHeader('PD', 'Productkwaliteit algemeen'), metrics) if metrics else None

    def __product_section(self, product: domain.Product) -> Optional[Section]:
        """ Return the section for the product. """
        metrics = self.__required_subject_metrics(
            product, requirement.TrackBugs, requirement.TrackSecurityBugs, requirement.TrackStaticSecurityBugs,
            requirement.TrackSecurityTestDate,
            requirement.TrackFindings, requirement.TrackTechnicalDebt, requirement.TrackQualityGate,
            requirement.UnitTests, requirement.UnitTestCoverage, requirement.ART, requirement.ARTCoverage,
            requirement.UserStoriesAndLTCs, requirement.TrackReadyUS, requirement.TrackSecurityAndPerformanceRisks,
            requirement.CodeQuality, requirement.PerformanceLoad, requirement.PerformanceEndurance,
            requirement.PerformanceScalability, requirement.OWASPDependencies, requirement.OWASPZAP,
            requirement.Checkmarx, requirement.TrackDurationOfUserStories, requirement.TrackUserStoriesInProgress)
        metrics.extend(self.__art_metrics(product.art()))
        metrics.extend(self.__required_subject_metrics(product, requirement.TrackBranches))
        self.__metrics.extend(metrics)
        return Section(SectionHeader(product.short_name(), product.name(), self.latest_product_version(product)),
                       metrics, product=product) if metrics else None

    def __create_meta_section(self, sections: Sequence[Section]) -> Section:
        """ Create and return the meta section. """
        metrics: List[domain.Metric] = []
        for section in sections:
            metrics.extend(section.metrics())
        meta_metrics: List[domain.Metric] = [meta_metric_class(metrics, project=self.__project) for
                                             meta_metric_class in (metric.GreenMetaMetric, metric.RedMetaMetric,
                                                                   metric.YellowMetaMetric, metric.GreyMetaMetric,
                                                                   metric.MissingMetaMetric)]
        self.__metrics.extend(meta_metrics)
        return Section(SectionHeader('MM', 'Meta metrieken'), meta_metrics)

    def __art_metrics(self, art: domain.RequirementSubject) -> List[domain.Metric]:
        """ Return a list of Automated Regression Test metrics for the (ART) product. """
        return self.__required_subject_metrics(art, requirement.CodeQuality, requirement.ARTCoverage,
                                               requirement.ART, requirement.TrackBranches) if art else []

    def __required_subject_metrics(self, subject: domain.RequirementSubject,
                                   *requirements: Type[domain.Requirement]) -> List[domain.Metric]:
        """ Return a list of metrics for the subject that should be measured and are applicable. """
        metrics: List[domain.Metric] = []
        for req in requirements:
            for metric_class in req.metric_classes():
                if subject.should_be_measured_by(metric_class):
                    metric_instance = metric_class(subject, project=self.__project)
                    if metric_instance.is_applicable():
                        self.__requirements.add(req)
                        metrics.append(metric_instance)
        return metrics
