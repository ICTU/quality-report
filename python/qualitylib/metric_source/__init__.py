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


# Test report
from .abstract.test_report import TestReport
from .test_report.jasmine_html_report import JasmineHTMLReport
from .test_report.jenkins_test_report import JenkinsTestReport
from .test_report.junit_test_report import JunitTestReport

# Coverage report
from .abstract.coverage_report import CoverageReport
from .coverage_report.jacoco import JaCoCo
from .coverage_report.ncover import NCover

# Performance report
from .abstract.performance_report import PerformanceReport
from .performance_report.jmeter import JMeter
from .performance_report.ymor import Ymor

# Version control system
from .abstract.version_control_system import VersionControlSystem
from .version_control_system.git import Git
from .version_control_system.subversion import Subversion

# Other metric sources
from .ansible_config_report import AnsibleConfigReport
from .birt import Birt
from .birt2 import Birt2
from .dependencies import Dependencies
from .history import History
from .holiday_planner import HolidayPlanner
from .jenkins import Jenkins, JenkinsOWASPDependencyReport, JenkinsYmorPerformanceReport
from .jira import Jira
from .maven import Maven
from .pom import Pom
from .release_candidates import ReleaseCandidates
from .sonar import Sonar
from .trello import TrelloBoard, TrelloActionsBoard, TrelloRiskBoard, TrelloUnreachableException
from .wiki import Wiki

