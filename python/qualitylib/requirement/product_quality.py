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

from ..domain import Requirement
from .. import metric


class OWASPDependencies(Requirement):
    _name = 'OWASP Top 10 2013 Dependencies'
    url = 'https://www.owasp.org/'
    _metric_classes = (metric.HighPriorityOWASPDependencyWarnings, metric.NormalPriorityOWASPDependencyWarnings)


class OWASPZAP(Requirement):
    _name = 'OWASP Top 10 2013 ZAP'
    url = 'https://www.owasp.org/'
    _metric_classes = (metric.HighRiskZAPScanAlertsMetric, metric.MediumRiskZAPScanAlertsMetric)


class OpenVAS(Requirement):
    _name = 'Open VAS'
    _metric_classes = (metric.HighRiskOpenVASScanAlertsMetric, metric.MediumRiskOpenVASScanAlertsMetric)


class TrustedProductMaintainability(Requirement):
    _name = 'Trusted Product Maintainability, version 6.1'
    url = 'http://www.sig.eu/nl/diensten/Software%20Product%20Certificering/Evaluation%20Criteria/'
    _metric_classes = (metric.TotalLOC,)


class UnitTests(Requirement):
    _name = 'Unit and/or integration tests'
    _metric_classes = (metric.FailingUnittests, metric.UnittestLineCoverage, metric.UnittestBranchCoverage,
                       metric.IntegrationtestLineCoverage, metric.IntegrationtestBranchCoverage,
                       metric.UnitAndIntegrationTestLineCoverage, metric.UnitAndIntegrationTestBranchCoverage)


class ART(Requirement):
    _name = 'Automated regression tests'
    _metric_classes = (metric.FailingRegressionTests, metric.RegressionTestAge)


class ARTCoverage(Requirement):
    _name = 'Automated regression test coverage'
    _metric_classes = (metric.ARTStatementCoverage, metric.ARTBranchCoverage)


class CodeQuality(Requirement):
    _name = 'Code quality'
    _metric_classes = (metric.BlockerViolations, metric.CriticalViolations, metric.MajorViolations,
                       metric.CyclomaticComplexity, metric.CyclicDependencies, metric.JavaDuplication,
                       metric.ProductLOC, metric.LongMethods, metric.ManyParameters, metric.CommentedLOC,
                       metric.NoSonar, metric.FalsePositives, metric.SonarAnalysisAge)


class JSFCodeQuality(Requirement):
    _name = 'JSF code quality'
    _metric_classes = (metric.JsfDuplication, metric.ProductLOC)


class Performance(Requirement):
    _name = 'Performance'
    _metric_classes = (metric.PerformanceLoadTestWarnings, metric.PerformanceLoadTestErrors,
                       metric.PerformanceEnduranceTestWarnings, metric.PerformanceEnduranceTestErrors,
                       metric.PerformanceScalabilityTestWarnings, metric.PerformanceScalabilityTestErrors)


class NoSnapshotDependencies(Requirement):
    _name = 'No snapshot dependencies'
    _metric_classes = (metric.SnapshotDependencies,)


class TrackBranches(Requirement):
    _name = 'Track branches'
    _metric_classes = (metric.UnmergedBranches,)
