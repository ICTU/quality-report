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
import logging

from hqlib import log


class SuppressRepeatMessagesTest(unittest.TestCase):
    """ Unit tests of the SuppressRepeatMessages class. """
    def setUp(self):
        self.__suppressor = log.SuppressRepeatMessages()

    @staticmethod
    def log_message(number=0):
        """ Create a log message. """
        return logging.LogRecord('name', 'level', 'pathname', 1, 'msg {0}'.format(number), [], 'exc_info')

    def test_filter_one_message(self):
        """Test one message. """
        self.assertTrue(self.__suppressor.filter(self.log_message()))

    def test_filter_two_different_messages(self):
        """Test two different messages. """
        self.assertTrue(self.__suppressor.filter(self.log_message(1)))
        self.assertTrue(self.__suppressor.filter(self.log_message(2)))

    def test_filter_two_equal_messages(self):
        """Test two equal messages. """
        self.assertTrue(self.__suppressor.filter(self.log_message()))
        self.assertFalse(self.__suppressor.filter(self.log_message()))


class InitLogTest(unittest.TestCase):
    """ Unit tests for the initLogging method. """

    def test_init(self):
        """ Test that the logging system is initialized properly. """

        root_logger = logging.getLogger()

        def reset_logging_system():
            """ Reset the logging system so we can initialize it. """
            for handler in root_logger.handlers:
                root_logger.removeHandler(handler)

        reset_logging_system()
        log.init_logging("DEBUG")
        self.assertEqual(logging.DEBUG, root_logger.getEffectiveLevel())
        reset_logging_system()
        log.init_logging("CRITICAL")
        self.assertEqual(logging.CRITICAL, root_logger.getEffectiveLevel())
