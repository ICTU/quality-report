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

import os
import sys
import logging

from hqlib import metric_source, domain


""" This is a default project definition for HQ. """

# Metric sources

SONAR = metric_source.Sonar('http://www.sonar.my_project.my_organization:9000/')


# Project

DEFAULT_PROJECT = domain.Project(
    'Default organization', name='Default project',
    metric_sources={
        metric_source.Sonar: SONAR})


# Software the project develops

MY_APPLICATION = domain.Application(
    short_name='AP', name='My Application',
    metric_source_ids={
        SONAR: 'my_applications_sonar_key'})

DEFAULT_PROJECT.add_product(MY_APPLICATION)


# Dashboard

# Columns in the dashboard is specified as a list of tuples. Each tuple
# contains a column header and the column span.
DASHBOARD_COLUMNS = [('Application', 1), ('Meta', 1)]

# Rows in the dashboard is a list of row tuples. Each row tuple consists of
# tuples that describe a cell in the dashboard. Each cell is a tuple containing
# the product or team and the color. Optionally the cell tuple can contain a
# third value which is a tuple containing the column and row span for the cell.
C1, C2, C3 = 'lightsteelblue', 'lightgrey', 'lavender'
DASHBOARD_ROWS = [
    [(MY_APPLICATION, C1), ('MM', C3)]
]

DEFAULT_PROJECT.set_dashboard(DASHBOARD_COLUMNS, DASHBOARD_ROWS)

""" End of the default project definition for HQ. """


class Configuration(object):
    """ Project configuration. """
    PROJECT_DEFINITION_FILENAME = 'project_definition.py'

    @classmethod
    def project(cls, project_folder_or_filename, __import=__import__):
        """ Import the project from the project definition file in the project folder. """
        if project_folder_or_filename.endswith('.py'):
            project_folder, project_definition_filename = project_folder_or_filename.rsplit('/', 1)
        else:
            project_folder, project_definition_filename = project_folder_or_filename, cls.PROJECT_DEFINITION_FILENAME

        # Add the parent folder of the project folder to the python path so the
        # project definition can import shared resources from other folders.
        sys.path.insert(0, os.path.abspath(os.path.join(project_folder, '..')))

        # Add the project folder itself to the python path so that we can import the project definition itself.
        sys.path.insert(0, project_folder)

        # Import the project definition and get the project from it.
        # Use the default project definition if it doesn't exist.
        module_name = project_definition_filename[:-len('.py')]
        try:
            return __import(module_name).PROJECT
        except ModuleNotFoundError as reason:
            logging.error("Couldn't open %s: %s. Using default project definition.", module_name, reason)
        except AttributeError as reason:
            logging.error("Couldn't get PROJECT from %s: %s. Using default project definition.", module_name, reason)
        return DEFAULT_PROJECT
