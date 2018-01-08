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
import {MainContainer} from '../../js/components/main_container.js';

import { shallow, mount } from 'enzyme';
import Enzyme from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';

Enzyme.configure({ adapter: new Adapter() });

import jsdom from 'jsdom'
const doc = jsdom.jsdom('<!doctype html><html><body></body></html>')
global.document = doc
global.window = doc.defaultView


test('footer renders report title, date and HQ version', (t) => {
    const wrapper = mount(<MainContainer metrics_data={{"report_date": [2018, 1, 4, 16, 29, 52], "report_title": "Report Title", "hq_version": "2.28.0"}} />);
    t.equal(wrapper.find('footer').contains("Report Title"), true)
    t.equal(wrapper.find('footer').contains("4-1-2018 16:29"), true)
    t.equal(wrapper.find('footer').contains("2.28.0"), true)
    t.end();
});

test('main container rendered empty when unexpected tab name is given', (t) => {
    const wrapper = shallow(<MainContainer tab="something_else" metrics_data={{"hq_version": ""}} />)
    t.equal(wrapper.find('div.row div.col-md-12').children().exists(), false);
    t.end();
});

test('trend graphs are rendered', (t) => {
    const wrapper = shallow(<MainContainer tab="trend_tab" metrics_data={{"hq_version": ""}} />)
    t.equal(wrapper.find('TrendGraphs').length, 1);
    t.end();
});

test('metrics are rendered', (t) => {
    const wrapper = shallow(<MainContainer tab="metrics_tab" metrics_data={{"hq_version": "v"}} 
                                show_dashboard='shwdsh' show_one_table='shw1tbl' on_hide_metric='ohm' />)
    t.equal(wrapper.find('Metrics').length, 1);
    t.equal(wrapper.find('Metrics').prop('metrics_data').hq_version, "v");
    t.equal(wrapper.find('Metrics').prop('show_dashboard'), "shwdsh");
    t.equal(wrapper.find('Metrics').prop('show_one_table'), "shw1tbl");
    t.equal(wrapper.find('Metrics').prop('on_hide_metric'), "ohm");
    t.end();
});

test('metric sections are rendered', (t) => {
    const wrapper = shallow(<MainContainer tab="metrics_tab" metrics_data={{"hq_version": "v"}}  
                            metrics="mtrcs"  show_one_table='shw1tbl' on_hide_metric='ohm' />)
    t.equal(wrapper.find('Metrics').dive().find('MetricsSections').length, 1);
    t.deepEqual(wrapper.find('Metrics').dive().find('MetricsSections').prop('metrics_data'), {"hq_version": "v"});
    t.equal(wrapper.find('Metrics').dive().find('MetricsSections').prop('metrics'), "mtrcs");
    t.equal(wrapper.find('Metrics').dive().find('MetricsSections').prop('show_one_table'), "shw1tbl");
    t.equal(wrapper.find('Metrics').dive().find('MetricsSections').prop('on_hide_metric'), "ohm");
    t.end();
});

test('dashboard table is rendered', (t) => {
    const wrapper = shallow(<MainContainer tab="metrics_tab" show_dashboard="has_some_value" metrics_data={{"hq_version": "v"}} metrics="mtrcs" />)
    t.equal(wrapper.find('Metrics').dive().find('DashboardTable').length, 1);
    t.equal(wrapper.find('Metrics').prop('metrics_data').hq_version, "v");
    t.equal(wrapper.find('Metrics').prop('metrics'), "mtrcs");
    t.end();
});

test('dashboard table is not rendered when no value', (t) => {
    const wrapper = shallow(<MainContainer tab="metrics_tab" metrics_data={{"hq_version": ""}} />)
    t.equal(wrapper.find('Metrics').dive().find('DashboardTable').exists(), false);
    t.end();
});

test('help is rendered with correct version number', (t) => {
    const wrapper = shallow(<MainContainer tab="help_tab" metrics_data={{"hq_version": "version_number"}} />)
    t.equal(wrapper.find('Help').length, 1);
    t.equal(wrapper.find('Help').prop('hq_version'), "version_number");
    t.end();
});
