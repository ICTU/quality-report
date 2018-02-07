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
import {BootstrapTable} from 'widgets/bootstrap_table.js';


class MetricsTable extends React.Component {
    sparkline(metric) {
        return <img width="100px" height="25px" src={"img/" + metric["id_format"] + ".svg"}/>;
    }

    bgColorClassName(metric) {
        return metric["status"] + "_metric";
    }
    
    id_format(metric) {
        return (<div className="btn-group"><span className={this.bgColorClassName(metric)}>{metric["id_format"]}</span></div>);
    }
    
    stuffTableRows(has_comments) {
        var table_rows = [];
        this.props.metrics.forEach(function (metric) {
            var cells = [this.id_format(metric), this.sparkline(metric),
            { __html: metric["status_format"] }, { __html: metric["measurement"] },
            { __html: metric["norm"] }];
            if (has_comments) {
                cells.push({ __html: metric["comment"] });
            }
            table_rows.push({
            cells: cells,
                className: this.bgColorClassName(metric), id: metric["id_value"],
                name: metric['name'], extra_info: metric["extra_info"]
            });
        }, this);
        return table_rows;
    }

    render() {
        const has_comments = this.props.metrics.some(function(metric) {
            return metric["comment"];
        });
        var table_rows = this.stuffTableRows(has_comments);
        var headers = [["",""], ["id_format", "Id"], ["sparkline", "Trend"], ["status_format", "Status"],
                       ["measurement", "Meting"], ["norm", "Norm"]];
        if (has_comments) {
            headers.push(["comment", "Comment"]);
        }
        return (
            <BootstrapTable headers={headers} onSort={this.props.onSort}
                              table_sort_column_name={this.props.table_sort_column_name}
                              table_sort_ascending={this.props.table_sort_ascending}>
                {table_rows}
            </BootstrapTable>
        );
    }
}

export {MetricsTable};
