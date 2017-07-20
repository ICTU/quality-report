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


class Caret extends React.Component {
    render() {
        if (!this.props.show) {
            return null;
        }
        var caret = <span className="caret"></span>;
        if (this.props.table_sort_ascending) {
            caret = <span className="dropup">{caret}</span>;
        }
        return caret;
    }
}

class BootstrapTableHeader extends React.Component {
    render() {
        const headers = this.props.headers.map(
            (header, index) =>
                <th id={header[0]} key={index} onClick={this.props.onSort} style={{cursor: "pointer"}}>
                    {header[1]}<Caret show={header[0] === this.props.table_sort_column_name}
                                      table_sort_ascending={this.props.table_sort_ascending}/>
                </th>
        );
        return (
            <thead>
                <tr>
                    {headers}
                </tr>
            </thead>
        );
    }
}

class BootstrapTableBody extends React.Component {
    render() {
        var rows = [];
        this.props.children.forEach(function(row) {
            rows.push(row['cells'].map((cell, index) => <td key={index} dangerouslySetInnerHTML={cell}></td>));
        });
        const table_rows = rows.map((row, index) => <tr key={index}
                                                        className={this.props.children[index]['className']}>{row}</tr>);
        return (
            <tbody>
                {table_rows}
            </tbody>
        )
    }
}

class BootstrapTable extends React.Component {
    render() {
        return (
            <table className="table">
                <BootstrapTableHeader {...this.props} />
                <BootstrapTableBody>
                    {this.props.children}
                </BootstrapTableBody>
            </table>
        );
    }
}

class MetricsTable extends React.Component {
    sparkline(metric) {
        return '<img width="100px" height="25px" src="img/' + metric["id_format"] + '.svg"/>';
    }

    render() {
        const has_comments = this.props.metrics.some(function(metric) {
            return metric["comment"];
        });
        var table_rows = [];
        this.props.metrics.forEach(function(metric) {
            var cells = [{__html: metric["id_format"]}, {__html: this.sparkline(metric)},
                         {__html: metric["status_format"]}, {__html: metric["measurement"]},
                         {__html: metric["norm"]}];
            if (has_comments) {
                cells.push({__html: metric["comment"]});
            }
            table_rows.push({cells: cells, className: metric['status'] + '_metric'});
        }, this);
        var headers = [["id_format", "Id"], ["sparkline", "Trend"], ["status_format", "Status"],
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
