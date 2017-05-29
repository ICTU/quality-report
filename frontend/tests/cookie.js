/* Copyright 2012-2017 Ministerie van Sociale Zaken en Werkgelegenheid
 *
 * Licensed under the Apache License, Version 2.0 (the "License")
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import test from 'tape';
import {read_cookie, write_cookie} from '../js/cookie.js';

test('non-existing cookies are undefined', function(t) {
    global.document = {};
    global.document.cookie = '';
    t.deepEqual(read_cookie('foo'), undefined);
    t.end();
});

test('cookies can be written and read', function(t) {
    global.document = {};
    global.document.cookie = '';
    write_cookie('name', 'value');
    t.equals(read_cookie('name'), 'value');
    t.end();
});

test('cookie expiration date can be set', function(t) {
    global.document = {};
    global.document.cookie = '';
    write_cookie('name', 'value', 4);
    t.equals(global.document.cookie.substring(46, 50), 'GMT;');
    t.end();
});

test('when reading cookies, initial spaces are skipped', function(t) {
    global.document = {};
    global.document.cookie = ' name=value;';
    t.equals(read_cookie('name'), 'value');
    t.end();
});
