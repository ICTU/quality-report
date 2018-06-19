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
import pathlib
import json
import logging
from typing import List, Dict, Union


class JsonPersister():
    """ Abstract class defining the interface for json persistence (to file system, mongo db or else). """

    @classmethod
    def read_json(cls, location: str) -> Dict[str, Union[List, Dict]]:
        """ Reads persisted json document. """
        raise NotImplementedError

    @classmethod
    def write_json(cls, document, location: str):
        """ Writes json document to the persistence layer. """
        raise NotImplementedError


class FilePersister(JsonPersister):
    """ Saves/reads json documents to file system. """

    @classmethod
    def read_json(cls, location: str) -> Dict[str, Union[List, Dict]]:
        """ Returns the parsed json document from the file. """
        path = pathlib.Path(location)
        try:
            return json.loads(path.read_text())
        except (IOError, FileNotFoundError):
            logging.error("Error reading file %s.", location)
            return None

    @classmethod
    def write_json(cls, document, location: str):
        """ Writes json document to a file. """
        path = pathlib.Path(location)
        try:
            path.write_text(json.dumps(document, sort_keys=True, indent=2), encoding='utf-8')
        except IOError:
            logging.error("Error writing file %s.", location)
