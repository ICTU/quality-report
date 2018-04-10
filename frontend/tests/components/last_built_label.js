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
import ReactTestUtils from 'react-dom/test-utils';
import {LastBuiltLabel} from '../../js/components/last_built_label.js';


test('when last change date is later than 2000 last built element is correctly rendered', function(t) {
    const renderer = new ShallowRenderer();
    const lastChangeDate = "2001-01-01 00:00:00"

    renderer.render(<LastBuiltLabel latest_change_date={lastChangeDate} />);
    const result = renderer.getRenderOutput();

    t.equal(result.type, 'span');
    t.equal(result.props.className, 'badge badge-secondary label_space');
    t.equal(result.props.children[0].trim(), 'gewijzigd')
    t.equal(result.props.children[1].type.Function : 'TimeAgo')
    t.equal(result.props.children[1].props.date, lastChangeDate)
    t.equal(result.props.children[1].props.now.Function : 'now' )

    t.end();
});

test('when last change date is before 2000 last built element is not rendered', function(t) {
    const renderer = new ShallowRenderer();
    const lastChangeDate = "1999-01-01 00:00:00"

    renderer.render(<LastBuiltLabel latest_change_date={lastChangeDate} />);
    const result = renderer.getRenderOutput();

    t.equal(result, '')

    t.end();
});

test('when last change date is undefined last built element is not rendered', function(t) {
    const renderer = new ShallowRenderer();
    const lastChangeDate = undefined;

    renderer.render(<LastBuiltLabel latest_change_date={lastChangeDate} />);
    const result = renderer.getRenderOutput();

    t.equal(result, '')
    t.end();
});
