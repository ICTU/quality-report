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

import React from 'react';
import Pie from 'react-chartjs-2';
import {STATUS_COLORS} from 'colors.js';


class DashboardTableRow extends React.Component {
    status_counts(metrics, section_id, statuses) {
        var section_metrics = metrics.filter(function(metric) {return metric["section"] === section_id});
        var counts = [];
        statuses.forEach(function(status) {
            counts.push(section_metrics.filter(function(metric) {return metric["status"] === status}).length);
        });
        return counts;
    }

    pie_options(section_id, section_title) {
        return {
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
                document.getElementById('section_' + section_id).scrollIntoView();
                window.scrollBy(0, -50);
            }
        };
    }

    pie_data(metrics, section_id) {
        return {
            datasets: [{
                data: this.status_counts(
                    metrics, section_id, ['perfect', 'green', 'yellow', 'red','grey', 'missing', 'missing_source']),
                backgroundColor: STATUS_COLORS,
                borderWidth: 1
            }],
            labels: ['Perfect', 'Goed', 'Bijna goed', 'Actie vereist', 'Technische schuld', 'Bron niet beschikbaar',
                     'Bron niet geconfigureerd']
        }
    }

    render() {
        var tds = [];
        this.props.cells.forEach(function(cell, index) {
            if (cell['section_id']) {  // Cell has a section id and thus should get a pie chart
                const pie_options = this.pie_options(cell['section_id'], cell['section_title']);
                const pie_data = this.pie_data(this.props.metrics, cell['section_id']);
                // The has "margin: auto" to make it center in a wide td
                tds.push(
                    <td key={index} colSpan={cell['colspan']} rowSpan={cell['rowspan']}
                        style={{backgroundColor: cell['bgcolor'], cursor: "pointer", verticalAlign: "middle"}}>
                        <div style={{width: this.props.pie_width, height: this.props.pie_height, margin: "auto"}}>
                            <Pie type='pie' data={pie_data} options={pie_options} legend={{display: false}}/>
                        </div>
                    </td>
                )
            } else {  // Empty or text-only cell
                tds.push(
                    <td key={index} colSpan={cell['colspan']} rowSpan={cell['rowspan']}
                        style={{backgroundColor: cell['bgcolor']}}>{cell['section_id']}
                    </td>
                )
            }
        }, this);
        return (
            <tr>
                {tds}
            </tr>
        )
    }
}

class DashboardTable extends React.Component {
    render() {
        let headers = [];
        const nr_rows = this.props.metrics_data["dashboard"]["rows"].length;
        let nr_columns = 0;
        this.props.metrics_data["dashboard"]["headers"].forEach(function(header, index) {
            nr_columns += header["colspan"];
            headers.push(
                <th key={index} colSpan={header["colspan"]} style={{textAlign: "center"}}>
                    {header["header"]}
                </th>
            );
        });
        // Calculate the size of the pie charts as percentage of the viewport, excluding margin
        const pie_width = Math.round(90 / nr_columns).toString() + 'vw';
        const pie_height = Math.round(80 / nr_rows).toString() + 'vh';
        let rows = [];
        this.props.metrics_data["dashboard"]["rows"].forEach(function(row, index) {
            rows.push(
                <DashboardTableRow key={index} cells={row} metrics={this.props.metrics}
                                   pie_width={pie_width} pie_height={pie_height} />
            );
        }, this);
        return (
            <div id="section_dashboard">
                <table className="table table-condensed table-bordered dashboard">
                    <thead>
                        <tr style={{color: "white", fontWeight: "bold", backgroundColor: "#2F95CF"}}>
                            {headers}
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        );
    }
}

export {DashboardTable, DashboardTableRow};
