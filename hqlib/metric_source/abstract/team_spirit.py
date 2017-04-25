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

from ... import domain


class TeamSpirit(domain.MetricSource):
    """ Abstract class representing a team spirit indicator. """
    metric_source_name = 'Team spirit'

    def team_spirit(self, team_id: str) -> str:
        """ Return the team spirit of the team. Team spirit is either :-), :-|, or :-( """
        raise NotImplementedError  # pragma: nocover
