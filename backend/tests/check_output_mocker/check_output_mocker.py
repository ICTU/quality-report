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


POPENARGS_MAP = {
    ('git', 'pull', '--prune'): '',
    ('git', 'branch', '--list', '--remote', '--no-color', '--no-merged'):
        '''origin/HEAD -> origin/master
           origin/feature-1-something-to-implement
            origin/bug-22-something-to-fix
            origin/master''',

    ('git', 'cherry', 'origin/master', 'origin/feature-1-something-to-implement'):
        ''''+ ac3feb8fc36d6901dcb83190cad8e841c086a883
        + 23e56adcd4b127e20292854c21e5c271c5161d74
        + 08750ef039111aac7810d9712aa33c174aa051b2
        + 0dffe11c2e94a5b32b7a9437bfb594c54d4d862f''',
    ('git', 'log', '--format="%ct"', '-n', '1', 'origin/feature-1-something-to-implement'): '1532678343',

    ('git', 'cherry', 'origin/master', 'origin/bug-22-something-to-fix'):
        ''''+ ac3feb8fc36d6901dcb83190cad8e841c086a883
        + 23e56adcd4b127e20292854c21e5c271c5161d74''',
    ('git', 'log', '--format="%ct"', '-n', '1', 'origin/bug-22-something-to-fix'): '1532678445',

    ('git', 'log', '--format="%ct"', '-n', '1', '.'): '1532436642',
    ('git', 'branch', '--list', '--remote', '--no-color'):
        '''origin/HEAD -> origin/master
           origin/feature-1-something-to-implement
            origin/bug-22-something-to-fix
            origin/master'''
}


class CheckOutputMocker(object):
    """ Wrap for mock function check_output. """

    # pylint: disable=too-few-public-methods
    # pylint: disable=unused-argument
    @staticmethod
    def check_output(*popenargs, timeout=None, **kwargs):
        """ The function mocks behaviour of subprocess.check_output function"""

        if popenargs[0] in POPENARGS_MAP.keys():
            return POPENARGS_MAP[popenargs[0]]
        logging.info("Command '%s' is still not mocked for example report!", popenargs[0])
        return ''
