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
import React from 'react';
import ShallowRenderer from 'react-test-renderer/shallow';
import {DashboardTable, DashboardTableRow} from '../../js/components/dashboard_table.js';
import {STATUS_COLORS} from '../../js/colors.js';


test('status counts without metrics', function(t) {
    var row = new DashboardTableRow();
    t.deepEqual(
        row.status_counts([], "section_id", ["red", "yellow"]),
        [0, 0]
    );
    t.end();
});

test('status counts with one metric', function(t) {
    var row = new DashboardTableRow();
    t.deepEqual(
        row.status_counts([{section: "section_id", status: "red"}], "section_id", ["red", "yellow"]),
        [1, 0]
    );
    t.end();
});

test('status counts with multiple metrics, in different sections', function(t) {
    var row = new DashboardTableRow();
    t.deepEqual(
        row.status_counts([{section: "section_id", status: "red"}, {section: "other section", status: "yellow"}],
                           "section_id", ["red", "yellow"]),
        [1, 0]
    );
    t.end();
});

test('empty dashboard table', function(t) {
    const renderer = new ShallowRenderer();
    const metrics_data = {dashboard: {headers: [], rows: []}};
    renderer.render(<DashboardTable metrics_data={metrics_data}></DashboardTable>);
    const result = renderer.getRenderOutput();
    t.equals(result.type, 'div');
    t.equals(result.props.children.type, 'table');
    t.equals(result.props.children.props.className, 'table table-condensed table-bordered dashboard');
    t.end();
});

test('dashboard table row pie data', function(t) {
    const metrics_data = {dashboard: {headers: [], rows: []}};
    var row = new DashboardTableRow();
    t.deepEqual(
        row.pie_data([], 'section_id'),
        {
            datasets: [{
                backgroundColor: STATUS_COLORS,
                borderWidth: 1,
                data: [0, 0, 0, 0, 0, 0, 0]
            }],
            labels: ['Perfect', 'Goed', 'Bijna goed', 'Actie vereist', 'Technische schuld', 'Bron niet beschikbaar',
                     'Bron niet geconfigureerd']
        });
    t.end();
});
