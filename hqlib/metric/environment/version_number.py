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

import re
from distutils.version import LooseVersion

from ... import metric_source, utils
from ...domain import HigherIsBetterMetric


class SonarVersion(HigherIsBetterMetric):
    """ Measure the version number of Sonar. """
    name = 'Sonar versie'
    unit = ''
    norm_template = 'Sonar heeft minimaal versie {target}, lager dan versie {low_target} is rood.'
    template = 'Sonar is versie {value}.'
    target_value = LooseVersion('4.5.7')
    perfect_value = LooseVersion('999.999.999')
    low_target_value = LooseVersion('4.5.6')
    metric_source_classes = (metric_source.Sonar,)

    def numerical_value(self):
        return -1 if self._missing() else utils.version_number_to_numerical(self.value().version)

    def value(self):
        return -1 if self._missing() else LooseVersion(self._metric_source.version_number())

    def _missing(self):
        return self._metric_source.version_number() is None


class SonarQualityProfileVersion(HigherIsBetterMetric):
    """ Measure the version number of the default Sonar quality profile for a specific language. """
    name = 'Sonar quality profile versie'
    unit = ''
    language_key = 'Subclass responsibility'
    language_name = 'Subclass responsibility'
    norm_template = 'Sonar {language} quality profile heeft minimaal versie {target}, ' \
                    'lager dan versie {low_target} is rood.'
    template = 'Sonar {language} quality profile is versie {value}.'
    target_value = LooseVersion('1.0')
    perfect_value = LooseVersion('999.999.999')
    low_target_value = LooseVersion('0.9')
    metric_source_classes = (metric_source.Sonar,)

    @classmethod
    def norm_template_default_values(cls):
        default_values = super(SonarQualityProfileVersion, cls).norm_template_default_values()
        default_values['language'] = cls.language_name
        return default_values

    def numerical_value(self):
        if self._missing():
            return -1
        else:
            numerical_parts = [part for part in self.value().version if isinstance(part, int) and part < 999]
            return utils.version_number_to_numerical(numerical_parts)

    def value(self):
        if self._missing():
            return LooseVersion('0.0')
        else:
            profile_name = self._metric_source.default_quality_profile(self.language_key)
            match = re.search(r"v\d+(\.\d+){1,2}", profile_name)
            profile_version = match.group()[1:] if match else '0.0'
            return LooseVersion(profile_version)

    def _metric_source_urls(self):
        return [self._metric_source.quality_profiles_url()]

    def _parameters(self):
        parameters = super(SonarQualityProfileVersion, self)._parameters()
        parameters['language'] = self.language_name
        return parameters

    def _missing(self):
        return self._metric_source.default_quality_profile(self.language_key) in ('', None)


class SonarQualityProfileVersionJava(SonarQualityProfileVersion):
    """ Measure the version number of the default Sonar quality profile for Java. """
    name = 'Sonar Java quality profile versie'
    language_key = 'java'
    language_name = 'Java'
    target_value = LooseVersion('1.8')
    low_target_value = LooseVersion('1.7')


class SonarQualityProfileVersionCSharp(SonarQualityProfileVersion):
    """ Measure the version number of the default Sonar quality profile for CSharp. """
    name = 'Sonar C# quality profile versie'
    language_key = 'cs'
    language_name = 'C#'
    target_value = LooseVersion('1.1')
    low_target_value = LooseVersion('1.0')


class SonarQualityProfileVersionJS(SonarQualityProfileVersion):
    """ Measure the version number of the default Sonar quality profile for JavaScript. """
    name = 'Sonar JavaScript quality profile versie'
    language_key = 'js'
    language_name = 'JavaScript'
    target_value = LooseVersion('1.4')
    low_target_value = LooseVersion('1.2')


class SonarQualityProfileVersionWeb(SonarQualityProfileVersion):
    """ Measure the version number of the default Sonar quality profile for Web. """
    name = 'Sonar Web quality profile versie'
    language_key = 'web'
    language_name = 'Web'
    target_value = LooseVersion('1.1')
    low_target_value = LooseVersion('1.0')


class SonarPluginVersion(HigherIsBetterMetric):
    """ Measure the version number of a Sonar plugin. """
    name = 'Sonar plugin versie'
    unit = ''
    plugin_key = 'Subclass responsibility'
    plugin_name = 'Subclass responsibility'
    norm_template = 'Sonar plugin {plugin} heeft minimaal versie {target}, lager dan versie {low_target} is rood.'
    template = 'Sonar plugin {plugin} is versie {value}.'
    target_value = LooseVersion('1.0')
    perfect_value = LooseVersion('999.999.999')
    low_target_value = LooseVersion('0.1')
    metric_source_classes = (metric_source.Sonar,)

    @classmethod
    def norm_template_default_values(cls):
        default_values = super(SonarPluginVersion, cls).norm_template_default_values()
        default_values['plugin'] = cls.plugin_name
        return default_values

    def numerical_value(self):
        return -1 if self._missing() else utils.version_number_to_numerical(self.value().version)

    def value(self):
        return LooseVersion('0.0' if self._missing() else self._metric_source.plugin_version(self.plugin_key))

    def _metric_source_urls(self):
        return [self._metric_source.plugins_url()]

    def _parameters(self):
        parameters = super(SonarPluginVersion, self)._parameters()
        parameters['plugin'] = self.plugin_name
        return parameters

    def _missing(self):
        return self._metric_source.plugin_version(self.plugin_key) in ('0.0', None)


class SonarPluginVersionJava(SonarPluginVersion):
    """ Measure the version number of the Java Sonar plugin. """
    name = 'Versie van de Sonar Java plugin'
    plugin_key = 'java'
    plugin_name = 'Java'
    target_value = LooseVersion('3.14')
    low_target_value = LooseVersion('3.13.1')


class SonarPluginVersionCheckStyle(SonarPluginVersion):
    """ Measure the version number of the CheckStyle Sonar plugin. """
    name = 'Versie van de Sonar CheckStyle plugin'
    plugin_key = 'checkstyle'
    plugin_name = 'CheckStyle'
    target_value = LooseVersion('2.4')
    low_target_value = LooseVersion('2.3')


class SonarPluginVersionPMD(SonarPluginVersion):
    """ Measure the version number of the PMD Sonar plugin. """
    name = 'Versie van de Sonar PMD plugin'
    plugin_key = 'pmd'
    plugin_name = 'PMD'
    target_value = LooseVersion('2.5')
    low_target_value = LooseVersion('2.4.1')


class SonarPluginVersionFindBugs(SonarPluginVersion):
    """ Measure the version number of the FindBugs Sonar plugin. """
    name = 'Versie van de Sonar FindBugs plugin'
    plugin_key = 'findbugs'
    plugin_name = 'FindBugs'
    target_value = LooseVersion('3.3')
    low_target_value = LooseVersion('3.2')


class SonarPluginVersionCSharp(SonarPluginVersion):
    """ Measure the version number of the C# Sonar plugin. """
    name = 'Versie van de Sonar C# plugin'
    plugin_key = 'csharp'
    plugin_name = 'C#'
    target_value = LooseVersion('5.2')
    low_target_value = LooseVersion('4.2')


class SonarPluginVersionStyleCop(SonarPluginVersion):
    """ Measure the version number of the StyleCop Sonar plugin. """
    name = 'Versie van de Sonar StyleCop plugin'
    plugin_key = 'stylecop'
    plugin_name = 'StyleCop'
    target_value = LooseVersion('1.1')
    low_target_value = LooseVersion('1.0')


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
