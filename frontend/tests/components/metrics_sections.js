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

import { shallow } from 'enzyme';
import Enzyme from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';

Enzyme.configure({ adapter: new Adapter() });

import {MetricsSections} from '../../js/components/metrics_sections.js';
import {EmptyStorage} from '../stubs/storage.js';


test('metrics sections show one table', function(t) {
    const wrapper = shallow(<MetricsSections show_one_table storage={new EmptyStorage()} metrics={[]} />);
    t.equal(wrapper.find("MetricsSection").length, 1);
    t.end();
});

test('metrics sections show multible tables', function(t) {
    const wrapper = shallow(
        <MetricsSections storage={new EmptyStorage()}
                         metrics={[{section: "section1"}, {section: "section2"}]}
                         metrics_data={{sections: [{id: "section1"}, {id: "section2"}]}}/>
    );
    t.equal(wrapper.find("MetricsSection").length, 2);
    t.end();
});
