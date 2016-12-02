[![PyPI](https://img.shields.io/pypi/v/quality_report.svg)](https://pypi.python.org/pypi/quality_report)
[![Build Status](https://travis-ci.org/ICTU/quality-report.png?branch=master)](https://travis-ci.org/ICTU/quality-report)
[![Quality Gate](https://sonarqube.com/api/badges/gate?key=nl.ictu:quality_report)](https://sonarqube.com/dashboard/index/nl.ictu:quality_report)
[![Test Coverage](https://codeclimate.com/github/ICTU/quality-report/badges/coverage.svg)](https://codeclimate.com/github/ICTU/quality-report/coverage)
[![Code Climate](https://codeclimate.com/github/ICTU/quality-report/badges/gpa.svg)](https://codeclimate.com/github/ICTU/quality-report)
[![Code Health](https://landscape.io/github/ICTU/quality-report/master/landscape.svg?style=flat)](https://landscape.io/github/ICTU/quality-report/master)
[![BCH compliance](https://bettercodehub.com/edge/badge/ICTU/quality-report)](https://bettercodehub.com)
[![Dependency Status](https://dependencyci.com/github/ICTU/quality-report/badge)](https://dependencyci.com/github/ICTU/quality-report)
[![](https://images.microbadger.com/badges/image/ictu/quality-report.svg)](https://microbadger.com/images/ictu/quality-report "Get your own image badge on microbadger.com")

HQ - Holistic Software Quality Reporting
========================================

Application to generate quality reports for software development projects.
Holistic because HQ attempts to measure as many aspects of software development as
possible, seeing how software development can go off the rails in so many ways.

HQ itself is developed in Python, but can report on the quality of software 
developed in any language as it doesn't measure the quality itself, but instead
relies on other tools to feed it information. Metric sources include SonarQube, Jenkins,
Jira, Jacoco, JMeter, OWASP dependency checker, and more.

The user interface is in Dutch. 

An example report is available via http://ictu.github.io/quality-report/.

This software was developed by ICTU (http://www.ictu.nl) to support the 
development of the Landelijk Register Kinderopvang for the Ministerie van
Sociale Zaken en Werkgelegenheid.

See docs/AUTHORS.txt for contact information.
See docs/LICENSE.txt for license information.
See docs/INSTALL.txt for installation information.
See docs/HOWTO.txt for information on how to configure quality reports.
