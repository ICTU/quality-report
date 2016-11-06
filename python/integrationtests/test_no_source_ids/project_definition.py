""" Project definition for testing a project with all requirements and sources, but no source ids. """

from qualitylib.domain import Project, Product, Application, Component, Team, Document, Person
from qualitylib import metric_source, requirement


# Sources
HISTORY = metric_source.History('python/integrationtests/test_no_source_ids/history.json')
GIT = metric_source.Git(url='http://git/repo')
SONAR = metric_source.Sonar('http://sonar/')
JIRA = metric_source.Jira(url='http://jira/', username='user', password='pass')

# The project
PROJECT = Project(
    'Integrationtest', name='all requirements and sources, but no source ids',
    metric_sources={
        metric_source.History: HISTORY,
        metric_source.ArchiveSystem: GIT,
        metric_source.VersionControlSystem: GIT,
        metric_source.Jira: JIRA,
        metric_source.Sonar: SONAR},
    requirements=[requirement.TrustedProductMaintainability, requirement.Web, requirement.JavaScript,
                  requirement.CSharp, requirement.Java, requirement.TrackManualLTCs,
                  requirement.TrackBugs, requirement.TrackTechnicalDebt,
                  requirement.TrackActions, requirement.TrackRisks, requirement.TrackSecurityAndPerformanceRisks,
                  requirement.TrackReadyUS, requirement.TrackJavaConsistency,
                  requirement.TrackCIJobs, requirement.TrackSonarVersion])

# Documents.
DOC = Document(name='Document XYZ')
PROJECT.add_document(DOC)

# Teams of the project.
TEAM = Team(
    name='Team 123',
    requirements=[requirement.ScrumTeam, requirement.TrackSpirit, requirement.TrackAbsence])
TEAM.add_member(Person(name='Person 1'))
TEAM.add_member(Person(name='Person 2'))
PROJECT.add_team(TEAM)

# Products the project(s) develop(s).
PRODUCT = Product(
    PROJECT, 'PR', name='Product ABC',
    requirements=[requirement.OWASPDependencies, requirement.OWASPZAP, requirement.OpenVAS,
                  requirement.UserStoriesAndLTCs, requirement.UnitTests, requirement.ART, requirement.ARTCoverage,
                  requirement.CodeQuality, requirement.Performance, requirement.NoSnapshotDependencies,
                  requirement.TrackBranches],
    unittests=Product(
        PROJECT, name='Product ABC unit tests'),
    art=Product(
        PROJECT, name='Product ABC ART', requirements=[requirement.CodeQuality, requirement.TrackBranches]),
    jsf=Product(
        PROJECT, name='Product ABC JSF', requirements=[requirement.JSFCodeQuality]))

PRODUCT_V1 = Product(
    PROJECT, 'PT', name='Product ABC v1',
    product_version='1',
    requirements=[requirement.OWASPDependencies, requirement.OWASPZAP, requirement.UserStoriesAndLTCs,
                  requirement.UnitTests, requirement.ART, requirement.CodeQuality, requirement.Performance,
                  requirement.NoSnapshotDependencies, requirement.TrackBranches],
    unittests=Product(
        PROJECT, name='Product ABC v1 unit tests'),
    art=Product(
        PROJECT, name='Product ABC v1 ART', requirements=[requirement.CodeQuality, requirement.TrackBranches]),
    jsf=Product(
        PROJECT, name='Product ABC v1 JSF', requirements=[requirement.JSFCodeQuality]))

APPLICATION = Application(PROJECT, 'AP', name='Application FOO')
COMPONENT = Component(PROJECT, 'CO', name='Component FOO')

PROJECT.add_product(PRODUCT)
PROJECT.add_product(PRODUCT_V1)
PROJECT.add_product(APPLICATION)
PROJECT.add_product(COMPONENT)

# Dashboard layout

# Columns in the dashboard is specified as a list of tuples. Each tuple
# contains a column header and the column span.
DASHBOARD_COLUMNS = [('Products', 1), ('Teams', 1), ('Algemeen', 2)]

# Rows in the dashboard is a list of row tuples. Each row tuple consists of
# tuples that describe a cell in the dashboard. Each cell is a tuple containing
# the product or team and the color. Optionally the cell tuple can contain a
# third value which is a tuple containing the column and row span for the cell.
DASHBOARD_ROWS = [((PRODUCT, 'lightsteelblue'), (TEAM, 'lavender', (1, 4)), ('PD', 'lightgrey'), ('PE', 'lightgrey')),
                  ((PRODUCT_V1, 'lightsteelblue'), ('PC', 'lightgrey', (1, 3)), ('MM', 'lightgrey', (1, 3))),
                  ((APPLICATION, 'lightsteelblue'),),
                  ((COMPONENT, 'lightsteelblue'),)]

PROJECT.set_dashboard(DASHBOARD_COLUMNS, DASHBOARD_ROWS)
