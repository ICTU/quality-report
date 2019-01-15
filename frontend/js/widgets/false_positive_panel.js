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

class FalsePositivePanel extends React.Component {
    constructor(props) {
        super(props);
        var _isFalsePositive = props.false_positive === 'True';
        this.state = {
            isFalsePositive: _isFalsePositive,
            label: _isFalsePositive ? "Tonen" : "Verbergen",
            reason: props.false_positive_reason
        }
        this.handleReasonChange = this.handleReasonChange.bind(this);
    }
    
    componentDidMount() {
        $(function () {
            $('[data-toggle="tooltip"]').tooltip()
        })
    }

    // If changes were made in between a HQ build
    componentDidUpdate(prevProps) {
        if(prevProps.false_positive_list !== this.props.false_positive_list && this.props.false_positive_list) {
            var item = this.props.false_positive_list[this.props.warning_id];
            if(item) {
                this.setState({
                    isFalsePositive: true,
                    label: 'Tonen',
                    reason: item.reason
                });
            }
            else {
                this.setState({
                    isFalsePositive: false,
                    label: 'Verbergen',
                    reason: ''
                });
            }
        }
    }

    setFalsePositive = () => {
        var self = this;
        if (self.state.isFalsePositive === true) {
            fetch(self.props.false_positive_api_url + 'api/fp/' + self.props.warning_id, {
                method: 'delete'
            }).then(function (response) {
                if (response.ok) {
                    self.setState({
                        isFalsePositive: false,
                        label: 'Verbergen',
                        reason: ''
                    });
                }
            });
        }
        else {
            if(self.state.reason === "") {
                return;
            }
            
            fetch(self.props.false_positive_api_url + 'api/fp/' + self.props.warning_id, {
                method: 'post',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ "reason": self.state.reason })
            }).then(function (response) {
                if (response.ok) {
                    self.setState({
                        isFalsePositive: true,
                        label: 'Tonen'
                    });
                }
            });
        }
    }

    handleReasonChange(event) {
        this.setState({
            reason: event.target.value
        });
    }

    render() {
        return (
            <div className="btn-group" role="group" aria-label="Action Panel">
                <input type="text" className="form-control" value={this.state.reason} placeholder="Verplicht: voer een reden in." aria-label="Verplicht: Voer een reden in." onChange={this.handleReasonChange} />
                &nbsp;
                <button type="button" id={this.props.warning_id} className="btn btn-default" data-toggle="tooltip" data-placement="right"
                    title="(De)Markeer als false-positive." onClick={this.setFalsePositive}>
                    {this.state.label}
                </button>
            </div>
        );
    }
}

export { FalsePositivePanel };