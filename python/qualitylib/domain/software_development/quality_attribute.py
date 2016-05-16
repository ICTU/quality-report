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

from ..base import DomainObject


class QualityAttribute(DomainObject):
    """ Class representing a quality attribute of a product or process. """
    def __init__(self, id_string, *args, **kwargs):
        self.__id_string = id_string
        super(QualityAttribute, self).__init__(*args, **kwargs)

    def id_string(self):
        """ Return the id of the quality attribute. """
        return self.__id_string

    def __nonzero__(self):
        """ Return whether this is a valid quality attribute. """
        return bool(self.__id_string)

    def __lt__(self, other):
        return self.id_string() < other.id_string()

    def __eq__(self, other):
        return self.id_string() == other.id_string()
