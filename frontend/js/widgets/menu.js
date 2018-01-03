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


class Menu extends React.Component {
    render() {
        if (this.props.hide) {
            return null;
        }
        return (
            <li className="dropdown">
                <a id={this.props.id} className="dropdown-toggle" role="button"
                   data-toggle="dropdown" href="#" aria-haspopup="true" aria-expanded="false">
                    {this.props.title}<span className="caret"></span>
                </a>
                <ul className="dropdown-menu" aria-labelledby={this.props.id}>
                    {this.props.children}
                </ul>
            </li>
        )
    }
}

class MenuItem extends React.Component {
    render() {
        if (this.props.hide) {
            return null;
        }
        var icon;
        if (this.props.icon) {
            icon = 'glyphicon glyphicon-' + this.props.icon;
        } else {
            icon = this.props.check ? 'glyphicon glyphicon-ok' : '';
        }
        var disabled = this.props.disabled ? 'disabled' : '';
        return (
            <li className={disabled}>
                <a className={this.props.className} id={this.props.id} href={"#" + this.props.href}
                   onClick={this.props.onClick} data-toggle={this.props.data_toggle}>
                    <span aria-hidden="true" className={icon}></span> {this.props.title}
                </a>
            </li>
        );
    }
}


export {Menu, MenuItem};
