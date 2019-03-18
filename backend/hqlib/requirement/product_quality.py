"""
Copyright 2012-2019 Ministerie van Sociale Zaken en Werkgelegenheid

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


from .. import metric
from ..domain import Requirement


class OWASPDependencies(Requirement):
    """ Require dependencies to be analyzed for vulnerabilities. """
    _name = 'OWASP Top 10 2013 Dependencies'
    _url = 'https://www.owasp.org/'
    _metric_classes = (metric.HighPriorityOWASPDependencyWarnings, metric.NormalPriorityOWASPDependencyWarnings,
                       metric.OWASPDependencyReportAge)


class Checkmarx(Requirement):
    """ Require applications to be statically analyzed for security vulnerabilities. """
    _name = 'Checkmarx SCA'
    _url = 'https://www.checkmarx.com/'
    _metric_classes = (metric.HighRiskCheckmarxAlertsMetric, metric.MediumRiskCheckmarxAlertsMetric,
                       metric.CheckmarxReportAge)


class OWASPZAP(Requirement):
    """ Require OWASP Zap to be used to scan applications for security vulnerabilities. """
    _name = 'OWASP Top 10 2013 ZAP'
    _url = 'https://www.owasp.org/'
    _metric_classes = (metric.HighRiskZAPScanAlertsMetric, metric.MediumRiskZAPScanAlertsMetric)


class TrustedProductMaintainability(Requirement):
    """ Require the total size of the source code to be tracked. """
    _name = 'Trusted Product Maintainability, version 6.1'
    _url = 'http://www.sig.eu/nl/diensten/Software%20Product%20Certificering/Evaluation%20Criteria/'
    _metric_classes = (metric.TotalLOC,)


class UnitTests(Requirement):
    """ Require the product to have unit tests. """
    _name = 'Unit tests'
    _metric_classes = (metric.FailingUnittests, metric.UnittestReportAge)


class UnitTestCoverage(Requirement):
    """ Require the product to have unit tests coverage to be measured. """
    _name = 'Unit test coverage'
    _metric_classes = (metric.UnittestLineCoverage, metric.UnittestBranchCoverage)


class ART(Requirement):
    """ Require the product to have an automated regression test suite. """
    _name = 'Automated regression tests'
    _metric_classes = (metric.FailingRegressionTests, metric.RegressionTestAge)


class ARTCoverage(Requirement):
    """ Require the coverage of the automated regression test suite to be measured. """
    _name = 'Automated regression test coverage'
    _metric_classes = (metric.ARTStatementCoverage, metric.ARTBranchCoverage, metric.ARTCoverageReportAge)


class AggregatedTestCoverage(Requirement):
    """ Require the coverage of the aggregated tests to be measured. """
    _name = 'Aggregated test coverage'
    _metric_classes = (metric.AggregatedTestStatementCoverage, metric.AggregatedTestBranchCoverage,
                       metric.AggregatedTestCoverageReportAge)


class CodeQuality(Requirement):
    """ Require the source code quality of the product to be tracked. """
    _name = 'Code quality'
    _metric_classes = (metric.CyclomaticComplexity, metric.JavaDuplication, metric.ProductLOC, metric.LongMethods,
                       metric.ManyParameters, metric.CommentedLOC, metric.SonarAnalysisAge,
                       metric.ViolationSuppressions)


class ViolationsBySeverity(Requirement):
    """ Require violations of programming rules to be tracked. """
    _name = 'Violations by severity'
    _metric_classes = (metric.BlockerViolations, metric.CriticalViolations, metric.MajorViolations)


class ViolationsByType(Requirement):
    """ Require violations of programming rules to be tracked. """
    _name = 'Violations by type'
    _metric_classes = (metric.MaintainabilityBugs, metric.Vulnerabilities, metric.CodeSmells)


class OJAuditViolations(Requirement):
    """ Require OJ Audit violations to be tracked. """
    _name = 'OJAudit violations'
    _metric_classes = (metric.OJAuditWarnings, metric.OJAuditErrors, metric.OJAuditExceptions)


class Accessibility(Requirement):
    """ Require accessibility violations of programming rules to be tracked. """
    _name = 'Accessibility'
    _metric_classes = (metric.AccessibilityMetric,)


class PerformanceLoad(Requirement):
    """ Require a performance load test. """
    _name = 'Performance load'
    _metric_classes = (metric.PerformanceLoadTestWarnings, metric.PerformanceLoadTestErrors,
                       metric.PerformanceLoadTestAge, metric.PerformanceLoadTestDuration,
                       metric.PerformanceLoadTestFaultPercentage)


class PerformanceEndurance(Requirement):
    """ Require a performance endurance test. """
    _name = 'Performance endurance'
    _metric_classes = (metric.PerformanceEnduranceTestWarnings, metric.PerformanceEnduranceTestErrors,
                       metric.PerformanceEnduranceTestAge, metric.PerformanceEnduranceTestDuration,
                       metric.PerformanceEnduranceTestFaultPercentage)


class PerformanceScalability(Requirement):
    """ Require a performance scalability (stress) test. """
    _name = 'Performance scalability'
    _metric_classes = (metric.PerformanceScalabilityTestWarnings, metric.PerformanceScalabilityTestErrors,
                       metric.PerformanceScalabilityTestAge, metric.PerformanceScalabilityTestDuration,
                       metric.PerformanceScalabilityTestFaultPercentage)


class TrackBranches(Requirement):
    """ Track branches for unmerged revisions. """
    _name = 'Track branches'
    _metric_classes = (metric.UnmergedBranches,)
