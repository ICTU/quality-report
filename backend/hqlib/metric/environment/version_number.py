"""
Copyright 2012-2019 Ministerie van Sociale Zaken en Werkgelegenheid

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


import re
from distutils.version import LooseVersion
from typing import List

from hqlib.typing import MetricParameters, Number
from ... import metric_source, utils
from ...domain import HigherIsBetterMetric


class SonarVersion(HigherIsBetterMetric):
    """ Measure the version number of Sonar. """
    name = 'Versie van Sonar'
    unit = ''
    norm_template = 'Sonar heeft minimaal versie {target}, lager dan versie {low_target} is rood.'
    template = 'Sonar is versie {value}.'
    target_value = LooseVersion('6.7.0')
    perfect_value = LooseVersion('999.999.999')
    low_target_value = LooseVersion('5.6.4')
    metric_source_class = metric_source.Sonar

    def numerical_value(self) -> Number:
        return -1 if self._missing() else utils.version_number_to_numerical(self.value().version)

    def value(self):
        return -1 if self._missing() else LooseVersion(self._metric_source.version_number())

    def _missing(self) -> bool:
        return self._metric_source.version_number() is None if self._metric_source else True

    def _metric_source_urls(self) -> List[str]:
        """ Return a list of metric source urls to be used to create the url dict. """
        if self._metric_source:
            return [self._metric_source.url()]
        return []


class SonarQualityProfileVersion(HigherIsBetterMetric):
    """ Measure the version number of the default Sonar quality profile for a specific language. """
    name = 'Versie van het Sonar <subclass responsibility> quality profile'
    unit = ''
    language_key = 'Subclass responsibility'
    language_name = 'Subclass responsibility'
    norm_template = 'Sonar {language} quality profile heeft minimaal versie {target}, ' \
                    'lager dan versie {low_target} is rood.'
    template = 'Sonar {language} quality profile is versie {value}.'
    target_value = LooseVersion('1.0')
    perfect_value = LooseVersion('999.999.999')
    low_target_value = LooseVersion('0.9')
    metric_source_class = metric_source.Sonar

    @classmethod
    def norm_template_default_values(cls) -> MetricParameters:
        default_values = super(SonarQualityProfileVersion, cls).norm_template_default_values()
        default_values['language'] = cls.language_name
        return default_values

    def numerical_value(self) -> Number:
        if self._missing():
            return -1
        numerical_parts = tuple([part for part in self.value().version if isinstance(part, int) and part < 999])
        return utils.version_number_to_numerical(numerical_parts)

    def value(self):
        if self._missing():
            return LooseVersion('0.0')
        profile_name = self._metric_source.default_quality_profile(self.language_key)
        match = re.search(r"v\d+(\.\d+){1,2}", profile_name)
        profile_version = match.group()[1:] if match else '0.0'
        return LooseVersion(profile_version)

    def _metric_source_urls(self) -> List[str]:
        return [self._metric_source.quality_profiles_url()] if self._metric_source else []

    def _parameters(self) -> MetricParameters:
        parameters = super()._parameters()
        parameters['language'] = self.language_name
        return parameters

    def _missing(self) -> bool:
        return self._metric_source.default_quality_profile(self.language_key) in ('', None) \
            if self._metric_source else True


class SonarQualityProfileVersionJava(SonarQualityProfileVersion):
    """ Measure the version number of the default Sonar quality profile for Java. """
    name = 'Versie van het Sonar Java quality profile'
    language_key = 'java'
    language_name = 'Java'
    target_value = LooseVersion('1.8')
    low_target_value = LooseVersion('1.7')


class SonarQualityProfileVersionCSharp(SonarQualityProfileVersion):
    """ Measure the version number of the default Sonar quality profile for CSharp. """
    name = 'Versie van het Sonar C# quality profile'
    language_key = 'cs'
    language_name = 'C#'
    target_value = LooseVersion('1.4')
    low_target_value = LooseVersion('1.4')


class SonarQualityProfileVersionJS(SonarQualityProfileVersion):
    """ Measure the version number of the default Sonar quality profile for JavaScript. """
    name = 'Versie van het Sonar JavaScript quality profile'
    language_key = 'js'
    language_name = 'JavaScript'
    target_value = LooseVersion('1.4')
    low_target_value = LooseVersion('1.2')


class SonarQualityProfileVersionWeb(SonarQualityProfileVersion):
    """ Measure the version number of the default Sonar quality profile for Web. """
    name = 'Versie van het Sonar Web quality profile'
    language_key = 'web'
    language_name = 'Web'
    target_value = LooseVersion('1.1')
    low_target_value = LooseVersion('1.0')


class SonarQualityProfileVersionVisualBasic(SonarQualityProfileVersion):
    """ Measure the version number of the default Sonar quality profile for Visual Basic .NET. """
    name = 'Versie van het Sonar Visual Basic .NET quality profile'
    language_key = 'vbnet'
    language_name = 'Visual Basic .NET'
    target_value = LooseVersion('1.0')
    low_target_value = LooseVersion('1.0')


class SonarQualityProfileVersionPython(SonarQualityProfileVersion):
    """ Measure the version number of the default Sonar quality profile for Python. """
    name = 'Versie van het Sonar Python quality profile'
    language_key = 'py'
    language_name = 'Python'
    target_value = LooseVersion('1.0')
    low_target_value = LooseVersion('1.0')


class SonarQualityProfileVersionTypeScript(SonarQualityProfileVersion):
    """ Measure the version number of the default Sonar quality profile for TypeScript. """
    name = 'Versie van het Sonar TypeScript quality profile'
    language_key = 'ts'
    language_name = 'TypeScript'
    target_value = LooseVersion('1.0')
    low_target_value = LooseVersion('1.0')


class SonarPluginVersion(HigherIsBetterMetric):
    """ Measure the version number of a Sonar plugin. """
    name = 'Versie van de Sonar <subclass responsibility> plugin'
    unit = ''
    plugin_key = 'Subclass responsibility'
    plugin_name = 'Subclass responsibility'
    norm_template = 'Sonar plugin {plugin} heeft minimaal versie {target}, lager dan versie {low_target} is rood.'
    template = 'Sonar plugin {plugin} is versie {value}.'
    target_value = LooseVersion('1.0')
    perfect_value = LooseVersion('999.999.999')
    low_target_value = LooseVersion('0.1')
    metric_source_class = metric_source.Sonar

    @classmethod
    def norm_template_default_values(cls) -> MetricParameters:
        default_values = super(SonarPluginVersion, cls).norm_template_default_values()
        default_values['plugin'] = cls.plugin_name
        return default_values

    def numerical_value(self) -> int:
        return -1 if self._missing() else utils.version_number_to_numerical(self.value().version)

    def value(self):
        return LooseVersion('0.0' if self._missing() else self._metric_source.plugin_version(self.plugin_key))

    def _metric_source_urls(self) -> List[str]:
        return [self._metric_source.plugins_url()] if self._metric_source else []

    def _parameters(self) -> MetricParameters:
        parameters = super()._parameters()
        parameters['plugin'] = self.plugin_name
        return parameters

    def _missing(self) -> bool:
        return self._metric_source.plugin_version(self.plugin_key) in ('0.0', None) if self._metric_source else True


class SonarPluginVersionJava(SonarPluginVersion):
    """ Measure the version number of the Java Sonar plugin. """
    name = 'Versie van de Sonar Java plugin'
    plugin_key = 'java'
    plugin_name = 'Java'
    target_value = LooseVersion('3.14')
    low_target_value = LooseVersion('3.13.1')


class SonarPluginVersionCSharp(SonarPluginVersion):
    """ Measure the version number of the C# Sonar plugin. """
    name = 'Versie van de Sonar C# plugin'
    plugin_key = 'csharp'
    plugin_name = 'C#'
    target_value = LooseVersion('5.11')
    low_target_value = LooseVersion('5.2')


class SonarPluginVersionJS(SonarPluginVersion):
    """ Measure the version number of the JavaScript Sonar plugin. """
    name = 'Versie van de Sonar JavaScript plugin'
    plugin_key = 'javascript'
    plugin_name = 'JavaScript'
    target_value = LooseVersion('2.13')
    low_target_value = LooseVersion('2.12')


class SonarPluginVersionWeb(SonarPluginVersion):
    """ Measure the version number of the Web Sonar plugin. """
    name = 'Versie van de Sonar Web plugin'
    plugin_key = 'web'
    plugin_name = 'Web'
    target_value = LooseVersion('2.4')
    low_target_value = LooseVersion('2.3')


class SonarPluginVersionVisualBasic(SonarPluginVersion):
    """ Measure the version number of the Visual Basic .NET Sonar plugin. """
    name = 'Versie van de Sonar Visual Basic .NET plugin'
    plugin_key = 'vbnet'
    plugin_name = 'VB.NET'
    target_value = LooseVersion('3.0.3')
    low_target_value = LooseVersion('3.0')


class SonarPluginVersionPython(SonarPluginVersion):
    """ Measure the version number of the Python Sonar plugin. """
    name = 'Versie van de Sonar Python plugin'
    plugin_key = 'python'
    plugin_name = 'Python'
    target_value = LooseVersion('1.7')
    low_target_value = LooseVersion('1.6')


class SonarPluginVersionTypeScript(SonarPluginVersion):
    """ Measure the version number of the TypeScript Sonar plugin. """
    name = 'Versie van de Sonar TypeScript plugin'
    plugin_key = 'typescript'
    plugin_name = 'TypeScript'
    target_value = LooseVersion('0.98')
    low_target_value = LooseVersion('0.97')
