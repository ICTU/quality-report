# Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Run the unit tests for the quality report software.
# This script assumes it runs in a Jenkins job.
# It expects a WORKSPACE environment variable that contains the location
# of the job's workspace folder.

if [[ "$WORKSPACE" == "" ]]; then
    WORKSPACE="."
fi 
PYENV_HOME=$WORKSPACE/.pyenv/

# Delete previously built virtualenv, if any
if [ -d $PYENV_HOME ]; then
    rm -rf $PYENV_HOME
fi

# Create virtualenv and activate it
virtualenv $PYENV_HOME
. $PYENV_HOME/bin/activate
cd python

# Install the required packages
pip install --quiet -r requirements.txt

# Run unit tests and create coverage report
python -m coverage run --branch run_unittests.py discover -s unittests -p "*_tests.py"
python -m coverage html --omit "*site-packages*"
python -m coverage xml --omit "*site-packages*"

# Deactivate and remove virtualenv
cd ..
deactivate
rm -rf $PYENV_HOME
