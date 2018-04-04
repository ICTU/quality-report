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
import {MetricsTable} from '../../js/components/metrics_table.js';

import { shallow, mount } from 'enzyme';
import Enzyme from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';
import jQuery from 'jquery';

Enzyme.configure({ adapter: new Adapter() });

import jsdom from 'jsdom'
const doc = jsdom.jsdom('<!doctype html><html><body></body></html>')
global.document = doc
global.window = doc.defaultView
global.$ = require('jquery')(global.window);

test('metrics table rendered without metrics', (t) => {
    const wrapper = shallow(<MetricsTable metrics={[]} onSort="onSrt" table_sort_column_name="tscn"
                                          table_sort_ascending="tsc" on_hide_metric='onHideMetricFn'/>)
    t.equal(wrapper.find('BootstrapTable').length, 1);
    t.equal(wrapper.find('BootstrapTable').prop('onSort'), "onSrt");
    t.equal(wrapper.find('BootstrapTable').prop('table_sort_column_name'), "tscn");
    t.equal(wrapper.find('BootstrapTable').prop('table_sort_ascending'), "tsc");
    t.equal(wrapper.find('BootstrapTable').prop('table_sort_ascending'), "tsc");
    t.equal(wrapper.find('BootstrapTable').prop('on_hide_metric'), "onHideMetricFn");
    t.deepEqual(wrapper.find('BootstrapTable')
        .prop('headers'), [["", ""], ["id_format", "Id"], ["sparkline", "Trend"],
                            ["status_format", "Status"], ["measurement", "Meting"], ["norm", "Norm"]]);
    t.equal(wrapper.find('BootstrapTable').children().exists(), false);
    t.end();
});

test('metrics table rendered with comment header if there is at least one comment', (t) => {
    const wrapper = shallow(<MetricsTable metrics={[{"comment": "Whatever",
                                                     "status_start_date": [2018, 1, 1, 12, 0, 0]}]} />)
    t.deepEqual(wrapper.find('BootstrapTable').prop('headers'),
            [["", ""], ["id_format", "Id"], ["sparkline", "Trend"],
             ["status_format", "Status"], ["measurement", "Meting"], ["norm", "Norm"], ["comment", "Comment"]]);
    t.end();
});

test('metrics table rendered without comment header if the comment is empty', (t) => {
    const wrapper = shallow(<MetricsTable metrics={[{"comment": "", "status_start_date": [2018, 1, 1, 12, 0, 0]}]} />)
    t.deepEqual(wrapper.find('BootstrapTable').prop('headers'),
            [["", ""], ["id_format", "Id"], ["sparkline", "Trend"],
             ["status_format", "Status"], ["measurement", "Meting"], ["norm", "Norm"]]);
    t.end();
});

test('metrics table rendered correctly', (t) => {
    const wrapper = mount(<MetricsTable metrics={[{"id_value": "PD-01", "id_format": "PD-1", "section": "PD",
        "status_start_date": [2018, 1, 1, 12, 0, 0], "sparkline": "<img src='img/PD-1.png' />;",
        "status": "missing_source",
        "measurement": "Measurement result", "norm": "Norm message", "comment": "Comment!", "extra_info":{}}]} />)

    t.equal(wrapper.find('BootstrapTable').children().length, 1);

    // columns' headers
    t.equal(wrapper.find('thead th[id="id_format"]').text(), "Id");
    t.equal(wrapper.find('thead th[id="sparkline"]').text(), "Trend");
    t.equal(wrapper.find('thead th[id="status_format"]').text(), "Status");
    t.equal(wrapper.find('thead th[id="measurement"]').text(), "Meting");
    t.equal(wrapper.find('thead th[id="norm"]').text(), "Norm");
    t.equal(wrapper.find('thead th[id="comment"]').text(), "Comment");

    // button and dropdown
    t.equal(wrapper.find('span.missing_source_metric').text().trim(), "PD-1");

    // metric data
    t.equal(wrapper.find('img[src="img/PD-1.svg"]').exists(), true);
    t.equal(wrapper.find('img[alt="🛠"]').exists(), true);
    t.equal(wrapper.find("td[dangerouslySetInnerHTML]")
        .findWhere(x => x.prop('dangerouslySetInnerHTML').__html === "Measurement result").exists(), true);
    t.equal(wrapper.find("td[dangerouslySetInnerHTML]")
        .findWhere(x => x.prop('dangerouslySetInnerHTML').__html === "Norm message").exists(), true);
    t.equal(wrapper.find("td[dangerouslySetInnerHTML]")
        .findWhere(x => x.prop('dangerouslySetInnerHTML').__html === "Comment!").exists(), true);
    t.end();
});
