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

import $ from 'jquery';
import 'bootstrap/dist/js/bootstrap';
import React from 'react';
import ReactDOM from 'react-dom';

import 'bootstrap/dist/css/bootstrap.css';
import '../css/quality_report.css';

import {NavBar} from 'components/navbar.js';
import {MainContainer} from 'components/main_container.js';
import {Loader} from 'widgets/loader.js';


$(document).ready(create_dashboard);


class App extends React.Component {
    constructor() {
        super();
        let state = {
            metrics_data: 'loading', tab: 'metrics_tab', show_one_table: false, show_dashboard: true,
            metrics: [], filter: this.filter_all(true)
        };
        const stored_filter = JSON.parse(localStorage.getItem('filter'));
        if (stored_filter !== null) {
            let filter = Object.assign(this.filter_all(true), stored_filter['filter']);
            Object.assign(state, {filter: filter});
        }
        const stored_show_one_table = JSON.parse(localStorage.getItem('show_one_table'));
        if (stored_show_one_table !== null) {
            Object.assign(state, {show_one_table: stored_show_one_table});
        }
        const stored_show_dashboard = JSON.parse(localStorage.getItem('show_dashboard'));
        if (stored_show_dashboard !== null) {
            Object.assign(state, {show_dashboard: stored_show_dashboard});
        }
        this.state = state;
        this.onToggleOneTable = this.onToggleOneTable.bind(this);
        this.onToggleDashboard = this.onToggleDashboard.bind(this);
        this.onTab = this.onTab.bind(this);
        this.onFilter = this.onFilter.bind(this);
    }

    filter_all(state) {
        return {
            filter_all: state,
            filter_status_week: state,
            filter_color_red: state,
            filter_color_yellow: state,
            filter_color_green: state,
            filter_color_perfect: state,
            filter_color_grey: state,
            filter_color_missing_source: state,
            filter_color_missing: state
        };
    }

    componentDidMount() {
        var self = this;
        $.getJSON("json/metrics.json", "", function(metrics_data) {
            self.setState({
                metrics_data: metrics_data,
                metrics: self.filter(metrics_data, self.state.filter)
            });
            document.title = metrics_data["report_title"]
        });
    }

    onToggleOneTable() {
        this.setState(function(previous_state, props) {
            const next_state = !previous_state.show_one_table;
            localStorage.setItem('show_one_table', JSON.stringify(next_state));
            return {show_one_table: next_state};
        });
    }

    onToggleDashboard() {
        this.setState(function(previous_state, props) {
            const next_state = !previous_state.show_dashboard;
            localStorage.setItem('show_dashboard', JSON.stringify(next_state));
            return {show_dashboard: next_state};
        });
    }

    onTab(event) {
        event.preventDefault();
        this.setState({tab: event.target.id});
    }

    onFilter(event) {
        event.preventDefault();
        var self = this;
        const target = event.target.id;
        this.setState(function(previous_state, props) {
            let filter = Object.assign({}, previous_state.filter);  // Copy filter
            if (target === 'filter_all') {
                // User clicked "all metrics": turn all filters on or off, depending on its previous state
                filter = self.filter_all(!previous_state.filter['filter_all']);
            } else {
                // User clicked a specific filter: toggle it
                filter[target] = !filter[target];
                // Also adjust the "all metrics" menu item state accordingly
                filter['filter_all'] = true;
                filter['filter_all'] = !Object.values(filter).includes(false);
            }
            localStorage.setItem('filter', JSON.stringify({filter: filter}));
            return {filter: filter, metrics: self.filter(previous_state.metrics_data, filter)};
        });
    }

    filter(metrics_data, filter) {
        var metrics = [];
        const now = new Date();
        metrics_data['metrics'].forEach(function(metric) {
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
                                   tab={this.state.tab} />
                </div>
            );
        }
    }
}

function create_dashboard() {
    fix_navigation_links();
    ReactDOM.render(<App/>, document.getElementById('app'));
}

function fix_navigation_links() {
    // When clicking a navigation link, compensate for the fixed header.
    var shiftWindow = function() { scrollBy(0, -50) };
    if (location.hash) shiftWindow();
    window.addEventListener("hashchange", shiftWindow);
}
