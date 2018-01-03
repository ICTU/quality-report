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

test('bootstrap table header thead', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<BootstrapTableHeader headers={[["id", "title"]]} />);
    const result = renderer.getRenderOutput();
    t.equals(result.type, 'thead');
    t.end();
});

test('bootstrap table body tbody', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<BootstrapTableBody>{[{cells: ["cell 1"], className: ''}]}</BootstrapTableBody>);
    const result = renderer.getRenderOutput();
    t.equals(result.type, 'tbody');
    t.end();
});

test('bootstrap table body html', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<BootstrapTableBody>{[{cells: [{__html: "<p>cell 1</p>"}], className: ''}]}</BootstrapTableBody>);
    const result = renderer.getRenderOutput();
    t.equals(result.props.children[0].props.children[0].props.dangerouslySetInnerHTML.__html, '<p>cell 1</p>');
    t.end();
});

test('bootstrap table header with caret', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<BootstrapTableHeader table_sort_column_name="id" table_sort_ascending headers={[["id", "title"]]} />);
    const result = renderer.getRenderOutput();
    t.deepEquals(result.props.children.props.children[0].props.children[1], <Caret show table_sort_ascending />);
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
