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
import {App} from '../js/app.js';
import {Loader} from '../js/widgets/loader.js';
import {EmptyStorage} from './stubs/storage.js';

import jQuery from 'jquery';
import {mount} from 'enzyme';
import Enzyme from 'enzyme';
import sinon from 'sinon';
import Adapter from 'enzyme-adapter-react-16';

Enzyme.configure({ adapter: new Adapter() });

import jsdom from 'jsdom'
const doc = jsdom.jsdom('<!doctype html><html><head><script src=""></head><body></body></html>')
global.document = doc
global.window = doc.defaultView
global.$ = require('jquery')(global.window);


test('app', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<App storage={new EmptyStorage()}/>);
    const result = renderer.getRenderOutput();
    t.equals(result.type, 'div');
    t.end();
});

test('app starts loading', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<App storage={new EmptyStorage()} />);
    const result = renderer.getRenderOutput();
    t.comment(Object.keys(result.props));
    t.deepEquals(result.props.children.props.children.props.children, <Loader/>);
    t.end();
});

test('xapp filter without metrics', function(t) {
    var getJsonMock = sinon.spy($, "getJSON");

    mount(<App storage={new EmptyStorage()}/>)
    mount(<App storage={new EmptyStorage()}/>)

    var callArgs1 = getJsonMock.firstCall.args[0].split("?v=")
    var callArgs2 = getJsonMock.secondCall.args[0].split("?v=")

    t.equals(getJsonMock.calledTwice, true);
    t.equals(callArgs1[0], 'json/metrics.json')
    t.equals(callArgs2[0], 'json/metrics.json')
    t.notEquals(callArgs1[1], callArgs2[1])
    t.end();
});

test('app filter without metrics', function(t) {
    let app = new App({storage: new EmptyStorage()});
    t.deepEqual(app.filter({metrics: []}, {search_string: ""}), []);
    t.end();
});

test('app filter without filter', function(t) {
    let app = new App({storage: new EmptyStorage()});
    t.deepEqual(
        app.filter(
            {metrics: [{status: 'green', id_format: '', measurement: '', norm: '', comment: ''}]},
            {hidden_metrics: '', filter_status_week: true, filter_color_green: true, search_string: ''}
        ),
        [{status: 'green', id_format: '', measurement: '', norm: '', comment: ''}]
    );
    t.end();
});

test('app filter by status', function(t) {
    let app = new App({storage: new EmptyStorage()});
    t.deepEqual(
        app.filter(
            {metrics: [{status: 'green', id_format: '', measurement: '', norm: '', comment: ''}]},
            {hidden_metrics: '', filter_status_week: true, filter_color_green: false, search_string: ''}
        ),
        []
    );
    t.end();
});

test('app filter hidden metric', function(t) {
    let app = new App({storage: new EmptyStorage()});
    t.deepEqual(
        app.filter(
            {metrics: [{status: 'green', id_value: 'id', id_format: '', measurement: '', norm: '', comment: ''}]},
            {hidden_metrics: 'id', filter_status_week: true, filter_color_green: true, search_string: ''}
        ),
        []
    );
    t.end();
});

test('app filter by status start date, without status start', function(t) {
    let app = new App({storage: new EmptyStorage()});
    t.deepEqual(
        app.filter(
            {metrics: [{status: 'green', status_start_date: [], id_format: '', measurement: '', norm: '',
                        comment: ''}]},
            {hidden_metrics: '', filter_status_week: false, filter_color_green: true, search_string: ''}
        ),
        []
    );
    t.end();
});
