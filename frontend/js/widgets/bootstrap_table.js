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
    buildReportHeaders(headers) {
        return [<th key={0} />, 
                <th id={headers[1][0]} key={1} width="90px" onClick={this.props.onSort} style={{cursor: "pointer"}}>
                    {headers[1][1]}<Caret show={headers[1][0] === this.props.table_sort_column_name}
                            table_sort_ascending={this.props.table_sort_ascending}/>
                </th>
            ].concat(
                headers.slice(2).map(
                    (header, index) =>
                        <th id={header[0]} key={index+2} onClick={this.props.onSort} style={{cursor: "pointer"}}>
                            {header[1]}<Caret show={header[0] === this.props.table_sort_column_name}
                                            table_sort_ascending={this.props.table_sort_ascending}/>
                        </th>
            ));
    }

    buildHelpHeaders(headers) {
        return headers.map((header, index) =>
            <th id={header[0]} key={index}>
                {header[1]}
            </th>);
    }

    render() {
        var headers;
        if (this.props.headers[0][0]==="") {
            headers = this.buildReportHeaders(this.props.headers);
        } else {
            headers = this.buildHelpHeaders(this.props.headers)
        }
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

    buildTdCells(children) {
        var rows = [];
        children.forEach(function(row) {
            rows.push(row['cells'].map((cell, index) => 
                cell.hasOwnProperty('__html') ?
                    <td className="report_cell" key={index} dangerouslySetInnerHTML={cell}></td> : 
                    <td className="report_cell" key={index}>{cell}</td>
            ));
        });
        return rows;
    }

    buildRowsOfReport(rows) {
       return rows.map((row, index) => 
            {
                var hasDetailPane = !(!(this.props.children[index]['comment']));
                var chdId = this.props.children[index]['id'];

                var toggleButton = hasDetailPane ?
                    <DetailToggleButton key={chdId} data_target={'#' + chdId + '_details'} /> :
                    <button type="button" key={chdId} className="btn glyphicon glyphicon-chevron-right disabled" />
                
                var ret = [
                    <tr key={chdId} className={this.props.children[index]['className']}>
                        <td>{toggleButton}</td>
                        {row}
                    </tr>]

                if (hasDetailPane) {
                    ret.push(<DetailPane key={chdId + 'p'} metric_detail={this.props.children[index]} />);
                }
                return ret;
            });
    }

    buildRowsOfHelp(rows) {
        return rows.map((row, index) => 
        <tr key={this.props.children[index]['id']}>
            {row}
        </tr>);
    }

    render() {
        var rows = this.buildTdCells(this.props.children);

        var table_rows;
        if(this.props.children[0]['comment'] === undefined) {
            table_rows = this.buildRowsOfHelp(rows)
        } else {
            table_rows = this.buildRowsOfReport(rows);
        }

        return (
            <tbody>
                {table_rows}
            </tbody>
        )
    }
}

class DetailPane extends React.Component {
    render() {
        var cls = this.props.metric_detail['className'];
        return (
            <tr id={this.props.metric_detail['id'] + '_details'} className={cls + " collapse"}>
                <td className="detail_pane" colSpan="6">
                    <div className="panel panel-default">
                        <h4 className="panel-heading">Commentaar</h4>
                        <div className="panel-body">{this.props.metric_detail['comment']}</div>
                    </div>
                </td>
            </tr>
        );
    }
}

class DetailToggleButton extends React.Component {
    state = {
        isExpanded: false
    }
    
    handleClick = () => this.setState({ isExpanded: !this.state.isExpanded});
    
    render() {
        return (
            <button type="button" 
                className={"btn glyphicon can_expand" + 
                        (this.state.isExpanded ? " glyphicon-chevron-down" : " glyphicon-chevron-right")}

                onClick={this.handleClick} 
                data-toggle="collapse" 
                data-target={this.props.data_target}>
            </button>
        );
    }
}

class BootstrapTable extends React.Component {
    render() {
        return (
            <table className={"table" + (this.props.className ? " " + this.props.className : "")}>
                <BootstrapTableHeader {...this.props} />
                <BootstrapTableBody>
                    {this.props.children}
                </BootstrapTableBody>
            </table>
        );
    }
}

export {BootstrapTable, BootstrapTableHeader, BootstrapTableBody, Caret};
