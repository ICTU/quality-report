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

// These functions depend on cookie.js.

/*
Some event handlers are generated using closures. See
http://stackoverflow.com/questions/3495679/passing-parameters-in-javascript-onclick-event
*/

// FIXME: magic numbers for columns

google.load('visualization', '1', {'packages': ['corechart', 'table']});

var settings = [];
var tables = [];

var COLOR_GREEN = '#4CC417';
var COLOR_YELLOW = '#FDFD90';
var COLOR_RED = '#FC9090';
var COLOR_GREY = '#808080';
var COLOR_MISSING = '#F8F8F8';
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

function create_metrics_table(metrics_data) {
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
    metrics.addRows(metrics_data);
    color_metrics(BG_COLOR_GREEN, BG_COLOR_YELLOW, BG_COLOR_RED, BG_COLOR_GREY, BG_COLOR_MISSING);
}

function create_dashboard(metrics_data, history_data) {
    /*jshint loopfunc: true */
    read_settings_from_cookies();
    create_metrics_table(metrics_data);
    var sections = window.metrics.getDistinctValues(METRICS_COLUMN_SECTION);

    tables.all = new google.visualization.Table(document.getElementById('table_all'));
    google.visualization.events.addListener(tables.all, 'sort', save_sort_order);
    for (var index = 0; index < sections.length; index++) {
        var section = sections[index];
        tables[section] = new google.visualization.Table(document.getElementById('table_' + section));
        google.visualization.events.addListener(tables[section], 'sort', save_sort_order);
        draw_section_summary_chart(section);
    }
    draw_area_chart('meta_metrics_history_graph', history_data);

    set_radio_indicator('filter_color', settings.filter_color);
    set_check_indicator('show_dashboard', settings.show_dashboard);
    set_check_indicator('show_multiple_tables', settings.show_multiple_tables);
    show_or_hide_dashboard();
    draw_tables(tables);

    // Event handler for navigating between tabs
    $('#dashboard_tab_control a').click(function (event) {
          event.preventDefault();
          $(this).tab('show');
    });

    // Event handler for the (Toon) "Dashboard" menu item
    document.getElementById('show_dashboard').onclick = function() {
        switch_toggle('show_dashboard', function() {
            show_or_hide_dashboard();
        });
    };

    // Event handler for the "Tabel per product/team" menu item
    document.getElementById('show_multiple_tables').onclick = function() {
        switch_toggle('show_multiple_tables', function() {
            draw_tables(tables);
        });
    };

    // Event handlers for the filter by color menu items.
    var colors = ['filter_color_all', 'filter_color_red_and_yellow', 'filter_color_grey'];
    for (index = 0; index < colors.length; index++) {
        document.getElementById(colors[index]).onclick = (function() {
            var color = colors[index];
            return function() {
                set_filter('filter_color', color, tables);
            };
        })();
    }
}

function read_settings_from_cookies() {
    settings.filter_color = read_cookie('filter_color', 'filter_color_all');
    settings.show_dashboard = read_cookie('show_dashboard', 'true') === 'true';
    settings.show_multiple_tables = read_cookie('show_multiple_tables', 'true') === 'true';
    settings.table_sort_column = parseInt(read_cookie('table_sort_column', '0'), 10);
    settings.table_sort_ascending = read_cookie('table_sort_ascending', 'true') === 'true';
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

function color_metrics(color_green, color_yellow, color_red, color_grey, color_missing) {
    var numberOfColumns = window.metrics.getNumberOfColumns();
    var statusToColor = {'perfect': color_green, 'green': color_green, 'yellow': color_yellow, 'red': color_red,
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
    document.getElementById('section_' + section).style.display = 'block';
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
    document.getElementById('section_' + section).style.display = 'none';
    hide_links_to(section);
}

function table_view(section) {
    var view = new google.visualization.DataView(window.metrics);
    var rows = [];

    // Section
    if (section === 'all') {
        for (var index = 0; index < window.metrics.getNumberOfRows(); index++) {
            rows.push(index);
        }
    } else {
        rows = window.metrics.getFilteredRows([{column: METRICS_COLUMN_SECTION, value: section}]);
    }

    // Color
    var filtered_color = settings.filter_color;
    if (filtered_color !== 'filter_color_all') {
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
        rows = intersection(rows, colored_rows);
    }
    view.setRows(rows);
    return view;
}

function draw_section_summary_chart(section) {
    draw_pie_chart(section);
}

function status_count(section, color) {
   return window.metrics.getFilteredRows([{column: METRICS_COLUMN_SECTION, value: section},
                                          {column: METRICS_COLUMN_STATUS_TEXT, value: color}]).length;
}

function draw_pie_chart(section) {
    var piechart_div = document.getElementById('section_summary_chart_' + section);
    if (piechart_div === null) {
        // Not all sections have a pie chart, e.g. the meta metrics (MM) section.
        return;
    }

    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Status');
    data.addColumn('number', 'Number');
    data.addRows([
      ['Groen', status_count(section, 'green') + status_count(section, 'perfect')],
      ['Geel', status_count(section, 'yellow')],
      ['Rood', status_count(section, 'red')],
      ['Grijs', status_count(section, 'grey')],
      ['Ontbrekend', status_count(section, 'missing') + status_count(section, 'missing_source')]
    ]);
    var bg_color = piechart_div.parentNode.getAttribute('bgcolor');
    var options = {
      slices: [{color: COLOR_GREEN}, {color: COLOR_YELLOW},
               {color: COLOR_RED}, {color: COLOR_GREY}, {color: COLOR_MISSING}],
      pieSliceText: 'none',
      tooltip: {textStyle: {fontSize: 14}},
      legend: 'none',
      width: 80, height: 80,
      backgroundColor: bg_color,
      chartArea: {left:7, top:7, width:66, height:66},
      is3D: true
    };
    var chart = new google.visualization.PieChart(piechart_div);
    chart.draw(data, options);
}

function draw_area_chart(section, history) {
    var data = new google.visualization.DataTable();
    data.addColumn('datetime', 'Datum');
    data.addColumn('number', '% groene metrieken');
    data.addColumn('number', '% gele metrieken');
    data.addColumn('number', '% rode metrieken');
    data.addColumn('number', '% grijze metrieken');
    data.addColumn('number', '% ontbrekende metrieken');
    data.addRows(history);
    var options = {
      width: 1200, height: 400,
      isStacked: true,
      hAxis: {format:'d-M-yy'},
      colors: [COLOR_GREEN, COLOR_YELLOW, COLOR_RED, COLOR_GREY, COLOR_MISSING]
    };
    var chart = new google.visualization.AreaChart(document.getElementById(section));
    chart.draw(data, options);
}

function show_or_hide_dashboard() {
    var display_style;
    if (settings.show_dashboard) {
        display_style = 'block';
        show_links_to('dashboard');
    } else {
        display_style = 'none';
        hide_links_to('dashboard');
    }
    document.getElementById('section_dashboard').style.display = display_style;
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

function intersection(array1, array2) {
    var intersection_array = [];
    for (var index1 = 0; index1 < array1.length; index1++) {
        for (var index2 = 0; index2 < array2.length; index2++) {
            if (array1[index1] === array2[index2]) {
                intersection_array[intersection_array.length] = array1[index1];
            }
        }
    }
    return intersection_array;
}
