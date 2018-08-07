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
import {DetailPane} from '../../js/widgets/detail_pane';

import { shallow, mount } from 'enzyme';
import Enzyme from 'enzyme';
import sinon from 'sinon';
import Adapter from 'enzyme-adapter-react-16';

Enzyme.configure({ adapter: new Adapter() });

import jsdom from 'jsdom'
const doc = jsdom.jsdom('<!doctype html><html><head><script src=""></head><body></body></html>')
global.document = doc
global.window = doc.defaultView


test('detail pane renders headers of table panel with extra info', (t) => {
    const wrapper = shallow(<DetailPane has_extra_info={true} 
        metric_detail = {{cells: ["cell 1"], className: 'cls', id: 'IDx', comment:'', extra_info: {"headers": {"link": "Branch"}, "title":"Extra Info Title"}}}>
    </DetailPane>)
    t.equals(wrapper.find('TablePanel').exists(), true);
    t.equals(wrapper.find('TablePanel').dive().find('th').text(), "Branch ");
    t.equals(wrapper.find('TablePanel').dive().find('h4').text(), "Extra Info Title");
    t.end();
});

test('detail pane renders empty headers', (t) => {
    const wrapper = shallow(<DetailPane has_extra_info={true} metric_detail = {{extra_info: {"headers": ''}}}>
    </DetailPane>)
    t.equals(wrapper.find('TablePanel').exists(), true);
    t.equals(wrapper.find('TablePanel').dive().find('thead').children().exists(), false);
    t.end();
});

test('detail pane does not render headers of table panel beginning with underscore', (t) => {
    const wrapper = shallow(<DetailPane has_extra_info={true} 
        metric_detail = {{cells: ["cell 1"], extra_info: {"headers": {"col1": "X", "col2": "_x"}}}}>
    </DetailPane>)
    t.equals(wrapper.find('TablePanel').dive().find('th').length, 1);
    t.equals(wrapper.find('TablePanel').dive().find('th').text(), "X ");
    t.end();
});


test('detail pane does not render columns of the table panel if their header begins with underscore', (t) => {
    const wrapper = shallow(<DetailPane has_extra_info={true} 
        metric_detail = {{cells: ["cell 1"], extra_info: {"headers": {"str": "_x", "num": "Number"},
                                "data":[{"str": "First Row", "num": "1"}, {"str": "Second Row", "num": "2"}]}}}>
    </DetailPane>)
    t.equals(wrapper.find('TablePanel').dive().find('tbody tr').first().find('td').length, 1);
    t.equals(wrapper.find('TablePanel').dive().contains('First Row'), false);
    t.equals(wrapper.find('TablePanel').dive().find('tbody tr').first().contains('1'), true);
    t.equals(wrapper.find('TablePanel').dive().last().contains('Second Row'), false);
    t.equals(wrapper.find('TablePanel').dive().find('tbody tr').last().contains('2'), true);
    t.end();
});

test('detail pane renders with css classes in header names', (t) => {
    const wrapper = shallow(<DetailPane has_extra_info={true} 
        metric_detail = {{cells: ["cell 1"], extra_info: {"headers": {"str": "FirstHeader__css_class"},
        "data":[{"str": "First Row"}]}}}>
    </DetailPane>)
    
    t.equals(wrapper.find('TablePanel').dive().find('tbody tr').first().find('td').length, 1);
    t.equals(wrapper.find('TablePanel').dive().find('tbody tr td.css_class').contains('First Row'), true);
    t.equals(wrapper.find('TablePanel').dive().find('th.css_class').text(), "FirstHeader ");
    t.end();
});

test('detail pane renders rows of the table panel with <className> if the column with _<className> header text is "true"', (t) => {
    const wrapper = shallow(<DetailPane has_extra_info={true} 
        metric_detail = {{cells: ["cell 1"], extra_info: {"headers": {"str": "String", "format": "_italic"},
                             "data":[{"str": "First Row", "format": "true"}, {"str": "Second Row", "format": "false"}]}}}>
    </DetailPane>)

    t.equals(wrapper.find('TablePanel').dive().find('tbody tr').first().text(), 'First Row');
    t.equals(wrapper.find('TablePanel').dive().find('tbody tr').first().find('.italic').exists(), true);
    t.equals(wrapper.find('TablePanel').dive().find('tbody tr').last().text(), 'Second Row');
    t.equals(wrapper.find('TablePanel').dive().find('tbody tr').last().find('.italic').exists(), false);

    t.end();
});

test('detail pane renders rows of the table panel with extra info', (t) => {
    const wrapper = shallow(<DetailPane has_extra_info={true} 
        metric_detail = {{cells: ["cell 1"], extra_info: {"headers": {"str": "String", "num": "Number"},
                                "data":[{"str": "First Row", "num": "1"}, {"str": "Second Row", "num": "2"}]}}}>
    </DetailPane>)

    t.equals(wrapper.find('TablePanel').exists(), true);
    t.equals(wrapper.find('TablePanel').dive().find('tbody tr').first().contains('First Row'), true);
    t.equals(wrapper.find('TablePanel').dive().find('tbody tr').first().contains('1'), true);
    t.equals(wrapper.find('TablePanel').dive().find('tbody tr').last().contains('Second Row'), true);
    t.equals(wrapper.find('TablePanel').dive().find('tbody tr').last().contains('2'), true);
    t.end();
});

test('detail pane renders rows of the table panel with links in extra info', (t) => {
    const wrapper = shallow(<DetailPane has_extra_info={true} 
        metric_detail = {{cells: ["cell 1"], extra_info: {"headers": {"col": "Link"},
                                "data":[{"col": {"href":"http://xxx", "text": "Description"}}]}}} />)

    t.equals(wrapper.find('TablePanel').exists(), true);
    t.equals(wrapper.find('TablePanel').dive().find('tbody tr a').text(), "Description");
    t.equals(wrapper.find('TablePanel').dive().find('tbody tr a[href="http://xxx"]').exists(), true);
    t.end();
});

test('detail pane renders rows of the table panel with links in extra info, with link as the text', (t) => {
    const wrapper = shallow(<DetailPane has_extra_info={true} 
        metric_detail = {{cells: ["cell 1"], extra_info: {"headers": {"col": "Link"},
                "data":[{"col": {"href":"http://xxx", "text": ""}}]}}} />)
    t.equals(wrapper.find('TablePanel').exists(), true);
    t.equals(wrapper.find('TablePanel').dive().find('tbody tr a').text(), "http://xxx");
    t.equals(wrapper.find('TablePanel').dive().find('tbody tr a[href="http://xxx"]').exists(), true);
    t.end();
});

test('detail pane renders action panel', (t) => {
    const wrapper = shallow(<DetailPane on_hide_metric='onClickFunction' metric_detail={{id: 'IDx', extra_info: {}}} />)
    t.equals(wrapper.find('ActionPanel').exists(), true);
    t.equals(wrapper.find('ActionPanel').prop('onClick'), 'onClickFunction');
    t.equals(wrapper.find('ActionPanel').prop('metric_id'), 'IDx');
    t.end();
});

test('detail pane renders hide metric button', (t) => {
    const wrapper = shallow(<DetailPane on_hide_metric='onClickFunction' metric_detail={{id: 'IDx', extra_info: {}}} />)
    t.equals(wrapper.find('ActionPanel').dive().find('button').first().text(), 'Verberg deze metriek');
    t.equals(wrapper.find('ActionPanel').dive().find('button').first().prop('id'), 'IDx');
    t.equals(wrapper.find('ActionPanel').dive().find('button').first().prop('onClick'), 'onClickFunction');
    t.equals(wrapper.find('ActionPanel').dive().find('button').first().prop('data-toggle'), 'tooltip');
    t.equals(wrapper.find('ActionPanel').dive().find('button').first().prop('data-placement'), 'right');
    t.equals(wrapper.find('ActionPanel').dive().find('button').first().prop('title'),
            'Gebruik het Toon-menu om verborgen metrieken weer zichtbaar te maken.');
    t.end();
});

test('detail pane renders history chart', (t) => {
    const wrapper = shallow(<DetailPane on_hide_metric='onClickFunction' 
                            metric_detail={{name: 'Title', unit: 'day', stable_id: 'x x ', id: 'IDx', extra_info: {}}} />)
    t.equals(wrapper.find('HistoryChart').exists(), true);
    t.equals(wrapper.find('HistoryChart').prop('title'), 'Title');
    t.equals(wrapper.find('HistoryChart').prop('unit'), 'day');
    t.equals(wrapper.find('HistoryChart').prop('stable_metric_id'), 'x_x_');
    t.end();
});

test('detail pane renders history chart without stable id', (t) => {
    const wrapper = shallow(<DetailPane on_hide_metric='onClickFunction' metric_detail={{id: 'IDx', extra_info: {}}} />)
    t.equals(wrapper.find('HistoryChart').prop('stable_metric_id'), '');
    t.end();
});

test('detail pane executes function that should hide metric when hide button clicked', (t) => {
    const onButtonClick = sinon.spy();
    const wrapper = shallow(<DetailPane on_hide_metric={onButtonClick} metric_detail={{id: 'IDx', extra_info: {}}} />)
    var button = wrapper.find('ActionPanel').dive().find('button');
    t.equals(button.first().text(), 'Verberg deze metriek');
    button.simulate('click');
    t.equals(onButtonClick.callCount, 1);
    t.end();
});

test('detail pane does render detail table if there is extra info', (t) => {
    const wrapper = shallow(<DetailPane has_extra_info={true} 
        metric_detail = {{cells: ["cell 1"], className: 'cls', id: 'IDx', comment:'', 
        extra_info: {title: "Extra!", headers: {"x": "y"}, data:[{"x":"extra data"}]}}} />)
    t.equals(wrapper.find('tr.cls.collapse[id="IDx_details"] td.detail_pane').length, 1);
    t.equals(wrapper.find('TablePanel').length, 1);
    var rendered_table = wrapper.find('TablePanel').dive();
    t.equals(rendered_table.find('div.panel.panel-default').length, 1);
    t.equals(rendered_table.find('div.panel.panel-default h4.panel-heading').text(), "Extra!");
    t.equals(rendered_table.find('div.panel.panel-default div.panel-body table.table-striped').length, 1);
    t.equals(rendered_table.find('thead>tr>th.detail-table-header').first().text(), 'y ');
    t.equals(rendered_table.find('tbody>tr>td').first().text(), 'extra data');
    t.end();
});

test('when clicked on header of detail table, extra info is sorted', (t) => {
    const wrapper = mount(<DetailPane has_extra_info={true} 
        metric_detail = {{cells: ["cell 1"], className: 'cls', id: 'IDx', comment:'', 
        extra_info: {title: "Extra!", headers: {"c1": "Col Name"}, data:[{"c1":"bb"}, {"c1":"aa"}]}}} />)
    t.equals(wrapper.find('tr.cls.collapse[id="IDx_details"] td.detail_pane table.table-striped tbody>tr').first().find('td').first().text(), 'bb');
    var header = wrapper.find('tr.cls.collapse[id="IDx_details"] td.detail_pane table.table-striped thead>tr>th').first();
    t.equals(header.text(), 'Col Name ');
    header.simulate('click');
    t.equals(wrapper.find('tr.cls.collapse[id="IDx_details"] td.detail_pane table.table-striped tbody>tr').first().find('td').first().text(), 'aa');
    t.equals(header.text(), 'Col Name▾');
    t.end();
});

test('when clicked on header of detail table that contains link, extra info is sorted on text', (t) => {
    const wrapper = mount(<DetailPane has_extra_info={true} 
        metric_detail = {{cells: ["cell 1"], className: 'cls', id: 'IDx', comment:'', 
        extra_info: {title: "Extra!", headers: {"c1": "whatever"}, data:[{"c1": {"href":"http://xxx", "text": "bb"}}, {"c1": {"href":"http://yyy", "text": "aa"}}]}}} />)
    t.equals(wrapper.find('tr.cls.collapse[id="IDx_details"] td.detail_pane table.table-striped tbody>tr').first().find('td').first().text(), 'bb');
    var header = wrapper.find('tr.cls.collapse[id="IDx_details"] td.detail_pane table.table-striped thead>tr>th').first();
    header.simulate('click');
    t.equals(wrapper.find('tr.cls.collapse[id="IDx_details"] td.detail_pane table.table-striped tbody>tr').first().find('td').first().text(), 'aa');
    t.end();
});

test('when clicked again on the header of detail table, extra info is sorted in reversed order', (t) => {
    const wrapper = mount(<DetailPane has_extra_info={true} 
        metric_detail = {{cells: ["cell 1"], className: 'cls', id: 'IDx', comment:'', 
        extra_info: {title: "Extra!", headers: {"c1": "Col Name"}, data:[{"c1":"bb"}, {"c1":"aa"}]}}} />)
    t.equals(wrapper.find('tr.cls.collapse[id="IDx_details"] td.detail_pane table.table-striped tbody>tr').first().find('td').first().text(), 'bb');
    var header = wrapper.find('tr.cls.collapse[id="IDx_details"] td.detail_pane table.table-striped thead>tr>th.detail-table-header').first();
    t.equals(header.text(), 'Col Name ');
    header.simulate('click');
    t.equals(wrapper.find('tr.cls.collapse[id="IDx_details"] td.detail_pane table.table-striped tbody>tr').first().find('td').first().text(), 'aa');
    t.equals(header.text(), 'Col Name▾');
    header.simulate('click');
    t.equals(wrapper.find('tr.cls.collapse[id="IDx_details"] td.detail_pane table.table-striped tbody>tr').first().find('td').first().text(), 'bb');
    t.equals(header.text(), 'Col Name▴');
    t.end();
});

test('when clicked on the other header of the detail table, extra info is sorted ascending on that column', (t) => {
    const wrapper = mount(<DetailPane has_extra_info={true} 
        metric_detail = {{cells: ["cell 1"], className: 'cls', id: 'IDx', comment:'', 
        extra_info: {title: "Extra!", headers: {"c1": "whatever", "c2": "header2"}, data:[{"c1":"bb", "c2":"xx"}, {"c1":"aa", "c2":"zz"}]}}} />)
    t.equals(wrapper.find('tr.cls.collapse[id="IDx_details"] td.detail_pane table.table-striped tbody>tr').first().find('td').first().text(), 'bb');
    var header = wrapper.find('tr.cls.collapse[id="IDx_details"] td.detail_pane table.table-striped thead>tr>th.detail-table-header').first();
    header.simulate('click');
    t.equals(wrapper.find('tr.cls.collapse[id="IDx_details"] td.detail_pane table.table-striped tbody>tr').first().find('td').first().text(), 'aa');
    var header2 = wrapper.find('tr.cls.collapse[id="IDx_details"] td.detail_pane table.table-striped thead>tr>th.detail-table-header').last();
    header2.simulate('click');
    t.equals(wrapper.find('tr.cls.collapse[id="IDx_details"] td.detail_pane table.table-striped tbody>tr').first().find('td').last().text(), 'xx');
    t.end();
});

