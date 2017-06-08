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

import Chart from 'chart.js';

function draw_pie_chart(window, doc, section_id, section_title, data, colors, labels, width, height) {
    var piechart_canvas = doc.getElementById('section_summary_chart_' + section_id);
    if (piechart_canvas === null) {
        // Not all sections have a pie chart, e.g. the meta metrics (MM) section.
        return;
    };
    piechart_canvas.parentNode.style.width = width;
    piechart_canvas.parentNode.style.height = height;
    var piechart = new Chart(piechart_canvas, {
        type: 'pie',
        data: {
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 1,
            }],
            labels: labels,
        },
        options: {
            title: {
                display: true,
                text: section_title,
                fontSize: 14,
                fontStyle: 'normal',
                padding: 5
            },
            legend: {
                display: false
            },
            animation: {
                duration: 0
            },
            responsive: true,
            maintainAspectRatio: false,
            onClick: function(event, array) {
                doc.getElementById('section_' + section_id).scrollIntoView();
                window.scrollBy(0, -50);
            }
        }
    });
    return piechart;
}

export {draw_pie_chart};
