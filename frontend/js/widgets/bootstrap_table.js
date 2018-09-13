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
import {DetailPane} from './detail_pane';

class Caret extends React.Component {
    render() {
        if (!this.props.show) {
            return null;
        }
        return (
            <span> {this.props.table_sort_ascending ? "▴" : "▾"}</span>
        );
    }
}

class BootstrapTableHeader extends React.Component {
    buildReportHeaders(headers) {
        return [<th key={0} />,
                <th id={headers[1][0]} key={1} width="90px" onClick={this.props.onSort} style={{cursor: "pointer"}}>
                    {headers[1][1]}<Caret show={headers[1][0] === this.props.table_sort_column_name}
                            table_sort_ascending={this.props.table_sort_ascending}/>
                </th>
            ].concat(
                headers.slice(2).map(
                    (header, index) =>
                        <th id={header[0]} key={index+2} onClick={this.props.onSort}
                            style={{cursor: "pointer", minWidth: "90px"}}>
                            {header[1]}<Caret show={header[0] === this.props.table_sort_column_name}
                                              table_sort_ascending={this.props.table_sort_ascending}/>
                        </th>
            ));
    }

    render() {
        return (
            <thead>
                <tr>
                    {this.buildReportHeaders(this.props.headers)}
                </tr>
            </thead>
        );
    }
}

class BootstrapTableRow extends React.Component {
    state = {
        is_expanded: false
    }

    handleClick = () => this.setState((state) => ({is_expanded: !state.is_expanded}));

    splitOnLinks(str) {
        var ret = [];
        var regexPatern = /{\s*'href':\s*(\S+),\s*'text':\s*([^}]+)\s*}/i
        var pos = str.search(regexPatern);
        
        if(pos >= 0) {
            ret.push(str.substring(0, pos));
            var p1 = str.indexOf("}") + 1;
            var hrf = str.substring(pos, p1);
            var txt = hrf.replace(regexPatern, '$1}$2');
            var href_text = txt.split('}');
            ret.push(<a href={href_text[0].slice(1,-1)} target="_blank">{href_text[1].slice(1,-1)}</a>);
            ret = ret.concat(this.splitOnLinks(str.substring(p1)));
        } else {
            ret.push(str);
        }
        return ret;
    }

    formatCellText (cell) {
        if (typeof(cell) === 'string') {
            return this.splitOnLinks(cell);
        } else {
            return cell;
        }
    }
    
    makeRowCells(row) {
        return row['cells'].map((cell, index) => 
                    <td className="report_cell" key={index}>
                        {this.formatCellText(cell)}
                    </td>
                );
    }

    renderDetailPane(chdId) {
        var hasExtraInfo =  (this.props.row['extra_info'] 
                                    && !(Object.keys(this.props.row['extra_info']).length === 0));

        return <DetailPane key={chdId + 'p'} col_span={this.props.col_span} has_extra_info={hasExtraInfo} 
                    report_dates={this.props.report_dates} is_expanded={this.state.is_expanded}
                    on_hide_metric={this.props.on_hide_metric} metric_detail={this.props.row} />
    }

    render() {
        var chdId = this.props.row['id'];
        let icon = this.state.is_expanded ? "➖" : "➕";
        return (
            <React.Fragment>
                <tr key={chdId} className={this.props.row['className']} style={{verticalAlign: "top"}}>
                    <td>
                        <button type="button" 
                            className="btn can_expand"
                            onClick={this.handleClick} 
                            data-toggle="collapse" 
                            data-target={'#' + chdId + '_details'}>
                            {icon}
                        </button>
                    </td>
                    {this.makeRowCells(this.props.row)}
                </tr>
                {this.renderDetailPane(chdId)}
            </React.Fragment>
        );
    }
}

class BootstrapTableBody extends React.Component {
    buildRowsOfReport(children) {

        return children.map((data_row, index) => 
            <BootstrapTableRow key={index} col_span={this.props.col_span}
                               row={data_row}
                               report_dates={this.props.report_dates} 
                               on_hide_metric={this.props.on_hide_metric}/>);
    }

    render() {
        return (
            <tbody>
                {this.buildRowsOfReport(this.props.children)}
            </tbody>
        )
    }
}

class BootstrapTable extends React.Component {
    render() {
        return (
            <table className={"table" + (this.props.className ? " " + this.props.className : "")}>
                <BootstrapTableHeader {...this.props} />
                <BootstrapTableBody report_dates={this.props.report_dates} 
                                    col_span={this.props.headers ? this.props.headers.length : 0} on_hide_metric={this.props.on_hide_metric}>
                    {this.props.children}
                </BootstrapTableBody>
            </table>
        );
    }
}

export {BootstrapTable};
