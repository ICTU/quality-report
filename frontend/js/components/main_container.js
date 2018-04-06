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

import {DashboardTable} from 'components/dashboard_table.js';
import {MetricsSections} from 'components/metrics_sections.js';
import {TrendGraphs} from 'components/trend_graphs.js';
import {Loader} from 'widgets/loader.js';
import {Help} from 'components/help.js';
import {format_date_time} from 'utils.js';


class Metrics extends React.Component {
    constructor(props) {
        super(props);
        let state = { report_dates: null };
        this.state = state;
    }

    dataRetrievedCallback = (report_dates) => {
        this.setState((state) => ({
            report_dates: report_dates
        }));
    }

    componentDidMount() {
        let self = this;
        $.get("json/dates.txt?v=" + Math.random(), "", self.dataRetrievedCallback);
    }
    render() {
        return (
            <div>
                {this.props.show_dashboard &&
                    <DashboardTable metrics_data={this.props.metrics_data}
                                    metrics={this.props.metrics} />
                }
                <MetricsSections metrics_data={this.props.metrics_data}
                                report_dates={this.state.report_dates}
                                metrics={this.props.metrics}
                                show_one_table={this.props.show_one_table}
                                on_hide_metric={this.props.on_hide_metric} />
            </div>
        )
    }
}

class Footer extends React.Component {
    render() {
        const report_date_time = format_date_time(...this.props.report_date);
        return (
            <footer className="text-center">
                <hr />
                <span>{this.props.report_title}, {report_date_time}</span>
                <br />
                <span>Gegenereerd door HQ versie {this.props.hq_version}</span>
            </footer>
        );
    }
}

class MainContainer extends React.Component {
    render() {        
        var tabs = {
            metrics_tab: <Metrics metrics_data={this.props.metrics_data}
                                  metrics={this.props.metrics}
                                  show_dashboard={this.props.show_dashboard}
                                  show_one_table={this.props.show_one_table}
                                  on_hide_metric={this.props.on_hide_metric} />,
            trend_tab: <TrendGraphs />,
            help_tab: <Help hq_version={this.props.metrics_data["hq_version"]} />
        };
        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col-md-12">
                        {tabs[this.props.tab]}
                    </div>
                </div>
                <Footer report_title={this.props.metrics_data["report_title"]} report_date={this.props.metrics_data["report_date"]} hq_version={this.props.metrics_data["hq_version"]} />
            </div>
        );
    }
}

export {MainContainer};
