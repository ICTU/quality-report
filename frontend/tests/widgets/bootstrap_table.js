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
import Adapter from 'enzyme-adapter-react-16';

Enzyme.configure({ adapter: new Adapter() });

import jsdom from 'jsdom'
const doc = jsdom.jsdom('<!doctype html><html><head><script src=""></head><body></body></html>')
global.document = doc
global.window = doc.defaultView

test('bootstrap table empty', function(t) {
    const wrapper = shallow(<BootstrapTable/>);
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

test('bootstrap table caret ascending', function(t) {
    const wrapper = shallow(<BootstrapTable headers={[["", ""],["id", "ID"]]} table_sort_column_name='id' table_sort_ascending='?' />);
    t.equals(wrapper.find('BootstrapTableHeader').dive().find('Caret').prop('table_sort_ascending'), '?');
    t.equals(wrapper.find('BootstrapTableHeader').dive().find('Caret').dive().find('span.caret').exists(), true);
    t.end();
});

test('bootstrap table caret descending', function(t) {
    const wrapper = shallow(<BootstrapTable headers={[["", ""],["id", "ID"]]} table_sort_column_name='id' table_sort_ascending />);
    t.equals(wrapper.find('BootstrapTableHeader').dive().find('Caret').dive().find('span.dropup').exists(), true);
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
    t.equal(wrapper.find('BootstrapTableBody').dive().find("td[dangerouslySetInnerHTML]")
                                                        .prop('dangerouslySetInnerHTML').__html, "<p>cell 1</p>");
    t.end();
});

test('bootstrap table body rendered', (t) => {
    const wrapper = mount(<BootstrapTable headers={[["", ""],["id", "ID"]]}>{[{cells: ["cell 1"], id:"x"}]}</BootstrapTable>);
    t.equals(wrapper.find('tbody tr td.report_cell').text(), "cell 1");
    t.end();
});

test('bootstrap table renders headers of table panel with extra info', (t) => {
    const wrapper = shallow(<BootstrapTable>
        {[{cells: ["cell 1"], className: 'cls', id: 'IDx', comment:'', extra_info: {"headers": {"link": "Branch"}, "title":"Extra Info Title"}}]}
    </BootstrapTable>)
    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailPane').dive().find('TablePanel').exists(), true);
    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailPane').dive().find('TablePanel').dive().find('th').text(), "Branch");
    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailPane').dive().find('TablePanel').dive().find('h4').text(), "Extra Info Title");
    t.end();
});

test('bootstrap table renders rows of the table panel with extra info', (t) => {
    const wrapper = shallow(<BootstrapTable>
        {[{cells: ["cell 1"], className: 'cls', id: 'IDx', comment:'', extra_info: {"headers": {"str": "String", "num": "Number"}, 
                "data":[{"str": "First Row", "num": "1"}, {"str": "Second Row", "num": "2"}]}}]}
    </BootstrapTable>)
    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailPane').dive().find('TablePanel').exists(), true);
    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailPane').dive().find('TablePanel').dive().find('tbody tr').first().contains('First Row'), true);
    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailPane').dive().find('TablePanel').dive().find('tbody tr').first().contains('1'), true);
    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailPane').dive().find('TablePanel').dive().find('tbody tr').last().contains('Second Row'), true);
    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailPane').dive().find('TablePanel').dive().find('tbody tr').last().contains('2'), true);
    t.end();
});

test('bootstrap table renders rows of the table panel with links in extra info', (t) => {
    const wrapper = shallow(<BootstrapTable>
        {[{cells: ["cell 1"], className: 'cls', id: 'IDx', comment:'', extra_info: {"headers": {"col": "Link"}, 
                "data":[{"col": {"href":"http://xxx", "text": "Description"}}]}}]}
    </BootstrapTable>)
    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailPane').dive().find('TablePanel').exists(), true);
    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailPane').dive().find('TablePanel').dive().find('tbody tr a').text(), "Description");
    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailPane').dive().find('TablePanel').dive().find('tbody tr a[href="http://xxx"]').exists(), true);    
    t.end();
});

test('bootstrap table renders rows of the table panel with links in extra info, with link as the text', (t) => {
    const wrapper = shallow(<BootstrapTable>
        {[{cells: ["cell 1"], className: 'cls', id: 'IDx', comment:'', extra_info: {"headers": {"col": "Link"}, 
                "data":[{"col": {"href":"http://xxx", "text": ""}}]}}]}
    </BootstrapTable>)
    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailPane').dive().find('TablePanel').exists(), true);
    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailPane').dive().find('TablePanel').dive().find('tbody tr a').text(), "http://xxx");
    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailPane').dive().find('TablePanel').dive().find('tbody tr a[href="http://xxx"]').exists(), true);
    t.end();
});


test('bootstrap table renders toggle button', (t) => {
    const wrapper = shallow(
        <BootstrapTable headers={[["", ""],["id", "ID"]]}>
            {[{cells: ["cell 1"], className: 'cls', id: 'IDx', name: 'Metric Name', comment:'commentX'}]}
        </BootstrapTable>)
    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailToggleButton').length, 1);
    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailToggleButton').prop('data_target'), '#IDx_details');
    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailToggleButton').dive()
                .find('button.can_expand.btn.glyphicon.glyphicon-chevron-right[data-target="#IDx_details"]').length, 1);
    t.end();
});

test('bootstrap table renders disabled toggle button if there is no comment and no extra info', (t) => {
    const wrapper = shallow(
        <BootstrapTable headers={[["", ""],["id", "ID"]]}>{[{cells: ["cell 1"], className: 'cls', id: 'IDx', comment:'', extra_info: {}}]}
    </BootstrapTable>)
    t.equals(wrapper.find('BootstrapTableBody').dive().find('button.disabled.btn.glyphicon.glyphicon-chevron-right').length, 1);
    t.end();
});

test('bootstrap table does not render detail table if there is no comment and no extra info', (t) => {
    const wrapper = shallow(<BootstrapTable headers={[["", ""],["id", "ID"]]}>{[{cells: ["cell 1"], className: 'cls', id: 'IDx', comment:'', extra_info: {}}]}</BootstrapTable>)
    t.equals(wrapper.find('BootstrapTableBody').dive().find('tr.collapse').exists(), false);
    t.end();
});

test('bootstrap table does render detail table if there is extra info', (t) => {
    const wrapper = shallow(
        <BootstrapTable headers={[["", ""],["id", "ID"]]}>
            {[{cells: ["cell 1"], className: 'cls', id: 'IDx', comment:'', extra_info: {title: "Extra!", headers: {"x": "y"}, data:[{"x":"extra data"}]}}]}
        </BootstrapTable>)
    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailPane').prop('has_comment'), false);
    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailPane').prop('has_extra_info'), true);
    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailPane')
                                    .dive().find('tr.cls.collapse[id="IDx_details"] td.detail_pane').length, 1);
    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailPane').dive().find('TablePanel').length, 1);
    
    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailPane').dive().find('TablePanel').dive()
            .equals(<div className="panel panel-default">
                        <h4 className="panel-heading">Extra!</h4>
                        <div className="panel-body">
                            <table className="table-striped">
                            <thead>
                                <tr><th>y</th></tr>
                            </thead>
                            <tbody>
                                <tr><td>extra data</td></tr>
                            </tbody>
                            </table>
                        </div>
                    </div>), true);
    t.end();
});

test('bootstrap table does render detail table if there is a comment and no extra info', (t) => {
    const wrapper = shallow(
        <BootstrapTable headers={[["", ""],["id", "ID"]]}>
            {[{cells: ["cell 1"], className: 'cls', id: 'IDx', comment:'commentX', extra_info: {}}]}
        </BootstrapTable>)
    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailPane').prop('has_comment'), true);
    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailPane').prop('has_extra_info'), false);
    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailPane')
                                    .dive().find('tr.cls.collapse[id="IDx_details"] td.detail_pane').length, 1);
    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailPane').dive().find('CommentPanel').length, 1);

    t.equals(wrapper.find('BootstrapTableBody').dive().find('DetailPane').dive().find('CommentPanel').dive()
            .equals(<div className="panel panel-default">
                        <h4 className="panel-heading">Commentaar</h4>
                        <div className="panel-body">commentX</div>
                    </div>), true);
    
    t.end();
});

test('bootstrap table toggle button click', (t) => {
    const wrapper = mount(
        <BootstrapTable headers={[["", ""],["id", "ID"]]}>
            {[{cells: ["cell 1"], className: 'cls', id: 'IDx', comment:'commentX', extra_info: {}}]}
        </BootstrapTable>)
    var x = wrapper.find('button.can_expand.btn.glyphicon.glyphicon-chevron-right[data-target="#IDx_details"]');
    t.equals(x.length, 1);
    x.simulate('click');
    t.equals(wrapper.find('button.can_expand.btn.glyphicon.glyphicon-chevron-down[data-target="#IDx_details"]').length, 1);
    x.simulate('click');
    t.equals(wrapper.find('button.can_expand.btn.glyphicon.glyphicon-chevron-down[data-target="#IDx_details"]').exists(), false);
    t.equals(wrapper.find('button.can_expand.btn.glyphicon.glyphicon-chevron-right[data-target="#IDx_details"]').length, 1);
    t.end();
});

