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

class NavBar extends React.Component {
    report_date_time_class() {
        var now = new Date();
        var seconds = parseInt((now - this.props.report_date_time)/1000, 10);
        if (seconds > 60 * 60) {
            return seconds > 60 * 60 * 24 ? 'very_old' : 'old';
        } else {
            return ''
        }
    }

    render() {
        var report_date_time = format_date_time(this.props.report_date_time)
        var section_menu_items = [];
        this.props.sections.forEach(function(section) {
            var id = section["id"], title = section["title"];
            section_menu_items.push(
                <MenuItem key={id} className={"link_section_" + id} href={"section_" + id} title={title} />
            );
        });
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
                        <ul className="nav navbar-nav">
                            <MenuItem id="metrics_tab" onClick={this.props.on_tab} title="Metrieken"
                                      hide={this.props.tab === 'metrics_tab'} />
                            <Menu id="navigation_menu" title="Metrieken" hide={this.props.tab !== 'metrics_tab'}>
                                <MenuItem href="section_dashboard" icon="dashboard" title="Dashboard"
                                          hide={!this.props.show_dashboard} />
                                {section_menu_items}
                            </Menu>
                            <MenuItem title="Toon" hide={this.props.tab === 'metrics_tab'} disabled={true} />
                            <Menu id="toon_menu" title="Toon" hide={this.props.tab !== 'metrics_tab'}>
                                <MenuItem id="show_dashboard" title="Dashboard"
                                          check={this.props.show_dashboard}
                                          onClick={this.props.on_toggle_dashboard} />
                                <MenuItem id="show_multiple_tables" title="Tabel per product/team"
                                          check={!this.props.show_one_table}
                                          onClick={this.props.on_toggle_one_table} />
                                <li role="separator" className="divider"></li>
                                <MenuItem id="filter_color_all" title="Alle metrieken"
                                          check={this.props.filter_color.filter_color_all}
                                          onClick={this.props.on_filter_color} />
                                <MenuItem id="filter_color_red" title="Rode metrieken"
                                          check={this.props.filter_color.filter_color_red}
                                          onClick={this.props.on_filter_color} />
                                <MenuItem id="filter_color_yellow" title="Gele metrieken"
                                          check={this.props.filter_color.filter_color_yellow}
                                          onClick={this.props.on_filter_color} />
                                <MenuItem id="filter_color_green" title="Groene metrieken"
                                          check={this.props.filter_color.filter_color_green}
                                          onClick={this.props.on_filter_color} />
                                 <MenuItem id="filter_color_perfect" title="Perfecte metrieken"
                                          check={this.props.filter_color.filter_color_perfect}
                                          onClick={this.props.on_filter_color} />
                                <MenuItem id="filter_color_grey" title="Grijze metrieken"
                                          check={this.props.filter_color.filter_color_grey}
                                          onClick={this.props.on_filter_color} />
                                <MenuItem id="filter_color_missing_source" title="Metrieken zonder bron"
                                          check={this.props.filter_color.filter_color_missing_source}
                                          onClick={this.props.on_filter_color} />
                                <MenuItem id="filter_color_missing" title="Metrieken met onbeschikbare bron"
                                          check={this.props.filter_color.filter_color_missing}
                                          onClick={this.props.on_filter_color} />
                            </Menu>
                            <MenuItem id="trend_tab" onClick={this.props.on_tab} title="Trend"
                                      hide={this.props.tab === 'trend_tab'} />
                            <Menu id="trend_navigation_menu" title="Trend" hide={this.props.tab !== 'trend_tab'}>
                                <MenuItem href="meta_metrics_history_absolute_graph" title="Aantal metrieken per status" />
                                <MenuItem href="meta_metrics_history_relative_graph" title="Percentage metrieken per status" />
                            </Menu>
                            <MenuItem id="help_tab" onClick={this.props.on_tab} title="Help"
                                      hide={this.props.tab === 'help_tab'} />
                            <Menu id="help_tab_menu" title="Help" hide={this.props.tab !== 'help_tab'}>
                                <MenuItem href="help_about" title="Over HQ" icon="info-sign" />
                                <MenuItem href="help_on_metrics" title="Metrieken" icon="tasks" />
                                <MenuItem href="help_on_metric_sources" title="Metriekbronnen" icon="open" />
                                <MenuItem href="help_on_requirements" title="Eisen" icon="check" />
                                <MenuItem href="help_on_domain_objects" title="Domeinobjecten" icon="file" />
                                <MenuItem href="help_on_configuration" title="Configuratie" icon="wrench" />
                            </Menu>
                        </ul>
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
