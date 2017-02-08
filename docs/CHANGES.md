2017-02-08  Release 1.77.0

  * It's no longer necessary to specify unittests and integration tests as a sub component.
  

2017-02-04  Release 1.76.4

  * Bug fix: Don't crash when JMeter report or Ansible report are unavailable.
  

2017-02-04  Release 1.76.3

  * Bug fix: Don't crash when the holiday planner is unavailable.
  

2017-02-04  Release 1.76.2

  * Bug fix: Don't crash when Jira is unavailable.
  

2017-02-02  Release 1.76.1

  * Bug fix: Don't crash when Jenkins is unavailable.
  

2017-02-02  Release 1.76.0

  * Add metrics for measuring the version of Visual Basic, TypeScript, and Python SonarQube plugins and quality 
    profiles.
  

2017-02-01  Release 1.75.6

  * Bug fix: Don't crash when the team spirit wiki is missing a date in the last column.
  

2017-02-01  Release 1.75.5

  * Bug fix: Don't crash when a Junit report is empty.
  

2017-01-30  Release 1.75.4

  * Bug fix: Add measurements with missing source to the history graph.
  
  
2017-01-30  Release 1.75.3

  * Bug fix: Add perfect measurements to the history graphs.
  
  
2017-01-30  Release 1.75.2

  * Bug fix: Don't show missing history in the graphs.
  
  
2017-01-30  Release 1.75.1

  * Bug fix: Don't crash with division by zero error when the history contains empty records.
  
  
2017-01-30  Release 1.75.0

  * Add a trend graph that shows the absolute number of metrics over time.
  * Bug fix: Don't crash when trying to measure the age of a performance test report that hasn't been configured.
  
  
2017-01-22  Release 1.74.3
 
  * Bug fix: Don't crash when doing a git pull.
 
 
2017-01-22  Release 1.74.2
 
  * Bug fix: Don't crash when reporting on risk or action log age. 
  
  
2017-01-22  Release 1.74.1
 
  * Bug fix: Don't crash when reporting on team spirit.
   
 
2017-01-21  Release 1.74.0

  * Add a metric for the number of days since regression test coverage reports were last generated.
  * Add a metric for the number of days since the team spirit was last edited.
  * Bug fix: Don't crash when an alert metric doesn't have a metric source configured.
  * Don't clone Git repos when reading the project definition, but only when needed.
  
  
2017-01-06  Release 1.73.1

  * Bug fix: Url of performance test age metrics didn't work.
   
   
2017-01-05  Release 1.73.0

  * Add metrics for the number of days since performance tests were last run.
  

2017-01-02  Release 1.72.2

  * Bug fix: Encode passwords in Git URLs.
  
  
2016-12-15  Release 1.72.1

  * Bug fix: The JSF code quality requirement was missing from the help menu.
  
  
2016-12-06  Release 1.72.0

  * Split `requirement.Performance` into separate requirements for load, endurance, and scalability:
    `requirement.PerformanceLoad`, `requirement.PerformanceEndurance`, and `requirement.PerformanceScalability`.
    This makes is possible to specify that an application or component only has certain types of performance tests
    required.


2016-12-05  Release 1.71.4

  * Don't remove details and repeated measurements from old measurements in the history file to make it easier to use 
    the history for research purposes.
    
    
2016-11-29  Release 1.71.3

  * Bug fix: Resolve name conflict between library and script. The library is now called `hqlib`. The script is
    still called `quality_report.py`.
  
  
2016-11-29  Release 1.71.2

  * Bug fix: Use creation date of manual test cases as last execution date as long as the test hasn't been executed yet.
  * Refactoring of source code layout.
  

2016-11-25  Release 1.71.1

  * Better metric report for metric.TeamAbsence.
  
  
2016-11-25  Release 1.71.0

  * Allow for ignoring known future overlapping absences by passing a start_date option to the team absence metric:
    `Team(..., metric_options={metric.TeamAbsence: dict(start_date=datetime.date(2016, 4, 1))})`
    
    
2016-11-24  Release 1.70.0

  * Give the software a proper name: HQ - Holistic Quality.
  * Rename doc folders to docs to prepare for Github Pages.
  

2016-11-21  Release 1.69.1

  * Bug fix: Add `requirement.OpenVAS` to optional project requirements.
  
  
2016-11-21  Release 1.69.0

  * Remove the ability to remove Sonar analyses, which isn't needed anymore since the quality report software doesn't create
    Sonar analyses anymore.
  * Move the OpenVAS metrics to the environment quality section, because the OpenVAS scan primarily scans the application hosts
    and not so much the software itself. This means `requirement.OpenVAS` should be passed to the project to have the OpenVAS
    metrics added.
  
  
2016-11-14  Release 1.68.0

  * Remove the latest release, dependency and branch feature: this means that the quality report only contains trunk versions of
    software products.
  

2016-11-12  Release 1.67.0

  * Remove the release candidate feature.
  
  
2016-11-11  Release 1.66.2

  * Bug fix: Remove links to dependencies from the HTML report.
  
  
2016-11-11  Release 1.66.1

  * Bug fix: Don't crash when a product has a `requirement.Performance`, but hasn't got a metric source id for the performance report.
  
  
2016-11-09  Release 1.66.0

  * Remove the dependency graph feature.
  
  
2016-10-30  Release 1.65.5

  * Bug fix: Don't crash when Jenkins isn't available.
  
  
2016-10-30  Release 1.65.4

  * Update dependencies to latest versions.
  

2016-10-26  Release 1.65.3

  * Bug fix: Don't crash when a property in a pom file can't be resolved.
  

2016-10-24  Release 1.65.2

  * Bug fix: Don't crash when `requirement.ART` is required, but no test reports are provided as metric source.
  
  
2016-10-24  Release 1.65.1

  * Bug fix: The metrics that report on individual SonarQube violations, such as cyclomatic complexity, included resolved
    issues in their count.
    

2016-10-23  Release 1.65.0

  * Add a metric for the number of open security bugs from static security analysis listed in Jira. To use it,
    define a filter in Jira that lists the number of open static security analysis bugs and pass it to Jira:
    `myJira = metric_source.Jira('http://jira/', 'username', 'password', open_static_security_analysis_bug_query_id=567)`
    The `metric.OpenStaticSecurityAnalysisBugs` will be added to the project provided the project has the
    `requirement.TrackBugs`.
 
  
2016-10-18  Release 1.64.2

  * Remove ReSharper SonarQube plugin version measurement from C# requirements because the ReSharper plugin has been 
    deprecated.
  
  
2016-10-09  Release 1.64.1
 
  * Add component and application domain objects.
  
  
2016-10-09  Release 1.64.0

  * Give domain objects default requirements. See the help menu domain objects for the default and optional requirements
    for each type of domain object.


2016-10-03  Release 1.63.2

  * Bug fix: The happiness metric source wouldn't correctly read the JSON.
  

2016-10-03  Release 1.63.1

  * Support the ICTU Happiness metric source for team smileys.


2016-10-02  Release 1.63.0

  * Prepare for multiple metric source types for the team spirit measurement.
  
  
2016-09-29  Release 1.62.5

  * Better norm explanation for the metric measuring the amount of logical test cases without duration filled in.
  * Support multiple Silk Performer reports for the performance scalability metric.
  
  
2016-09-20  Release 1.62.4

  * Support SonarQube API changes starting with SonarQube 5.4.
  

2016-09-19  Release 1.62.3

  * Bug fix: Add missing import statement.
  
  
2016-09-19  Release 1.62.2

  * Bug fix: Links to Trello boards were missing.
  

2016-09-19  Release 1.62.1

  * Bug fix: Don't crash when Trello reports there are no cards.
  

2016-09-13  Release 1.62.0

  * Add performance scalability test metrics.
  
  
2016-09-12  Release 1.61.2

  * Remove resources tab as most of the information is now also in the help menu.
  * Reorganize help menu.
  

2016-09-11  Release 1.61.1

  * Bug fix: Don't crash when Birt has no sprint progress report.
  
  
2016-09-11  Release 1.61.0

  * Add metrics for performance endurance testing.
  

2016-09-09  Release 1.60.1

  * Bug fix: Don't crash when reporting the new performance test metrics.
  
  
2016-09-09  Release 1.60.0

  * Rename `metric_source.Ymor` to `metric_source.SilkPerformer`.
  * Split the response times metric into two separate metrics: one for performance test warnings and one for 
    performance test errors. Performance test warnings are performance test queries that take longer than the
    desirable response time. Performance test errors are performance test queries that take longer than the
    maximum response time.
  
  
2016-09-07  Release 1.59.0

  * Added a new possible location for documents: Nexus.
  
  
2016-09-06  Release 1.58.4

  * Bug fix: Don't crash when Trello isn't configured.
  

2016-09-06  Release 1.58.3

  * Bug fix: Uncommitted changes were included in the previous release.
  

2016-09-06  Release 1.58.2

  * Bug fix: The Trello urls to overdue cards wouldn't be correct, making the quality report appear empty.
  

2016-09-05  Release 1.58.1

  * Bug fix: The test report metrics, when using a JUnit test report as source, would try to read the HTML
    Junit report to get the data instead of the XML JUnit report.
    
    
2016-09-05  Release 1.58.0

  * Roll back overriding the url of a metric (release 1.57.0).
  * The OWASP dependency warnings metrics now link to the HTML report when using the XML report as source.
  * The test report metrics, when using a JUnit test report as source, now links to the HTML JUnit report 
    instead of the XML JUnit report.
  
  
2016-09-01  Release 1.57.3

  * Roll back dashboard change.
  
  
2016-09-01  Release 1.57.2

  * Bug fix: Better report for the metrics that count user stories without security and performance risk assessment.
  * More consistent dashboard layout.
  
  
2016-08-31  Release 1.57.1

  * Bug fix: Don't crash when a Document has no version control system.
  

2016-08-31  Release 1.57.0

  * Allow for overriding the url of a metric by passing a url via the metric options:
    `Product(..., metric_options={metric.FailingRegressionTests: dict(url='http://path/to/html/test/report/')})`
  

2016-08-30  Release 1.56.2

  * Changed target_value and low_target_value for user stories without security and performance risk assessment.


2016-08-30  Release 1.56.1

  * Previous version didn't install correctly.
  

2016-08-30  Release 1.56.0

  * Add a requirement and two metrics for tracking the number of user stories without security and performance risk
    assessment.


2016-08-30  Release 1.55.1

  * Junit reports would be reported as missing when the number of failures is higher than the number of test cases.
  
  
2016-08-28  Release 1.55.0
  
  * Use CamelCase requirement names for consistency with metric and metric source names.


2016-08-26  Release 1.54.1

  * Allow for using credentials with performance reports.


2016-08-26  Release 1.54.0

  * Remove support for the "old" BIRT reports (ICTU specific).
  
  
2016-08-24  Release 1.53.4

  * Bug fix: The Open VAS requirement contained a ZAP Scan metric.


2016-08-24  Release 1.53.3

  * Bug fix: Don't crash when a performance report metric source hasn't been configured.


2016-08-24  Release 1.53.2

  * Bug fix: Don't crash when a performance report metric source hasn't been configured.


2016-08-24  Release 1.53.1

  * Bug fix: Don't crash when a performance report metric source hasn't been configured.
  
  
2016-08-24  Release 1.53.0

  * Add a metric for the Open VAS Scan report.
  
  
2016-08-20  Release 1.52.0

  * Remove the quality attributes and ability to filter on it.
  * Read and parse each OWASP dependency XML report just once to improve performance.
  
  
2016-08-18  Release 1.51.2

  * Have `metric.FailingUnittests` report there are no unit tests rather than say that 0 of 0 unit tests fail, 
    if there are no unit tests.
    
    
2016-08-17  Release 1.51.1

  * Bug fix: Don't crash on credentials passed to the OWASP dependency XML report.
  
  
2016-08-17  Release 1.51.0

  * Support OWASP dependency XML reports as metric source for the OWASP dependency metric:
    `OWASP_REPORT = metric_source.OWASPDependencyXMLReport('http://url/report.xml')`
    `PROJECT = Project(..., metric_sources={metric_source.OWASPDependencyReport: OWASP_REPORT})`
  

2016-08-16  Release 1.50.0

  * Prepare for multiple implementations of the OWASP dependency report metric source. This means that adding the 
    `metric_source.JenkinsOWASPDependencyReport` to the project now needs to use `metric_source.OWASPDependencyReport`
    as key:
    `OWASP_REPORT = metric_source.JenkinsOWASPDependencyReport('http://jenkins')`
    `PROJECT = Project(..., metric_sources={metric_source.OWASPDependencyReport: OWASP_REPORT})`
  

2016-08-15  Release 1.49.2

  * Bug fix: Don't crash when a product should have a coverage report, but the coverage URL isn't supplied.
  
  
2016-08-15  Release 1.49.1

  * Bug fix: Don't crash when a product should have a coverage report, but the coverage URL isn't supplied.
  

2016-08-14  Release 1.49.0

  * List all requirements in the help menu and indicate which are included in the current report.
  
  
2016-08-13  Release 1.48.0

  * Consistent requirement names.


2016-08-12  Release 1.47.0

  * Remove the `domain.Team` parameter `is_scrum_team` because it is no longer needed.
  
  
2016-08-11  Release 1.46.0

  * Remove `metric.ARTStability` and `domain.Street` because the stability of automated regression tests is also
    measured via the regression test reports.
    

2016-08-11  Release 1.45.4

  * Rollback 1.45.3 because the problem was not that Jenkins needed to retry but that the credentials weren't entered
    correctly.
    

2016-08-11  Release 1.45.3

  * When receiving a 403 forbidden (e.g. from Jenkins), retry with basic authentication.
  
  
2016-08-09  Release 1.45.2

  * Add `requirement.TRACK_BRANCHES` to enable deciding whether branches should be tracked.
  
  
2016-08-08  Release 1.45.1

  * Split `requirement.ART` into two different requirements: `requirement.ART` for the regression test success and age
    and `requirement.ART_COVERAGE` for the coverage metrics.
    
    
2016-08-08  Release 1.45.0

  * Include metrics in the report based on requirements, not on whether they can be measured or not.
  

2016-07-15  Release 1.44.3

  * Don't crash when no Sonar or Birt instances are configured.
  
  
2016-07-13  Release 1.44.2

  * Remove incomplete help information.
  * Better reporting on metric sources that have not been configured completely.
  

2016-07-11  Release 1.44.1

  * Bug fix: The pie charts in the dashboard wouldn't include metrics that are missing due to missing configuration.


2016-07-11  Release 1.44.0

  * Remove the `metric.DependencyQuality` as it wasn't really used.
  
  
2016-07-11  Release 1.43.1

  * Bug fix: Give the metrics that are missing due to missing configuration the same background color as metrics 
    that are missing due to sources being unreachable.
    
    
2016-07-11  Release 1.43.0

  * Distinguish between metrics that can't be measured because the source hasn't been configured and that can't be measured
    because the source isn't available or because the metric source id (e.g. url, Sonar key) isn't configured.
    
    
2016-07-09  Release 1.42.2

  * Bug fix: Don't crash when a Jenkins test report can't be reached.


2016-07-08  Release 1.42.1

  * Bug fix: Mention product name in regression test age metric.
  

2016-07-08  Release 1.42.0

  * Remove support for Jasmine HTML test reports.
  * Add `metric.RegressionTestAge` for measuring how many days since regression tests last ran.
  
  
2016-07-06  Release 1.41.1

  * Bug fix: Show the OWASP dependency metrics when filtering security metrics.
  
  
2016-07-05  Release 1.41.0

  * Removed the additional_resources option to add extra urls to projects.
  
  
2016-07-05  Release 1.40.1

  * Better norm description for the ZAP Scan alerts metrics.
  * Create separate requirement for the ZAP Scan alerts metrics to ease introduction: `requirement.OWASP_ZAP`.
  

2016-07-05  Release 1.40.0 

  * Support for the ZAP Scan report. To use it, in the project definition, create the metric source:
    `ZAP_SCAN_REPORT = metric_source.ZAPScanReport()`
    Add the metric source to the project:
    `PROJECT = Project(..., metric_sources={metric_source.ZAPScanReport: ZAP_SCAN_REPORT})`
    And then specify for each product the security requirement and where its ZAP Scan report can be found:
    `PRODUCT = Product(requirements=[requirement.OWASP], metric_source_ids={ZAP_SCAN_REPORT: 'http://url/to/report.html'}`
    This will cause the report to contain to new metrics: `metric.HighRiskZAPScanAlertsMetric` and
    `metric.MediumRiskZAPScanAlertsMetric`.


2016-07-01  Release 1.39.0

  * Split the OWASP dependency warning metric into two metrics, one for high priority warnings and one for normal 
    priority warnings. 
  

2016-06-29  Release 1.38.2

  * Bug fix: Two metrics had no proper name in the help information.
  

2016-06-29  Release 1.38.1

  * Use condensed-table style for the dashboard so it takes a little bit less space.
  
  
2016-06-29  Release 1.38.0

  * Add URLs of configured metric sources to the help menu.
  
  
2016-06-28  Release 1.37.4

  * Bug fix: Use target=_blank for the link to the change history.
  
  
2016-06-28  Release 1.37.3

  * Rename "Filter metrieken" menu to "Filter" menu for consistency.
  * Remove dividers between components with multiple versions to shorten the navigation menu.


2016-06-27  Release 1.37.2

  * Replace both "KPI" and "meting" with "metriek" in the user interface for better consistency.


2016-06-27  Release 1.37.1

  * Use dividers between components with multiple versions in the navigation menu for better readability.


2016-06-27  Release 1.37.0

  * Upgrade to Bootstrap 3.


2016-06-27  Release 1.36.5

  * Bug fix: Don't crash when Jenkins jobs don't have a buildable flag.


2016-06-25  Release 1.36.4

  * Bug fix: Don't report negative failing unit tests when Sonar can't be reached.


2016-06-25  Release 1.36.3

  * Bug fix: Don't report Sonar as being at version 0.0 when it can't be reached, but report it as not measurable.


2016-06-25  Release 1.36.2

  * Bug fix: Don't crash when wiki page isn't available.


2016-06-25  Release 1.36.1

  * Bug fix: Unit of duration of manual logical test cases is minutes, not logical test cases.


2016-06-25  Release 1.36.0

  * The unit of metrics is taken from the metric classes so the `TechnicalDebtTarget` and `DynamicalDebtTarget` classes
    don't take a unit argument anymore.


2016-06-24  Release 1.35.1

  * Bug fix: Don't report 0 failing unit tests out of 0 unit tests as perfect but rather as red.


2016-06-24  Release 1.35.0

  * Remove graph with metrics and metric sources as it was hard to read. Use the help information instead.


2016-06-23  Release 1.34.5

  * Bug fix: Show the default "metric source is missing" report when a performance test report isn't available.


2016-06-23  Release 1.34.4

  * Bug fix: Don't crash when a performance test report isn't available.


2016-06-23  Release 1.34.3

  * Bug fix: Don't crash when a performance test report isn't available.


2016-06-23  Release 1.34.2

  * Bug fix: Remove extraneous "<<<<<<<<" from the help information of the quality report.
  * Bug fix: Don't crash when a regression test coverage report isn't available.


2016-06-22  Release 1.34.1

  * Bug fix: Don't crash when generating the list of metric sources.


2016-06-22  Release 1.34.0

  * Show a list of metric sources in the help information of the quality report.


2016-06-22  Release 1.33.2

  * Bug fix: Don't crash when adding OWASP as requirement without providing a OWASP dependency checker metric source.


2016-06-22  Release 1.33.1

  * Bug fix: Don't crash.


2016-06-21  Release 1.33.0

  * Include the OWASP dependency checker metric in the report for products that have OWASP as requirement:
    `Product(..., requirements=[requirement.OWASP])`. This will add the metric `metric.OWASPDependencies` to the
    section of the product.


2016-06-21  Release 1.32.1

  * Bug fix: Show OWASP dependency metric as missing when the OWASP dependency report is not available.


2016-06-21  Release 1.32.0

  * Setting technical debt metric targets via the `technical_debt_target` parameter is no longer supported.
    Use the `metric_options` parameter introduced in release 1.31.0.


2016-06-20  Release 1.31.2

  * Bug fix: Don't crash on `httplib.BadStatusLine` when opening a URL.


2016-06-19  Release 1.31.1

  * Bug fix: Don't ignore a subject's comment when a metric has a technical debt comment.


2016-06-19  Release 1.31.0

  * Overriding metric target and low targets via the `targets` and `low_targets` parameters is no longer supported.
    Use the `metric_options` parameter introduced in release 1.30.0.
  * Allow for accepting technical debt metric targets via the metric options, e.g.
    `Product(..., metric_options={metric.MajorViolations: dict(debt_target=TechnicalDebtTarget(50))})`


2016-06-18  Release 1.30.0

  * Allow for overriding metric targets and low targets via the metric options, e.g.
    `Product(..., metric_options={metric.MajorViolations: dict(target=10, low_target=5)})`


2016-06-18  Release 1.29.0

  * Comments via a Wiki are no longer supported. Use the project definition for comments. See release 1.28.0 below.


2016-06-17  Release 1.28.1

  * Bug fix: Don't crash when opening a Sonar url throws a socket error.


2016-06-15  Release 1.28.0

  * Allow for adding comments to metrics in the project definition, e.g.
    `Product(..., metric_options={metric.UnmergedBranches: dict(comment="This is a comment")})`


2016-06-15  Release 1.27.3

  * Bug fix: Center the icons in the help information.


2016-06-15  Release 1.27.2

  * Bug fix: Center the icons in the help information.


2016-06-15  Release 1.27.1

  * Bug fix: Use the correct icons in the help information.


2016-06-15  Release 1.27.0

  * In the help information, show which of the metrics are actually included in the current report.


2016-06-14  Release 1.26.2

  * Bug fix: Don't crash when there's no Sonar analysis of the trunk version of a product.


2016-06-14  Release 1.26.1

  * Bug fix: Adding technical debt to `metric.ARTStability` would cause an exception.


2016-06-12  Release 1.26.0

  * Add `--version` command line argument.


2016-06-11  Release 1.25.1

  * Bug fix: Birt reports use commas as thousands separators. Remove commas before converting strings to integers.


2016-06-11  Release 1.25.0

  * Include user stories and logical test case metrics in the report for products that have user stories and logical
    test cases as requirement: `Product(..., requirements=[requirement.USER_STORIES_AND_LTCS])`. This will add
    the metrics `UserStoriesNotReviewed`, `UserStoriesNotApproved`, `LogicalTestCasesNotReviewed`,
    `LogicalTestCasesNotApproved`, `UserStoriesWithTooFewLogicalTestCases`, `LogicalTestCasesNotAutomated`,
    `ManualLogicalTestCases`, and `NumberOfManualLogicalTestCases` to the section of the product.


2016-06-11  Release 1.24.0

  * Remove the blocking test issues metric as it is not used anymore.


2016-06-10  Release 1.23.0

  * Include test coverage metrics in the report depending on whether the product has unit tests, integration tests, or
    both. When the product has only unit tests, report on the unit test coverage. When the product has only integration
    tests, report on the integration test coverage. When the product has both unit and integration tests, report on
    the combined coverage only.


2016-06-09  Release 1.22.0

  * Add metrics for combined unit and integration test line and branch coverage.


2016-06-09  Release 1.21.0

  * Add metrics for integration test line and branch coverage.


2016-06-06  Release 1.20.0

  * Allow for monitoring only specific branches for unmerged revisions, using a metric option. For example,
    `metric_options={metric.UnmergedBranches: dict(branches_to_include=['test branch', 'dev branch'])}`


2016-06-04  Release 1.19.8

  * Indicate that the metric cannot be measured when the source is not configured or unavailable.


2016-06-04  Release 1.19.7

  * Update required Sonar version and Sonar plugin versions.


2016-06-03  Release 1.19.6

  * Be better prepared for Sonar metric sources being down.


2016-05-28  Release 1.19.5

  * Be better prepared for Birt metric sources being down.


2016-05-28  Release 1.19.4

  * Be better prepared for Birt metric sources being down.


2016-05-28  Release 1.19.3

  * Be better prepared for Birt metric sources being down.


2016-05-28  Release 1.19.2

  * Be better prepared for Birt metric sources being down.


2016-05-28  Release 1.19.1

  * Be better prepared for Birt metric sources being down.


2016-05-23  Release 1.19.0

  * Allow for ignoring unmerged branches using a regular expression. Use the `branches_to_ignore` option to specify a
    regular expression, like this:

    `subversion = metric_source.Subversion()
    product = domain.Product(project, name='Product', short_name='PR',
                             metric_source_ids={subversion: 'http://svn/trunk/foo/'},
                             metric_options={metric.UnmergedBranches: dict(branches_to_ignore_re='feature.*')})`


2016-05-23  Release 1.18.2

  * Split the `WEB_JS` requirement into separate `Web` and `Javascript` requirements so that adding one doesn't imply the
    other.


2016-05-23  Release 1.18.1

  * Remove obsolete code.
  * Add a C# Squid rule to use in Sonar for measuring the many-parameter metric.


2016-05-22  Release 1.18.0

  * Add metrics to measure SonarQube quality profile version.


2016-05-16  Release 1.17.0

  * Add metrics to measure SonarQube plugin version.


2016-05-10  Release 1.16.2

  * Include HTML, CSS, JavaScript, and image resources in the source distribution.


2016-05-09  Release 1.16.1

  * Include requirements.txt in source distribution.


2016-05-09  Release 1.16.0

  * Lots of undocumented changes.
  * Add an OWASP dependency metric that uses the Jenkins OWASP dependency
    check plugin to check for dependencies with OWASP issues.
  * Products take an optional `is_main` boolean parameter. Set it to `False` to have
    the size of a product be ignored in the Total LOC metric.
  * Don't report CI-jobs without builds as failing.
  * Allow for overriding the total LOC metric via the project.
  * Split the metric for measuring the number of user stories not approved or
    not reviewed into separate metrics for not approved and not reviewed user
    stories.
  * Split the metric for measuring the number of logical test cases not approved
    or not reviewed into separate metrics for not approved and not reviewed
    logical test cases.
  * Remove support for writing a summary to the summary.csv file.
  * Remove support for filtering metrics by team.
  * Remove release age metric.
  * Remove support for Emma.
  * Bug fix: make the team spirit yellow or red when the measurement date gets
    old.
  * Bug fix: HTML escape comments retrieved from the Wiki.
  * Bug fix: Make `LowerIsBetterMetrics` red when the measured value is invalid
    (below zero).
  * Bug fix: Have Git check remote branches for unmerged commits instead of just
    local branches.


2015-01-19  Release 1.15.0

  * Allow for requirements to be added to a project. The requirements
    will determine what needs to be measured later on.
  * Introduce a abstract version control system class with `Subversion` and `Git`
    as concrete instances.
  * Use metric source id mapping to find teams in the Wiki.
  * Allow for adding a default team to a Jenkins instance. The default team is
    responsible for all jobs that have not explicitly been assigned to a team.
  * Bug fix: if a product or team has a target or low target of 0 specified in
    the project definition, don't ignore it.


2014-11-03  Release 1.14.0

  * Task functionality has been removed, `metric_source.Tasks` no longer exists.
  * Documents now need a Subversion metric source id (the Subversion path).
  * The Pom metric source needs a reference to both Sonar and Subversion.
  * The Sonar metric source needs a reference to Subversion.
  * Add a blocker violations metric.


2014-09-18  Release 1.13.2

  * Bug fix: use the language of a component to decide what the rule name is
    for the number of parameters from Sonar.
  * Bug fix: don't crash when the language of a component in Sonar can't be
    retrieved.


2014-09-18  Release 1.13.1

  * Bug fix: use C-sharp and Javascript specific rule names when the language of
    a component is C-sharp or Javascript to get violations from Sonar.
  * Add metric class names to Help menu as reference for specifying targets and
    technical debt in the project definition file.


2014-09-11  Release 1.13.0

  * The unit test coverage metric is renamed `UnittestLineCoverage` to prepare for
    the addition of metrics for other types of unit test coverage.
  * Add a unit test branch coverage metric (`UnittestBranchCoverage`).
  * Pom metric source now needs a Sonar instance as parameter because it uses
    the Sonar ids of products.


2014-09-03  Release 1.12.1

  * Bug fix: don't crash when a document has an invalid URL.


2014-09-03  Release 1.12.0

  * Jenkins job names can be regular expressions. The regular expressions
    should resolve to exactly one job.
  * Coverage report metric sources (JaCoCo and Emma) now take a Jenkins instance
    as first argument. This allows for using job names with regular expressions.
  * Allow for adding people (`Person` class) as team members to teams. The
    team members are listed as part of the team resources.
  * Documents can have one or more teams responsible for them.


2014-08-21  Release 1.11.1

  * Allow for specifying branch ids per metric source. Useful if the branch is
    named differently in e.g. Sonar than in Subversion.


2014-08-21  Release 1.11.0

  * Allow for adding branches of products to the project.


2014-08-14  Release 1.10.2

  * Bugfix: don't crash when history charts can't be downloaded when creating
    the report.


2014-08-14  Release 1.10.1

  * Recent history charts for metrics are now downloaded when creating the
    report instead of when the user loads the report.
  * Bug fix: don't use memory address of objects when generating a stable
    id of metrics for use in the history.


2014-08-08  Release 1.10.0

  * The dashboard now uses column charts when displaying all versions of
    products and pie charts when displaying only the trunk versions of products.


2014-08-07  Release 1.9.1

  * Bug fix: strip revision numbers before passing them to Subversion.


2014-08-07  Release 1.9.0

  * The dashboard now uses column charts instead of pie chart so that it can
    give an overview of all product versions that are included in the quality
    report.
  * Introduce new quality attribute - dependency quality - and specify that the
    related metrics measure that quality attribute.
  * Bug fix: ignore revisions created by Maven on tags when checking for
    unmerged revisions of branches.
  * Bug fix: don't invoke the Sonar runner on products without Sonar id.
  * Remove ART performance metric. Not used anymore.


2014-07-31  Release 1.8.1

  * Bug fix: don't report the number of dependencies on snapshot versions for
    the snapshot version of products.


2014-07-31  Release 1.8.0

  * Add a metric for measuring the number of dependencies on snapshot versions.


2014-07-31  Release 1.7.4

  * Bug fix: dependency graph would be corrupted in case of snapshot
    dependencies.


2014-07-31  Release 1.7.3

  * Bug fix: don't try to add snapshot dependencies to the project.


2014-07-31  Release 1.7.2

  * Support snapshot dependencies.


2014-07-30  Release 1.7.1

  * Bug fix: add the metric for measuring regression test success to the report
    even when the Jenkins test report job is a metric source id of the ART
    component of a product.
  * Bug fix: deal with Jenkins test reports that have no pass count.


2014-07-28  Release 1.7.0

  * Add a metric for measuring regression test success, based on a Jenkins job's
    test report.


2014-07-28  Release 1.6.0

  * The name parameter for domain objects like project, team, street is now
    a keyword parameter.
  * Make a number of metrics absolute instead of relative so it is easier to set
    an upper bound on the number of cases that do not meet the criteria.
    The metrics changed are the metrics for measuring whether user stories and
    logical test cases are reviewed and approved, whether user stories have
    enough logical test cases, and whether logical test cases to be automated
    are actually automated.


2014-07-03  Release 1.5.2

  * Upgrade jQuery to 1.11.1.


2014-07-03  Release 1.5.1

  * Bug fix: Better compatibility with Internet Explorer.


2014-07-03  Release 1.5.0

  * Write a summary of metrics to the summary.csv file in the report folder,
    if and only if that file exists.


2014-06-27  Release 1.4.0

  * Don't use abbreviations for the dashboard layout, but references to
    products and teams.


2014-06-26  Release 1.3.4

  * Bug fix: Don't fail when a violation can't be read from Sonar.


2014-06-26  Release 1.3.3

  * Bug fix: Don't fail when removing a Sonar analysis fails.


2014-06-26  Release 1.3.2

  * Bug fix: Sonar runner would inadvertently change the Sonar options of a
    product.


2014-06-26  Release 1.3.1

  * Look up tag folders in Subversion by version number instead of assuming
    the folder names comply with a certain format.


2014-06-25  Release 1.3.0

  * Don't use the term key performance indicator (KPI) since there are way too
    many metrics to justify usage of the phrase "key". Consequently, the main
    script is renamed to quality_report.py.
  * Bug fix: Don't assume other products have Subversion paths when looking for
    dependencies.


2014-06-23  Release 1.2.11

  * Bug fix: Don't assume other products have pom files when looking for
    dependencies.


2014-06-23  Release 1.2.10

  * Bug fix: Don't assume a pom file exists if a product has a Subversion url.


2014-06-23  Release 1.2.9

  * Bug fix: Don't list the history file as missing when it is not.
  * Bug fix: Don't fail when the Python Package Index (PyPI) can't be reached
    for checking the latest released version.


2014-06-20  Release 1.2.8

  * Bug fix: Indication of availability of new versions didn't work.


2014-06-20  Release 1.2.7

  * Show version number of the software in the help information of the
    generated quality reports. Also show whether a newer version is available.


2014-06-19  Release 1.2.6

  * Bug fix: Don't use default Maven if a user specified Maven is passed.


2014-06-19  Release 1.2.5

  * Bug fix: Make the call to Maven to build a specific product version
    platform independent.


2014-06-19  Release 1.2.4

  * Bug fix: Make the call to Maven to build a specific product version
    platform independent.


2014-06-19  Release 1.2.3

  * Bug fix: Don't assume all products have a Sonar id.


2014-06-19  Release 1.2.2

  * Bug fix: Sonar wouldn't work without passing it a Maven metric source. Use a
    default Maven when no Maven is specified.


2014-06-19  Release 1.2.1

  * Allow Subversion paths where there is a subpath below the trunk folder.
    For example, http://svn/product/trunk/sources/.


2014-06-18  Release 1.2.0

  * Metric sources and metric options are now passed to the project via the
    `metric_sources` and `metric_options` parameters so that the project class
    doesn't need to know what metric sources exist.
  * Bug fix: Time stamps in the history file without milliseconds wouldn't be
    parsed.


2014-06-12  Release 1.1.0

  * Measurable objects like products and teams now take a `metric_source_ids`
    parameter. See the example project definitions on how to use it.


2014-05-26  Release 1.0.10

  * Allow for giving a development street a url.


2014-05-22  Release 1.0.9

  * Make the document class a measurable object so it's possible to specify
    per document after how many days the document should be considered out of
    date.


2014-05-19  Release 1.0.8

  * Bug fix: write image files in binary mode on Windows.


2014-05-15  Release 1.0.7

  * Bug fix: Jenkins may return unquoted URLs, quote them before using them.
  * Added: ability to provide additional resources for a project.


2014-05-15  Release 1.0.6

  * Bug fix: can't rename a file on Windows if the target exists.


2014-05-15  Release 1.0.5

  * Use a platform independent method to change the mode of folders and files.
  * Remove dependency on argparse 1.2, use Python included version of argparse.
  * Remove dependency on simplejson, use Python included json.


2014-05-12  Release 1.0.4

  * Bug fix for getting violations from Sonar.
  * Give a warning when a specific metric can't be retrieved via the Sonar API.


2014-05-12  Release 1.0.3

  * Use only the Sonar API to access Sonar.


2014-05-09  Release 1.0.2

  * Add debug logging to Sonar metric source.


2014-05-08  Release 1.0.1

  * Add document age metric.


2014-04-24  Release 1.0

  * Initial release to PyPI.
