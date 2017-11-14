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
import TimeAgo from 'react-timeago'
import dutchStrings from 'react-timeago/lib/language-strings/nl'
import buildFormatter from 'react-timeago/lib/formatters/buildFormatter'


class LastBuiltLabel extends React.Component {
    render() {
        const formatter = buildFormatter(dutchStrings);

        var year = this.props.latest_change_date ?
                   parseInt(this.props.latest_change_date.substr(0, 4), 10) : 0;

        if (year > 2000) {
            return (

                <span className="label label-default label_space">
                    gewijzigd <TimeAgo date={this.props.latest_change_date} formatter={formatter} />
                </span>
            );
        }
        return '';
    }
}

export {LastBuiltLabel};
