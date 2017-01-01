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

from .requirement import RequirementSubject
from ..measurement.measurable import MeasurableObject


class Document(RequirementSubject, MeasurableObject):
    """ Class representing a document. """

    @staticmethod
    def default_requirements():
        from ... import requirement  # Run time import to prevent circular dependency.
        return {requirement.TrackDocumentAge}

    def __str__(self):
        """ Return the id string of the document. """
        return self.id_string()

    def id_string(self):
        """ Return an id string for the document. """
        return self.name().lower().replace(' ', '_')
