/* Copyright 2012-2017 Ministerie van Sociale Zaken en Werkgelegenheid
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
import {format_date_time} from '../js/utils.js';


test('format 1st of january without time', function(t) {
    t.equal(format_date_time(2017, 1, 1, 0, 0), '1-1-2017 0:00');
    t.end();
});

test('format 31st of december with time', function(t) {
    t.equal(format_date_time(2017, 12, 31, 23, 59, 59), '31-12-2017 23:59');
    t.end();
});
