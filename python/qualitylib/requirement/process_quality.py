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


USER_STORIES_AND_LTCS = Requirement(
    name='User stories and logical test cases',
    identifier='USER_STORIES_AND_LTCS',
    metric_classes=(metric.UserStoriesNotReviewed, metric.UserStoriesNotApproved,
                    metric.LogicalTestCasesNotReviewed, metric.LogicalTestCasesNotApproved,
                    metric.UserStoriesWithTooFewLogicalTestCases, metric.LogicalTestCasesNotAutomated,
                    metric.ManualLogicalTestCases, metric.NumberOfManualLogicalTestCases))

TRACK_MANUAL_LTCS = Requirement(
    name='Track manual logical test cases',
    identifier='TRACK_MANUAL_LTCS',
    metric_classes=(metric.DurationOfManualLogicalTestCases, metric.ManualLogicalTestCasesWithoutDuration))

TRACK_BUGS = Requirement(
    name='Track open bug reports',
    identifier='TRACK_BUGS',
    metric_classes=(metric.OpenBugs, metric.OpenSecurityBugs))

TRACK_TECHNICAL_DEBT = Requirement(
    name='Track technical debt',
    identifier='TRACK_TECHNICAL_DEBT',
    metric_classes=(metric.TechnicalDebtIssues,))

TRACK_ACTIONS = Requirement(
    name='Track actions',
    identifier='TRACK_ACTIONS',
    metric_classes=(metric.ActionActivity, metric.ActionAge))

TRACK_RISKS = Requirement(
    name='Track risks',
    identifier='TRACK_RISKS',
    metric_classes=(metric.RiskLog,))

TRACK_READY_US = Requirement(
    name='Track ready user stories',
    identifier='TRACK_READY_US',
    metric_classes=(metric.ReadyUserStoryPoints,))
