ANNOUNCEMENT
============

**HQ has been replaced by [*Quality-time*](https://github.com/ICTU/quality-time). As of January 1st, 2021, HQ is no longer maintained. No bugs will be fixed. No new features will be developed.**

---

[![PyPI](https://img.shields.io/pypi/v/quality_report.svg)](https://pypi.python.org/pypi/quality_report)
[![Build Status](https://travis-ci.org/ICTU/quality-report.png?branch=master)](https://travis-ci.org/ICTU/quality-report)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=nl.ictu%3Ahq&metric=alert_status)](https://sonarcloud.io/dashboard?id=nl.ictu%3Ahq)
[![BCH compliance](https://bettercodehub.com/edge/badge/ICTU/quality-report?branch=master)](https://bettercodehub.com/)
[![Test Coverage](https://codeclimate.com/github/ICTU/quality-report/badges/coverage.svg)](https://codeclimate.com/github/ICTU/quality-report/coverage)
[![codecov](https://codecov.io/gh/ICTU/quality-report/branch/master/graph/badge.svg)](https://codecov.io/gh/ICTU/quality-report)
[![Code Climate](https://codeclimate.com/github/ICTU/quality-report/badges/gpa.svg)](https://codeclimate.com/github/ICTU/quality-report)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/90b2d74043284cdda06aecc442182946)](https://www.codacy.com/app/frank_10/quality-report?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ICTU/quality-report&amp;utm_campaign=Badge_Grade)
[![codebeat badge](https://codebeat.co/badges/cbffeefc-5efb-41c4-88e1-30a0fc7dd249)](https://codebeat.co/projects/github-com-ictu-quality-report)
[![CodeFactor](https://www.codefactor.io/repository/github/ictu/quality-report/badge)](https://www.codefactor.io/repository/github/ictu/quality-report)
[![Requirements Status](https://requires.io/github/ICTU/quality-report/requirements.svg?branch=master)](https://requires.io/github/ICTU/quality-report/requirements/?branch=master)
[![Known Vulnerabilities](https://snyk.io/test/github/ictu/quality-report/badge.svg?targetFile=backend%2Frequirements.txt)](https://snyk.io/test/github/ictu/quality-report?targetFile=backend%2Frequirements.txt)
[![Updates](https://pyup.io/repos/github/ICTU/quality-report/shield.svg)](https://pyup.io/repos/github/ICTU/quality-report/)
[![](https://images.microbadger.com/badges/image/ictu/quality-report.svg)](https://microbadger.com/images/ictu/quality-report "Get your own image badge on microbadger.com")

HQ - Holistic Software Quality Reporting
========================================

Application  to generate quality reports for software development projects.
Holistic because HQ attempts to measure as many aspects of software development as
possible, seeing how software development can go off the rails in so many ways.

HQ itself is developed in Python (backend) and JavaScript (frontend), but can report on the quality of software
developed in any language as it doesn't measure the quality itself, but instead
relies on other tools to feed it information. Metric sources include SonarQube, Jenkins,
Jira, Jacoco, JMeter, OWASP dependency checker, and more.

The user interface is currently available in Dutch only.

An example report is available via http://ictu.github.io/quality-report/.

This software was developed by ICTU (http://www.ictu.nl) to support the
development of the Landelijk Register Kinderopvang for the Ministerie van
Sociale Zaken en Werkgelegenheid.

See docs/AUTHORS.txt for contact information.
See docs/LICENSE.txt for license information.
See docs/HOWTO.txt for information on how to configure quality reports.

To be notified about HQ releases, you can subscribe to the releases atom feed via
[![Blogtrottr](https://blogtrottr.com/images/icons/blogtrottr-button-91x17px.gif)](https://blogtrottr.com/?subscribe=https://github.com/ICTU/quality-report/releases.atom)

Screenshots
-----------

### Dashboard

Each report has a dashboard that provides an overview of the project.

![Screenshot](docs/screenshot.png)

### Metrics

Clicking a component (pie chart) in the dashboard navigates to the metrics of the clicked component.

![Screenshot](docs/screenshot2.png)

### Trend

Recent changes in individual metrics are displayed using spark line graphs.
Long term changes are visible in the trend graphs.

![Screenshot](docs/screenshot3.png)

Usage
-----

### Using Python 3.7

We recommend using virtualenv:

```console
$ mkdir hq
$ cd hq
$ virtualenv --python-python3.7 .venv
$ . .venv/bin/activate
```

Unfortunately, one package that HQ uses isn't available from the Python Package Index (PyPI) and needs to be installed manually before we can install HQ itself:
```console
$ pip install 'git+https://github.com/wekan/wekan-python-api-client.git#egg=wekanapi&subdirectory=src'
$ pip install quality_report
```

HQ can now be started from the command line. Adding the `--help` parameter should show a brief help message:

```console
$ quality_report.py --help
```

See the [HQ Wiki](https://github.com/ICTU/quality-report/wiki) for more information on how to configure quality reports.

### Using Docker

Pull the image from Docker Hub:

```console
$ docker pull ictu/quality-report
```

HQ can now be started from the command line. Adding the `--help` parameter should show a brief help message:

```console
$ docker run --rm -u `id -u`:`id -g` -v /etc/localtime:/etc/localtime:ro -v `pwd`:/work -w /work ictu/quality-report --help
```

See the [HQ Wiki](https://github.com/ICTU/quality-report/wiki) for more information on how to configure quality reports.

