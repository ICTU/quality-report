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

function format_date_time(date_time) {
    // Format the Date object as a date and time string
    var date_string = date_time.getDate() + "-" + (date_time.getMonth() + 1) + "-" + date_time.getFullYear();
    var minutes = date_time.getMinutes();
    minutes = minutes < 10 ? '0' + minutes : minutes;
    var time_string = date_time.getHours() + ":" + minutes;
    return date_string + ' ' + time_string;
}

function intersection(array1, array2) {
    var intersection_array = [];
    for (var index1 = 0; index1 < array1.length; index1++) {
        for (var index2 = 0; index2 < array2.length; index2++) {
            if (array1[index1] === array2[index2]) {
                intersection_array[intersection_array.length] = array1[index1];
            }
        }
    }
    return intersection_array;
}

export {format_date_time, intersection};

