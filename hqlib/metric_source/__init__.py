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

from .abstract.archive_system import ArchiveSystem
from .abstract.coverage_report import CoverageReport
from .abstract.owasp_dependency_report import OWASPDependencyReport
from .abstract.performance_report import PerformanceLoadTestReport, PerformanceEnduranceTestReport, \
    PerformanceScalabilityTestReport
from .abstract.team_spirit import TeamSpirit
from .abstract.test_report import TestReport
from .abstract.version_control_system import VersionControlSystem
from .ansible_config_report import AnsibleConfigReport
from .archive_system.nexus import Nexus
from .birt import Birt
from .coverage_report.jacoco import JaCoCo
from .coverage_report.ncover import NCover
from .history import History
from .holiday_planner import HolidayPlanner
from .jenkins import Jenkins
from .jira import Jira
from .open_vas_scan_report import OpenVASScanReport
from .owasp_dependency_report.jenkins_owasp_dependency_plugin import JenkinsOWASPDependencyReport
from .owasp_dependency_report.owasp_dependency_xml_report import OWASPDependencyXMLReport
from .performance_report.jmeter import JMeterPerformanceLoadTestReport, JMeterPerformanceEnduranceTestReport, \
    JMeterPerformanceScalabilityTestReport
from .performance_report.silkperformer import SilkPerformerPerformanceLoadTestReport, \
    SilkPerformerPerformanceEnduranceTestReport, SilkPerformerPerformanceScalabilityTestReport
from .sonar import Sonar
from .team_spirit.happiness import Happiness
from .team_spirit.wiki import Wiki
from .test_report.jenkins_test_report import JenkinsTestReport
from .test_report.junit_test_report import JunitTestReport
from .trello import TrelloBoard, TrelloActionsBoard, TrelloRiskBoard
from .url_opener import UrlOpener
from .version_control_system.git import Git
from .version_control_system.subversion import Subversion
from .zap_scan_report import ZAPScanReport
