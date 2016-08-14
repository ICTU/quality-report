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

from ..domain import Requirement
from .. import metric


TRACK_JAVA_CONSISTENCY = Requirement(
    name='Track Java consistency',
    identifier='TRACK_JAVA_CONSISTENCY',
    metric_classes=(metric.JavaVersionConsistency,))

TRACK_CI_JOBS = Requirement(
    name='Track status and usage of continuous integration jobs',
    identifier='TRACK_CI_JOBS',
    metric_classes=(metric.FailingCIJobs, metric.UnusedCIJobs))

TRACK_SONAR_VERSION = Requirement(
    name='Track Sonar version',
    identifier='TRACK_SONAR_VERSION',
    metric_classes=(metric.SonarVersion,))
