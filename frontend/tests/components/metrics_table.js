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
import { MenuItem } from '../../js/widgets/menu';
import {MetricsTable} from '../../js/components/metrics_table.js';

import { shallow, mount } from 'enzyme';
import Enzyme from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';

Enzyme.configure({ adapter: new Adapter() });

import jsdom from 'jsdom'
const doc = jsdom.jsdom('<!doctype html><html><body></body></html>')
global.document = doc
global.window = doc.defaultView


test('metrics table rendered without metrics', (t) => {
    const wrapper = shallow(<MetricsTable metrics={[]} onSort="onSrt" table_sort_column_name="tscn" table_sort_ascending="tsc" />)
    t.equal(wrapper.find('BootstrapTable').length, 1);
    t.equal(wrapper.find('BootstrapTable').prop('onSort'), "onSrt");
    t.equal(wrapper.find('BootstrapTable').prop('table_sort_column_name'), "tscn");
    t.equal(wrapper.find('BootstrapTable').prop('table_sort_ascending'), "tsc");
    t.deepEqual(wrapper.find('BootstrapTable')
        .prop('headers'), [["", ""], ["id_format", "Id"], ["sparkline", "Trend"], 
                            ["status_format", "Status"], ["measurement", "Meting"], ["norm", "Norm"]]);
    t.equal(wrapper.find('BootstrapTable').children().exists(), false);
    t.end();
});

test('metrics table rendered correctly', (t) => {
    const wrapper = mount(<MetricsTable metrics={[{"id_value": "PD-01", "id_format": "PD-1", "section": "PD",
                "sparkline": "<img src='img/PD-1.png' />;", "status_format": "status_format_html_str", "status": "missing_source",
                "measurement": "Measurement result", "norm": "Norm message", "comment": "Comment!"}]} />)
    
    t.equal(wrapper.find('BootstrapTable').children().length, 1);

    // columns' headers
    t.equal(wrapper.find('thead th[id="id_format"]').text(), "Id");
    t.equal(wrapper.find('thead th[id="sparkline"]').text(), "Trend");
    t.equal(wrapper.find('thead th[id="status_format"]').text(), "Status");
    t.equal(wrapper.find('thead th[id="measurement"]').text(), "Meting");
    t.equal(wrapper.find('thead th[id="norm"]').text(), "Norm");
    
    // button and dropdown
    t.equal(wrapper.find('span.missing_source_metric').text().trim(), "PD-1");
    
    // metric data
    t.equal(wrapper.find('img[src="img/PD-1.svg"]').exists(), true);
    t.equal(wrapper.find("td[dangerouslySetInnerHTML]")
        .findWhere(x => x.prop('dangerouslySetInnerHTML').__html === "status_format_html_str").exists(), true);
    t.equal(wrapper.find("td[dangerouslySetInnerHTML]")
        .findWhere(x => x.prop('dangerouslySetInnerHTML').__html === "Measurement result").exists(), true);
    t.equal(wrapper.find("td[dangerouslySetInnerHTML]")
        .findWhere(x => x.prop('dangerouslySetInnerHTML').__html === "Norm message").exists(), true);
    t.equal(wrapper.find("div.panel-body").text(), "Comment!");
    t.end();
});
