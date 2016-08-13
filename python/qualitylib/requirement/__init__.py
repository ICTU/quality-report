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


# Package for concrete requirements, not specific to a specific project.

from .product_quality import TRUSTED_PRODUCT_MAINTAINABILITY, OWASP_DEPENDENCIES, OWASP_ZAP, UNITTESTS, ART, ART_COVERAGE, \
    CODE_QUALITY, JSF_CODE_QUALITY, PERFORMANCE, PERFORMANCE_YMOR, NO_SNAPSHOT_DEPENDENCIES, TRACK_BRANCHES
from .sonar import JAVA, C_SHARP, JAVASCRIPT, WEB
from .process_quality import USER_STORIES_AND_LTCS, TRACK_MANUAL_LTCS, TRACK_BUGS, \
    TRACK_TECHNICAL_DEBT, TRACK_ACTIONS, TRACK_RISKS, TRACK_READY_US
from .environment import TRACK_JAVA_CONSISTENCY, TRACK_CI_JOBS, TRACK_SONAR_VERSION
from .team import SCRUM_TEAM, TRACK_SPIRIT, TRACK_ABSENCE
from .document import TRACK_DOCUMENT_AGE
