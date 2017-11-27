from hqlib import metric_source
from hqlib.domain import Project, Application

# Metric sources
HISTORY = metric_source.CompactHistory("history.json")
SONAR = metric_source.Sonar("https://sonarcloud.io/")

# The project
PROJECT = Project(
    "ICTU", name="HQ",
    metric_sources={
        metric_source.History: HISTORY,
        metric_source.Sonar: SONAR})

# The product developed by the project
APPLICATION = Application(
    short_name="HQ", name="HQ - Holistic Software Quality Reporting",
    metric_source_ids={
        SONAR: 'nl.ictu:hq'})

PROJECT.add_product(APPLICATION)

# Dashboard layout
# Columns in the dashboard is specified as a list of tuples. Each tuple
# contains a column header and the column span.
DASHBOARD_COLUMNS = [("Product", 1), ("Meta", 1)]

# Rows in the dashboard is a list of row tuples. Each row tuple consists of
# tuples that describe a cell in the dashboard. Each cell is a tuple containing
# the product or team and the color. Optionally the cell tuple can contain a
# third value which is a tuple containing the column and row span for the cell.
DASHBOARD_ROWS = [
    [(APPLICATION, "lightsteelblue"), ("MM", "lavender")]
]

PROJECT.set_dashboard(DASHBOARD_COLUMNS, DASHBOARD_ROWS)
