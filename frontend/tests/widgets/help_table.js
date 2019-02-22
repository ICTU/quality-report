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
import {HelpTable, HelpTableHeader, HelpTableBody} from '../../js/widgets/help_table.js';

import { shallow, mount } from 'enzyme';
import Enzyme from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';

Enzyme.configure({ adapter: new Adapter() });

import jsdom from 'jsdom'
const doc = jsdom.jsdom('<!doctype html><html><head><script src=""></head><body></body></html>')
global.document = doc
global.window = doc.defaultView

test('bootstrap table empty', function(t) {
    const wrapper = shallow(<HelpTable/>);
    t.equals(wrapper.find('table.table').exists(), true);
    t.end();
});

test('bootstrap table header', (t) => {
    const wrapper = shallow(<HelpTable headers={[["x", "X"]]} />);
    t.equals(wrapper.find('HelpTableHeader').exists(), true);
    t.equals(wrapper.find('HelpTableHeader').dive().equals(<thead><tr><th id="x">X</th></tr></thead>), true);
    t.end();
});

test('bootstrap table body', (t) => {
    const wrapper = mount(<HelpTable headers={[["x", "X"]]}>{[{cells: ["cell 1"]}]}</HelpTable>);
    t.equals(wrapper.find('tbody tr td').text(), "cell 1");
    t.end();
});
