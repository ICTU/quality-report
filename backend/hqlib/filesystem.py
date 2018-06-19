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
import stat

from typing import Union


PathType = Union[str, pathlib.Path]


class FileSystem(object):
    """ Class for methods that manipulate the file system. """
    @staticmethod
    def write_file(contents: str, filename: PathType, mode: str, encoding: str = None) -> None:
        """ Write the contents to the specified file. """
        path = pathlib.Path(filename)
        if path.exists():
            FileSystem.make_file_readable(path)
        if 'b' in mode:
            path.write_bytes(contents.encode() if isinstance(contents, str) else bytes(contents))
        else:
            path.write_text(contents, encoding=encoding)
        FileSystem.make_file_readable(path)

    @staticmethod
    def create_dir(dir_name: PathType) -> None:
        """ Create a directory and make it accessible. """
        dir_path = pathlib.Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
        dir_path.chmod(stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH | stat.S_IRUSR | stat.S_IWUSR)

    @staticmethod
    def make_file_readable(filename: PathType) -> None:
        """ Make the file readable and writeable for the user and readable for everyone else. """
        path = pathlib.Path(filename)
        path.chmod(stat.S_IWUSR | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)


# pylint: disable=invalid-name
write_file = FileSystem.write_file
create_dir = FileSystem.create_dir
