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

from ..measurement.measurable import MeasurableObject


class Document(MeasurableObject):
    """ Class representing a document. """

    def __str__(self):
        """ Return the id string of the document. """
        return self.id_string()

    def id_string(self):
        """ Return an id string for the document. """
        return self.name().lower().replace(' ', '_')

    def product_version(self):
        """ Documents have no versions. """
        return None

    def product_branch_id(self, subversion):
        """ Documents have no branches. """
        return None
