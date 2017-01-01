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

from __future__ import absolute_import

from .. import metric
from ..domain import Requirement


class OWASPDependencies(Requirement):
    """ Require dependencies to be analyzed for vulnerabilities. """
    _name = 'OWASP Top 10 2013 Dependencies'
    url = 'https://www.owasp.org/'
    _metric_classes = (metric.HighPriorityOWASPDependencyWarnings, metric.NormalPriorityOWASPDependencyWarnings)


class OWASPZAP(Requirement):
    """ Require OWASP Zap to be used to scan applications for security vulnerabilities. """
    _name = 'OWASP Top 10 2013 ZAP'
    url = 'https://www.owasp.org/'
    _metric_classes = (metric.HighRiskZAPScanAlertsMetric, metric.MediumRiskZAPScanAlertsMetric)


class TrustedProductMaintainability(Requirement):
    """ Require the total size of the source code to be tracked. """
    _name = 'Trusted Product Maintainability, version 6.1'
    url = 'http://www.sig.eu/nl/diensten/Software%20Product%20Certificering/Evaluation%20Criteria/'
    _metric_classes = (metric.TotalLOC,)


class UnitTests(Requirement):
    """ Require the product to have unit and/or integration tests. """
    _name = 'Unit and/or integration tests'
    _metric_classes = (metric.FailingUnittests, metric.UnittestLineCoverage, metric.UnittestBranchCoverage,
                       metric.IntegrationtestLineCoverage, metric.IntegrationtestBranchCoverage,
                       metric.UnitAndIntegrationTestLineCoverage, metric.UnitAndIntegrationTestBranchCoverage)


class ART(Requirement):
    """ Require the product to have an automated regression test suite. """
    _name = 'Automated regression tests'
    _metric_classes = (metric.FailingRegressionTests, metric.RegressionTestAge)


class ARTCoverage(Requirement):
    """ Require the coverage of the automated regression test suite to be measured. """
    _name = 'Automated regression test coverage'
    _metric_classes = (metric.ARTStatementCoverage, metric.ARTBranchCoverage)


class CodeQuality(Requirement):
    """ Require the source code quality of the product to be tracked. """
    _name = 'Code quality'
    _metric_classes = (metric.BlockerViolations, metric.CriticalViolations, metric.MajorViolations,
                       metric.CyclomaticComplexity, metric.CyclicDependencies, metric.JavaDuplication,
                       metric.ProductLOC, metric.LongMethods, metric.ManyParameters, metric.CommentedLOC,
                       metric.NoSonar, metric.FalsePositives, metric.SonarAnalysisAge)


class JSFCodeQuality(Requirement):
    """ Require the source code quality of the JSF component be tracked. """
    _name = 'JSF code quality'
    _metric_classes = (metric.JsfDuplication, metric.ProductLOC)


class PerformanceLoad(Requirement):
    """ Require a performance load test. """
    _name = 'Performance load'
    _metric_classes = (metric.PerformanceLoadTestWarnings, metric.PerformanceLoadTestErrors)


class PerformanceEndurance(Requirement):
    """ Require a performance endurance test. """
    _name = 'Performance endurance'
    _metric_classes = (metric.PerformanceEnduranceTestWarnings, metric.PerformanceEnduranceTestErrors)


class PerformanceScalability(Requirement):
    """ Require a performance scalability (stress) test. """
    _name = 'Performance scalability'
    _metric_classes = (metric.PerformanceScalabilityTestWarnings, metric.PerformanceScalabilityTestErrors)


class TrackBranches(Requirement):
    """ Track branches for unmerged revisions. """
    _name = 'Track branches'
    _metric_classes = (metric.UnmergedBranches,)
