2018-09-21  Release 2.72.0

  * Feature #513, #512, #511: Detail info for detected code maintainability issues (bugs, vulnerabilities and code smells).
  * Feature #514: Detail info table for code maintainability issues has links to the Sonar.


2018-09-20  Release 2.71.0

  * Feature #424: Added metrics for code maintainability: Maintainability Bugs, Vulnerabilities and Code Smells.


2018-09-14  Release 2.70.0

  * Feature #175: The trend spark-line chart displays the data of last 7 days.


2018-09-14  Release 2.69.3

  * Bug #502: problem with links with spaces corrected.


2018-09-13  Release 2.69.2

  * Bug #500: escaped quotes in norm texts fixed.


2018-09-12  Release 2.69.1

  * Tech #234: removed html elements generation from server side and html direct setting on client side.


2018-09-10  Release 2.69.0

  * Feature #497: now it is possible to have different display link than the source link for metric source.


2018-09-03  Release 2.68.0

  * Feature #496: LCOV coverage report metric source added.


2018-08-30  Release 2.67.0

  * Feature #491: Allow for configuring how the URL for the Junit xml file is translated into the url for the HTML report.
  
  
2018-08-22  Release 2.66.2

  * Bug #409 fixed: branch metrics were green when unauthorised to clone repo.
  * Bug #486 fixed: when owasp xml report was not present, the application was crashing.


2018-08-20  Release 2.66.1

  * Bug #484: OWASP details table links fixed for reports with more than OWASP report.


2018-08-17  Release 2.66.0

  * Feature #472: ZAP scan report detail table added.


2018-08-16  Release 2.65.0

  * Feature #471: detail table implemented for OWASP measures.


2018-08-07  Release 2.64.0

  * Feature #470: detail table sorting added.


2018-08-01  Release 2.63.3

  * Bug #465: results for specific SonarQube violations (Sonar version>7) corrected


2018-07-31  Release 2.63.2

  * Feature #387: implemented ART using testx.


2018-07-27  Release 2.63.1

  * Bug #364: Improve wording of failing regression test metric.
  
  
2018-07-27  Release 2.63.0

  * Feature: Add duration of manual test cases to the detail table of the duration of manual test cases metric. 
  * Feature: Add user story points of ready user stories to the detail table of the ready user story points metric. 
  * Bug #435: Fix label of the manual test case duration detail table.


2018-07-26  Release 2.62.2

  * Bug fix: Remove repetitive label from the unmerged branches detail table.
  

2018-07-26  Release 2.62.1

  * Bug fix: Retrieving the date of the last change on a branch would sometimes crash HQ with a decode unicode error.


2018-07-25  Release 2.62.0

  * Feature #390: Show when branches were last changed in the detail pane of the unmerged branches metric.


2018-07-24  Release 2.61.13

  * Bug #453: Report crash fixed for JaCoCo metric source - fix.


2018-07-24  Release 2.61.12

  * Bug #453: Report crash fixed for JaCoCo metric source.


2018-07-23  Release 2.61.11

  * Bug fix: Fix Travis deploy stage.


2018-07-23  Release 2.61.10

  * Bug fix: Fix Travis deploy stage.


2018-07-20  Release 2.61.9

  * Bug fix: More reliable release process. 


2018-07-20  Release 2.61.8

  * Bug fix: More reliable release process. 


2018-07-13  Release 2.61.7

  * Bug #372: Branch coverage not shown in the report when not applicable.


2018-07-12  Release 2.61.6

  * Bug fix: Don't crash when a performance report contains an empty transaction.


2018-07-12  Release 2.61.5

  * Tech: Upgrade backend to Python 3.7.


2018-07-03  Release 2.61.4

  * Bug #345: dummy links in CI-jobs and Sonar version corrected.


2018-07-03  Release 2.61.3

  * Bug #440: crash because of the string as a part of plugin version solved.


2018-07-02  Release 2.61.2

  * Bug #434: crash of report by Sonar Qube server version lower than 5.4 fixed.


2018-06-29  Release 2.61.1

  * Bug fix: Don't crash when running commands in the shell on Windows.
  
  
2018-06-29  Release 2.61.0

  * Feature #433: API for Sonar Qube versions 7.x implemented.
  * Tech #430: Using of different Sonar links sets per version implemented.


2018-06-11  Release 2.60.5

  * Bug fix: Don't crash when SonarQube isn't available.
    
    
2018-06-11  Release 2.60.4

  * Bug fix: Stop using the deprecated /projects/index SonarQube API to check for the existence of analyses in 
    SonarQube.
  
  
2018-06-06  Release 2.60.3

  * Bug fix: Make sure the Docker container uses the right version of the HQ python package.
  
  
2018-06-06  Release 2.60.2

  * Bug fix: Don't crash on the old performance report format.
  
  
2018-06-06  Release 2.60.1

  * Bug fix: Don't crash on changed performance report format.
  
  
2018-06-05  Release 2.60.0

  * Feature: Updated default test coverage norms. 
  * Bug #417: Fix typos in the GROS user story points prediction metric.
  
  
2018-06-01  Release 2.59.0

  * Feature: Add release tags to Docker images. Closes #367.
  
  
2018-06-01  Release 2.58.6

  * Bug fix: The meta metrics were not written correctly to the history file.
  
  
2018-06-01  Release 2.58.5

  * Bug #410: Don't turn off the "Longer than a week the same status" filter when unchecking "All statuses". 
    It's confusing to users.
    

2018-05-22  Release 2.58.4

  * Bug #407: Problem with history updates solved.


2018-05-22  Release 2.58.3

  * Tech #400: JSON persistence layer implemented; old History class phased out.


2018-05-17  Release 2.58.2

  * Tech. #399: Images of charts are moved to a separate folder.


2018-05-08  Release 2.58.1

  * Bug #363: Pipeline name added to the job name in the list of the CI jobs.


2018-05-08  Release 2.58.0

  * Feature #393: Option added to the report generator to generate just data files (json) and to omit frontend.


2018-05-04  Release 2.57.2

  * Bug fix: More consistent use of logging levels: CRITICAL if the report can't be created,
    ERROR if data retrieved from a metric source can't be parsed, WARNING if a metric source
    can't be reached, and INFO for progress.


2018-05-04  Release 2.57.1

  * Bug fix: More consistent use of logging levels: ERROR if the report can't be created,
    WARNING if metric sources can't be reached or information can't be parsed, INFO for
    progress.


2018-05-03  Release 2.57.0

  * Remove feature #389: Remove support for Nexus as metric source because Nexus 3 doesn't provide
    the last date an artifact was changed which is needed to report on the last date a document
    was changed.


2018-05-02  Release 2.56.5

  * Bug fix #383: Wiki metric source for team spirit didn't work.


2018-05-02  Release 2.56.4

  * Bug #384 solved: History charts of newly introduced metrics are shifted in the past.


2018-04-30  Release 2.56.3

  * Bug #379 solved: forward slashes in component names produced crash.


2018-04-29  Release 2.56.2

  * Bug fix: Set time outs on shell commands so HQ doesn't wait forever when e.g. a Git server is down.


2018-04-29  Release 2.56.1

  * Bug fix: Don't crash when retrieving Jenkins jobs times out.


2018-04-28  Release 2.56.0

  * Feature #373: Allow for using regular expressions when specifying jobs that contain Jenkins test reports.
    See https://github.com/ICTU/quality-report/wiki/Jenkins-test-report.


2018-04-24  Release 2.55.2

  * Bug fix #302: link reference in the metric comment fixed to also accept port number and parameters.


2018-04-24  Release 2.55.1

  * Bug fix #368: Reading the old history format (using the metric source "History") failed.


2018-04-24  Release 2.55.0

  * Feature #128: history chart in detail pane


2018-04-22  Release 2.54.0

  * Feature: Add user story point prediction metric, based on the "Grip op Software" (GROS) research project
    conducted at ICTU (see https://www.ictu.nl/nieuws/softwareontwikkeling-onder-wetenschappelijke-loep, in Dutch).
    Configuration documentation at https://github.com/ICTU/quality-report/wiki/Prediction-metrics.


2018-04-18  Release 2.53.0

  * Feature #358: Add aggregated test coverage metrics.
    See https://github.com/ICTU/quality-report/wiki/Aggregated-test-coverage-metrics


2018-04-11  Release 2.52.2

  * Bug fix: Add percentage signs to y-axis labels of the relative trend graph.


2018-04-10  Release 2.52.1

  * Refactoring: Upgrade to Bootstrap version 4.


2018-04-05  Release 2.52.0

  * Feature #302: URLs in the comment text are automaticaly converted to link references.


2018-04-04  Release 2.51.2

  * Refactoring: Emoji look nice on macOS but are rather ugly on Windows and Linux; roll-back.


2018-04-02  Release 2.51.1

  * Refactoring: Replace icons with emoji.


2018-03-30  Release 2.51.0

  * Feature #336: Add text-based metric filtering capability via search field in the navigation bar.


2018-03-29  Release 2.50.0

  * Remove feature: HQ no longer tracks the versions of the PMD, Checkstyle, and Findbugs SonarQube plugins.


2018-03-28  Release 2.49.3

  * Refactoring: When querying SonarQube for available quality profiles, download all information at once instead of
    language by language.


2018-03-28  Release 2.49.2

  * Bug #335 fix: browser caching of json files disabled.


2018-03-28  Release 2.49.1

  * Bug fix: Ignore running builds when asking Jenkins for builds as Jenkins considers running builds successful.


2018-03-23  Release 2.49.0

  * Remove feature: The ICTU specific performance report for the LRK-project is no longer used, so the accompanying
    metric source has been removed from HQ.


2018-03-22  Release 2.48.0

  * Feature #292: Generic detail pane implemented for all metrics with Jira filter as a source.


2018-03-19  Release 2.47.1

  * Bug fix: When reading test results from a Jenkins test report, don't rely on plugin specific information to
    find the test results.


2018-03-17  Release 2.47.0

  * Remove feature: Measuring absence of team members is no longer supported.


2018-03-16  Release 2.46.11

  * Bug fix: Dockerfile referenced a Github repository that was removed, causing the release to fail.


2018-03-16  Release 2.46.10

  * Bug fix: Release build failed, retry.


2018-03-16  Release 2.46.9

  * Bug fix: Fix a regression in reading test results from a Jenkins test report.


2018-03-15  Release 2.46.8

  * Bug fix: Mention the domain objects Scrum, IssueManagement and ProjectManagement on the help page.


2018-03-14  Release 2.46.7

  * Bug fix: When reading the latest test results from a Jenkins test report, try both last completed build and the
    last successful build to find the results.


2018-03-13  Release 2.46.6

  * Bug #310: A problem where Action Activity metric showed -1 days solved.


2018-03-09  Release 2.46.5

  * Bug #296: A problem of exceeding Trello api call limits solved.


2018-03-08  Release 2.46.4

  * Feature: Add metric class to internal metrics JSON file for use in meta reports.


2018-03-07  Release 2.46.3

  * Bug fix: Improve the readability of the norms and measurements of the meta metrics.


2018-03-02  Release 2.46.2

  * Bug #298: Problem with reading url content solved.


2018-03-02  Release 2.46.1

  * Bug fix: Reading Checkmarx scan dates with an explicit time zone would fail.


2018-03-01  Release 2.46.0

  * Feature: Allow for authenticating with SonarQube using a token.


2018-02-27  Release 2.45.1

  * Bug #294: Alignment of numeric columns fixed.


2018-02-27  Release 2.45.0

  * Feature #250: Action Panel implemented.


2018-02-23  Release 2.44.0

  * Feature #288: Action activity metrics got detail panes.


2018-02-21  Release 2.43.2

  * Bug fix: Don't crash when the performance report is invalid.


2018-02-20  Release 2.43.1

  * Bug #282: Detail table layout problem solved.


2018-02-19  Release 2.43.0

  * Feature #276: Jenkins jobs' detail info available.


2018-02-16  Release 2.42.3

  * Bug fix #264: The description of the norm of user stories in progress metric was incorrect.


2018-02-12  Release 2.42.2

  * Bug fix: Don't crash when Checkmarx report is missing.


2018-02-12  Release 2.42.1

  * Bug fix: Don't crash when Checkmarx report is missing.


2018-02-08  Release 2.42.0

  * Feature #265: Comment column put back to the report table instead of detail pane.


2018-02-07  Release 2.41.0

  * Feature #210: In UserStoriesDuration metric a list of stories added in extra information pane.


2018-02-04  Release 2.40.0

  * The Sonar metric source can now be used as unit test report, coverage report and Sonar, so that it's no longer
    needed to create different instances of the Sonar metric source when using Sonar as metric source for code quality,
    unit tests and test coverage. See https://github.com/ICTU/quality-report/wiki/SonarQube.


2018-02-02  Release 2.39.0

  * Feature #262: Use coverage reports as source for unit test metrics so that different metric sources can be used as
    source for coverage information. See https://github.com/ICTU/quality-report/wiki/Unit-test-coverage-metrics and
    https://github.com/ICTU/quality-report/wiki/System-test-coverage-metrics.


2018-01-29  Release 2.38.5

  * Bug fix: Reading the date and time of the OWASP dependency checker report would fail when using the Jenkins OWASP
    dependency checker plugin.


2018-01-28  Release 2.38.4

  * Bug fix #233: Links to Wiki metric source were broken.


2018-01-26  Release 2.38.3

  * Bug fix #252: Type error 'cannot read comment' solved.


2018-01-25  Release 2.38.2

  * Bug fix #226: Round the average number of days that user stories are in progress to one decimal.


2018-01-25  Release 2.38.1

  * Bug fix #51: Take Jenkins pipeline jobs into account when measuring inactive or failing jobs.


2018-01-25  Release 2.38.0

  * Feature #244: Unmerged branches are now listed in the details pane instead of the metric text.


2018-01-24  Release 2.37.0

  * Feature #246: No longer use separate metrics for integration tests and unit tests, since SonarQube >= 6.2
    doesn't support this anymore. The integration test metrics and combined unit and integration test metrics have
    been removed.


2018-01-22  Release 2.36.0

  * Feature #238: Remove the feature of using a default project definition when the actual project definition has
    errors as this results in a working (but useless) report, hiding the problem with the incorrect project definition.


2018-01-20  Release 2.35.0

  * Feature #245: Allow for ignoring specific lists on action and risk boards.
    See https://github.com/ICTU/quality-report/wiki/Trello and https://github.com/ICTU/quality-report/wiki/Wekan.


2018-01-20  Release 2.34.1

  * Bug fix: Don't crash when reading new Silkperformer report.


2018-01-16  Release 2.34.0

  * Feature #209: detail metric information pane implemented.


2018-01-16  Release 2.33.1

  * Bug fix: Don't log a HTTP 404 as error for SonarQube when it's expected to occur.


2018-01-15  Release 2.33.0

  * Remove the JSF-subcomponent and accompanying metrics since it's no longer needed to support separate analysis of
    JSF-code in SonarQube.


2018-01-15  Release 2.32.1

  * Bug fix: The time-since-last-security-test metric would not be added to product sections, even if required.


2018-01-11  Release 2.32.0

  * Add metrics for measuring the duration of performance tests so HQ can check that performance tests run long enough.
    This only works for the SilkPerformer reports because the other performance report types don't contain the needed
    information.


2018-01-11  Release 2.31.2

  * Bug fix: When trying multiple JaCoCo session urls, only log a failure if the last one can't be read.


2018-01-09  Release 2.31.1

  * Bug fix: Better metric report sentences for some process-related metrics.


2018-01-09  Release 2.31.0

  * Add three process types: Project management, Issue management, and Scrum.
    See https://github.com/ICTU/quality-report/wiki/Processes.


2018-01-08  Release 2.30.1

  * Bug fix: Don't try to reach timed-out URLs multiple times.


2018-01-08  Release 2.30.0

  * Footer with report title and date added. Closes #214.


2018-01-07  Release 2.29.0

  * Add a process domain object for measuring process metrics such as number of open bugs, overdue actions, and
    number of ready user stories. See https://github.com/ICTU/quality-report/wiki/Processes.


2018-01-04  Release 2.28.4

  * Bug fix: Don't mention the number of unit tests in the unit test coverage metrics since the coverage and the
    number of tests may come from different sources.


2018-01-04  Release 2.28.3

  * Bug fix: Don't complain in the log when one version of the SonarQube API doesn't work, but an older one does.
    Closes #174.


2018-01-03  Release 2.28.2

  * Bug fix: Don't complain in the log about the meta metrics not having a metric source.
  * Bug fix: Don't complain in the log about Jenkins jobs not having a last stable or completed build.


2018-01-03  Release 2.28.1

  * Show the total number of stories in the user story duration metric.


2018-01-02  Release 2.28.0

  * Feature #206: TeamProgress metric removed.


2018-01-02  Release 2.27.2

  * Bug fix: Don't mark Jira filters as unavailable when they return no issues.


2018-01-02  Release 2.27.1

  * Bug fix: Don't report that the last security test was just now when the date provided is in the future.


2017-01-02  Release 2.27.0

  * Feature #195: metric for user stories duration added.


2017-12-28  Release 2.26.2

  * Bug fix: Don't crash if Jenkins is unreachable.


2017-12-28  Release 2.26.1

  * Bug fix: Don't crash if Jenkins is unreachable.


2017-12-28  Release 2.26.0

  * All metric sources need a metric source id. See for example
    https://github.com/ICTU/quality-report/wiki/CI-server-metrics.


2017-12-21  Release 2.25.3

  * Bug fix: Instead of reporting an UFT test report as broken, assume no tests were skipped if the total number of
    tests can't be read from the UFT test report.


2017-12-20  Release 2.25.2

  * Bug fix: Fix description of the security test frequency metric. (#190)


2017-12-20  Release 2.25.1

  * Add information about skipped tests to the failing unit/regression test metrics. (#196)


2017-12-20  Release 2.25.0

  * TrackUserStoriesInProgress is now an optional requirement of Project, Product, and Team. (#185)


2017-12-19  Release 2.24.1

  * Read the step count in the UFT test report to calculate the skipped number of tests.


2017-12-15  Release 2.24.0

  * Make the board id of Trello and Wekan instance the metric source id in project definitions for consistency with
    other metric sources.


2017-12-13  Release 2.23.0

  * Feature #185: Add metric for the number of user stories In Progress


2017-12-09  Release 2.22.0

  * Add Robot Framework test report as metric source for regression test and unit test metrics.
    See https://github.com/ICTU/quality-report/wiki/Robot-Framework-test-report. Closes #182.


2017-12-07  Release 2.21.0

  * Feature 164: support for branch analysis implemented


2017-12-07  Release 2.20.2

  * Bug fix: Jira url did not work.


2017-12-02  Release 2.20.1

  * Bug fix: Show a link to Checkmarx in the Checkmarx metrics, even if Checkmarx is not reachable. Closes #81.


2017-12-01  Release 2.20.0

  * Show adapted metric targets in the report, in the metric comment. Closes #172.
    See https://github.com/ICTU/quality-report/wiki/Metric-options.


2017-11-29  Release 2.19.0

  * Add metric for time last security test.


2017-11-23  Release 2.18.1

  * Bug fix: Jira filter metric source didn't work.


2017-11-23  Release 2.18.0

  * Add Jira filter metric source for all issue tracker metrics.
    See https://github.com/ICTU/quality-report/wiki/Issue-tracker-metrics.


2017-11-20  Release 2.17.4

  * Bug fix: Metric source analysis age gives age of 0 days if it appears to be negative. Closes #152.


2017-11-18  Release 2.17.3

  * Don't keep contacting hosts that are known to be unavailable. Closes #142.


2017-11-16  Release 2.17.2

  * Bug fix: Don't crash when multiple Sonar instances have been configured but no metric source id.


2017-11-16  Release 2.17.1

  * Bug fix: Don't crash when multiple Sonar instances have been configured but no metric source id.


2017-11-14  Release 2.17.0

  * Add label that shows time since last commit


2017-11-13  Release 2.16.0

  * Add a Quality gate metric. See https://github.com/ICTU/quality-report/wiki/Bug-tracker-metrics.


2017-11-13  Release 2.15.0

  * Add the Track findings and Track technical debt requirement as optional requirement to the Product, Application,
    and Component domain objects.


2017-11-12  Release 2.14.2

  * Bug fix: Look at the most recently changed card when reporting the last activity of a Wekan board instead of at the
    oldest card.
  * Bug fix: Don't consider Wekan cards inactive if their start date is in the future.


2017-11-12  Release 2.14.1

  * Bug fix: Don't crash when parsing the date and time of Bamboo test reports.


2017-11-12  Release 2.14.0

  * Add Jira filter metric source for bug tracker metrics.
    https://github.com/ICTU/quality-report/wiki/Issue-tracker-metrics.
  * Bug fix: Don't count the rows in the trend table of Silkperformer performance reports as transactions.


2017-10-29  Release 2.13.2

  * Bug fix: Reports are not loading in Internet Explorer 11.
    Attempted fix for https://github.com/ICTU/quality-report/issues/130


2017-10-28  Release 2.13.1

  * Bug fix: Docker image wouldn't build correctly.


2017-10-28  Release 2.13.0

  * Add WekanBoard metric source which can be used as RiskLog and ActionLog, in addition to TrelloBoard.
    See https://github.com/ICTU/quality-report/wiki/Action-log-metrics,
    https://github.com/ICTU/quality-report/wiki/Risk-log-metrics and
    https://github.com/ICTU/quality-report/wiki/Wekan.


2017-10-23  Release 2.12.0

  * Introduce abstract RiskLog and ActionLog metric sources. The only concrete implemention is TrelloBoard.
    See https://github.com/ICTU/quality-report/wiki/Action-log-metrics,
    https://github.com/ICTU/quality-report/wiki/Risk-log-metrics and
    https://github.com/ICTU/quality-report/wiki/Trello.


2017-10-23  Release 2.11.2

  * Bug fix: Get OpenVAS report date from first table.


2017-10-22  Release 2.11.1

  * Bug fix: Don't crash when the OpenVAS report date and time can't be parsed.


2017-10-22  Release 2.11.0

  * Introduce an abstract CIServer metric source. The only concrete implementation is Jenkins. Note that Jenkins need
    to be added to the project using the CIServer key. See
    https://github.com/ICTU/quality-report/wiki/CI-server-metrics and
    https://github.com/ICTU/quality-report/wiki/Jenkins.


2017-10-20  Release 2.10.5

  * Bug fix: The SonarQube API for retrieving the date and time of the last analysis only works for projects, not for
    components. As of SonarQube 6.4, the components API returns the date and time of the last analysis date for both
    projects and components. So, HQ now uses the components API for retrieving the date and time of the last analysis
    if SonarQube is version 6.4 or newer.


2017-10-19  Release 2.10.4

  * Allow for using regular expressions in the Splunk performance report metric source id.
    See https://github.com/ICTU/quality-report/wiki/Performance-test-metrics.


2017-10-19  Release 2.10.3

  * Bug fix: Don't crash when Checkmarx data can't be read.


2017-10-19  Release 2.10.2

  * Add BambooTestReport metric source that can retrieve tests and test failures using the Bamboo API.
    See https://github.com/ICTU/quality-report/wiki/Bamboo-test-report.


2017-10-17  Release 2.10.1

  * Bug fix: SonarTestReport didn't correctly implement the TestReport interface.


2017-10-17  Release 2.10.0

  * Introduce new abstract class for unit test reports: metric_source.UnitTestReport. Note that metric_source.Sonar
    is no longer used as metric source for unit test metrics. You need to add a SonarTestReport as metric source to the
    project. See https://github.com/ICTU/quality-report/wiki/Unit-test-metrics.


2017-10-16  Release 2.9.9

  * Update openvas metric parser and unit tests to be compatible with reports generated by openvas version 9.


2017-10-11  Release 2.9.8

  * Bug fix: Use a default project definition if the project definition file can't be read, but don't write it to disk
    to prevent overwriting the (faulty) project definition file.


2017-10-09  Release 2.9.7

  * New release identical to release 2.9.6 for testing purposes.


2017-10-09  Release 2.9.6

  * Allow for querying measurable objects for the metrics that have options. This is useful for meta reports.


2017-10-04  Release 2.9.5

  * Bug fix: Don't crash due to missing logging parameters.


2017-10-04  Release 2.9.4

  * Add HQ version to logging.


2017-10-04  Release 2.9.3

  * Bug fix: Don't crash when Jenkins hasn't been configured.


2017-10-04  Release 2.9.2

  * Bug fix: Don't crash when Jenkins hasn't been configured.


2017-10-04  Release 2.9.1

  * Bug fix: When determining last Checkmarx run, be prepared for checks without date and time.


2017-09-29  Release 2.9.0

  * metric_source.TestReport has been renamed to metric_source.SystemTestReport in preparation for multiple test
    report types. Search project definitions for usage of metric_source.TestReport and replace them with
    metric_source.SystemTestReport.


2017-09-27  Release 2.8.1

  * Bug fix: When determining last Checkmarx run, take into account that Checkmarx skips runs when code is unchanged.


2017-09-26  Release 2.8.0

  * Add an UFT test report metric source.


2017-09-25  Release 2.7.0

  * Add a Checkmarx report age metric.


2017-09-25  Release 2.6.8

  * Bug fix: Don't crash when the JaCoCo session HTML file does not contain session information.


2017-09-25  Release 2.6.7

  * Bug fix: Don't count ignored TestNG tests as skipped, but ignore them completely.


2017-09-21  Release 2.6.6

  * Bug fix: Force day-first for for the dates in Splunk performance reports.


2017-09-21  Release 2.6.5

  * Bug fix: Use correct date from the Splunk performance report.


2017-09-21  Release 2.6.4

  * Bug fix: Better template for open findings metrics.


2017-09-21  Release 2.6.3

  * Slightly longer time-out to cater for slow Jira queries.


2017-09-20  Release 2.6.2

  * Bug fix: Support subprojects in Sonar.


2017-09-20  Release 2.6.1

  * Bug fix: Metrics for open findings were missing in the set of optional project requirements.


2017-09-18  Release 2.6.0

  * Add Jira metrics for the number of open findings in different environments.


2017-09-18  Release 2.5.5

  * Bug fix: The target and low target values of the ready user stories metric were reversed.


2017-09-15  Release 2.5.4

  * Bug fix: Mark the manual test cases metric perfect when there are no manual test cases.


2017-09-15  Release 2.5.3

  * Bug fix: Don't mark the manual test cases metric red when there are no manual test cases.


2017-09-15  Release 2.5.2

  * Bug fix: Total LOC metric would report size as number of products times -1 if Sonar is unavailable.
  * Bug fix: Rename Visual Basic to VB.NET


2017-09-11  Release 2.5.1

  * Bug fix: Prevent really long time outs when opening URLs.


2017-09-11  Release 2.5.0

  * Allow for putting strings in dashboard table cells and use them as labels.


2017-09-08  Release 2.4.2

  * Bug fix: Don't crash when SonarQube doesn't respond to the old measures API.


2017-09-06  Release 2.4.1

  * Bug fix: Don't crash when SonarQube doesn't respond to the new measures API.


2017-09-06  Release 2.4.0

  * Add a TestNG test report metric source.


2017-09-05  Release 2.3.0

  * Add a CompactHistory metric source that stores the history in a real JSON format and requires less disk space.
  * Bug fix: Menu items with a check mark didn't work.


2017-08-28  Release 2.2.10

  * Bug fix: The Splunk performance report CSV is encoded in ANSI.


2017-08-28  Release 2.2.9

  * More logging when Splunk performance report can't be parsed.


2017-08-28  Release 2.2.8

  * More logging when Splunk performance report can't be parsed.


2017-08-28  Release 2.2.7

  * Fix Travis release build.


2017-08-28  Release 2.2.6

  * Show traceback when Splunk performance report can't be parsed.


2017-08-27  Release 2.2.5

  * Bug fix: Update parser for new ZAP report structure.


2017-07-21  Release 2.2.4

  * Bug fix: Work around npm dependency issues.


2017-07-20  Release 2.2.3

  * Bug fix: The comment column would sometimes disappear.


2017-07-19  Release 2.2.2

  * Bug fix: Don't show legends in the dashboard.


2017-07-19  Release 2.2.1

  * Use Travis to push the Docker image to Docker Hub.


2017-07-19  Release 2.2.0

  * Add a filter for hiding metrics that haven't had a status change for more than a week.
  * Bug fix: Product size metric was shown twice in the help information.


2017-07-13  Release 2.1.2

  * Bug fix: Don't include related dependencies in the number of dependencies with warnings (OWASP Dependency Check).


2017-07-13  Release 2.1.1

  * Bug fix: Don't let Travis clean the workspace before creating the source distribution.


2017-07-13  Release 2.1.0

  * To provide more accurate feedback to developers, changed the return value for both OWASP Dependency Check parsers
    from total number of severity nodes to total number of vulnerable dependencies.


2017-07-12  Release 2.0.0

  * Remove Google Chart dependencies from frontend and replace with Chart.js so that no internet access is
    needed for creating quality reports.
  * Use React for the front-end.
  * Use Pygal on the back-end to create SVGs of sparkline charts.
  * Use local storage for front-end settings instead of cookies.
  * Move help info into its own tab.


2017-07-06  Release 1.83.1

  * Bug fix: Don't crash when a Checkmarx analysis can't be found.
  * Bug fix: Open CSV files in text mode.


2017-06-30  Release 1.83.0

  * Add metric source for the CSV performance report exported from Splunk by Spirit.


2017-06-28  Release 1.82.9

  * Bug fix: Allow for multiple SonarQube instances as metric source.


2017-06-22  Release 1.82.8

  * Bug fix: Don't crash when a metric can't be retrieved from SonarQube v4.5.7.


2017-06-21  Release 1.82.7

  * Bug fix: Frontend was missing in the Python package.


2017-06-21  Release 1.82.6

  * Bug fix: Don't crash when a metric can't be retrieved from SonarQube.
  * Bug fix: Bring back support for SonarQube v4.5.7.


2017-06-20  Release 1.82.5

  * Bug fix: Update deprecated SonarQube API for fetching a component.
  * Bug fix: New API for fetching component version number and last analyse date and time doesn't work
    before SonarQube v6.3, fallback on older API if necessary.


2017-06-16  Release 1.82.4

  * Bug fix: Don't crash when SonarQube has no analyses for a project yet.


2017-06-16  Release 1.82.3

  * Bug fix: Update deprecated SonarQube API for fetching the SonarQube version number.
  * Bug fix: Update deprecated SonarQube API for fetching a component version number.
  * Bug fix: Update deprecated SonarQube API for fetching a quality profile.
  * Bug fix: Update deprecated SonarQube API for fetching the date and time of the last analysis.
  * Updated minimal SonarQube version to 5.6.6 (the current Long Term Support version).


2017-06-08  Release 1.82.2

  * Bug fix: Required version numbers for C# quality profile and plugin were mixed up.


2017-06-07  Release 1.82.1

  * Bug fix: Use a fluid container for better layout.


2017-06-07  Release 1.82.0

  * Add metric source for a performance report format that is specific to ICTU.


2017-06-06  Release 1.81.17

  * Bug fix: Don't crash when the OpenVAS scan report is invalid or empty.
  * Bug fix: Don't push a canvas in empty dashboard table cells.
  * Remove animation from charts, it's too slow.


2017-06-06  Release 1.81.16

  * Add animation to charts.
  * Make dashboard with pie charts responsive.
  * Add navigation menu to the trends tab.


2017-06-03  Release 1.81.15

  * Bug fix: Don't crash when there are no Checkmarx reports for a specific project.


2017-06-03  Release 1.81.14

  * Make Checkmarx a default requirement for Application domain objects.
  * Generate a default project definition file if no project definition file exists yet.


2017-05-26  Release 1.81.13

  * Use Webpack to bundle the web application.


2017-05-23  Release 1.81.12

  * Bug fix: Show Checkmarx url in the metric sources help menu.


2017-05-18  Release 1.81.11

  * Bug fix: Add missing requirements (VisualBasic, TypeScript, Python) to help information.
  * Move trend graphs to a separate tab so the trend data can be loaded on demand.


2017-05-16  Release 1.81.10

  * Show loading message while loading data.
  * JaCoCo sessions URL changed from .sessions.html to jacoco-session.html. Try both the old and the new one.


2017-05-07  Release 1.81.9

  * Bug fix: Ignore line breaks in Wiki table cells.
  * Remove package cycle metric, it's not supported by SonarQube anymore.


2017-05-07  Release 1.81.8

  * Bug fix: Basic authentication was not working.


2017-05-06  Release 1.81.7

  * Bug fix: Don't crash when the project has a test report, but a product doesn't have a metric source id for the test
    report.


2017-05-06  Release 1.81.6

  * Bug fix: Don't try to use a metric source that needs a metric source id without one.


2017-05-06  Release 1.81.5

  * Bug fix: Don't crash when the coverage percentage in a NCover report is missing.
  * Bug fix: Don't crash when the Wiki is not formatted correctly.
  * Processed latest SIG/TUV evaluation criteria: duplication norm lowered from 5% to 4%.


2017-04-18  Release 1.81.4

  * Bug fix: Escape backslashes in branch names when generating the metrics JSON file.


2017-04-18  Release 1.81.3

  * Bug fix: Don't crash when measuring team progress.


2017-04-18  Release 1.81.2

  * Bug fix: Link to the manual tests Birt report for the number of manual test cases instead of to the what's missing
    report.
  * Bug fix: Quote project names before passing them to Checkmarx.


2017-04-14  Release 1.81.1

  * Bug fix: Don't use card titles of Trello cards to prevent leaking information.


2017-04-13  Release 1.81.0

  * New metric and metric source for reporting on number of Checkmarx warnings.


2017-04-05  Release 1.80.3

  * Bug fix: HTML report would be invalid when metric comments contain new lines.
  * Bug fix: Use correct language codes when querying SonarQube for Python and TypeScript quality profiles.
  * Bug fix: Don't crash when users enter invalid dates in the Wiki.


2017-03-19  Release 1.80.2

  * Bug fix: Don't assume ASCII when decoding JSON.


2017-03-19  Release 1.80.1

  * Bug fix: Don't crash when using Subversion.


2017-03-19  Release 1.80.0

  * Upgrade to Python 3 (tested with Python 3.4 and 3.5).
  * Remove metric and metric source for measuring consistency of Java versions across environments as it's no longer
    used.


2017-03-07  Release 1.79.3

  * Bug fix: Manifest file was incomplete.


2017-03-07  Release 1.79.2

  * Load meta metric history data asynchronously from a JSON file.
  * Update rule names to try when fetching metrics from SonarQube.


2017-03-02  Release 1.79.1

  * Performance improvement.


2017-03-01  Release 1.79.0

  * Introduce an environment domain class.


2017-02-26  Release 1.78.0

  * Remove the need to pass the project as argument to Product, Application, and Component domain classes.


2017-02-22  Release 1.77.10

  * Bug fix: Allow for spaces in Git paths.


2017-02-21  Release 1.77.9

  * Remove the metric for the SonarQube StyleCop plugin as the StyleCop plugin is obsolete.
  * Bug fix: Don't crash when Jenkins hostname can't be resolved.


2017-02-16  Release 1.77.8

  * Add metric for measuring the age of Open VAS Scan reports.


2017-02-15  Release 1.77.7

  * Add metric for measuring the age of OWASP dependency checker reports.


2017-02-12  Release 1.77.6

  * Bug fix: Don't crash when no history file is defined.


2017-02-12  Release 1.77.5

  * Bug fix: Don't crash when no history file is defined.


2017-02-12  Release 1.77.4

  * Bug fix: Don't crash when no history file is defined.


2017-02-12  Release 1.77.3

 * The --project argument can be a filename or a folder. This allows for having multiple project definitions in the
   same folder.


2017-02-12  Release 1.77.2

  * Return exit status 2 if any metric is red or missing and the --failure-exit-code command line option is passed.


2017-02-10  Release 1.77.1

  * Color the report date yellow or red, depending on the age of the report.
  * Bug fix: Don't crash when the coverage percentage in a NCover report is missing.


2017-02-09  Release 1.77.0

  * It's no longer necessary to specify unittests and integration tests as a sub component.
  * Return exit status 2 if not all metrics are green and the --failure-exit-code command line option is passed.


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
