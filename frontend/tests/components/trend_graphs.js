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
import {TrendGraph,TrendGraphs} from '../../js/components/trend_graphs.js';

import {mount, shallow} from 'enzyme';
import Enzyme from 'enzyme';
import sinon from 'sinon';
import Adapter from 'enzyme-adapter-react-16';
import { wrap } from 'module';

Enzyme.configure({ adapter: new Adapter() });

test('trend graphs component is loading', function(t) {
    const wrapper = shallow(<TrendGraphs />);
    t.equals(wrapper.state().history_data, "loading");
    t.equals(wrapper.find('Loader').exists(), true);
    t.end();
});

test('trend graphs component is loaded', function(t) {
    const wrapper = shallow(<TrendGraphs />);
    t.equals(wrapper.state().history_data, "loading");
    wrapper.setState({history_data: 'loaded history data'});

    t.equals(wrapper.find('TrendGraph#meta_metrics_history_absolute_graph').exists(), true);
    t.equals(wrapper.find('TrendGraph#meta_metrics_history_absolute_graph').prop('history_data'), 'loaded history data');
    t.equals(wrapper.find('TrendGraph#meta_metrics_history_absolute_graph').prop('title'), 'Aantal metrieken per status');
    t.equals(wrapper.find('TrendGraph#meta_metrics_history_relative_graph').exists(), true);
    t.equals(wrapper.find('TrendGraph#meta_metrics_history_relative_graph').prop('history_data'), 'loaded history data');
    t.equals(wrapper.find('TrendGraph#meta_metrics_history_relative_graph').prop('title'), 'Percentage metrieken per status');
    t.end();
});

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

test('trend graphs component retrieves data when rendered', (t) => {
    var getJsonMock = sinon.spy($, "getJSON", );
    const wrapper = shallow(<TrendGraphs />);

    t.equals(getJsonMock.calledOnce, true);
    t.equals(getJsonMock.firstCall.args[0], "json/meta_history.json");
    t.equals(wrapper.instance().dataRetrievedCallback, getJsonMock.firstCall.args[2]);

    $.getJSON.restore();
    t.end();
});

test('trend graphs component fills history data after retrieval', (t) => {
    const wrapper = shallow(<TrendGraphs />);

    wrapper.instance().dataRetrievedCallback([
        [[2018, 3, 6, 14, 58, 14], [1, 4, 5, 8, 0, 15, 41]],
        [[2018, 3, 23, 16, 50, 2], [1, 4, 5, 8, 0, 15, 41]]
    ]);
    
    t.deepEquals(wrapper.state().history_data, 
        { 
            labels: [new Date(2018, 3, 6, 14, 58, 14), new Date(2018, 3, 23, 16, 50, 2)], 
            datasets: [
                { label: 'Perfect', fill: true, pointRadius: 0, backgroundColor: '#45E600', data: [ 1, 1 ] }, 
                { label: 'Goed', fill: true, pointRadius: 0, backgroundColor: '#4CC417', data: [ 4, 4 ] }, 
                { label: 'Bijna goed', fill: true, pointRadius: 0, backgroundColor: '#FDFD90', data: [ 5, 5 ] }, 
                { label: 'Actie vereist', fill: true, pointRadius: 0, backgroundColor: '#FC9090', data: [ 8, 8 ] }, 
                { label: 'Technische schuld', fill: true, pointRadius: 0, backgroundColor: '#808080', data: [ 0, 0 ] }, 
                { label: 'Bron niet beschikbaar', fill: true, pointRadius: 0, backgroundColor: '#F0F0F0', data: [ 15, 15 ] }, 
                { label: 'Bron niet geconfigureerd', fill: true, pointRadius: 0, backgroundColor: '#F0F0F0', data: [ 41, 41 ] }
            ]
        }
    );

    t.end();
});