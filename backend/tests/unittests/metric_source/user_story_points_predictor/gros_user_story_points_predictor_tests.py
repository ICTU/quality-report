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

import unittest
from unittest.mock import patch
from urllib.error import URLError

from hqlib.metric_source import GROSUserStoryPointsPredictor, UrlOpener


class GROSUserStoryPointsPredictorTest(unittest.TestCase):
    """ Unit tests for the GROS user story points predictor metric source. """

    @patch.object(UrlOpener, "url_read")
    def test_planned(self, mock_url_read):
        """ Test that the planned number of user story points can be retrieved. """
        mock_url_read.return_value = '{"features": {"num_story_points": 50}}'
        predictor = GROSUserStoryPointsPredictor("url")
        self.assertEqual(50, predictor.planned_number_of_user_story_points("project"))

    @patch.object(UrlOpener, "url_read")
    def test_prediction(self, mock_url_read):
        """ Test that the predicted number of user story points can be retrieved. """
        mock_url_read.return_value = '{"prediction": 42}'
        predictor = GROSUserStoryPointsPredictor("url")
        self.assertEqual(42, predictor.predicted_number_of_user_story_points("project"))

    @patch.object(UrlOpener, "url_read")
    def test_url_exception(self, mock_url_read):
        """ Test that the predictor returns -1 on error. """
        mock_url_read.side_effect = URLError("reason")
        predictor = GROSUserStoryPointsPredictor("url")
        self.assertEqual(-1, predictor.predicted_number_of_user_story_points("project"))

    @patch.object(UrlOpener, "url_read")
    def test_faulty_json(self, mock_url_read):
        """ Test that the predictor returns -1 on error. """
        mock_url_read.return_value = "{buggy json"
        predictor = GROSUserStoryPointsPredictor("url")
        self.assertEqual(-1, predictor.predicted_number_of_user_story_points("project"))

    @patch.object(UrlOpener, "url_read")
    def test_missing_field(self, mock_url_read):
        """ Test that the predictor returns -1 on error. """
        mock_url_read.return_value = "{}"
        predictor = GROSUserStoryPointsPredictor("url")
        self.assertEqual(-1, predictor.predicted_number_of_user_story_points("project"))

    def test_urls(self):
        """ Test that the predictor returns the correct urls. """
        predictor = GROSUserStoryPointsPredictor("http://gros/")
        self.assertEqual(["http://gros/branch/abe-validation-results/project"], predictor.metric_source_urls("project"))
