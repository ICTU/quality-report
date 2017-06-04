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
import {create_dashboard_table} from '../js/dashboard_table.js';

test('dashboard table without rows', function(t) {
    t.deepEqual(
        create_dashboard_table(
            {"headers": [{"header": "header 1", "colspan": 1}, {"header": "header 2", "colspan": 2}],
             "rows": []}),
        '<div id="section_dashboard"><table class="table table-condensed table-bordered"><thead>\
<tr style="color: white; font-weight: bold; background-color: #2F95CF">\
<th colspan=1 style="text-align: center;">header 1</th><th colspan=2 style="text-align: center;">header 2</th></th>\
</thead><tbody></tbody></table>');
    t.end();
});

test('dashboard table with one column and one row', function(t) {
    t.deepEqual(
        create_dashboard_table(
            {"headers": [{"header": "header 1", "colspan": 1}],
             "rows": [[{"section_id": "id", "section_title": "title", "colspan": 1, "rowspan": 1, "bgcolor": "red"}]]}),
        '<div id="section_dashboard"><table class="table table-condensed table-bordered"><thead>\
<tr style="color: white; font-weight: bold; background-color: #2F95CF">\
<th colspan=1 style="text-align: center;">header 1</th></th></thead><tbody><tr>\
<td colspan=1 rowspan=1 align="center" bgcolor="red">\
<div class="piechart_div"><canvas class="piechart_canvas" width=200 height=80 id="section_summary_chart_id">\
</canvas></div></td></tr></tbody></table>');
    t.end();
});

