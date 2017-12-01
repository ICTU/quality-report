""" Project definition for testing metric options. """

from hqlib import metric, domain

# The project
PROJECT = domain.Project(
    'Integrationtest', name='metric options')

# Products the project develops.
APPLICATION = domain.Application(
    short_name='AP', name='Application FOO',
    metric_options={
        metric.ARTStatementCoverage: dict(
            debt_target=domain.TechnicalDebtTarget(42, explanation="How do we explain this?")),
        metric.ARTBranchCoverage: dict(target=35, low_target=30)
    })

PROJECT.add_product(APPLICATION)

# Dashboard layout

# Columns in the dashboard is specified as a list of tuples. Each tuple
# contains a column header and the column span.
DASHBOARD_COLUMNS = [('Products', 1), ('Algemeen', 1)]

# Rows in the dashboard is a list of row tuples. Each row tuple consists of
# tuples that describe a cell in the dashboard. Each cell is a tuple containing
# the product or team and the color. Optionally the cell tuple can contain a
# third value which is a tuple containing the column and row span for the cell.
DASHBOARD_ROWS = [((APPLICATION, 'lightsteelblue', (1, 3)), ('PD', 'lightgrey')),
                  (('PC', 'lightgrey'),),
                  (('MM', 'lightgrey'),)]

PROJECT.set_dashboard(DASHBOARD_COLUMNS, DASHBOARD_ROWS)
