import test from 'tape';
import React from 'react';
import {Help} from '../../js/components/help.js';

import { shallow, mount } from 'enzyme';
import Enzyme from 'enzyme';
import sinon from 'sinon';
import Adapter from 'enzyme-adapter-react-16';

Enzyme.configure({ adapter: new Adapter() });

test('help component rendered loading', (t) => {
    const wrapper = shallow(<Help />);
    t.equals(wrapper.state().meta_data, 'loading');
    t.equals(wrapper.find('Loader').exists(), true);
    t.end();
});

test('help component rendered loaded', (t) => {
    const wrapper = shallow(<Help />);
    t.equals(wrapper.state().meta_data, 'loading');
    wrapper.setState({meta_data: '{something: "else"}'});
    t.equals(wrapper.find('Loader').exists(), false);
    t.equals(wrapper.find('div').exists(), true);
    t.end();
});

test('help component retrieves meta data when mounted', (t) => {
    var getJsonMock = sinon.spy($, "get");
    const wrapper = shallow(<Help />);

    t.equals(getJsonMock.calledOnce, true);

    t.equals(getJsonMock.firstCall.args[0], "json/meta_data.json");
    $.get.restore();
    t.end();
});