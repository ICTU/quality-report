""" Project definition for testing a project with all requirements and sources, but no source ids. """

from hqlib import metric_source, requirement
from hqlib.domain import Project, Product, Application, Component, Team, Document, Person, Environment

# Sources
HISTORY = metric_source.History('tests/integrationtests/test_no_source_ids/history.json')
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
    added_requirements=Project.optional_requirements())

# Documents.
DOC = Document(name='Document XYZ')
PROJECT.add_document(DOC)

# Teams of the project.
TEAM = Team(
    name='Team 123', short_name='TE',
    added_requirements=Team.optional_requirements())
TEAM.add_member(Person(name='Person 1'))
TEAM.add_member(Person(name='Person 2'))
PROJECT.add_team(TEAM)

# Environment of the project

ENVIRONMENT = Environment(name='Environment', short_name='EN', added_requirements=Environment.optional_requirements())
PROJECT.add_environment(ENVIRONMENT)

# Products the project(s) develop(s).
PRODUCT = Product(
    short_name='PR', name='Product ABC',
    added_requirements=Product.optional_requirements(),
    art=Product(
        name='Product ABC ART', added_requirements=[requirement.CodeQuality, requirement.TrackBranches]),
    jsf=Product(
        name='Product ABC JSF', added_requirements=[requirement.JSFCodeQuality]))


APPLICATION = Application(short_name='AP', name='Application FOO',
                          added_requirements=Application.optional_requirements())
COMPONENT = Component(short_name='CO', name='Component FOO',
                      added_requirements=Component.optional_requirements())

PROJECT.add_product(PRODUCT)
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
DASHBOARD_ROWS = [((PRODUCT, 'lightsteelblue'), (TEAM, 'lavender', (1, 3)), ('PD', 'lightgrey'),
                   (ENVIRONMENT, 'lightgrey')),
                  ((APPLICATION, 'lightsteelblue'), ('PC', 'lightgrey', (1, 2)), ('MM', 'lightgrey', (1, 2))),
                  ((COMPONENT, 'lightsteelblue'),)]

PROJECT.set_dashboard(DASHBOARD_COLUMNS, DASHBOARD_ROWS)
