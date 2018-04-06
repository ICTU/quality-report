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
import {Line} from 'react-chartjs-2';

class HistoryChart extends React.Component {
    constructor(props) {
        super(props);
        let state = { chart_data: null };
        this.state = state;
    }

    getChartData() {
        let self = this;
        $.get("json/" + this.props.stable_metric_id.replace(' ', '_') + ".txt?v=" + Math.random(), "", function(chart_data) {
            self.setState((state) => ({
                chart_data: chart_data
            }));
        });
    }

    getOptions() {
        return ({
            legend: {
                display: false
            },
            title: {
                display: true,
                text: this.props.title
            },
            scales: {
                xAxes: [{
                    type: 'time',
                    time: {
                        unit: 'day',
                        tooltipFormat: 'll HH:mm'
                    },
                    scaleLabel: {
                        display: true,
                        labelString: 'datum'
                    }
                }],
                yAxes: [{
                    zeroLineBorderDashOffset: 1,
                    scaleLabel: {
                        display: true,
                        labelString: this.props.unit
                    }
                }]
            }
        });
    }
    
    render() {
        if(!this.props.is_expanded) {
           return null;
        } else if (!this.state.chart_data) {
            this.getChartData()
        }

        const data = {
            labels: (this.props.report_dates) ? this.props.report_dates.split(',') : [],
            datasets: [
                {
                    fill: false,
                    spanGaps: false,
                    lineTension: 0,
                    borderColor: "rgba(255,7,7,0.4)",
                    borderWidth: 2,
                    radius: 1,
                    data: (this.state && this.state.chart_data) ? this.state.chart_data.split(',').map(x => parseInt(x, 10)) : []
                }]
        }

        return (
            <Line
                data={data}
                options={this.getOptions()}
            />
        )
    }
}

export {HistoryChart};