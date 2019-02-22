/* Copyright 2012-2019 Ministerie van Sociale Zaken en Werkgelegenheid
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
import {HistoryChart} from './history_chart';

class DetailPane extends React.Component {
    renderExtraInfoPanel(extra_info) {
        return this.props.has_extra_info ? <TablePanel extra_info={extra_info}/> : '';
    }

    renderDetailedContent() {
        var stable_id = this.props.metric_detail['stable_id'] ? this.props.metric_detail['stable_id'].replace(/ /g, "_") : '';
        return(
            <tr>
                <td colSpan={3}>
                    <div className="row">
                        <div className="col-sm-1" />
                        <div className="col-sm-5">
                            <HistoryChart title={this.props.metric_detail['name']} 
                                            unit={this.props.metric_detail['unit']} 
                                            is_expanded = {this.props.is_expanded}
                                            report_dates={this.props.report_dates} 
                                            stable_metric_id = {stable_id}/>
                        </div>
                        <div className="col-sm-1" />
                        <div className="col-sm-4">
                            {this.renderExtraInfoPanel(this.props.metric_detail['extra_info'])}
                        </div>
                        <div className="col-sm-1" />
                    </div>
                </td>
            </tr>);
    }

    render() {
        var cls = this.props.metric_detail['className'];
        return (
            <tr id={this.props.metric_detail['id'] + '_details'} className={cls + " collapse"}>
                <td className="detail_pane container" colSpan={this.props.col_span}>
                    <table className={cls + " table"}>
                        <tbody className={cls}>
                            <tr>
                                <td colSpan={3}>
                                    <ActionPanel metric_id={this.props.metric_detail['id']} onClick={this.props.on_hide_metric} />
                                </td>
                            </tr>
                            {this.renderDetailedContent()}
                        </tbody>
                    </table>
                </td>
            </tr>
        );
    }
}

class ActionPanel extends React.Component {
    componentDidMount() {
        $(function () {
            $('[data-toggle="tooltip"]').tooltip()
        })
    }
    render() {
        return (
            <div className="btn-group" role="group" aria-label="Action Panel">
                <button type="button" id={this.props.metric_id} className="btn btn-default" data-toggle="tooltip" data-placement="right"
                        title="Gebruik het Toon-menu om verborgen metrieken weer zichtbaar te maken." onClick={this.props.onClick}>
                        Verberg deze metriek
                </button>
            </div>
        );
    }
}

class TablePanel extends React.Component {
    constructor(props) {
        super(props);
        let state = { headers: this.props.extra_info.headers, data: this.props.extra_info.data, sort_column: '', sort_asc: true };
        this.state = state;
    }

    renderHeaderCell(header_text, header_key, index) {
        if (header_text[0] !== '_') {
            var sorting_char = this.getSortingIndicator(header_key);
            var header = header_text.split('__');
            if (header.length>1) {
                return <th key={index} onClick={() => this.sortBy(header_key)} className={header[1] + " detail-table-header"}>
                            {header[0] + sorting_char}
                        </th>
            }
            return <th key={index} onClick={() => this.sortBy(header_key)} className="detail-table-header">
                        {header[0] + sorting_char}
                    </th>
        }
        return null;
    }

    getSortingIndicator(header_key) {
        return this.state.sort_column === header_key ? (this.state.sort_asc ? '▾' : '▴') : ' ';
    }

    compareBy(key, sort_order) {
        return function (a, b) {
            let aField = a[key];
            let bField = b[key];
            if (Array.isArray(aField)) {
                aField = aField[0];
                bField = bField[0];
            }
            if (aField !== null && typeof aField === 'object') {
                aField = aField['text'];
                bField = bField['text'];
            }
            let sortSign = sort_order ? 1 : -1;
            return (aField >= bField) ? sortSign : -sortSign;
        };
    }

    sortBy(key) {
        var sort_order = true;
        if (this.state.sort_column === key) {
            sort_order = !this.state.sort_asc
        }
        let arrayCopy = [...this.state.data];
        arrayCopy.sort(this.compareBy(key, sort_order));
        this.setState({data: arrayCopy, sort_asc: sort_order, sort_column: key});
    }

    renderHeader(headers) {
        if (headers) {
            var header_keys = Object.keys(headers);
            return (
                <thead>
                    <tr>
                        {Object.values(headers).map((col, index) => {
                            return this.renderHeaderCell(col, header_keys[index], index);
                        })}
                    </tr>
                </thead>);
        } else {
            return <thead />;
        }
    }

    formatLink(cell_content) {
        if (cell_content.hasOwnProperty('href')) {
            return <a href={cell_content.href} target="_blank">{cell_content.text || cell_content.href}</a>
        }
        return cell_content;
    }

    formatCell(cell_content) {
        if (cell_content) {
            if (Array.isArray(cell_content)) {
                return cell_content.map(
                    (c, i, content) => content[i+1] ? [this.formatLink(c), ', '] : this.formatLink(c)
                );
            } else {
                return  this.formatLink(cell_content);
            }
        }
        return cell_content;
    }

    getFormatColumns(headers) {
        var format_columns = [];

        for (var k in headers)
        {
            if(headers[k][0] === '_')
            {
            	format_columns.push(k);
            }
        }
        return format_columns;
    }

    applyClassNames(row, format_columns, headers) {
        var classNames = [];

        for(var h in format_columns)
        {
            if (row[format_columns[h]] === true || row[format_columns[h]] === "true") {
                classNames.push(headers[format_columns[h]].substr(1));
            }
        }
        return classNames;
    }

    renderRowCell(header_text, val, index) {
        if(header_text[0] !== '_') {
            var header = header_text.split('__');
            if (header.length>1) {
                return <td key={header[0] + "_" + index} className={header[1]}>{this.formatCell(val)}</td>;
            }
            return <td key={header[0] + "_" + index}>{this.formatCell(val)}</td>;
        }
        return null;
    }

    renderTableBody(headers, data) {
        const columns = Object.keys(headers);
        var rows;
        var format_columns = this.getFormatColumns(headers);

        if(headers && data) {
            rows = data.map((row, index) => {

                var classNames = this.applyClassNames(row, format_columns, headers);
                var clsName = 'detail-row-default';
                if (classNames.length > 0) {
                    clsName = classNames.join(' ');
                }

                return (
                <tr key={index} className={clsName}>
                    {columns.map((col) => {
                        return this.renderRowCell(headers[col], row[col], index);
                    })}
                </tr>
                );
            })
        }
        return (
            <tbody>
                {rows}
            </tbody>
        );
    }

    render() {
        return (
            <div className="panel panel-default">
                <h4 className="panel-heading">{this.props.extra_info["title"]}</h4>
                <div className="panel-body">
                    <table className="table-striped">
                        {this.renderHeader(this.state.headers)}
                        {this.renderTableBody(this.state.headers, this.state.data)}
                    </table>
                </div>
            </div>
        );
    }
}

export {DetailPane};
