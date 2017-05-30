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
import {intersection, format_date_time} from '../js/utils.js';

test('intersection of two empty arrays is an empty array', function(t) {
    t.deepEqual([], intersection([], []));
    t.end();
});

test('intersection with first array empty is an empty array', function(t) {
    t.deepEqual([], intersection([], [1, 2]));
    t.end();
});

test('intersection with second array empty is an empty array', function(t) {
    t.deepEqual([], intersection([1, 2], []));
    t.end();
});

test('intersection of equal arrays equals both arrays', function(t) {
    t.deepEqual([1, 2], intersection([1, 2], [1, 2]));
    t.end();
});

test('intersection of differently ordered equal arrays equals first array', function(t) {
    t.deepEqual([1, 2], intersection([1, 2], [2, 1]));
    t.end();
});

test('intersection of different arrays is empty', function(t) {
    t.deepEqual([], intersection([1, 2], [3, 4]));
    t.end();
});

test('intersection of overlapping arrays is the overlap', function(t) {
    t.deepEqual([2], intersection([1, 2], [2, 3]));
    t.end();
});

test('format 1st of january without time', function(t) {
    t.equal(format_date_time(new Date(2017, 0, 1)), '1-1-2017 0:00');
    t.end();
});

test('format 31st of december with time', function(t) {
    t.equal(format_date_time(new Date(2017, 11, 31, 23, 59, 59)), '31-12-2017 23:59');
    t.end();
});
