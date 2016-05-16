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

from ..domain import QualityAttribute


AVAILABILITY = QualityAttribute('availability', name='Beschikbaarheid')
TEST_COVERAGE = QualityAttribute('test_coverage', name='Testdekking')
CODE_QUALITY = QualityAttribute('code_quality', name='Codekwaliteit')
DEPENDENCY_QUALITY = QualityAttribute('dependency_quality', name='Kwaliteit van afhankelijkheden')
TEST_QUALITY = QualityAttribute('test_quality', name='Testkwaliteit')
DOC_QUALITY = QualityAttribute('doc_quality', name='Documentatiekwaliteit')
SIZE = QualityAttribute('size', name='Omvang')
PERFORMANCE = QualityAttribute('performance', name='Performance')
PROJECT_MANAGEMENT = QualityAttribute('project_management', name='Project management')
ENVIRONMENT_QUALITY = QualityAttribute('environment_quality', name='Kwaliteit van omgevingen')
PROGRESS = QualityAttribute('progress', name='Voortgang')
SPIRIT = QualityAttribute('spirit', name='Stemming')
SECURITY = QualityAttribute('security', name='Beveiliging')
