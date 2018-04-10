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
import {Menus, MetricsMenu, FilterMenu, TrendMenu, HelpMenu, Search} from '../../js/components/menu.js';
import {Menu} from '../../js/widgets/menu.js';


test('menus', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<Menus />);
    const result = renderer.getRenderOutput();
    t.equal(result.type, 'div');
    t.end();
});

test('metrics menu', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<MetricsMenu sections={[{id: "id", title: "title"}]}/>);
    const result = renderer.getRenderOutput();
    t.equal(result.type, <Menu/>.type);
    t.end();
});

test('filter menu', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<FilterMenu filter={{hidden_metrics: []}} />);
    const result = renderer.getRenderOutput();
    t.equal(result.type, <Menu/>.type);
    t.end();
});

test('filter input', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<Search filter={{search_string: ""}} />);
    const result = renderer.getRenderOutput();
    t.equal(result.type, 'form');
    t.end();
});

test('trend menu', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<TrendMenu />);
    const result = renderer.getRenderOutput();
    t.equal(result.type, <Menu/>.type);
    t.end();
});

test('help menu', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<HelpMenu />);
    const result = renderer.getRenderOutput();
    t.equal(result.type, <Menu/>.type);
    t.end();
});

