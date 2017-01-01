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


# <MetricSource><DomainObject>Info classes provide bridges between metric
# sources and domain objects. They make it possible that domain objects have
# no knowledge of metric sources and vice versa.

from .sonar_product_info import SonarProductInfo
from .version_control_system_product_info import VersionControlSystemProductInfo
