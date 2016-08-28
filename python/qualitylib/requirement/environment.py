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


class TrackJavaConsistency(Requirement):
    _name = 'Track Java consistency'
    _metric_classes = (metric.JavaVersionConsistency,)


class TrackCIJobs(Requirement):
    _name = 'Track status and usage of continuous integration jobs'
    _metric_classes = (metric.FailingCIJobs, metric.UnusedCIJobs)


class TrackSonarVersion(Requirement):
    _name = 'Track Sonar version'
    _metric_classes = (metric.SonarVersion,)
