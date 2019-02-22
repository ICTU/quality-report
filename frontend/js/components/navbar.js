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
        let title = this.props.report_title;
        title = title.length > 40 ? title.substr(0, 40) + "..." : title;
        return (
            <nav className="navbar navbar-expand-sm navbar-light bg-light fixed-top">
                <a className="navbar-brand" href="#">{title}</a>
                <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav"
                        aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                     <span className="navbar-toggler-icon"></span>
                </button>
                <div className="collapse navbar-collapse" id="navbarNav">
                    <Menus {...this.props} />
                    <span className="navbar-text">
                        Rapportage van <span className={this.report_date_time_class()}>{report_date_time}</span>
                    </span>
                </div>
            </nav>
        );
    }
}

export {NavBar};
