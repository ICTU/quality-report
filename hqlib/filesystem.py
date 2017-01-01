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
from __future__ import absolute_import

import codecs
import os
import stat


class FileSystem(object):
    """ Class for methods that manipulate the file system. """
    @staticmethod
    def write_file(contents, filename, mode, encoding):
        """ Write the contents to the specified file. """
        if os.path.exists(filename):
            FileSystem.make_file_readable(filename)
        output_file = codecs.open(filename, mode, encoding)
        output_file.write(contents)
        output_file.close()
        FileSystem.make_file_readable(filename)

    @staticmethod
    def create_dir(dir_name):
        """ Create a directory and make it accessible. """
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        os.chmod(dir_name, stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH | stat.S_IRUSR | stat.S_IWUSR)

    @staticmethod
    def make_file_readable(filename):
        """ Make the file readable and writeable for the user and readable for everyone else. """
        os.chmod(filename, stat.S_IWUSR | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)


# pylint: disable=invalid-name
write_file = FileSystem.write_file
create_dir = FileSystem.create_dir
make_file_readable = FileSystem.make_file_readable
