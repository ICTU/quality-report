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
import {create_sections, create_navigation_menu_items} from '../js/sections.js';

test('no sections', function(t) {
    t.deepEqual(
        create_sections([]),
        '<section id="section_all" style="display:none"><div id="table_all"></div></section>');
    t.end();
});

test('one section', function(t) {
    t.deepEqual(
        create_sections([{"id": "id", "title": "title", "subtitle": "subtitle"}]),
        '<section id="section_all" style="display:none"><div id="table_all"></div></section><section id="section_id">\
<div class="page-header="><h1>title <small>subtitle</small></h1></div><div id="table_id"></div></section>');
    t.end();
});

test('no navigation menu items without sections', function(t) {
    t.deepEqual(create_navigation_menu_items([]), '');
    t.end();
});

test('one navigation menu item for one section', function(t) {
    t.deepEqual(create_navigation_menu_items([{"id": "id", "title": "title", "subtitle": "subtitle"}]),
    '<li><a class="link_section_id" href="#section_id">title</a></li>');
    t.end();
});
