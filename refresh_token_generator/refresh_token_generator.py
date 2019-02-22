"""
Copyright 2012-2019 Ministerie van Sociale Zaken en Werkgelegenheid

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

import os
import bottle
from bottle import request

import requests_oauthlib

from hqlib.persistence import FilePersister


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

bottle.TEMPLATE_PATH = ['./refresh_token_generator']

CLIENT_ID = ''
CLIENT_SECRET =''
REDIRECT_URI = 'http://localhost:5005/login/authorized'
AUTHORITY_URL = 'https://login.microsoftonline.com/{org_id}'
AUTH_ENDPOINT = '/oauth2/authorize'
TOKEN_ENDPOINT = '/oauth2/token'
RESOURCE = 'https://graph.microsoft.com/'
ORG = ''

MSGRAPH = None

@bottle.route('/')
@bottle.view('index.html')
def index():
    """Render the home page."""
    return

@bottle.route('/login', method='POST')
def login():
    """Prompt user to authenticate."""

    # pylint: disable=global-statement

    global CLIENT_ID
    global CLIENT_SECRET
    global ORG
    global MSGRAPH

    CLIENT_ID = request.forms.get('client_id')
    ORG = request.forms.get('org_id')
    CLIENT_SECRET = request.forms.get('client_secret')

    MSGRAPH = requests_oauthlib.OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)

    auth_base = AUTHORITY_URL.format(org_id=ORG) + AUTH_ENDPOINT + '?resource=' + RESOURCE
    authorization_url, state = MSGRAPH.authorization_url(auth_base)
    MSGRAPH.auth_state = state
    return bottle.redirect(authorization_url)

@bottle.route('/login/authorized')
@bottle.view('authorized.html')
def authorized():
    """Handler for the application's Redirect Uri."""
    if bottle.request.query.state != MSGRAPH.auth_state:
        raise Exception('state returned to redirect URL does not match!')
    tokens = MSGRAPH.fetch_token(AUTHORITY_URL.format(org_id='common') + TOKEN_ENDPOINT,
                        client_secret=CLIENT_SECRET,
                        authorization_response=bottle.request.url, verify=False)
    file = FilePersister()
    file.write_json({'refresh_token': tokens['refresh_token']}, 'refresh_token.json')
    return {"token": file.read_json('refresh_token.json'), "token_file": os.getcwd() + '/refresh_token.json'}

if __name__ == '__main__':
    bottle.run(app=bottle.app(), server='wsgiref', host='localhost', port=5005)
