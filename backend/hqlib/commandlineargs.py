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


from argparse import ArgumentParser, Namespace

import hqlib


def parse() -> Namespace:
    """ Parse the command line arguments. """
    parser = ArgumentParser(description='Generate a quality report.')
    parser.add_argument('--project', help='folder with project definition file or filename of the project definition '
                                          'file (the history file is assumed to be in the same folder as the project '
                                          'definition file)', required=True)
    parser.add_argument('--report', help='folder to write the HTML report in', required=True)
    parser.add_argument('--failure-exit-code', help='return exit code 2 when the report needs direct action, i.e. any '
                                                    'metric is red or missing',
                        action='store_true')
    parser.add_argument('--log', default="WARNING", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="log level (default: WARNING)")
    parser.add_argument('--frontend', default="yes", choices=['yes', 'no'],
                        help="should backend process also build the frontend? (default: yes)")
    parser.add_argument('--version', action='version', version=hqlib.VERSION)
    return parser.parse_args()
