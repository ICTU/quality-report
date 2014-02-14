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


AVAILABILITY = QualityAttribute('availability', 'beschikbaarheid')
TEST_COVERAGE = QualityAttribute('test_coverage', 'testdekking')
CODE_QUALITY = QualityAttribute('code_quality', 'codekwaliteit')
TEST_QUALITY = QualityAttribute('test_quality', 'testkwaliteit')
DOC_QUALITY = QualityAttribute('doc_quality', 'documentatiekwaliteit')
SIZE = QualityAttribute('size', 'omvang')
PERFORMANCE = QualityAttribute('performance', 'performance')
PROJECT_MANAGEMENT = QualityAttribute('project_management', 
                                      'project management')
ENVIRONMENT_QUALITY = QualityAttribute('environment_quality', 
                                       'kwaliteit van omgevingen')
PROGRESS = QualityAttribute('progress', 'voortgang')
SPIRIT = QualityAttribute('spirit', 'stemming')
SECURITY = QualityAttribute('security', 'beveiliging')
