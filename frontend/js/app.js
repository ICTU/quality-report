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

import {NavBar} from 'components/navbar.js';
import {MainContainer} from 'components/main_container.js';
import {Loader} from 'widgets/loader.js';


class App extends React.Component {
    constructor(props) {
        super(props);
        let state = {
            metrics_data: 'loading', tab: 'metrics_tab', show_one_table: false, show_dashboard: true,
            metrics: [], filter: this.filter_all(true, [])
        };
        const stored_filter = JSON.parse(this.props.storage.getItem('filter'));
        if (stored_filter !== null) {
            let filter = Object.assign(this.filter_all(true, []), stored_filter['filter']);
            Object.assign(state, {filter: filter});
        }
        const stored_show_one_table = JSON.parse(this.props.storage.getItem('show_one_table'));
        if (stored_show_one_table !== null) {
            Object.assign(state, {show_one_table: stored_show_one_table});
        }
        const stored_show_dashboard = JSON.parse(this.props.storage.getItem('show_dashboard'));
        if (stored_show_dashboard !== null) {
            Object.assign(state, {show_dashboard: stored_show_dashboard});
        }
        this.state = state;
        this.onToggleOneTable = this.onToggleOneTable.bind(this);
        this.onToggleDashboard = this.onToggleDashboard.bind(this);
        this.onTab = this.onTab.bind(this);
        this.onFilter = this.onFilter.bind(this);
        this.onHideMetric = this.onHideMetric.bind(this);
    }

    filter_all(state, hidden_metrics) {
        return {
            filter_all: state,
            filter_status_week: state,
            filter_color_red: state,
            filter_color_yellow: state,
            filter_color_green: state,
            filter_color_perfect: state,
            filter_color_grey: state,
            filter_color_missing_source: state,
            filter_color_missing: state,
            hidden_metrics: hidden_metrics
        };
    }

    componentDidMount() {
        let self = this;
        $.getJSON("json/metrics.json", "", function(metrics_data) {
            self.setState({
                metrics_data: metrics_data,
                metrics: self.filter(metrics_data, self.state.filter)
            });
            document.title = metrics_data["report_title"]
        });
    }

    onToggleOneTable() {
        let self = this;
        this.setState(function(previous_state, props) {
            const next_state = !previous_state.show_one_table;
            self.props.storage.setItem('show_one_table', JSON.stringify(next_state));
            return {show_one_table: next_state};
        });
    }

    onToggleDashboard() {
        let self = this;
        this.setState(function(previous_state, props) {
            const next_state = !previous_state.show_dashboard;
            self.props.storage.setItem('show_dashboard', JSON.stringify(next_state));
            return {show_dashboard: next_state};
        });
    }

    onTab(event) {
        event.preventDefault();
        this.setState({tab: event.target.id});
    }

    onFilter(event) {
        event.preventDefault();
        let self = this;
        const target = event.target.id;
        this.setState(function(previous_state, props) {
            let filter = Object.assign({}, previous_state.filter);  // Copy filter
            if (target === 'hidden_metrics') {
                // User clicked "hidden metrics": clear the list of hidden metrics
                filter.hidden_metrics = [];
            } else if (target === 'filter_all') {
                // User clicked "all metrics": turn all filters on or off, depending on its previous state but
                // keep the list of hidden metrics unchanged
                filter = self.filter_all(!previous_state.filter.filter_all, previous_state.filter.hidden_metrics);
            } else {
                // User clicked a specific filter: toggle it
                filter[target] = !filter[target];
                // Also adjust the "all metrics" menu item state accordingly
                filter.filter_all = true;
                filter.filter_all = !Object.values(filter).includes(false);
            }
            self.props.storage.setItem('filter', JSON.stringify({filter: filter}));
            return {filter: filter, metrics: self.filter(previous_state.metrics_data, filter)};
        });
    }

    onHideMetric(event) {
        event.preventDefault();
        let self = this;
        const target = event.target.id;
        this.setState(function(previous_state, props) {
            let filter = Object.assign({}, previous_state.filter); // Copy filter
            filter['hidden_metrics'].push(target);
            self.props.storage.setItem('filter', JSON.stringify({filter: filter}));
            return {filter: filter, metrics: self.filter(previous_state.metrics_data, filter)};
        });
    }

    filter(metrics_data, filter) {
        var metrics = [];
        const now = new Date();
        metrics_data['metrics'].forEach(function(metric) {
            if (filter['hidden_metrics'].indexOf(metric["id_value"]) > -1) {
                return;
            }
            if (!filter['filter_status_week']) {
                const d = metric['status_start_date'];
                const status_change_date = d.length > 0 ? new Date(d[0], d[1] - 1, d[2], d[3], d[4], d[5]) : new Date(1970, 1, 1);
                const seconds = parseInt((now - status_change_date)/1000, 10);
                if (seconds > 60 * 60 * 24 * 7) {
                    return;
                }
            }
            if (filter['filter_color_' + metric["status"]]) {
                metrics.push(metric);
            }
        });
        return metrics
    }

    render() {
        if (this.state.metrics_data === 'loading') {
            return (
                <div className="container-fluid">
                    <div className="row">
                        <div className="col-md-12">
                            <Loader/>
                        </div>
                    </div>
                </div>
            )
        } else {
            return (
                <div>
                    <NavBar sections={this.state.metrics_data['sections']}
                            report_title={this.state.metrics_data["report_title"]}
                            report_date_time={this.state.metrics_data["report_date"]}
                            show_dashboard={this.state.show_dashboard}
                            show_one_table={this.state.show_one_table}
                            on_toggle_dashboard={this.onToggleDashboard}
                            on_toggle_one_table={this.onToggleOneTable}
                            tab={this.state.tab} on_tab={this.onTab}
                            filter={this.state.filter}
                            on_filter={this.onFilter} />
                    <MainContainer metrics_data={this.state.metrics_data}
                                   metrics={this.state.metrics}
                                   show_one_table={this.state.show_one_table}
                                   show_dashboard={this.state.show_dashboard}
                                   on_hide_metric={this.onHideMetric}
                                   tab={this.state.tab} />
                </div>
            );
        }
    }
}

export {App};
