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

import logging
from typing import Callable, List

from hqlib.utils import eval_json

from ..url_opener import UrlOpener
from ..abstract.user_story_points_predictor import UserStoryPointsPredictor


class GROSUserStoryPointsPredictor(UserStoryPointsPredictor):
    """ Metric source for the GROS ("Grip op Software") user story predictor API. """
    metric_source_name = "GROS user story points predictor"

    def __init__(self, url: str, username: str = "", password: str = "") -> None:
        self.__url_opener = UrlOpener(username=username, password=password)
        self.__base_url = url + "" if url.endswith("/") else "/"
        self.__url = self.__base_url + "api/v1-abe-validation-results/predict/jira/{metric_source_id}/sprint/latest"
        super().__init__()

    def metric_source_urls(self, *metric_source_ids: str) -> List[str]:
        """ Return the urls for the projects. """
        return [self.__base_url + 'branch/abe-validation-results/' + metric_source_id
                for metric_source_id in metric_source_ids]

    def predicted_number_of_user_story_points(self, *metric_source_ids: str) -> float:
        """ Return the predicted number of user story points of the given projects. """
        return self.__get_json_field(lambda json: json["prediction"], "json[prediction]", *metric_source_ids)

    def planned_number_of_user_story_points(self, *metric_source_ids: str) -> float:
        """ Return the planned number of user story points of the given projects. """
        return self.__get_json_field(lambda json: json["features"]["num_story_points"],
                                     "json[features][num_story_points]", *metric_source_ids)

    def __get_json_field(self, get_field_from_json: Callable, field_name: str, *metric_source_ids: str) -> float:
        """ Retrieve the JSON and use the callback to get the right field from the JSON structure. """
        result = 0
        for metric_source_id in metric_source_ids:
            url = self.__url.format(metric_source_id=metric_source_id)
            try:
                json_string = self.__url_opener.url_read(url)
            except UrlOpener.url_open_exceptions as reason:
                return -1
            try:
                json = eval_json(json_string)
            except (ValueError, TypeError, KeyError) as reason:
                logging.error("Couldn't evaluate JSON retrieved from %s: %s", url, reason)
                logging.error("JSON received: %s", json_string)
                return -1
            try:
                result += float(get_field_from_json(json))
            except (KeyError, ValueError) as reason:
                logging.error("Couldn't get %s from JSON retrieved from %s: %s", field_name, url, reason)
                logging.error("JSON received: %s", json)
                return -1
        return result
