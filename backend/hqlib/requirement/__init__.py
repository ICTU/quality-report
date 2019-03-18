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


# Package for concrete requirements, not specific to a specific project.

from .product_quality import TrustedProductMaintainability, OWASPDependencies, Checkmarx, OWASPZAP, UnitTests, \
    UnitTestCoverage, ART, ARTCoverage, AggregatedTestCoverage, CodeQuality, ViolationsBySeverity, ViolationsByType,\
    OJAuditViolations, PerformanceLoad, PerformanceEndurance, PerformanceScalability, TrackBranches, Accessibility
from .sonar import Java, CSharp, JavaScript, Web, Python, VisualBasic, TypeScript
from .process_quality import UserStoriesAndLTCs, TrackManualLTCs, TrackBugs, TrackSecurityBugs, \
    TrackStaticSecurityBugs, TrackFindings, TrackTechnicalDebt, TrackQualityGate, TrackActions, TrackRisks, \
    TrackReadyUS, TrackUserStoriesInProgress, TrackDurationOfUserStories, TrackSecurityAndPerformanceRisks, \
    TrackSecurityTestDate, PredictUserStories
from .environment import TrackCIJobs, TrackSonarVersion, OpenVAS
from .team import TrackSpirit
from .document import TrackDocumentAge
