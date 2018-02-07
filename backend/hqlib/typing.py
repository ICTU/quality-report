"""
Copyright 2012-2018 Ministerie van Sociale Zaken en Werkgelegenheid

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

import datetime
from distutils.version import LooseVersion
from typing import Dict, Union, Tuple, Sequence, Optional

from .domain.base import DomainObject


# pylint: disable=invalid-name

Number = Union[float, int]
DateTime = datetime.datetime
TimeDelta = datetime.timedelta

MetricValue = Union[Number, str, LooseVersion]
MetricParameters = Dict[str, MetricValue]
DashboardColumns = Sequence[Tuple[str, int]]
DashboardRows = Sequence[Sequence[Tuple[Union[DomainObject, str], str, Optional[Tuple[int, int]]]]]
Dashboard = Tuple[DashboardColumns, DashboardRows]
HistoryRecord = Dict[str, Union[Tuple[str, str, str], str]]
