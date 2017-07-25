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
import ShallowRenderer from 'react-test-renderer/shallow';
import {BootstrapTable, BootstrapTableHeader, BootstrapTableBody} from '../../js/widgets/bootstrap_table.js';


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
    renderer.render(<BootstrapTable headers={[["id", "title"]]}>{["cell 1"]}</BootstrapTable>);
    const result = renderer.getRenderOutput();
    t.deepEquals(result.props.children[1], <BootstrapTableBody>{["cell 1"]}</BootstrapTableBody>);
    t.end();
});
