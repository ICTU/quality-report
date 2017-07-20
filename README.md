[![PyPI](https://img.shields.io/pypi/v/quality_report.svg)](https://pypi.python.org/pypi/quality_report)
[![Build Status](https://travis-ci.org/ICTU/quality-report.png?branch=master)](https://travis-ci.org/ICTU/quality-report)
[![Quality Gate](https://sonarqube.com/api/badges/gate?key=nl.ictu:hq)](https://sonarqube.com/dashboard/index/nl.ictu:hq)
[![Test Coverage](https://codeclimate.com/github/ICTU/quality-report/badges/coverage.svg)](https://codeclimate.com/github/ICTU/quality-report/coverage)
[![Coverage Status](https://coveralls.io/repos/github/ICTU/quality-report/badge.png?branch=master)](https://coveralls.io/github/ICTU/quality-report?branch=master)
[![codecov](https://codecov.io/gh/ICTU/quality-report/branch/master/graph/badge.svg)](https://codecov.io/gh/ICTU/quality-report)
[![Code Climate](https://codeclimate.com/github/ICTU/quality-report/badges/gpa.svg)](https://codeclimate.com/github/ICTU/quality-report)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/90b2d74043284cdda06aecc442182946)](https://www.codacy.com/app/frank_10/quality-report?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ICTU/quality-report&amp;utm_campaign=Badge_Grade)
[![codebeat badge](https://codebeat.co/badges/cbffeefc-5efb-41c4-88e1-30a0fc7dd249)](https://codebeat.co/projects/github-com-ictu-quality-report)
[![CodeFactor](https://www.codefactor.io/repository/github/ictu/quality-report/badge)](https://www.codefactor.io/repository/github/ictu/quality-report)
[![Dependency Status](https://dependencyci.com/github/ICTU/quality-report/badge)](https://dependencyci.com/github/ICTU/quality-report)
[![Requirements Status](https://requires.io/github/ICTU/quality-report/requirements.svg?branch=master)](https://requires.io/github/ICTU/quality-report/requirements/?branch=master)
[![Dependency Status](https://www.versioneye.com/user/projects/58891e2fc64626004feb312f/badge.svg?style=flat-square)](https://www.versioneye.com/user/projects/58891e2fc64626004feb312f)
[![Updates](https://pyup.io/repos/github/ICTU/quality-report/shield.svg)](https://pyup.io/repos/github/ICTU/quality-report/)
[![](https://images.microbadger.com/badges/image/ictu/quality-report.svg)](https://microbadger.com/images/ictu/quality-report "Get your own image badge on microbadger.com")

HQ - Holistic Software Quality Reporting
========================================

Application to generate quality reports for software development projects.
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

### Using Python 3.6

Install HQ from the Python Package Index (PyPI):

    pip install quality_report

We recommend using virtualenv:

    $HQ_VIRTUAL_ENV=/home/jenkins/hq-pyenv  # For example

    # Delete previous version
    if [ -d $HQ_VIRTUAL_ENV ]; then
        rm -rf $HQ_VIRTUAL_ENV
    fi
    
    # Create the virtualenv and activate it
    virtualenv $HQ_VIRTUAL_ENV
    . $HQ_VIRTUAL_ENV/bin/activate
    
    # Install HQ
    pip install quality_report
    
HQ can now be started from the command line:

    $PROJECT=/path/to/project_definition_folder
    $REPORT=/path/to/folder/to/write/report/to
    quality_report.py --project $PROJECT --report $REPORT

### Using Docker

Pull the image from Docker Hub:

    docker pull ictu/quality-report

HQ can now be started from the command line:

    $PROJECT=/path/to/project_definition_folder
    $REPORT=/path/to/folder/to/write/report/to
    docker run --rm -u `id -u`:`id -g` -v /etc/localtime:/etc/localtime:ro -v `pwd`:/work -w /work ictu/quality-report --project $PROJECT --report $REPORT
