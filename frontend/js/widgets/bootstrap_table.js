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
            rows.push(row['cells'].map((cell, index) => cell.hasOwnProperty('__html') ?
                <td key={index} dangerouslySetInnerHTML={cell}></td> : <td key={index}>{cell}</td>));
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


export {BootstrapTable, BootstrapTableHeader, BootstrapTableBody};
