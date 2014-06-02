''' Project definition for the Quality Report software itself. '''

from qualitylib.domain import Project, Product, Team, TechnicalDebtTarget, \
    DynamicTechnicalDebtTarget
from qualitylib import metric_source, metric
import datetime


BUILD_SERVER = metric_source.Jenkins('http://jenkins/', 
                                     username='jenkings_user', 
                                     password='jenkings_password',
                                     job_re='-metrics')
SONAR = metric_source.Sonar('http://sonar/', username='sonar_user',
                            password='sonar_admin')
HISTORY = metric_source.History('quality-data/quality_report/history.json')
SUBVERSION = metric_source.Subversion()
ACOCO = metric_source.JaCoCo(BUILD_SERVER.url() + 'job/%s/lastSuccessfulBuild/'
                              'artifact/trunk/coveragereport/index.html', 
                              BUILD_SERVER.username(), BUILD_SERVER.password())

# The project
PROJECT = Project('Organization name', 'Quality Report', 
                  build_server=BUILD_SERVER, sonar=SONAR, history=HISTORY, 
                  maven_binary='mvn3', subversion=SUBVERSION, 
                  pom=metric_source.Pom(),
                  additional_resources=[
                      dict(title='GitHub Quality Report', 
                           url='https://github.com/ICTU/quality-report')] )

# Teams of the project.
QUALITY_TEAM = Team('Quality team', is_support_team=True)
PROJECT.add_team(QUALITY_TEAM, responsible=True)

# Products the project(s) develop(s).
QUALITY_REPORT_UNITTESTS = \
    Product(PROJECT, sonar_id='nl.ictu.quality-report:quality-report')

QUALITY_REPORT = \
    Product(PROJECT, 'QR',
            sonar_id = 'nl.ictu.quality-report:quality-report',
            svn_path='http://svn/commons/scripts/quality-report/',
            unittests=QUALITY_REPORT_UNITTESTS,
            technical_debt_targets={
                metric.UnittestCoverage:
                    TechnicalDebtTarget(0, 'Sonar incorrectly reports 0% ' \
                                        'unit test coverage', '%'),
                metric.MajorViolations:
                    DynamicTechnicalDebtTarget(47, datetime.datetime(2014, 2, 
                        12), 25, datetime.datetime(2014, 6, 1), 
                        unit='major violations')},
            metric_source_ids={JACOCO: 'quality-report-coverage-report'})

PROJECT.add_product(QUALITY_REPORT)

# Dashboard layout

# Columns in the dashboard is specified as a list of tuples. Each tuple
# contains a column header and the column span.
DASHBOARD_COLUMNS = [('Products', 1), ('Teams', 1)]

# Rows in the dashboard is a list of row tuples. Each row tuple consists of
# tuples that describe a cell in the dashboard. Each cell is a tuple containing
# the two letter abbreviation for the product or team, the name of the product
# or team and the color. Optionally the cell tuple can contain a fourth value
# which is a tuple containing the column and row span for the cell.
DASHBOARD_ROWS = [(('qr', 'quality-report', 'lightsteelblue'),
                   ('qu', 'quality team', 'lavender'))]

PROJECT.set_dashboard(DASHBOARD_COLUMNS, DASHBOARD_ROWS)
