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
import {draw_area_chart} from '../js/area_chart.js';

var MockBrowser = require('mock-browser').mocks.MockBrowser;

test('draw area chart', function(t) {
    var doc = MockBrowser.createDocument();
    var canvas_div = doc.createElement('div'),
    	canvas = doc.createElement('canvas');
    canvas_div.id = 'element_id';
    canvas_div.appendChild(canvas);
    doc.body.appendChild(canvas_div);
    var colors = ['#FFF', '#FFF', '#FFF', '#FFF', '#FFF', '#FFF', '#FFF'];
    var chart = draw_area_chart(doc, "element_id", [[1], [1], [1], [1], [1], [1], [1]], colors,"title", true);
    t.equals(chart['config']['type'], 'line');
    t.end();
});
