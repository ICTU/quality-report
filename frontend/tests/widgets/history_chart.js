import test from 'tape';
import React from 'react';
import {HistoryChart} from '../../js/widgets/history_chart.js';

import { shallow, mount } from 'enzyme';
import Enzyme from 'enzyme';
import sinon from 'sinon';
import Adapter from 'enzyme-adapter-react-16';

Enzyme.configure({ adapter: new Adapter() });

import jsdom from 'jsdom'
const doc = jsdom.jsdom('<!doctype html><html><head><script src=""></head><body></body></html>')
global.document = doc
global.window = doc.defaultView

test('history chart not rendered if not expanded', (t) => {
    const wrapper = shallow(
        <HistoryChart title='Name' unit='days' is_expanded = {false}
                    report_dates="2018-04-06 14:58:14,2018-04-10 13:19:01"
                    stable_metric_id = 'stable_id'/>
        );
    t.equals(wrapper.find('Line').exists(), false);
    t.end();
});

test('history chart rendered properly', (t) => {
    const wrapper = shallow(
        <HistoryChart title='Name' unit='days' is_expanded = {true}
                    report_dates="2018-04-06 14:58:14,2018-04-10 13:19:01"
                    stable_metric_id = 'stable_id'/>
        );

    t.equals(wrapper.exists(), true);
    t.equals(wrapper.find('Line').exists(), true);

    t.deepEquals(wrapper.find('Line').prop('data').datasets[0].data, []);
    t.deepEquals(wrapper.find('Line').prop('options').title.text, "Name");
    t.deepEquals(wrapper.find('Line').prop('options').scales.yAxes[0].scaleLabel.labelString, "days");
    t.deepEquals(wrapper.find('Line').prop('data').labels, ["2018-04-06 14:58:14", "2018-04-10 13:19:01"]);

    t.end();
});

test('history chart component passes data to the chart', (t) => {
    const wrapper = shallow(
        <HistoryChart title='Name' unit='days' is_expanded = {true}
                    report_dates="2018-04-06 14:58:14,2018-04-10 13:19:01"
                    stable_metric_id = 'stable_id'/>
        );

    t.equals(wrapper.exists(), true);

    wrapper.setState({chart_data: '1,2, -3'});
    t.equals(wrapper.find('Line').exists(), true);

    t.deepEquals(wrapper.find('Line').prop('data').datasets[0].data, [1, 2, -3]);
    t.end();
});

test('history chart retrieves data when expanded', (t) => {
    const wrapper = shallow(
        <HistoryChart title='Name' unit='days' is_expanded = {true}
                    report_dates="2018-04-06 14:58:14,2018-04-10 13:19:01"
                    stable_metric_id = 'stable id'/>
        );

    var getJsonMock = sinon.spy($, "get");
    
    t.equals(wrapper.exists(), true);
    t.equals(getJsonMock.notCalled, true);

    wrapper.setProps({ is_expanded: true });
    wrapper.update();

    t.equals(getJsonMock.calledOnce, true);
    var callArgs = getJsonMock.firstCall.args[0].split("?v=")

    t.equals(callArgs[0], "json/stable_id.txt");
    $.get.restore();
    t.end();
});

