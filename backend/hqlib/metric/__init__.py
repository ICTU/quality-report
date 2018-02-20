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


# Product metrics

from .product.analysis_age import SonarAnalysisAge, OWASPDependencyReportAge, OpenVASScanReportAge, \
    CheckmarxReportAge, UnittestReportAge
from .product.automated_regression_test_metrics import FailingRegressionTests, RegressionTestAge
from .product.automated_regression_test_coverage_metrics import (
    ARTStatementCoverage, ARTBranchCoverage, ARTCoverageReportAge)
from .product.duplication_metrics import JavaDuplication
from .product.logical_test_case_metrics import (
    LogicalTestCasesNotReviewed, LogicalTestCasesNotApproved, LogicalTestCasesNotAutomated,
    DurationOfManualLogicalTestCases, ManualLogicalTestCasesWithoutDuration, ManualLogicalTestCases,
    NumberOfManualLogicalTestCases)
from .product.openvas_scan_metrics import HighRiskOpenVASScanAlertsMetric, MediumRiskOpenVASScanAlertsMetric
from .product.owasp_dependency_metrics import HighPriorityOWASPDependencyWarnings, NormalPriorityOWASPDependencyWarnings
from .product.performance_metrics import PerformanceLoadTestWarnings, PerformanceLoadTestErrors, \
    PerformanceEnduranceTestWarnings, PerformanceEnduranceTestErrors, PerformanceScalabilityTestWarnings, \
    PerformanceScalabilityTestErrors, PerformanceLoadTestAge, PerformanceEnduranceTestAge, \
    PerformanceScalabilityTestAge, PerformanceLoadTestDuration, PerformanceEnduranceTestDuration, \
    PerformanceScalabilityTestDuration
from .product.size_metrics import ProductLOC, TotalLOC
from .product.source_code_metrics import CommentedLOC, CyclomaticComplexity, LongMethods, ManyParameters
from .product.unittest_metrics import FailingUnittests
from .product.unittest_coverage_metrics import UnittestLineCoverage, UnittestBranchCoverage
from .product.user_story_metrics import (
    UserStoriesNotReviewed, UserStoriesNotApproved, UserStoriesWithTooFewLogicalTestCases)
from .product.version_control_metrics import UnmergedBranches
from .product.violation_metrics import BlockerViolations, CriticalViolations, MajorViolations, NoSonar, FalsePositives
from .product.zap_scan_metrics import HighRiskZAPScanAlertsMetric, MediumRiskZAPScanAlertsMetric
from .product.checkmarx_metrics import HighRiskCheckmarxAlertsMetric, MediumRiskCheckmarxAlertsMetric

# Project metrics
from .project.bug_metrics import OpenBugs, OpenSecurityBugs, OpenStaticSecurityAnalysisBugs, TechnicalDebtIssues, \
    OpenFindings, QualityGate
from .project.last_security_test import LastSecurityTest
from .project.process_metrics import ReadyUserStoryPoints, UserStoriesWithoutSecurityRiskAssessment, \
    UserStoriesWithoutPerformanceRiskAssessment, UserStoriesInProgress, UserStoriesDuration
from .project.project_management_metrics import RiskLog, ActionActivity, IssueLogMetric, OverDueActions, StaleActions

# Team metrics
from .team.absence import TeamAbsence
from .team.spirit import TeamSpirit, TeamSpiritAge

# Document metrics
from .document.age import DocumentAge

# Environment metrics
from .environment.failing_ci_jobs import FailingCIJobs
from .environment.unused_ci_jobs import UnusedCIJobs
from .environment.version_number import (
    SonarVersion,
    SonarPluginVersionCheckStyle, SonarPluginVersionCSharp, SonarPluginVersionFindBugs, SonarPluginVersionJava,
    SonarPluginVersionJS, SonarPluginVersionPMD, SonarPluginVersionWeb, SonarPluginVersionVisualBasic,
    SonarPluginVersionPython, SonarPluginVersionTypeScript,
    SonarQualityProfileVersionCSharp, SonarQualityProfileVersionJava, SonarQualityProfileVersionJS,
    SonarQualityProfileVersionWeb, SonarQualityProfileVersionVisualBasic, SonarQualityProfileVersionPython,
    SonarQualityProfileVersionTypeScript)

# Meta metrics
from .meta_metrics import GreenMetaMetric, YellowMetaMetric, RedMetaMetric, GreyMetaMetric, MissingMetaMetric
