/* Copyright 2012-2019 Ministerie van Sociale Zaken en Werkgelegenheid
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
import {MetricsSection} from '../../js/components/metrics_section.js';

import { shallow, mount } from 'enzyme';
import Enzyme from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';

Enzyme.configure({ adapter: new Adapter() });

import jsdom from 'jsdom'
const doc = jsdom.jsdom('<!doctype html><html><body></body></html>')
global.document = doc
global.window = doc.defaultView


test('section is rendered with correct attributes', (t) => {
    const wrapper = shallow(<MetricsSection  latest_change_date="some_date" section="SECTION_KEY" class_name="cls" />)
    t.equal(wrapper.find('section[className="cls"][id="section_SECTION_KEY"]').length, 1);
    t.end();
});

test('last build label is rendered', (t) => {
    const wrapper = shallow(<MetricsSection latest_change_date="some_date" />)
    t.equal(wrapper.find('section div.page-header h1 small LastBuiltLabel').length, 1);
    t.equal(wrapper.find('LastBuiltLabel').prop('latest_change_date'), "some_date");
    t.end();
});

test('metrics table is rendered', (t) => {
    const wrapper = shallow(<MetricsSection section="SECTION_KEY" metrics="some_metrics" latest_change_date="some_date" 
                        table_sort_column_name="tscn" table_sort_ascending="tsa" on_hide_metric="ohm" onSort="on_sort" />)    
    t.equal(wrapper.find('section div[className="metric_table"][id="table_SECTION_KEY"] MetricsTable').length, 1);
    t.equal(wrapper.find('MetricsTable').prop('metrics'), "some_metrics");
    t.equal(wrapper.find('MetricsTable').prop('table_sort_column_name'), "tscn");
    t.equal(wrapper.find('MetricsTable').prop('table_sort_ascending'), "tsa");
    t.equal(wrapper.find('MetricsTable').prop('on_hide_metric'), "ohm");
    t.equal(wrapper.find('MetricsTable').prop('onSort'), "on_sort");
    t.end();
});
