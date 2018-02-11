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

import os
import sys
import logging


def project(project_folder_or_filename):
    """ Import the project from the project definition file in the project folder. """
    if project_folder_or_filename.endswith('.py'):
        project_folder, project_definition_filename = project_folder_or_filename.rsplit('/', 1)
    else:
        project_folder, project_definition_filename = project_folder_or_filename, 'project_definition.py'

    # Add the parent folder of the project folder to the python path so the
    # project definition can import shared resources from other folders.
    sys.path.insert(0, os.path.abspath(os.path.join(project_folder, '..')))

    # Add the project folder itself to the python path so that we can import the project definition itself.
    sys.path.insert(0, project_folder)

    # Import the project definition and get the project from it.
    # Use the default project definition if it doesn't exist.
    module_name = project_definition_filename[:-len('.py')]
    try:
        return __import__(module_name).PROJECT
    except ModuleNotFoundError as reason:
        logging.error("Couldn't open %s: %s.", module_name, reason)
        raise
    except AttributeError as reason:
        logging.error("Couldn't get PROJECT from %s: %s.", module_name, reason)
        raise
