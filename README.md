[![PyPI](https://img.shields.io/pypi/v/quality_report.svg)](https://pypi.python.org/pypi/quality_report)
[![Build Status](https://travis-ci.org/ICTU/quality-report.png?branch=master)](https://travis-ci.org/ICTU/quality-report)
[![Quality Gate](https://sonarqube.com/api/badges/gate?key=nl.ictu:quality_report)](https://sonarqube.com/dashboard/index/nl.ictu:quality_report)
[![Test Coverage](https://codeclimate.com/github/ICTU/quality-report/badges/coverage.svg)](https://codeclimate.com/github/ICTU/quality-report/coverage)
[![Coverage Status](https://coveralls.io/repos/github/ICTU/quality-report/badge.svg?branch=master)](https://coveralls.io/github/ICTU/quality-report?branch=master)
[![Code Climate](https://codeclimate.com/github/ICTU/quality-report/badges/gpa.svg)](https://codeclimate.com/github/ICTU/quality-report)
[![Code Issues](https://www.quantifiedcode.com/api/v1/project/97781bcab5044cbdb2ca863bc2b9c6bc/badge.svg)](https://www.quantifiedcode.com/app/project/97781bcab5044cbdb2ca863bc2b9c6bc)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/90b2d74043284cdda06aecc442182946)](https://www.codacy.com/app/frank_10/quality-report?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ICTU/quality-report&amp;utm_campaign=Badge_Grade)
[![codebeat badge](https://codebeat.co/badges/cbffeefc-5efb-41c4-88e1-30a0fc7dd249)](https://codebeat.co/projects/github-com-ictu-quality-report)
[![Dependency Status](https://dependencyci.com/github/ICTU/quality-report/badge)](https://dependencyci.com/github/ICTU/quality-report)
[![Requirements Status](https://requires.io/github/ICTU/quality-report/requirements.svg?branch=master)](https://requires.io/github/ICTU/quality-report/requirements/?branch=master)
[![Dependency Status](https://www.versioneye.com/user/projects/58891e2fc64626004feb312f/badge.svg?style=flat-square)](https://www.versioneye.com/user/projects/58891e2fc64626004feb312f)
[![Updates](https://pyup.io/repos/github/ictu/quality-report/shield.svg)](https://pyup.io/repos/github/ictu/quality-report/)
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
