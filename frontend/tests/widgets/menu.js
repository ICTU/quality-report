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
import {Menu, MenuItem} from '../../js/widgets/menu.js';


test('menu without menu items', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<Menu id="id" title="Menu"/>);
    const result = renderer.getRenderOutput();
    t.deepEquals(
        result.props.children,
        [
            <a id="id" className="dropdown-toggle" role="button" data-toggle="dropdown"
               href="#" aria-haspopup="true" aria-expanded="false">Menu<span className="caret"></span></a>,
            <ul className="dropdown-menu" aria-labelledby="id">{undefined}</ul>
        ]
    );
    t.end();
});

test('menu with menu item', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<Menu id="id" title="Menu"><MenuItem title="Menu item" /></Menu>);
    const result = renderer.getRenderOutput();
    t.deepEquals(
        result.props.children[1],
        <ul className="dropdown-menu" aria-labelledby="id">
            <MenuItem title="Menu item" />
        </ul>
    );
    t.end();
});

test('menu hidden', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<Menu hide />);
    const result = renderer.getRenderOutput();
    t.equals(result, null);
    t.end();
});

test('menu item title', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<MenuItem title="title" />);
    const result = renderer.getRenderOutput();
    t.equals(result.props.children.props.children[2], "title");
    t.end();
});

test('menu item hidden', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<MenuItem hide />);
    const result = renderer.getRenderOutput();
    t.equals(result, null);
    t.end();
});

test('menu item icon', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<MenuItem icon="foo" />);
    const result = renderer.getRenderOutput();
    t.equals(result.props.children.props.children[0].props.className, "glyphicon glyphicon-foo");
    t.end();
});

test('menu item check icon', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<MenuItem check />);
    const result = renderer.getRenderOutput();
    t.equals(result.props.children.props.children[0].props.className, "glyphicon glyphicon-ok");
    t.end();
});

test('menu item disabled', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<MenuItem disabled />);
    const result = renderer.getRenderOutput();
    t.equals(result.props.className, "disabled");
    t.end();
});
