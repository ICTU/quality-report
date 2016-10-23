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


class UserStoriesAndLTCs(Requirement):
    _name = 'User stories and logical test cases'
    _metric_classes = (metric.UserStoriesNotReviewed, metric.UserStoriesNotApproved,
                       metric.LogicalTestCasesNotReviewed, metric.LogicalTestCasesNotApproved,
                       metric.UserStoriesWithTooFewLogicalTestCases, metric.LogicalTestCasesNotAutomated,
                       metric.ManualLogicalTestCases, metric.NumberOfManualLogicalTestCases)


class TrackManualLTCs(Requirement):
    _name = 'Track manual logical test cases'
    _metric_classes = (metric.DurationOfManualLogicalTestCases, metric.ManualLogicalTestCasesWithoutDuration)


class TrackBugs(Requirement):
    _name = 'Track open bug reports'
    _metric_classes = (metric.OpenBugs, metric.OpenSecurityBugs, metric.OpenStaticSecurityAnalysisBugs)


class TrackTechnicalDebt(Requirement):
    _name = 'Track technical debt'
    _metric_classes = (metric.TechnicalDebtIssues,)


class TrackActions(Requirement):
    _name = 'Track actions'
    _metric_classes = (metric.ActionActivity, metric.ActionAge)


class TrackRisks(Requirement):
    _name = 'Track risks'
    _metric_classes = (metric.RiskLog,)


class TrackReadyUS(Requirement):
    _name = 'Track ready user stories'
    _metric_classes = (metric.ReadyUserStoryPoints,)


class TrackSecurityAndPerformanceRisks(Requirement):
    _name = 'Track whether user stories have security and performance risks'
    _metric_classes = (metric.UserStoriesWithoutSecurityRiskAssessment,
                       metric.UserStoriesWithoutPerformanceRiskAssessment)
