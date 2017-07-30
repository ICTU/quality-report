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
import {format_date_time} from 'utils.js';
import {Menus} from 'components/menu.js';


class NavBar extends React.Component {
    report_date_time_class() {
        let report_date_time = new Date(this.props.report_date_time[0], this.props.report_date_time[1] - 1,
                                        this.props.report_date_time[2], this.props.report_date_time[3],
                                        this.props.report_date_time[4])
        var now = new Date();
        var seconds = parseInt((now - report_date_time)/1000, 10);
        if (seconds > 60 * 60) {
            return seconds > 60 * 60 * 24 ? 'very_old' : 'old';
        } else {
            return ''
        }
    }

    render() {
        const report_date_time = format_date_time(...this.props.report_date_time)
        return (
            <nav className="navbar navbar-default navbar-fixed-top">
                <div className="container-fluid">
                    <div className="navbar-header">
                        <button type="button" className="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                            <span className="sr-only">Toggle navigation</span>
                            <span className="icon-bar"></span>
                            <span className="icon-bar"></span>
                            <span className="icon-bar"></span>
                        </button>
                        <a className="navbar-brand" href="#">{this.props.report_title}</a>
                    </div>
                    <div className="collapse navbar-collapse">
                        <Menus {...this.props} />
                        <p className="navbar-text pull-right">
                            Rapportage van <span className={this.report_date_time_class()}>{report_date_time}</span>
                        </p>
                    </div>
                </div>
            </nav>
        );
    }
}

export {NavBar};
