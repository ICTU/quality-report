""" Project definition for the Quality Report software itself. """

import datetime

from qualitylib import metric_source, metric, requirement
from qualitylib.domain import Project, Product, Team, Document, TechnicalDebtTarget, DynamicTechnicalDebtTarget


BUILD_SERVER = metric_source.Jenkins('http://jenkins/', username='jenkins_user', password='jenkins_password',
                                     job_re='-metrics')
SUBVERSION = metric_source.Subversion()
SONAR = metric_source.Sonar('http://sonar/', username='sonar_user', password='sonar_admin')
HISTORY = metric_source.History('quality-data/quality_report/history.json')
JACOCO = metric_source.JaCoCo(BUILD_SERVER.url() +
                              'job/%s/lastSuccessfulBuild/artifact/trunk/coveragereport/index.html')
ZAP_SCAN_REPORT = metric_source.ZAPScanReport()

# The project
PROJECT = Project('Organization name', name='Quality Report',
                  metric_sources={
                      metric_source.Jenkins: BUILD_SERVER,
                      metric_source.VersionControlSystem: SUBVERSION,
                      metric_source.ArchiveSystem: SUBVERSION,
                      metric_source.Sonar: SONAR,
                      metric_source.JaCoCo: JACOCO,
                      metric_source.ZAPScanReport: ZAP_SCAN_REPORT,
                      metric_source.History: HISTORY},
                  # Override the total loc metric targets:
                  metric_options={
                      metric.TotalLOC: dict(target=1000000, low_target=2000000)},
                  requirements=[requirement.TrustedProductMaintainability, requirement.Web, requirement.JavaScript,
                                requirement.Java, requirement.TrackSonarVersion])

# Teams of the project.
QUALITY_TEAM = Team(name='Quality team', requirements=[requirement.ScrumTeam, requirement.TrackSpirit])
PROJECT.add_team(QUALITY_TEAM)

# Documents of the project.
QUALITY_PLAN_URL = 'http://svn/commons/docs/quality_plan.doc'
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
            requirements=[requirement.OWASPZAP, requirement.UnitTests, requirement.ART, requirement.CodeQuality,
                          requirement.Performance],
            metric_source_ids={
                SONAR: 'nl.ictu.quality-report:quality-report',
                JACOCO: 'quality-report-coverage-report',
                SUBVERSION: 'http://svn/commons/scripts/quality-report/',
                ZAP_SCAN_REPORT: 'http://jenkins/job/zap_scan/ws/report.html'},
            metric_options={
                metric.UnittestLineCoverage:
                    dict(debt_target=TechnicalDebtTarget(0, 'Sonar incorrectly reports 0% unit test coverage')),
                metric.MajorViolations:
                    dict(debt_target=DynamicTechnicalDebtTarget(47, datetime.datetime(2014, 2, 12),
                                                                25, datetime.datetime(2014, 6, 1))),
                metric.UnmergedBranches:
                    dict(branches_to_ignore='spike', comment="Ignore the spike branch (2016-06-15).")})

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
