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
import {DomainObjectsTable, RequirementsTable, MetricClassesTable, MetricSourcesTable} from '../../js/components/meta_data_table.js';

import { shallow, mount } from 'enzyme';
import Enzyme from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';

Enzyme.configure({ adapter: new Adapter() });

import jsdom from 'jsdom'
const doc = jsdom.jsdom('<!doctype html><html><body></body></html>')
global.document = doc
global.window = doc.defaultView


test('domain objects table meta data rendered', (t) => {
    const wrapper = shallow(
        <DomainObjectsTable domain_objects={[{"included": true, "name": "Application", "default_requirements": [], "optional_requirements": []}]} />);
    t.equals(wrapper.find('MetaDataTable').length, 1);
    t.end();
});

test('domain objects table help table rendered', (t) => {
    const wrapper = shallow(
        <DomainObjectsTable domain_objects={[{"included": true, "name": "Application", "default_requirements": [], "optional_requirements": []}]} />);
    t.equals(wrapper.find('MetaDataTable').dive().find('HelpTable').length, 1);
    t.end();
});

test('requirements table meta data rendered', (t) => {
    const wrapper = shallow(
        <RequirementsTable requirements={[{"included": true, "name": "x", "metrics": ["A"]}]} />);
    t.equals(wrapper.find('MetaDataTable').length, 1);
    t.end();
});

test('requirements table help table rendered', (t) => {
    const wrapper = shallow(
        <RequirementsTable requirements={[{"included": true, "name": "x", "metrics": ["A"]}]} />);
        t.equals(wrapper.find('MetaDataTable').dive().find('HelpTable').length, 1);
    t.end();
});

test('metric classes table meta data rendered', (t) => {
    const wrapper = shallow(
        <MetricClassesTable metric_classes={["A"]} />);
    t.equals(wrapper.find('MetaDataTable').length, 1);
    t.end();
});

test('metric classes table help table rendered', (t) => {
    const wrapper = shallow(
        <MetricClassesTable metric_classes={["A"]} />);
        t.equals(wrapper.find('MetaDataTable').dive().find('HelpTable').length, 1);
    t.end();
});

test('metric sources table meta data rendered', (t) => {
    const wrapper = shallow(
        <MetricSourcesTable metric_sources={["A"]} />);
    t.equals(wrapper.find('MetaDataTable').length, 1);
    t.end();
});

test('metric sources table help table rendered', (t) => {
    const wrapper = shallow(
        <MetricSourcesTable metric_sources={["A"]} />);
        t.equals(wrapper.find('MetaDataTable').dive().find('HelpTable').length, 1);
    t.end();
});