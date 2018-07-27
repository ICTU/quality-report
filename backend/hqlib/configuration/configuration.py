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
import sys
import logging

from ..domain import Project


def project(project_folder_or_filename: str) -> Project:
    """ Import the project from the project definition file in the project folder. """
    project_definition_path = pathlib.Path(project_folder_or_filename).resolve()
    if project_definition_path.suffix != '.py':
        project_definition_path = project_definition_path / 'project_definition.py'

    # remember current path to restore it when we're done
    old_sys_path = sys.path.copy()

    # Add the parent folder of the project folder to the python path so the
    # project definition can import shared resources from other folders.
    sys.path.insert(0, str(project_definition_path.parent.parent))

    # Add the project folder itself to the python path so that we can import the project definition itself.
    sys.path.insert(0, str(project_definition_path.parent))

    # Import the project definition and get the project from it.
    module_name = project_definition_path.stem
    try:
        return __import__(module_name).PROJECT
    except ModuleNotFoundError as reason:
        logging.critical("Couldn't open %s: %s.", module_name, reason)
        raise
    except AttributeError as reason:
        logging.critical("Couldn't get PROJECT from %s: %s.", module_name, reason)
        raise
    finally:
        sys.path = old_sys_path
