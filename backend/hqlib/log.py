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

from typing import Set
import logging


class SuppressRepeatMessages(logging.Filter):  # pylint: disable=too-few-public-methods
    """ Filter to suppress logging of repeated messages. """
    def __init__(self) -> None:
        self.__messages_seen: Set[str] = set()
        super().__init__()

    def filter(self, record: logging.LogRecord) -> bool:
        """ Decide whether the record should be logged. """
        message = record.getMessage()
        is_new_message = message not in self.__messages_seen
        if is_new_message:
            self.__messages_seen.add(message)
        return is_new_message


def init_logging(log_level: str) -> None:
    """ Initialize logging for the application. """
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=log_level.upper())
    logging.getLogger().addFilter(SuppressRepeatMessages())
