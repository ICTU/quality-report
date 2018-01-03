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
import {UrlList} from '../../js/widgets/url_list.js';


test('url list consists of paragraphs', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<UrlList>{["http://url"]}</UrlList>);
    const result = renderer.getRenderOutput();
    t.equals(result.props.children[0].type, 'p');
    t.end();
});

test('empty url list consist of div only', function(t) {
    const renderer = new ShallowRenderer();
    renderer.render(<UrlList>{[]}</UrlList>);
    const result = renderer.getRenderOutput();
    t.equals(result.props.children.length, 0);
    t.end();
});
