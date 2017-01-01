"""
Copyright 2012-2017 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from __future__ import absolute_import

from .. import metric
from ..domain import Requirement


class Java(Requirement):
    """ Require Sonar to be ready for analyzing Java code. """
    _name = 'Java'
    _metric_classes = (metric.SonarPluginVersionJava, metric.SonarPluginVersionCheckStyle, metric.SonarPluginVersionPMD,
                       metric.SonarPluginVersionFindBugs, metric.SonarQualityProfileVersionJava)


class CSharp(Requirement):
    """ Require Sonar to be ready for analyzing C# code. """
    _name = 'C#'
    _metric_classes = (metric.SonarPluginVersionCSharp, metric.SonarPluginVersionStyleCop,
                       metric.SonarQualityProfileVersionCSharp)


class JavaScript(Requirement):
    """ Require Sonar to be ready for analyzing JavaScript code. """
    _name = 'JavaScript'
    _metric_classes = (metric.SonarPluginVersionJS, metric.SonarQualityProfileVersionJS)


class Web(Requirement):
    """ Require Sonar to be ready for analyzing Web (HTML, JSF) code. """
    _name = 'Web'
    _metric_classes = (metric.SonarPluginVersionWeb, metric.SonarQualityProfileVersionWeb)
