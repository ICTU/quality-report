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


function create_sections(sections) {
    var html_sections = ['<section id="section_all" style="display:none"><div id="table_all"></div></section>'];
    sections.forEach(function(section) {
        var id = section["id"], title = section["title"], subtitle = section["subtitle"];
        var html_section = '<section id="section_' + id + '"><div class="page-header="><h1>' + title;
        if (subtitle) {
            html_section += ' <small>' + subtitle + '</small>';
        };
        html_section += '</h1></div><div id="table_' + id + '"></div></section>';
        html_sections.push(html_section);
    });
    return html_sections.join("");
}

function create_navigation_menu_items(sections) {
    var menu_items = [];
    sections.forEach(function(section) {
        var id = section["id"], title = section["title"];
        var menu_item = '<li><a class="link_section_' + id + '" href="#section_' + id + '">' + title + '</a></li>';
        menu_items.push(menu_item);
    });
    return menu_items.join("");
}

function status_counts(metrics, section_id, statuses) {
    var section_metrics = metrics.filter(function(metric) {return metric[1] === section_id});
    var counts = [];
    statuses.forEach(function(status) {
        counts.push(section_metrics.filter(function(metric) {return metric[2] === status}).length);
    });
    return counts;
}

export {create_sections, create_navigation_menu_items, status_counts};
