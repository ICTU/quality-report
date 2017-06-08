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
import {draw_pie_chart} from '../js/pie_chart.js';

var MockBrowser = require('mock-browser').mocks.MockBrowser;

test('draw pie chart', function(t) {
    var doc = MockBrowser.createDocument();
    var canvas_div = doc.createElement('div'),
    	canvas = doc.createElement('canvas');
    canvas_div.id = 'section_summary_chart_id';
    canvas_div.appendChild(canvas);
    doc.body.appendChild(canvas_div);
    var pie_chart = draw_pie_chart(MockBrowser.createWindow(), doc, "id", "title", [1], ['#FFF'], ['Label'], 4, 4);
    t.equals(pie_chart['config']['type'], 'pie');
    t.end();
});

test('click pie chart', function(t) {
    var doc = MockBrowser.createDocument();
    var canvas_div = doc.createElement('div'),
    	section_div = doc.createElement('div'),
    	canvas = doc.createElement('canvas');
    canvas_div.id = 'section_summary_chart_id';
    canvas_div.appendChild(canvas);
    doc.body.appendChild(canvas_div);
    section_div.id = 'section_id';
    var clicked = false;
    section_div.scrollIntoView = function() {clicked = true};
    doc.body.appendChild(section_div);
    var pie_chart = draw_pie_chart(MockBrowser.createWindow(), doc, "id", "title", [1], ['#FFF'], ['Label'], 4, 4);
    pie_chart['options']['onClick']();
    t.equals(clicked, true);
    t.end();
});


test('do not draw pie chart without canvas', function(t) {
    var pie_chart = draw_pie_chart(MockBrowser.createWindow(), MockBrowser.createDocument(),
                                   "id", "title", [1], ['#FFF'], ['Label'], 4, 4);
    t.equals(pie_chart, undefined);
    t.end();
});
