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
import { TrendGraph } from '../../js/components/trend_graphs.js';

import { mount } from 'enzyme';
import Enzyme from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';

Enzyme.configure({ adapter: new Adapter() });


test('chart is stacked', function(t) {
    const wrapper = mount(<div><TrendGraph history_data={{}}/></div>);
    t.equals(wrapper.find('ChartComponent').props("options")["options"]["scales"]["yAxes"][0]["stacked"], true);
    t.end();
});

test('relative chart has plugin enabled', function(t) {
    const wrapper = mount(<div><TrendGraph relative={true} history_data={{}}/></div>);
    t.equals(wrapper.find('ChartComponent').props("options")["options"]["plugins"]["stackedline100"]["enable"], true);
    t.end();
});
