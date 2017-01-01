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

// Functions to read and write cookies.

function write_cookie(name, value, days) {
    // Write the cookie and make it expire in the future.
    if (typeof(days) === 'undefined') {
        // Use 7 days if days is not specified.
        days = 7;
    }
    var date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    var expires = '; expires=' + date.toGMTString();
    // Set the cookie.
    document.cookie = name + '=' + value + expires + '; path=/';
}

function read_cookie(name, default_value) {
    // Read and parse the cookie. If the cookie has no value, the default value is returned.
    var name_assignment = name + '=';
    var cookies = document.cookie.split(';');
    for(var i=0; i < cookies.length; i++) {
        var cookie = cookies[i];
        // Skip initial spaces.
        while (cookie.charAt(0) === ' ') {
            cookie = cookie.substring(1, cookie.length);
        }
        if (cookie.indexOf(name_assignment) === 0) {
            // Found the cookie, return its value.
            return cookie.substring(name_assignment.length, cookie.length);
        }
    }
    return default_value;
}
