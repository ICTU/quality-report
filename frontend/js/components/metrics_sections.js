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
import {MetricsSection} from 'components/metrics_section.js';


class MetricsSections extends React.Component {
    constructor(props) {
        super(props);
        this.storage = this.props.storage === undefined ? localStorage : this.props.storage;
        this.onSort = this.onSort.bind(this);
        let state = {
            table_sort_column_name: 'id_format',
            table_sort_key: 'id_value',
            table_sort_ascending: true
        };
        const stored_sort_order = JSON.parse(this.storage.getItem('sort_order'));
        if (stored_sort_order !== null) {
            Object.assign(state, stored_sort_order);
        }
        this.state = state;
    }

    onSort(event) {
        event.preventDefault();
        const column_name = event.target.id;
        const state = {
            table_sort_column_name: column_name,
            table_sort_key: {id_format: "id_value", sparkline: "status_value", status_format: "status_value",
                             measurement: "measurement", norm: "norm", comment: "comment"}[column_name],
            // Change the sort order if the current sort column was clicked:
            table_sort_ascending: (column_name === this.state.table_sort_column_name) ?
                !this.state.table_sort_ascending : this.state.table_sort_ascending
        };
        this.setState(state);
        this.storage.setItem('sort_order', JSON.stringify(state));
    }

    sorted_metrics() {
        var metrics = this.props.metrics.slice();
        var sort_key = this.state.table_sort_key;
        var ascending = this.state.table_sort_ascending;
        metrics.sort(function(a, b) {
            if (ascending) {
                return (a[sort_key] < b[sort_key]) ? -1 : (a[sort_key] > b[sort_key]) ? 1 : 0;
            } else {
                return (a[sort_key] < b[sort_key]) ? 1 : (a[sort_key] > b[sort_key]) ? -1 : 0;
            }
        });
        return metrics;
    }

    render() {
        var metrics = this.sorted_metrics();
        var metrics_sections = [];
        if (this.props.show_one_table) {
            metrics_sections.push(
                <MetricsSection key="all" section="all" class_name="" title="Alle metrieken"
                            metrics={metrics} onSort={this.onSort}
                            table_sort_column_name={this.state.table_sort_column_name}
                            table_sort_ascending={this.state.table_sort_ascending}
                            on_hide_metric={this.props.on_hide_metric} />);
        } else {
            this.props.metrics_data["sections"].forEach(function(section) {
                var section_metrics = [];
                metrics.forEach(function(metric) {
                    if (metric["section"] === section["id"]) {
                        section_metrics.push(metric);
                    }
                });
                metrics_sections.push(
                    <MetricsSection key={section["id"]} section={section["id"]}
                                    latest_change_date = {section["latest_change_date"]}
                                    class_name="metric_section" title={section["title"]} metrics={section_metrics}
                                    table_sort_column_name={this.state.table_sort_column_name}
                                    table_sort_ascending={this.state.table_sort_ascending}
                                    onSort={this.onSort} on_hide_metric={this.props.on_hide_metric} />
                );
            }, this);
        }
        return (
            <div>
                {metrics_sections}
            </div>
        );
    }
}

export {MetricsSections};
