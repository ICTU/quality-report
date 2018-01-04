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


test('footer is correctly rendered', (t) => {
    const wrapper = mount(<MainContainer metrics_data={{"report_date": [2018, 1, 4, 16, 29, 52], "report_title": "Report Title", "hq_version": "2.28.0"}} />);
    t.equal(wrapper.find('footer').contains(<span>Report Title, 4-1-2018 16:29</span>), true)
    t.equal(wrapper.find('footer').contains(<span>Gegenereerd door HQ versie 2.28.0</span>), true)
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
    const wrapper = shallow(<MainContainer tab="metrics_tab" metrics_data={{"hq_version": ""}} />)
    t.equal(wrapper.find('Metrics').length, 1);
    t.end();
});

test('dashboard table and metric sections are rendered', (t) => {
    const wrapper = shallow(<MainContainer tab="metrics_tab" show_dashboard="has_some_value" metrics_data={{"hq_version": ""}} />)
    t.equal(wrapper.find('Metrics').dive().find('DashboardTable').length, 1);
    t.equal(wrapper.find('Metrics').dive().find('MetricsSections').length, 1);
    t.end();
});

test('dashboard table is not rendered when no value and metric sections are rendered', (t) => {
    const wrapper = shallow(<MainContainer tab="metrics_tab" metrics_data={{"hq_version": ""}} />)
    t.equal(wrapper.find('Metrics').dive().find('DashboardTable').exists(), false);
    t.equal(wrapper.find('Metrics').dive().find('MetricsSections').length, 1);
    t.end();
});

test('help is rendered with correct version number', (t) => {
    const wrapper = shallow(<MainContainer tab="help_tab" metrics_data={{"hq_version": "version_number"}} />)
    t.equal(wrapper.find('Help').length, 1);
    t.equal(wrapper.find('Help').prop('hq_version'), "version_number");
    t.end();
});
