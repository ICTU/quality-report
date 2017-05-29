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


function parse_history_json(history_json) {
    var history = [];
    history_json.forEach(function(value) {
        var measurement = [];
        measurement.push(new Date(value[0][0], value[0][1], value[0][2], value[0][3], value[0][4], value[0][5]));
        measurement.push(value[1][0], value[1][1], value[1][2], value[1][3], value[1][4], value[1][5], value[1][6]);
        history.push(measurement);
    });
    return history;
}

export {parse_history_json};
