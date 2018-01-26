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

class HelpTableHeader extends React.Component {
    render() {
        return (
            <thead>
                <tr>
                    {this.props.headers.map((header, index) =>
                    <th id={header[0]} key={index}>
                        {header[1]}
                    </th>)}
                </tr>
            </thead>
        );
    }
}

class HelpTableBody extends React.Component {
    render() {
        return (
            <tbody>
                {this.props.children.map((row, index) =>
                    <tr key={index}>
                        {row.cells.map((cell, index) =>
                            <td className="report_cell" key={index}>{cell}</td>
                        )}
                    </tr>   
                )}
            </tbody>
        )
    }
}

class HelpTable extends React.Component {
    render() {
        return (
            <table className={"table" + (this.props.className ? " " + this.props.className : "")}>
                <HelpTableHeader {...this.props} />
                <HelpTableBody>
                    {this.props.children}
                </HelpTableBody>
            </table>
        );
    }
}

export {HelpTable};
