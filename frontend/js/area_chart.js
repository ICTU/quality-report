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
import '../js/chartjs-plugin-stackedline100.js';

function draw_area_chart(doc, element_id, datasets, colors, title, relative) {
    var canvas = doc.getElementById(element_id);
    var chart = new Chart(canvas, {
        type: 'line',
        data: {
            labels: datasets[0],
            datasets: [
                {
                    label: "Perfect",
                    fill: true,
                    pointRadius: 0,
                    backgroundColor: colors[0],
                    data: datasets[1]
                },
                {
                    label: "Goed",
                    fill: true,
                    pointRadius: 0,
                    backgroundColor: colors[1],
                    data: datasets[2]
                },
                {
                    label: "Bijna goed",
                    fill: true,
                    pointRadius: 0,
                    backgroundColor: colors[2],
                    data: datasets[3]
                },
                {
                    label: "Actie vereist",
                    fill: true,
                    pointRadius: 0,
                    backgroundColor: colors[3],
                    data: datasets[4]
                },
                {
                    label: "Technische schuld",
                    fill: true,
                    pointRadius: 0,
                    backgroundColor: colors[4],
                    data: datasets[5]
                },
                {
                    label: "Bron niet beschikbaar",
                    fill: true,
                    pointRadius: 0,
                    backgroundColor: colors[5],
                    data: datasets[6]
                },
                {
                    label: "Bron niet geconfigureerd",
                    fill: true,
                    pointRadius: 0,
                    backgroundColor: colors[6],
                    data: datasets[7]
                }
            ]},
        options: {
            title: {
                text: title,
                display: true,
                fontSize: 14
            },
            scales: {
                xAxes: [{
                    type: 'time',
                    time: {minUnit: 'week'}
                }],
                yAxes: [{
                    stacked: true
                }]
            },
            animation: {
                duration: 0
            },
            plugins: {
                stackedline100: {enable: relative}
            }
        }
    });
    return chart;
}

export {draw_area_chart};
