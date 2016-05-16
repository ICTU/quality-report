"""
Copyright 2012-2016 Ministerie van Sociale Zaken en Werkgelegenheid

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

import os

from .. import domain


class Dependencies(domain.MetricSource):
    """ Store and retrieve dependencies of released components. """
    metric_source_name = 'Dependencies cache database'

    def __init__(self, filename, file_=file):
        self.__file = file_
        self.__filename = os.path.abspath(filename)
        self.__db = self.load()
        super(Dependencies, self).__init__()

    def __repr__(self):
        return repr(self.__db)

    def load(self):
        """ Load the contents of the database from disk. """
        with self.__file(self.__filename) as db_file:  # pragma: no branch
            try:
                return eval(db_file.read())
            except SyntaxError:
                return dict()

    def save(self):
        """ Write the contents of the database to disk. """
        with self.__file(self.__filename, 'wb') as db_file:
            db_file.write(unicode(self.__db))

    def set_dependencies(self, product_name, product_version, dependencies):
        """ Add dependencies of product to the database. """
        self.__db[self.__key(product_name, product_version)] = dependencies

    def get_dependencies(self, product_name, product_version):
        """ Return the dependencies of the product as stored in the database. """
        return self.__db[self.__key(product_name, product_version)]

    def has_dependencies(self, product_name, product_version):
        """ Return whether the dependencies for the product are stored in the database. """
        return self.__key(product_name, product_version) in self.__db

    @staticmethod
    def __key(product_name, product_version):
        """ Create a string representation of the product that can be used as key in the database. """
        return product_name + ':' + (product_version or 'trunk')
