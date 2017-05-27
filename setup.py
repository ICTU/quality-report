#!/usr/bin/env python

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

from pip.download import PipSession
from pip.req import parse_requirements
from setuptools import setup, find_packages
from distutils import core, dir_util
import os

from hqlib import VERSION


class Bundle(core.Command):
    """ Bundle the webapp using npm (and webpack). """
    description = "bundle the frontend using npm and webpack"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.chdir('frontend')
        os.system('npm install; npm run build')
        dir_util.copy_tree('html', '../hqlib/app/html')
        dir_util.copy_tree('img', '../hqlib/app/img')
        os.chdir('..')


setup(name='quality_report',
      version=VERSION,
      description='Holistic Software Quality Reporting',
      long_description='''Application to generate quality reports for software development projects.
Holistic because HQ attempts to measure as many aspects of software development as
possible, seeing how software development can go off the rails in so many ways.''',
      author='ICTU',
      author_email='frank.niessink@ictu.nl',
      url='https://github.com/ICTU/quality-report',
      license='Apache License, Version 2.0',
      packages=find_packages(),
      scripts=['quality_report.py'],
      include_package_data=True,
      cmdclass={"bundle": Bundle},
      install_requires=[str(requirement.req) for requirement in parse_requirements('requirements.txt',
                                                                                   session=PipSession())],
      test_suite='tests',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Natural Language :: Dutch',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: JavaScript',
          'Topic :: Software Development :: Quality Assurance'],
      keywords=['quality', 'software development', 'metrics', 'measurement'])
