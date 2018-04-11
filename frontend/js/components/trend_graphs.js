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

import React from 'react';
import Line from 'react-chartjs-2';

import 'chartjs-plugin-stackedline100.js';
import {Loader} from 'widgets/loader.js';
import {STATUS_COLORS} from 'colors.js';


class TrendGraph extends React.Component {
    line_options(title, relative) {
        return {
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
    }

    render() {
        return (
            <div className="meta_metrics_history_graph" id={this.props.id}>
                <Line type='line' data={this.props.history_data}
                      options={this.line_options(this.props.title, this.props.relative)} />
            </div>
        )
    }
}

class TrendGraphs extends React.Component {
    constructor() {
        super();
        this.state = {history_data: 'loading'};
    }

    componentDidMount() {
        var self = this;
        $.getJSON("json/meta_history.json", "", function(history_data) {
            self.setState({history_data: self.line_data(TrendGraphs.parse_history_json(history_data))});
        });
    }

    static parse_history_json(history_json) {
        var datasets = [[], [], [], [], [], [], [], []];
        history_json.forEach(function(value) {
            datasets[0].push(new Date(value[0][0], value[0][1], value[0][2], value[0][3], value[0][4], value[0][5]));
            for (var index = 1; index < 8; index++) {
                datasets[index].push(value[1][index - 1]);
            }
        });
        return datasets;
    }

    line_data(datasets) {
        var colors = STATUS_COLORS;
        return {
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
            ]
         }
    }

    render() {
        if (this.state.history_data === 'loading') {
            return <Loader/>;
        } else {
            return (
                <div>
                    <TrendGraph id="meta_metrics_history_absolute_graph"
                                title="Aantal metrieken per status" relative={false}
                                history_data={this.state.history_data} />
                    <TrendGraph id="meta_metrics_history_relative_graph"
                                title="Percentage metrieken per status" relative={true}
                                history_data={this.state.history_data} />
                </div>
            );
        }
    }
}

export {TrendGraph, TrendGraphs};
