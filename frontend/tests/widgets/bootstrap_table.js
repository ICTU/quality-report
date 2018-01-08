/* Copyright 2012-2018 Ministerie van Sociale Zaken en Werkgelegenheid
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
import {BootstrapTable, BootstrapTableHeader, BootstrapTableBody, Caret} from '../../js/widgets/bootstrap_table.js';

import { shallow, mount } from 'enzyme';
import Enzyme from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';

Enzyme.configure({ adapter: new Adapter() });

import jsdom from 'jsdom'
const doc = jsdom.jsdom('<!doctype html><html><head><script src=""></head><body></body></html>')
global.document = doc
global.window = doc.defaultView

test('bootstrap table empty', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<BootstrapTable/>);
    const result = renderer.getRenderOutput();
    t.equals(result.type, 'table');
    t.end();
});

test('bootstrap table class', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<BootstrapTable/>);
    const result = renderer.getRenderOutput();
    t.equals(result.props.className, 'table');
    t.end();
});

test('bootstrap table header', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<BootstrapTable headers={[["id", "title"]]} />);
    const result = renderer.getRenderOutput();
    t.deepEquals(result.props.children[0], <BootstrapTableHeader headers={[["id", "title"]]} />);
    t.end();
});

test('bootstrap table body', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<BootstrapTable headers={[["id", "title"]]}>{[]}</BootstrapTable>);
    const result = renderer.getRenderOutput();
    t.deepEquals(result.props.children[1], <BootstrapTableBody>{[]}</BootstrapTableBody>);
    t.end();
});

test('bootstrap table header when first header empty', (t) => {
    const wrapper = shallow(<BootstrapTableHeader headers={[["", ""],["id", "ID"]]} />);
    t.equals(wrapper.find('tr th').first().children().exists(), false);
    t.equals(wrapper.find('tr th').first().find('th[style]').exists(), false);
    t.equals(wrapper.find('tr th').first().find('th[id]').exists(), false);
    t.end();
});

test('bootstrap table header when first header not empty', (t) => {
    const wrapper = shallow(<BootstrapTableHeader headers={[["x", "X"]]} />);
    t.equals(wrapper.find('tr th[id="x"]').text(), "X");
    t.end();
});

test('bootstrap table header second header width', (t) => {
    const wrapper = shallow(<BootstrapTableHeader headers={[["", ""],["id", "ID"]]} table_sort_ascending='x' table_sort_column_name='id' />);
    t.equals(wrapper.find('tr th[id="id"]').exists(), true);
    t.equals(wrapper.find('tr th[id="id"]').children().first().text(), "ID");
    t.equals(wrapper.find('tr th[id="id"]').children().at(1).find('Caret').length, 1);
    t.equals(wrapper.find('tr th[id="id"]').prop('width'), "90px");
    t.equals(wrapper.find('Caret').prop('show'), true);
    t.equals(wrapper.find('Caret').prop('table_sort_ascending'), "x");
    t.end();
});

test('bootstrap table header third header no width', (t) => {
    const wrapper = shallow(<BootstrapTableHeader headers={[["", ""],["id", "ID"],["xx", "XXX"]]} />);
    t.equals(wrapper.find('tr th[id="xx"]').exists(), true);
    t.equals(wrapper.find('tr th[id="xx"]').children().first().text(), "XXX");
    t.equals(wrapper.find('tr th[id="xx"]').children().at(1).find('Caret').length, 1);
    t.equals(wrapper.find('tr th[id="xx"]').find('Caret').prop('show'), false);
    t.end();
});

test('bootstrap table body tbody', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<BootstrapTableBody>{[{cells: ["cell 1"], className: ''}]}</BootstrapTableBody>);
    const result = renderer.getRenderOutput();
    t.equals(result.type, 'tbody');
    t.end();
});

test('bootstrap table body html', (t) => {
    const wrapper = shallow(<BootstrapTableBody>{[{cells: [{__html: "<p>cell 1</p>"}], className: ''}]}</BootstrapTableBody>)
    t.equal(wrapper.find("td[dangerouslySetInnerHTML]").prop('dangerouslySetInnerHTML').__html, "<p>cell 1</p>");
    t.end();
});

test('bootstrap table header with caret', function(t) {
    const wrapper = shallow(
        <BootstrapTableHeader headers={[["", ""],["id", "ID"],["xx", "XXX"]]} 
            table_sort_ascending='?' table_sort_column_name='xx'>
                {[{cells: [{__html: "<p>cell 1</p>"}], className: ''}]}
        </BootstrapTableHeader>)
    t.equals(wrapper.find('tr th[id="xx"]').find('Caret').length, 1);
    t.equals(wrapper.find('tr th[id="xx"]').find('Caret').prop('show'), true);
    t.equals(wrapper.find('tr th[id="xx"]').find('Caret').prop('table_sort_ascending'), '?');
    t.end();
});

test('bootstrap table caret is hidden by default', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<Caret />);
    const result = renderer.getRenderOutput();
    t.equals(result, null);
    t.end();
});

test('bootstrap table caret ascending', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<Caret show />);
    const result = renderer.getRenderOutput();
    t.equals(result.type, 'span');
    t.equals(result.props.className, 'caret');
    t.end();
});

test('bootstrap table caret descending', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<Caret show table_sort_ascending />);
    const result = renderer.getRenderOutput();
    t.equals(result.props.className, 'dropup');
    t.end();
});

test('bootstrap table renders detail table', (t) => {
    const wrapper = mount(<BootstrapTableBody>{[{cells: ["cell 1"], className: 'cls', id: 'IDx', name: 'Metric Name', comment:'commentX'}]}</BootstrapTableBody>)
    t.equals(wrapper.find('tr.cls.collapse[id="IDx_details"]').length, 1);
    t.equals(wrapper.find('tr.cls.collapse[id="IDx_details"] td.detail_pane').length, 1);
    t.equals(wrapper.find('button.can_expand.btn.glyphicon.glyphicon-chevron-right[data-target="#IDx_details"]').length, 1);
    t.end();
});

test('bootstrap table does not render detail table if th comment is empty', (t) => {
    const wrapper = shallow(<BootstrapTableBody>{[{cells: ["cell 1"], className: 'cls', id: 'IDx', comment:''}]}</BootstrapTableBody>)
    t.equals(wrapper.find('tr.collapse').exists(), false);
    t.equals(wrapper.find('button.disabled.btn.glyphicon.glyphicon-chevron-right').length, 1);
    t.end();
});

test('bootstrap table does not render show detail button if th comment is undefined', (t) => {
    const wrapper = shallow(<BootstrapTableBody>{[{cells: ["cell 1"], className: 'cls', id: 'IDx'}]}</BootstrapTableBody>)
    t.equals(wrapper.find('tr td').text(), "cell 1");
    t.equals(wrapper.find('button.btn.glyphicon').exists(), false);
    t.equals(wrapper.find('DetailToggleButton').exists(), false);
    t.end();
});

test('bootstrap table renders detail table CLICK', (t) => {
    const wrapper = mount(<BootstrapTableBody>{[{cells: ["cell 1"], className: 'cls', id: 'IDx', comment:'commentX'}]}</BootstrapTableBody>)
    var x = wrapper.find('button.can_expand.btn.glyphicon.glyphicon-chevron-right[data-target="#IDx_details"]');
    t.equals(x.length, 1);
    x.simulate('click');
    t.equals(wrapper.find('button.can_expand.btn.glyphicon.glyphicon-chevron-down[data-target="#IDx_details"]').length, 1);
    x.simulate('click');
    t.equals(wrapper.find('button.can_expand.btn.glyphicon.glyphicon-chevron-down[data-target="#IDx_details"]').exists(), false);
    t.equals(wrapper.find('button.can_expand.btn.glyphicon.glyphicon-chevron-right[data-target="#IDx_details"]').length, 1);
    t.end();
});