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

# Shell script to create a quality report.
#
# This script assumes it runs in a Jenkins job.
# It expects a WORKSPACE environment variable that contains the location
# of the job's workspace folder.
# It expects a PROJECT environment variable that contains the name of the
# project to create the quality report for.

if [[ "$WORKSPACE" == "" ]]; then
    WORKSPACE="."
fi
PYENV_HOME=$WORKSPACE/.pyenv/

# Delete previously built virtualenv
if [ -d $PYENV_HOME ]; then
    rm -rf $PYENV_HOME
fi

# Create virtualenv and activate it 
virtualenv $PYENV_HOME
. $PYENV_HOME/bin/activate

# Install required packages
pip install --quiet -r quality-report/python/requirements.txt 

# Create the quality report
python quality-report/python/retrieve_kpis.py --project $PROJECT/project_definition.py --html tmp.html --json $PROJECT/history.json --dot dependency.dot --log INFO
dot -Tsvg dependency.dot > dependency.svg
mv tmp.html index.html
chmod a+r index.html
chmod a+r dependency.svg
chmod a+x quality-report
chmod a+x quality-report/img
chmod a+r quality-report/img/*.png
chmod a+x quality-report/js
chmod a+r quality-report/js/*.js
chmod a+x quality-report/css
chmod a+r quality-report/css/*.css
svn commit -m "Updated history from Jenkins." $PROJECT

# Deactivate virtualenv and remove it
deactivate
rm -rf $PYENV_HOME

