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

import { shallow } from 'enzyme';
import Enzyme from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';

Enzyme.configure({ adapter: new Adapter() });

import {NavBar} from '../../js/components/navbar.js';


test('navbar title', function(t) {
    const wrapper = shallow(<NavBar report_title="Title" report_date_time={[2020, 1, 1, 12, 0, 0]}/>);
    t.equal(wrapper.find('a.navbar-brand').text(), "Title");
    t.end();
});

test('navbar report datetime', function(t) {
    const year = new Date().getFullYear() + 1;
    const wrapper = shallow(<NavBar report_title="Title" report_date_time={[year, 1, 1, 12, 0, 0]}/>);
    t.equal(wrapper.find('span.navbar-text').text(), "Rapportage van 1-1-" + year + " 12:00");
    t.end();
});

test('navbar report datetime old', function(t) {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth();
    const day = now.getDate();
    const hour = now.getHours();
    const wrapper = shallow(<NavBar report_title="Title" report_date_time={[year, month + 1, day, hour - 2, 0, 0]}/>);
    t.equal(wrapper.find('span > span').hasClass("old"), true);
    t.end();
});

test('navbar report datetime very old', function(t) {
    const year = new Date().getFullYear() - 2;
    const wrapper = shallow(<NavBar report_title="Title" report_date_time={[year, 1, 1, 12, 0, 0]}/>);
    t.equal(wrapper.find('span > span').hasClass("very_old"), true);
    t.end();
});
