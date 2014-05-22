'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''


class MeasurableObject(object):  # pylint: disable=too-few-public-methods
    ''' An object that has measurable characteristics. Base class for products,
        teams, etc. '''
    def __init__(self, targets=None, low_targets=None, 
                 technical_debt_targets=None):
        self._targets = targets or dict()
        self.__low_targets = low_targets or dict()
        self._technical_debt_targets = technical_debt_targets or dict()

    def target(self, metric_class):
        ''' Return the target for the specified metric. '''
        return self._targets.get(metric_class, None)

    def low_target(self, metric_class):
        ''' Return the low target for the specified metric. '''
        return self.__low_targets.get(metric_class, None)

    def technical_debt_target(self, metric_class):
        ''' Return whether a score below target is considered to be accepted
            technical debt. '''
        return self._technical_debt_targets.get(metric_class, None)
