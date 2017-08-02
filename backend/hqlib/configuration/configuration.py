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

from hqlib import filesystem


NEW_PROJECT_DEFINITION_CONTENTS = '''""" This is a generated project definition for HQ. Please adapt to your 
needs. """

from hqlib import metric_source, domain


# Metric sources

SONAR = metric_source.Sonar('http://www.sonar.my_project.my_organization:9000/')


# Project

PROJECT = domain.Project(
    'My organization', name='My project',
    metric_sources={
        metric_source.Sonar: SONAR})


# Software the project develops

MY_APPLICATION = domain.Application(
    short_name='AP', name='My Application',
    metric_source_ids={
        SONAR: 'my_applications_sonar_key'})

PROJECT.add_product(MY_APPLICATION)


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

PROJECT.set_dashboard(DASHBOARD_COLUMNS, DASHBOARD_ROWS)

'''


class Configuration(object):
    """ Project configuration. """
    PROJECT_DEFINITION_FILENAME = 'project_definition.py'

    @classmethod
    def project(cls, project_folder_or_filename):
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

        # Import the project definition and get the project from it. Create a project definition if it doesn't exist.
        module_name = project_definition_filename[:-len('.py')]
        try:
            project_definition_module = __import__(module_name)
        except ModuleNotFoundError as reason:
            project_definition_filepath = os.path.join(project_folder, project_definition_filename)
            logging.warning("Couldn't open %s: %s. Creating a default project definition in %s and using that.",
                            module_name, reason, project_definition_filepath)
            filesystem.write_file(NEW_PROJECT_DEFINITION_CONTENTS, project_definition_filepath, 'w')
            project_definition_module = __import__(module_name)
        return project_definition_module.PROJECT
