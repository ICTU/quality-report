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


SCRUM_TEAM = Requirement(
    name='Scrum team',
    identifier='SCRUM_TEAM',
    metric_classes=(metric.TeamProgress,))

TRACK_SPIRIT = Requirement(
    name='Track spirit',
    identifier='TRACK_SPIRIT',
    metric_classes=(metric.TeamSpirit,))

TRACK_ABSENCE = Requirement(
    name='Track absence',
    identifier='TRACK_ABSENCE',
    metric_classes=(metric.TeamAbsence,))
