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
import {MetricsTable} from 'components/metrics_table.js';
import {LastBuiltLabel} from 'components/last_built_label.js';

class MetricsSection extends React.Component {
    render() {
        return (
            <section key={this.props.section} id={"section_" + this.props.section}
                     style={{display: this.props.display}} className={this.props.class_name}>
                <div className="page-header">
                    <h1>
                        {this.props.title}
                        <small className="align-top">
                            <LastBuiltLabel latest_change_date={this.props.latest_change_date}/>
                        </small>
                    </h1>
                </div>
                <div className="metric_table" id={"table_" + this.props.section}>
                    <MetricsTable key={this.props.section} metrics={this.props.metrics}
                                  report_dates={this.props.report_dates}
                                  table_sort_column_name={this.props.table_sort_column_name}
                                  table_sort_ascending={this.props.table_sort_ascending}
                                  on_hide_metric={this.props.on_hide_metric}
                                  onSort={this.props.onSort}/>
                </div>
            </section>
        );
    }
}
export {MetricsSection};
