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
import {BootstrapTable} from '../../js/widgets/bootstrap_table.js';

import { shallow, mount } from 'enzyme';
import Enzyme from 'enzyme';
import sinon from 'sinon';
import Adapter from 'enzyme-adapter-react-16';

Enzyme.configure({ adapter: new Adapter() });

import jsdom from 'jsdom'
const doc = jsdom.jsdom('<!doctype html><html><head><script src=""></head><body></body></html>')
global.document = doc
global.window = doc.defaultView

test('bootstrap table empty', function(t) {
    const wrapper = shallow(<BootstrapTable headers={[]}/>);
    t.equals(wrapper.find('table.table').exists(), true);
    t.end();
});

test('bootstrap table header', (t) => {
    const wrapper = shallow(<BootstrapTable headers={[["x", "X"]]} />);
    t.equals(wrapper.find('BootstrapTableHeader').exists(), true);
    t.deepEquals(wrapper.find('BootstrapTableHeader').prop('headers'), [["x", "X"]]);
    t.end();
});

test('bootstrap table header first header empty', (t) => {
    const wrapper = shallow(<BootstrapTable headers={[["x", "X"],["y", "Y"]]} />);
    t.equals(wrapper.find('BootstrapTableHeader').dive().find('th').first().equals(<th />), true);
    t.end();
});

test('bootstrap table header second header width', (t) => {
    const wrapper = shallow(<BootstrapTable headers={[["", ""],["id", "ID"]]} />);
    t.equals(wrapper.find('BootstrapTableHeader').dive().find('thead tr th[id="id"]').exists(), true);
    t.equals(wrapper.find('BootstrapTableHeader').dive().find('thead tr th[id="id"]').children().first().text(), "ID");
    t.equals(wrapper.find('BootstrapTableHeader').dive().find('thead tr th[id="id"]').children().at(1).find('Caret').length, 1);
    t.equals(wrapper.find('BootstrapTableHeader').dive().find('thead tr th[id="id"]').prop('width'), "90px");
    t.end();
});

test('bootstrap table header third header no width', (t) => {
    const wrapper = shallow(<BootstrapTable headers={[["", ""],["id", "ID"],["xx", "XXX"]]} />);
    t.equals(wrapper.find('BootstrapTableHeader').dive().find('thead tr th[id="xx"]').exists(), true);
    t.equals(wrapper.find('BootstrapTableHeader').dive().find('thead tr th[id="xx"]').children().first().text(), "XXX");
    t.end();
});

test('bootstrap table caret is hidden by default', function(t) {
    const wrapper = shallow(<BootstrapTable headers={[["", ""],["id", "ID"]]} />);
    t.equals(wrapper.find('BootstrapTableHeader').dive().find('Caret').prop('show'), false);
    t.end();
});

test('bootstrap table caret is hidden when sort column name does not match', function(t) {
    const wrapper = shallow(<BootstrapTable headers={[["", ""],["id", "ID"]]} table_sort_column_name='x' />);
    t.equals(wrapper.find('BootstrapTableHeader').dive().find('Caret').prop('show'), false);
    t.end();
});

test('bootstrap table caret is shown when sort column name does match', function(t) {
    const wrapper = shallow(<BootstrapTable headers={[["", ""],["id", "ID"]]} table_sort_column_name='id' />);
    t.equals(wrapper.find('BootstrapTableHeader').dive().find('Caret').prop('show'), true);
    t.end();
});

test('bootstrap table caret ascending', function(t) {
    const wrapper = shallow(<BootstrapTable headers={[["", ""],["id", "ID"]]} table_sort_column_name='id' table_sort_ascending={true} />);
    t.equals(wrapper.find('BootstrapTableHeader').dive().find('Caret').dive().find("span").text(), " ▴");
    t.end();
});

test('bootstrap table caret descending', function(t) {
    const wrapper = shallow(<BootstrapTable headers={[["", ""],["id", "ID"]]} table_sort_column_name='id' table_sort_ascending={false} />);
    t.equals(wrapper.find('BootstrapTableHeader').dive().find('Caret').dive().find("span").text(), " ▾");
    t.end();
});

test('bootstrap table body header count', (t) => {
    const wrapper = shallow(<BootstrapTable headers={[["x", "X"]]} />);
    t.equals(wrapper.find('BootstrapTableBody').prop('col_span'), 1);
    t.end();
});

test('bootstrap table body empty header count', (t) => {
    const wrapper = shallow(<BootstrapTable />);
    t.equals(wrapper.find('BootstrapTableBody').prop('col_span'), 0);
    t.end();
});

test('bootstrap table body', (t) => {
    const wrapper = shallow(<BootstrapTable headers={[["x", "X"]]}><tr id="x1" /></BootstrapTable>);
    t.equals(wrapper.find('BootstrapTableBody').exists(), true);
    t.equals(wrapper.find('BootstrapTableBody').children().find('tr[id="x1"]').exists(), true);
    t.end();
});

test('bootstrap table body html filled', (t) => {
    const wrapper = shallow(
        <BootstrapTable headers={[["", ""],["id", "ID"]]}>
            {[{cells: [{__html: "<p>cell 1</p>"}], className: ''}]}
        </BootstrapTable>)
    t.equals(wrapper.find('BootstrapTableBody').exists(), true);
    t.equal(wrapper.find('BootstrapTableBody').dive().find("tbody").exists(), true)
     t.equal(wrapper.find('BootstrapTableBody').dive().find('BootstrapTableRow').dive()
                    .find("td[dangerouslySetInnerHTML]").prop('dangerouslySetInnerHTML').__html, "<p>cell 1</p>");
    t.end();
});

test('bootstrap table body rendered', (t) => {
    const wrapper = mount(<BootstrapTable headers={[["", ""],["id", "ID"]]}>{[{cells: ["cell 1"], id:"x"}]}</BootstrapTable>);
    t.equals(wrapper.find('tbody tr td.report_cell').text(), "cell 1");
    t.end();
});

test('bootstrap table renders bootstrap row', (t) => {
    var funct = (e)=>{return e;}
    const wrapper = shallow(<BootstrapTable headers={[["x", "X"],["id", "ID"]]} report_dates='just report_dates' on_hide_metric={funct} >
        {[{cells: ["cell 1"], extra_info: {"x":"x"}}]}
    </BootstrapTable>)
    t.equals(wrapper.find('BootstrapTableBody').dive().find('BootstrapTableRow').prop('col_span'), 2);
    t.equals(wrapper.find('BootstrapTableBody').dive().find('BootstrapTableRow').prop('report_dates'), 'just report_dates');
    t.equals(wrapper.find('BootstrapTableBody').dive().find('BootstrapTableRow').prop('on_hide_metric'), funct);
    t.deepEquals(wrapper.find('BootstrapTableBody').dive().find('BootstrapTableRow').prop('row'), {cells: ["cell 1"], extra_info: {"x":"x"}});
    t.end();
});

test('bootstrap table renders detail pane with col span information', (t) => {
    var fn = () => { return 0; }
    const wrapper = shallow(<BootstrapTable headers={[["x", "X"],["id", "ID"]]} report_dates='some report dates' on_hide_metric={fn}>
        {[{cells: ["cell 1"], extra_info: {"x":"x"}}]}
    </BootstrapTable>)
    t.equals(wrapper.find('BootstrapTableBody').dive().find('BootstrapTableRow').dive().find('DetailPane').prop('col_span'), 2);
    t.equals(wrapper.find('BootstrapTableBody').dive().find('BootstrapTableRow').dive().find('DetailPane').prop('report_dates'), 'some report dates');
    t.equals(wrapper.find('BootstrapTableBody').dive().find('BootstrapTableRow').dive().find('DetailPane').prop('has_extra_info'), true);
    t.equals(wrapper.find('BootstrapTableBody').dive().find('BootstrapTableRow').dive().find('DetailPane').prop('is_expanded'), false);
    t.equals(wrapper.find('BootstrapTableBody').dive().find('BootstrapTableRow').dive().find('DetailPane').prop('on_hide_metric'), fn);
    t.deepEquals(wrapper.find('BootstrapTableBody').dive().find('BootstrapTableRow').dive().find('DetailPane').prop('metric_detail'), {cells: ["cell 1"], extra_info: {"x":"x"}});
    t.end();
});

test('bootstrap table renders detail pane with col span information', (t) => {
    const wrapper = mount(<BootstrapTable headers={[["x", "X"],["id", "ID"]]}>
        {[{cells: ["cell 1"], id: 'IDx', extra_info: {"headers": {"col1": "X", "col2": "_x"}}}]}
    </BootstrapTable>)
    t.equals(wrapper.find('td.detail_pane').prop('colSpan'), 2);
    t.end();
});

test('bootstrap table renders toggle button', (t) => {
    const wrapper = shallow(
        <BootstrapTable headers={[["", ""],["id", "ID"]]}>
            {[{cells: ["cell 1"], className: 'cls', id: 'IDx', name: 'Metric Name', extra_info: {title: "Extra!"}}]}
        </BootstrapTable>)
    t.equals(wrapper.find('BootstrapTableBody').dive().find('BootstrapTableRow').dive().find('button[type="button"]').length, 1);
    t.equals(wrapper.find('BootstrapTableBody').dive().find('BootstrapTableRow').dive().find('button[data-toggle="collapse"]').length, 1);
    t.equals(wrapper.find('BootstrapTableBody').dive().find('BootstrapTableRow').dive()
                .find('button.can_expand[data-target="#IDx_details"]').length, 1);
    t.end();
});

test('bootstrap table does not render detail table if there is no extra info', (t) => {
    const wrapper = shallow(<BootstrapTable headers={[["", ""],["id", "ID"]]}>{[{cells: ["cell 1"], className: 'cls', id: 'IDx', comment:'xxx', extra_info: {}}]}</BootstrapTable>)
    t.equals(wrapper.find('BootstrapTableBody').dive().find('tr.collapse').exists(), false);
    t.end();
});

test('bootstrap table toggle button click', (t) => {
    const wrapper = shallow(
        <BootstrapTable headers={[["", ""],["id", "ID"]]} report_dates="2018-04-06 14:58:14,2018-04-10 13:19:01"
        table_sort_column_name="id"
        table_sort_ascending="">
            {[{cells: ["cell 1"], className: 'cls', name: 'Name', unit: 'day', id: 'IDx', extra_info: {title: "Extra!", headers: {"x": "y"}}}]}
        </BootstrapTable>)

    var tableRowContainer = wrapper.find('BootstrapTableBody').dive().find('BootstrapTableRow').dive();
    tableRowContainer.find('DetailPane').dive();
    
    t.equals(tableRowContainer.find('button.can_expand.btn[data-target="#IDx_details"]').exists(), true);
    t.equals(tableRowContainer.find('button.can_expand.btn[data-target="#IDx_details"]').text(), "➕")

    tableRowContainer.find('button.can_expand.btn[data-target="#IDx_details"]').simulate('click');

    t.equals(tableRowContainer.find('button.can_expand.btn[data-target="#IDx_details"]').text(), "➖")

    tableRowContainer.find('button.can_expand.btn[data-target="#IDx_details"]').simulate('click');

    t.equals(tableRowContainer.find('button.can_expand.btn[data-target="#IDx_details"]').text(), "➕")
    
    t.end();
});
