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

function format_date_time(year, month, day, hours, minutes) {
    // Format the date and time as a string
    var date_string = day + "-" + month + "-" + year;
    minutes = minutes < 10 ? '0' + minutes : minutes;
    var time_string = hours + ":" + minutes;
    return date_string + ' ' + time_string;
}

export {format_date_time};
