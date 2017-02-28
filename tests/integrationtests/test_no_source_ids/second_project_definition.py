""" Project definition for testing a project with all requirements and sources, but no source ids. """

from hqlib import metric_source
from hqlib.domain import Project

import project_definition

# Sources
HISTORY = metric_source.History('tests/integrationtests/test_no_source_ids/second_history.json')

# The project
PROJECT = Project(
    'Integrationtest', name='all requirements and sources, but no source ids',
    metric_sources={
        metric_source.History: HISTORY,
        metric_source.ArchiveSystem: project_definition.GIT,
        metric_source.VersionControlSystem: project_definition.GIT,
        metric_source.Jira: project_definition.JIRA,
        metric_source.Sonar: project_definition.SONAR},
    requirements=project_definition.PROJECT.requirements())

# Documents.
PROJECT.add_document(project_definition.DOC)

# Development environment
PROJECT.add_environment(project_definition.ENVIRONMENT)

# Teams of the project.
PROJECT.add_team(project_definition.TEAM)

# Products the project(s) develop(s).
PROJECT.add_product(project_definition.PRODUCT)
PROJECT.add_product(project_definition.APPLICATION)
PROJECT.add_product(project_definition.COMPONENT)

PROJECT.set_dashboard(project_definition.DASHBOARD_COLUMNS, project_definition.DASHBOARD_ROWS)
