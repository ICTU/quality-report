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

import $ from 'jquery';
import React from 'react';
import {UrlList} from 'widgets/url_list.js';
import {HelpTable} from 'widgets/help_table.js';


class MetaDataTable extends React.Component {
    render() {
        return (
            <HelpTable headers={this.props.headers} className="table-striped first-col-centered">
                {this.props.children}
            </HelpTable>
        );
    }
}

class NameWithIdentifier extends React.Component {
    render() {
        return <div>{this.props.title} (<code><small>{this.props.identifier}</small></code>)</div>;
    }
}

class DomainObjectsTable extends React.Component {
    render() {
        var table_rows = [];
        this.props.domain_objects.forEach(function(domain_object) {
            var icon = domain_object["included"] ? "✔️" : "";
            var title = <NameWithIdentifier title={domain_object["name"]} identifier={domain_object["id"]}/>
            var default_requirements = domain_object['default_requirements'].sort().join(', ');
            var optional_requirements = domain_object['optional_requirements'].sort().join(', ');
            table_rows.push({cells: [icon, title, default_requirements, optional_requirements]});
        });
        return (
            <MetaDataTable headers={[["included", "In dit rapport?"],
                                     ["title", <NameWithIdentifier title="Domeinobject" identifier="Identifier"/>],
                                     ["default_requirements", "Default eisen"],
                                     ["optional_requirements", "Optionele eisen"]]}>
                {table_rows}
            </MetaDataTable>
        );
    }
}

class RequirementsTable extends React.Component {
    render() {
        var table_rows = [];
        this.props.requirements.forEach(function(requirement) {
            var icon = requirement["included"] ? "✔️" : "";
            var title = <NameWithIdentifier title={requirement["name"]} identifier={requirement["id"]}/>;
            var metrics = requirement['metrics'].sort().join(', ');
            table_rows.push({cells: [icon, title, metrics]});
        });
        return (
            <MetaDataTable headers={[["included", "In dit rapport?"],
                                    ["title", <NameWithIdentifier title="Eis" identifier="Identifier"/>],
                                    ["metrics", "Metrieken"]]}>
                {table_rows}
            </MetaDataTable>
        );
    }
}

class MetricClassesTable extends React.Component {
    render() {
        var table_rows = [];
        this.props.metric_classes.forEach(function(metric_class) {
            var icon = metric_class["included"] ? "✔️" : "";
            var title = <NameWithIdentifier title={metric_class["name"]} identifier={metric_class["id"]}/>;
            table_rows.push({cells: [icon, title, metric_class['norm']]});
        });
        return (
            <MetaDataTable headers={[["included", "In dit rapport?"],
                                     ["title", <NameWithIdentifier title="Metriek" identifier="Identifier"/>],
                                     ["norm", "Norm"]]}>
                {table_rows}
            </MetaDataTable>
        );
    }
}

class MetricSourcesTable extends React.Component {
    render() {
        var table_rows = [];
        this.props.metric_sources.forEach(function(metric_source) {
            var icon = metric_source["included"] ? "✔️" : "";
            var title = <NameWithIdentifier title={metric_source["name"]} identifier={metric_source["id"]}/>;
            var url_list = <UrlList>{metric_source['urls']}</UrlList>;
            table_rows.push({cells: [icon, title, url_list]});
        });
        return (
            <MetaDataTable headers={[["included", "In dit rapport?"],
                                     ["title", <NameWithIdentifier title="Metriekbron" identifier="Identifier"/>],
                                     ["instances", "Instanties"]]}>
                {table_rows}
            </MetaDataTable>
        );
    }
}

export {DomainObjectsTable, RequirementsTable, MetricClassesTable, MetricSourcesTable};
