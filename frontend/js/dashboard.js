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

import $ from 'jquery';
import Chart from 'chart.js';
import '../js/chartjs-plugin-stackedline100.js';
import 'bootstrap/dist/js/bootstrap';
import 'bootstrap/dist/css/bootstrap.css';
import '../css/quality_report.css';
import {create_dashboard_table} from '../js/dashboard_table.js';
import {create_sections, create_navigation_menu_items} from '../js/sections.js';
import {read_cookie, write_cookie} from '../js/cookie.js';
import {intersection, format_date_time} from '../js/utils.js';
import {parse_history_json} from '../js/history.js';
import '../js/compatibility.js';

/*
Some event handlers are generated using closures. See
http://stackoverflow.com/questions/3495679/passing-parameters-in-javascript-onclick-event
*/

google.setOnLoadCallback(function() {create_dashboard()});
google.load('visualization', '1', {'packages': ['corechart', 'table']});

var settings = [];
var tables = [];
var trend_data_loaded = false;

var COLOR_PERFECT = '#45E600';
var COLOR_GREEN = '#4CC417';
var COLOR_YELLOW = '#FDFD90';
var COLOR_RED = '#FC9090';
var COLOR_GREY = '#808080';
var COLOR_MISSING = '#F0F0F0';
var BG_COLOR_PERFECT = '#EDFFE6';
var BG_COLOR_GREEN = '#E6F8E0';
var BG_COLOR_YELLOW = '#F8F8C0';
var BG_COLOR_RED = '#F8E0E0';
var BG_COLOR_GREY = '#CCCCCC';
var BG_COLOR_MISSING = '#F8F8F8';

// Column indices. FIXME: lookup instead of hard coding.

var METRICS_COLUMN_SECTION = 1;
var METRICS_COLUMN_STATUS_TEXT = 2;
var METRICS_COLUMN_TREND = 3;
var METRICS_COLUMN_STATUS_ICON = 4;
var METRICS_COLUMN_MEASUREMENT = 5;
var METRICS_COLUMN_NORM = 6;
var METRICS_COLUMN_COMMENT = 7;

function create_dashboard() {
    read_settings_from_cookies();
    create_metrics_table();
    create_event_handlers();
    set_indicators();

    // Retrieve the metrics for the metrics table after the sections have been loaded.
    $.getJSON("json/metrics.json", "", function(metrics_data) {
        $("#sections").append(create_dashboard_table(metrics_data["dashboard"]));
        $("#sections").append(create_sections(metrics_data["sections"]));
        $('#navigation_menu_items').append(create_navigation_menu_items(metrics_data['sections']));
        fill_metrics_table(metrics_data["metrics"]);
        hide('#loading');
        show('#sections');

        set_report_date(new Date(...metrics_data["report_date"]));
        $("#hq_version").html(metrics_data["hq_version"]);
        $(".report_title").html(metrics_data["report_title"]);
    });

    // Retrieve the files for the menu's
    $.getJSON("json/meta_data.json", "", function(meta_data) {
        create_domain_objects_table(meta_data['domain_objects']);
        create_requirements_table(meta_data['requirements']);
        create_metric_classes_table(meta_data['metrics']);
        create_metric_sources_table(meta_data['metric_sources']);
    });
}

function create_metrics_table() {
    var metrics = new google.visualization.DataTable();
    window.metrics = metrics;
    metrics.addColumn('string', 'ID');
    metrics.addColumn('string', 'Section');
    metrics.addColumn('string', 'Status text');
    metrics.addColumn('string', 'Trend');
    metrics.addColumn('string', 'Status');
    metrics.addColumn('string', 'Meting');
    metrics.addColumn('string', 'Norm');
    metrics.addColumn('string', 'Toelichting');
}

function fill_metrics_table(metrics_data) {
    window.metrics.addRows(metrics_data);
    color_metrics(BG_COLOR_PERFECT, BG_COLOR_GREEN, BG_COLOR_YELLOW, BG_COLOR_RED, BG_COLOR_GREY, BG_COLOR_MISSING);

    var sections = window.metrics.getDistinctValues(METRICS_COLUMN_SECTION);

    tables.all = new google.visualization.Table(document.getElementById('table_all'));
    google.visualization.events.addListener(tables.all, 'sort', save_sort_order);
    for (var index = 0; index < sections.length; index++) {
        var section = sections[index];
        tables[section] = new google.visualization.Table(document.getElementById('table_' + section));
        google.visualization.events.addListener(tables[section], 'sort', save_sort_order);
        draw_section_summary_chart(section);
    }
    show_or_hide_dashboard();
    draw_tables(tables);
}

function create_domain_objects_table(domain_objects) {
    var table_rows = [table_heading("In dit rapport?", "Domeinobject (<code><small>Identifier</small></code>)",
                                    "Default eisen", "Optionele eisen")];
    $.each(domain_objects, function(index, domain_object) {
        var icon = check_icon(domain_object);
        var title = meta_data_title(domain_object);
        var default_requirements = domain_object['default_requirements'].sort().join(', ');
        var optional_requirements = domain_object['optional_requirements'].sort().join(', ');
        table_rows.push(table_row(icon, title, default_requirements, optional_requirements));
    });
    create_meta_data_table('#domain_object_classes', table_rows);
}

function create_requirements_table(requirements) {
    var table_rows = [table_heading("In dit rapport?", "Eis (<code><small>Identifier</small></code>)", "Metrieken")];
    $.each(requirements, function(index, requirement) {
        var icon = check_icon(requirement);
        var title = meta_data_title(requirement);
        var metrics = requirement['metrics'].sort().join(', ');
        table_rows.push(table_row(icon, title, metrics));
    });
    create_meta_data_table('#requirements', table_rows);
}

function create_metric_classes_table(metric_classes) {
    var table_rows = [table_heading("In dit rapport?", "Metriek (<code><small>Identifier</small></code>)", "Norm")];
    $.each(metric_classes, function(index, metric_class) {
        var icon = check_icon(metric_class);
        var title = meta_data_title(metric_class);
        table_rows.push(table_row(icon, title, metric_class['norm']));
    });
    create_meta_data_table('#metric_classes', table_rows);
}

function create_metric_sources_table(metric_sources) {
    var table_rows = [table_heading("In dit rapport?", "Metriekbron (<code><small>Identifier</small></code>)",
                                    "Instanties")];
    $.each(metric_sources, function(index, metric_source) {
        var icon = check_icon(metric_source);
        var title = meta_data_title(metric_source);
        var urls = [];
        $.each(metric_source['urls'], function(index, url) {
            urls.push('<a href="' + url + '" target="_blank">' + url + '</a>');
        });
        table_rows.push(table_row(icon, title, urls.join('<br/>')));
    });
    create_meta_data_table('#metric_sources', table_rows);
}

function check_icon(meta_data_item) {
    return meta_data_item['included'] ? '<span aria-hidden="true" class="glyphicon glyphicon-ok"></span>' : '';
}

function meta_data_title(meta_data_item) {
    return meta_data_item['name'] + ' (<code><small>' + meta_data_item['id'] + '</small></code>)';
}

function table_heading(...headers) {
    return '<tr><th>' + headers.join('</th><th>') + '</th></tr>';
}

function table_row(...items) {
    return '<tr><td>' + items.join("</td><td>") + '</td></tr>';
}

function create_meta_data_table(element_id, table_rows) {
    $(element_id).append(
        $('<table/>', {'class': 'table table-striped first-col-centered', html: table_rows.join("")}));
}

function read_settings_from_cookies() {
    settings.filter_color = read_cookie('filter_color', 'filter_color_all');
    settings.show_dashboard = read_cookie('show_dashboard', 'true') === 'true';
    settings.show_multiple_tables = read_cookie('show_multiple_tables', 'true') === 'true';
    settings.table_sort_column = parseInt(read_cookie('table_sort_column', '0'), 10);
    settings.table_sort_ascending = read_cookie('table_sort_ascending', 'true') === 'true';
}

function create_event_handlers() {
    fix_navigation_links();

    // Event handler for the tabs
    $('#trend_tab').click(function() {
        // Retrieve the history for the meta metrics history charts.
        activate_parent('#trend_tab');
        show('#metrics_tab');
        hide('#navigation_menu');
        hide('#sections');
        hide("#toon_menu");
        if (trend_data_loaded) {
            show('#trend_graphs');
        } else {
            show('#loading');
            $.getJSON("json/meta_history.json", "", function(history_json) {
                draw_area_charts(parse_history_json(history_json));
                hide('#loading');
                show('#trend_graphs');
                trend_data_loaded = true;
            });
        };
    });

    $('#metrics_tab').click(function() {
        hide('#metrics_tab');
        deactivate_parent('#trend_tab');
        hide('#loading');
        show("#navigation_menu");
        show('#sections');
        hide('#trend_graphs');
        show("#toon_menu");
    });

    // Event handler for the (Toon) "Dashboard" menu item
    $('#show_dashboard').click(function() {
        switch_toggle('show_dashboard', function() {
            show_or_hide_dashboard();
        });
    });

    // Event handler for the "Tabel per product/team" menu item
    $('#show_multiple_tables').click(function() {
        switch_toggle('show_multiple_tables', function() {
            draw_tables(tables);
        });
    });

    // Event handlers for the filter by color menu items.
    $('#filter_color_all').click(function() {
        set_filter('filter_color', 'filter_color_all', tables)
    });
    $('#filter_color_red_and_yellow').click(function() {
        set_filter('filter_color', 'filter_color_red_and_yellow', tables)
    });
    $('#filter_color_grey').click(function() {
        set_filter('filter_color', 'filter_color_grey', tables)
    });
    $('#filter_color_missing_source').click(function() {
        set_filter('filter_color', 'filter_color_missing_source', tables)
    });
    $('#filter_color_missing').click(function() {
        set_filter('filter_color', 'filter_color_missing', tables)
    });
}

function set_indicators() {
    set_radio_indicator('filter_color', settings.filter_color);
    set_check_indicator('show_dashboard', settings.show_dashboard);
    set_check_indicator('show_multiple_tables', settings.show_multiple_tables);
}

function save_sort_order(event) {
    // Save the sort order. We use the same sort order for each column.
    var column = event.column;
    settings.table_sort_column = column;
    settings.table_sort_ascending = event.ascending;
    write_cookie('table_sort_column', column.toString());
    write_cookie('table_sort_ascending', event.ascending.toString());
    draw_tables(tables);
}

function switch_toggle(toggle, refresh) {
    settings[toggle] = !settings[toggle];
    write_cookie(toggle, settings[toggle].toString());
    set_check_indicator(toggle, settings[toggle]);
    refresh();
}

function set_filter(filter, filter_value, tables) {
    settings[filter] = filter_value;
    write_cookie(filter, filter_value);
    set_radio_indicator(filter, filter_value);
    draw_tables(tables);
}

function color_metrics(color_perfect, color_green, color_yellow, color_red, color_grey, color_missing) {
    var numberOfColumns = window.metrics.getNumberOfColumns();
    var statusToColor = {'perfect': color_perfect, 'green': color_green, 'yellow': color_yellow, 'red': color_red,
                         'grey': color_grey, 'missing': color_missing, 'missing_source': color_missing};
    for (var row_index = 0; row_index < window.metrics.getNumberOfRows(); row_index++) {
        var bg_color = statusToColor[window.metrics.getValue(row_index, METRICS_COLUMN_STATUS_TEXT)];
        for (var column_index = 0; column_index < numberOfColumns; column_index++) {
            var style = 'background-color: ' + bg_color;
            if (column_index === METRICS_COLUMN_TREND || column_index === METRICS_COLUMN_STATUS_ICON) {
                style += '; text-align: center';
            }
            window.metrics.setProperty(row_index, column_index, 'style', style);
        }
    }
}

function set_report_date(date_time) {
    $('#report_date_time').html(format_date_time(date_time));

    var now = new Date();
    var seconds = parseInt((now - date_time)/1000, 10);
    if (seconds > 60 * 60) {
        var cls = seconds > 60 * 60 * 24 ? 'very_old' : 'old';
        $('#report_date_time').attr('class', cls);
    }
}

function draw_tables(tables) {
    // Draw or hide the tables in each of the sections.
    for (var section in tables) {
        if (tables.hasOwnProperty(section)) {
            draw_table(tables[section], section);
        }
    }
}

function draw_table(table, section) {
    // Draw or hide the table in the section.
    if (user_wants_to_hide_table(section)) {
        hide_table(section);
    } else {
        show_or_hide_table(table, section);
    }
}

function user_wants_to_hide_table(section) {
    // The section should be hidden if the user wants to see one big table but
    // the section contains a product or team table OR if the user wants to
    // see the product and team tables but this section contains the one big
    // table.
    var show_multiple_tables = settings.show_multiple_tables;
    return section === 'all' ? show_multiple_tables : !show_multiple_tables;
}

function show_or_hide_table(table, section) {
    // Show the table if it has visible rows, hide otherwise.
    var view = table_view(section);
    if (view.getNumberOfRows() > 0) {
        show_table(table, section, view);
    } else {
        hide_table(section);
    }
}

function show_table(table, section, view) {
    show('#section_' + section);
    show_links_to(section);
    var columns_to_hide = [METRICS_COLUMN_SECTION, METRICS_COLUMN_STATUS_TEXT];
    var sort_column = settings.table_sort_column;
    var columns_to_hide_when_empty = [METRICS_COLUMN_COMMENT];
    for (var index = 0; index < columns_to_hide_when_empty.length; index++) {
        var column_index = columns_to_hide_when_empty[index];
        var distinct_values = view.getDistinctValues(column_index);
        if (distinct_values.length === 1 && distinct_values[0] === '') {
            // Hide the column since it's empty.
            columns_to_hide.push(column_index);
        }
    }
    view.hideColumns(columns_to_hide);
    table.draw(view, {allowHtml: true,
                      sortColumn: sort_column,
                      sortAscending: settings.table_sort_ascending});
}

function hide_table(section) {
    hide('#section_' + section);
    hide_links_to(section);
}

function table_view(section) {
    var view = new google.visualization.DataView(window.metrics);
    var rows = table_view_rows(section);
    if (settings.filter_color !== 'filter_color_all') {
        rows = intersection(rows, table_view_filtered_rows());
    }
    view.setRows(rows);
    return view;
}

function table_view_rows(section) {
    var rows = [];
    if (section === 'all') {
        for (var index = 0; index < window.metrics.getNumberOfRows(); index++) {
            rows.push(index);
        }
    } else {
        rows = window.metrics.getFilteredRows([{column: METRICS_COLUMN_SECTION, value: section}]);
    }
    return rows;
}

function table_view_filtered_rows() {
    var filtered_color = settings.filter_color;
    var colored_rows = [];
    if (filtered_color === 'filter_color_red_and_yellow') {
        var colors = ['yellow', 'red'];
        for (var color_index = 0; color_index < colors.length; color_index++) {
            var color_rows = window.metrics.getFilteredRows([{column: METRICS_COLUMN_STATUS_TEXT,
                                                              value: colors[color_index]}]);
            colored_rows = colored_rows.concat(color_rows);
        }
    }
    if (filtered_color === 'filter_color_grey') {
        colored_rows = window.metrics.getFilteredRows([{column: METRICS_COLUMN_STATUS_TEXT,
                                                        value: 'grey'}]);
    }
    if (filtered_color === 'filter_color_missing_source') {
        colored_rows = window.metrics.getFilteredRows([{column: METRICS_COLUMN_STATUS_TEXT,
                                                        value: 'missing_source'}]);
    }
    if (filtered_color === 'filter_color_missing') {
        colored_rows = window.metrics.getFilteredRows([{column: METRICS_COLUMN_STATUS_TEXT,
                                                        value: 'missing'}]);
    }
    return colored_rows;
}

function draw_section_summary_chart(section) {
    draw_pie_chart(section);
}

function status_count(section, color) {
   return window.metrics.getFilteredRows([{column: METRICS_COLUMN_SECTION, value: section},
                                          {column: METRICS_COLUMN_STATUS_TEXT, value: color}]).length;
}

function draw_pie_chart(section) {
    var piechart_canvas = document.getElementById('section_summary_chart_' + section);
     if (piechart_canvas === null) {
        // Not all sections have a pie chart, e.g. the meta metrics (MM) section.
        return;
    }
    var piechart = new Chart(piechart_canvas, {
        type: 'pie',
        data: {
            datasets: [{
                data: [
                    status_count(section, 'perfect'),
                    status_count(section, 'green'),
                    status_count(section, 'yellow'),
                    status_count(section, 'red'),
                    status_count(section, 'grey'),
                    status_count(section, 'missing'),
                    status_count(section, 'missing_source')
                ],
                backgroundColor: [COLOR_PERFECT, COLOR_GREEN, COLOR_YELLOW, COLOR_RED, COLOR_MISSING, COLOR_MISSING]
            }],
            labels: ['Perfect', 'Goed', 'Bijna goed', 'Actie vereist', 'Technische schuld', 'Bron niet beschikbaar',
                     'Bron niet geconfigureerd'],
        },
        options: {
            legend: {
                display: false
            },
            responsive: true,
            layout: {
                padding: {
                    left: 25,
                    right: 25,
                    top: 25,
                    bottom: 25
                }
            }
        }
    });
}

function draw_area_charts(history) {
    draw_area_chart(history, 'meta_metrics_history_relative_graph_canvas', "Percentage metrieken per status", true);
    draw_area_chart(history, 'meta_metrics_history_absolute_graph_canvas', "Aantal metrieken per status", false);
}

function draw_area_chart(history, element_id, title, relative) {
    var meta_metrics_history_relative_graph_canvas = document.getElementById(element_id);
    var datasets = [];
    for (var index = 0; index < 8; index ++) {
        var dataset = [];
        history.forEach(function(item) {dataset.push(item[index])});
        datasets.push(dataset);
    };
    var meta_metrics_history_relative_graph = new Chart(meta_metrics_history_relative_graph_canvas, {
        type: 'line',
        data: {
            labels: datasets[0],
            datasets: [
                {
                    label: "Perfect",
                    fill: true,
                    backgroundColor: COLOR_PERFECT,
                    data: datasets[1]
                },
                {
                    label: "Goed",
                    fill: true,
                    backgroundColor: COLOR_GREEN,
                    data: datasets[2]
                },
                {
                    label: "Bijna goed",
                    fill: true,
                    backgroundColor: COLOR_YELLOW,
                    data: datasets[3]
                },
                {
                    label: "Actie vereist",
                    fill: true,
                    backgroundColor: COLOR_RED,
                    data: datasets[4]
                },
                {
                    label: "Technische schuld",
                    fill: true,
                    backgroundColor: COLOR_GREY,
                    data: datasets[5]
                },
                {
                    label: "Bron niet beschikbaar",
                    fill: true,
                    backgroundColor: COLOR_MISSING,
                    data: datasets[6]
                },
                {
                    label: "Bron niet geconfigureerd",
                    fill: true,
                    backgroundColor: COLOR_MISSING,
                    data: datasets[7]
                }
            ]},
        options: {
            title: {
                text: title,
                display: true
            },
            scales: {
                xAxes: [{
                    type: 'time',
                    time: {
                        unit: 'month'
                    }
                }],
                yAxes: [{
                    stacked: true
                }]
            },
            plugins: {
                stackedline100: {enable: relative}
            }
        }
    });
}

function show_or_hide_dashboard() {
    if (settings.show_dashboard) {
        show('#section_dashboard');
        show_links_to('dashboard');
    } else {
        hide('#section_dashboard');
        hide_links_to('dashboard');
    };
}

function show_links_to(section) {
    var links = $('.link_section_' + section, document);
    for (var index = 0; index < links.length; index++) {
        if (links[index].tagName.toLowerCase() === 'a') {
            links[index].style.display = 'block';
        } else {
            var title = links[index].getAttribute('title');
            var style = links[index].getAttribute('style');
            links[index].innerHTML = '<a href="#section_' + section + '" style="' + style + '">' + title + '</a>';
        }
    }
}

function hide_links_to(section) {
    var links = $('.link_section_' + section, document);
    for (var index = 0; index < links.length; index++) {
        if (links[index].tagName.toLowerCase() === 'a') {
            links[index].style.display = 'none';
        } else {
            links[index].innerHTML = links[index].getAttribute('title');
        }
    }
}

function set_radio_indicator(radio_items_classname, id_of_radio_item_to_select) {
    var elements = $('.' + radio_items_classname, document);
    for (var index = 0; index < elements.length; index++) {
        var check = (elements[index].getAttribute('id') === id_of_radio_item_to_select);
        var icon = check ? 'glyphicon glyphicon-ok' : '';
        elements[index].getElementsByTagName('span')[0].setAttribute('class', icon);
    }
}

function set_check_indicator(id_of_check_item, check) {
    var element = document.getElementById(id_of_check_item);
    var icon = check ? 'glyphicon glyphicon-ok' : '';
    element.getElementsByTagName('span')[0].setAttribute('class', icon);
}

function hide(element_id) {
    $(element_id).css('display', 'none');
}

function show(element_id) {
    $(element_id).css('display', 'block');
}

function activate_parent(element_id) {
    $(element_id).parent().addClass('active');
}

function deactivate_parent(element_id) {
    $(element_id).parent().removeClass('active');
}

function fix_navigation_links() {
    // When clicking a navigation link, compensate for the fixed header.
    var shiftWindow = function() { scrollBy(0, -50) };
    if (location.hash) shiftWindow();
    window.addEventListener("hashchange", shiftWindow);
}
