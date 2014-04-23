'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from qualitylib.domain import QualityAttribute


AVAILABILITY = QualityAttribute('availability', 'Beschikbaarheid')
TEST_COVERAGE = QualityAttribute('test_coverage', 'Testdekking')
CODE_QUALITY = QualityAttribute('code_quality', 'Codekwaliteit')
TEST_QUALITY = QualityAttribute('test_quality', 'Testkwaliteit')
DOC_QUALITY = QualityAttribute('doc_quality', 'Documentatiekwaliteit')
SIZE = QualityAttribute('size', 'Omvang')
PERFORMANCE = QualityAttribute('performance', 'Performance')
PROJECT_MANAGEMENT = QualityAttribute('project_management', 
                                      'Project management')
ENVIRONMENT_QUALITY = QualityAttribute('environment_quality', 
                                       'Kwaliteit van omgevingen')
PROGRESS = QualityAttribute('progress', 'Voortgang')
SPIRIT = QualityAttribute('spirit', 'Stemming')
SECURITY = QualityAttribute('security', 'Beveiliging')
