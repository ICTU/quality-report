"""
Copyright 2012-2016 Ministerie van Sociale Zaken en Werkgelegenheid

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

from ..domain import Requirement
from .. import metric


JAVA_SONAR_PLUGINS = Requirement(
    name='SonarQube Java plugins',
    metric_classes={metric.SonarPluginVersionJava, metric.SonarPluginVersionCheckStyle, metric.SonarPluginVersionPMD,
                    metric.SonarPluginVersionFindBugs})

DOT_NET_SONAR_PLUGINS = Requirement(
    name='SonarQube DotNet plugins',
    metric_classes={metric.SonarPluginVersionCSharp, metric.SonarPluginVersionStyleCop,
                    metric.SonarPluginVersionReSharper})

WEB_SONAR_PLUGINS = Requirement(
    name='SonarQube Web plugins',
    metric_classes={metric.SonarPluginVersionWeb, metric.SonarPluginVersionJS})
