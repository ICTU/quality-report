''' Project definition for the Quality Report software itself. '''

from qualitylib.domain import Project, Product, Team, TechnicalDebtTarget, \
    DynamicTechnicalDebtTarget, MetricSource
from qualitylib import metric_source, metric
import datetime


BUILD_SERVER = metric_source.Jenkins('http://jenkins/', 
                                     username='jenkings_user', 
                                     password='jenkings_password',
                                     job_re='-metrics')
MAVEN = metric_source.Maven(binary='mvn3')
SUBVERSION = metric_source.Subversion()
SONAR = metric_source.Sonar('http://sonar/', username='sonar_user',
                            password='sonar_admin', maven=MAVEN,
                            version_control_system=SUBVERSION)
HISTORY = metric_source.History('quality-data/quality_report/history.json')
JACOCO = metric_source.JaCoCo(BUILD_SERVER.url() + 'job/%s/lastSuccessfulBuild/'
                              'artifact/trunk/coveragereport/index.html', 
                              BUILD_SERVER.username(), BUILD_SERVER.password())
POM = metric_source.Pom(sonar=SONAR, version_control_system=SUBVERSION)

# The project
PROJECT = Project('Organization name', name='Quality Report', 
                  metric_sources={
                      metric_source.Jenkins: BUILD_SERVER,
                      metric_source.VersionControlSystem: SUBVERSION,
                      metric_source.Sonar: SONAR,
                      metric_source.JaCoCo: JACOCO,
                      metric_source.Pom: POM,
                      metric_source.History: HISTORY},
                  additional_resources=[
                      MetricSource(name='GitHub Quality Report',
                               url='https://github.com/ICTU/quality-report')],
                  # Override the total loc metric targets:
                  targets={metric.TotalLOC: 1000000},
                  low_targets={metric.TotalLOC: 1200000})

# Teams of the project.
QUALITY_TEAM = Team(name='Quality team')
PROJECT.add_team(QUALITY_TEAM)

# Documents of the project.
QUALITY_PLAN_URL = SVN_BASE + 'http://svn/commons/docs/quality_plan.doc'
PROJECT.add_document(Document(name='Quality plan', url=QUALITY_PLAN_URL,
    metric_source_ids={SUBVERSION: QUALITY_PLAN_URL}))

# Products the project(s) develop(s).
QUALITY_REPORT_UNITTESTS = \
    Product(PROJECT,
            metric_source_ids={
                SONAR: 'nl.ictu.quality-report:quality-report',
                SUBVERSION: 'http://svn/commons/scripts/quality-report/'})

QUALITY_REPORT = \
    Product(PROJECT, 'QR',
            unittests=QUALITY_REPORT_UNITTESTS,
            technical_debt_targets={
                metric.UnittestLineCoverage:
                    TechnicalDebtTarget(0, 'Sonar incorrectly reports 0% ' \
                                           'unit test coverage', '%'),
                metric.MajorViolations:
                    DynamicTechnicalDebtTarget(47, datetime.datetime(2014, 2, 
                        12), 25, datetime.datetime(2014, 6, 1), 
                        unit='major violations')},
            metric_source_ids={
                SONAR: 'nl.ictu.quality-report:quality-report',
                JACOCO: 'quality-report-coverage-report',
                SUBVERSION: 'http://svn/commons/scripts/quality-report/'},
            metric_options={
                metric.UnmergedBranches: dict(branches_to_ignore='spike')},
            product_branches={'auto-discovery-branch':
                                   {SUBVERSION: 'auto-discovery',
                                    SONAR: 'auto_discovery'}})

PROJECT.add_product(QUALITY_REPORT)

# Dashboard layout

# Columns in the dashboard is specified as a list of tuples. Each tuple
# contains a column header and the column span.
DASHBOARD_COLUMNS = [('Products', 1), ('Teams', 1)]

# Rows in the dashboard is a list of row tuples. Each row tuple consists of
# tuples that describe a cell in the dashboard. Each cell is a tuple containing
# the product or team and the color. Optionally the cell tuple can contain a 
# third value which is a tuple containing the column and row span for the cell.
DASHBOARD_ROWS = [((QUALITY_REPORT, 'lightsteelblue'),
                   (QUALITY_TEAM, 'lavender'))]

PROJECT.set_dashboard(DASHBOARD_COLUMNS, DASHBOARD_ROWS)
