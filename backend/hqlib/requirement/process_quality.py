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


from .. import metric
from ..domain import Requirement


class UserStoriesAndLTCs(Requirement):
    """ Require user stories and logical testes to be reviewed and approved, and logical test cases to be automated. """
    _name = 'User stories and logical test cases'
    _metric_classes = (metric.UserStoriesNotReviewed, metric.UserStoriesNotApproved,
                       metric.LogicalTestCasesNotReviewed, metric.LogicalTestCasesNotApproved,
                       metric.UserStoriesWithTooFewLogicalTestCases, metric.LogicalTestCasesNotAutomated,
                       metric.ManualLogicalTestCases, metric.NumberOfManualLogicalTestCases)


class TrackManualLTCs(Requirement):
    """ Require the execution time of manual logical test cases to be recorded and not be too long. """
    _name = 'Track manual logical test cases'
    _metric_classes = (metric.DurationOfManualLogicalTestCases, metric.ManualLogicalTestCasesWithoutDuration)


class TrackBugs(Requirement):
    """ Require bug reports to be tracked. """
    _name = 'Track open bug reports'
    _metric_classes = (metric.OpenBugs,)


class TrackSecurityBugs(Requirement):
    """ Require security bug reports to be tracked. """
    _name = 'Track open security bug reports'
    _metric_classes = (metric.OpenSecurityBugs,)


class TrackSecurityTestDate(Requirement):
    """ Require security bug reports to be tracked. """
    _name = 'Track the last security test date'
    _metric_classes = (metric.LastSecurityTest,)


class TrackStaticSecurityBugs(Requirement):
    """ Require security bug reports to be tracked. """
    _name = 'Track open static security analysis bug reports'
    _metric_classes = (metric.OpenStaticSecurityAnalysisBugs,)


class TrackFindings(Requirement):
    """ Require findings for environments to be tracked. """
    _name = 'Track open findings'
    _metric_classes = (metric.OpenFindings,)


class TrackTechnicalDebt(Requirement):
    """ Require technical debt to be tracked. """
    _name = 'Track technical debt'
    _metric_classes = (metric.TechnicalDebtIssues,)


class TrackQualityGate(Requirement):
    """ Require the quality gate to be tracked. """
    _name = 'Track quality gate'
    _metric_classes = (metric.QualityGate,)


class TrackActions(Requirement):
    """ Require actions to be tracked. """
    _name = 'Track actions'
    _metric_classes = (metric.ActionActivity, metric.OverDueActions, metric.StaleActions)


class TrackRisks(Requirement):
    """ Require risks to be tracked. """
    _name = 'Track risks'
    _metric_classes = (metric.RiskLog,)


class TrackReadyUS(Requirement):
    """ Require the amount of ready user stories to be tracked. """
    _name = 'Track ready user stories'
    _metric_classes = (metric.ReadyUserStoryPoints,)


class TrackUserStoriesInProgress(Requirement):
    """ Require the amount of ready user stories to be tracked. """
    _name = 'Track user stories in progress'
    _metric_classes = (metric.UserStoriesInProgress,)


class TrackDurationOfUserStories(Requirement):
    """ Require the amount of ready user stories to be tracked. """
    _name = 'Track the duration of user stories'
    _metric_classes = (metric.UserStoriesDuration,)


class TrackSecurityAndPerformanceRisks(Requirement):
    """ Require user stories to have security and performance risks to be assessed. """
    _name = 'Track whether user stories have security and performance risks'
    _metric_classes = (metric.UserStoriesWithoutSecurityRiskAssessment,
                       metric.UserStoriesWithoutPerformanceRiskAssessment)
