""" Project definition for testing a project with all requirements but no sources. """

from hqlib import metric_source, requirement
from hqlib.domain import Project, Product, Team, Document, Application, Component, Environment, Process

# Sources
HISTORY = metric_source.CompactHistory('tests/integrationtests/test_all_requirements_no_sources/history.json')

# The project
PROJECT = Project(
    'Integrationtest', name='all requirements but no sources',
    metric_sources={metric_source.History: HISTORY},
    added_requirements=Project.optional_requirements())

# Documents.
DOC = Document(name='Document XYZ', added_requirements=Document.optional_requirements())
PROJECT.add_document(DOC)

# Teams of the project.
TEAM = Team(name='Team 123', short_name='TE', added_requirements=Team.optional_requirements())
PROJECT.add_team(TEAM)

# Environment of the project

ENVIRONMENT = Environment(name='Environment', short_name='EN', added_requirements=Environment.optional_requirements())
PROJECT.add_environment(ENVIRONMENT)

# Process of the project

PROCESS = Process(name="Scrum", short_name="SC", added_requirements=Process.optional_requirements())
PROJECT.add_process(PROCESS)

# Products the project develops.
PRODUCT = Product(
    short_name='PR', name='Product ABC',
    added_requirements=Product.optional_requirements(),
    art=Product(
        name='Product ABC ART', added_requirements=[requirement.CodeQuality, requirement.TrackBranches]))


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
