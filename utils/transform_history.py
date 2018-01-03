"""
Copyright 2012-2018 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json
import logging
import re
import sys

IGNORED_METRICS = set()


def ignore_metric(metric):
    """ Return whether the metric should be ignored. """
    patterns = [
        r"^.*-version$",                 # Version numbers of components. Not used by HQ.
        r"^.*:\d+(\.\d+){1,2}(-\w+)?$",  # Metrics on specific versions of components. No longer used by HQ.
        r"^[A-Z][A-Z]-\d+$",             # Two letter abbreviations of metrics. Don't know which metric that is.
        r"^.*MetaMetric.*$",             # Meta metrics. We calculate these from the status of the other metrics.
        r"^.* object at .*$"             # Bug in old version of HQ
    ]
    for pattern in patterns:
        if re.match(pattern, metric):
            if metric[:30] not in IGNORED_METRICS:
                IGNORED_METRICS.add(metric[:30])
                logging.warning("Ignoring %s because it matches %s", metric, pattern)
            return True
    return False


def extract_status_and_value(old_value):
    """ Extract the metric value and status from the old value. """
    value, status = -1, None
    if isinstance(old_value, int):
        value = old_value
    elif isinstance(old_value, str):
        value = float(old_value) if '.' in old_value else int(old_value)
    else:
        value, status = int(old_value[0]), old_value[1]
    return value, status


def fix_date(date):
    """ Make sure the date has a uniform format. """
    if len(date.split('-')[0]) == 2:
        date = '20' + date  # Add century
    if '.' in date:
        date = date.split('.')[0]  # Remove milliseconds
    return date


def fix_metric_name(metric):
    """ Fix buggy metric names if possible. """
    return "TotalLOC" if metric.startswith("TotalLOC(") else metric


def process_line(history, line):
    """ Process one line from the history file, i.e. one quality report. """
    report = eval(line)
    date = fix_date(report.pop("date"))
    history['dates'].append(date)
    history['statuses'].append(dict())
    for metric, old_value in report.items():
        metric = fix_metric_name(metric)
        if ignore_metric(metric):
            continue
        value, status = extract_status_and_value(old_value)
        measurements = history['metrics'].setdefault(metric, [])
        if measurements and measurements[-1].get('value', -1) == value and measurements[-1].get('status') == status:
            measurements[-1]['end'] = date
        else:
            new_measurement = dict(start=date, end=date)
            if value != -1:
                new_measurement['value'] = value
            if status:
                new_measurement['status'] = status
            measurements.append(new_measurement)
        if status:
            history['statuses'][-1][status] = history['statuses'][-1].get(status, 0) + 1


def main():
    """ Do the work. """
    history = dict(dates=[], statuses=[], metrics={})

    with open(sys.argv[1]) as history_file:
        for line in history_file:
            if line.strip():
                process_line(history, line)

    print(json.dumps(history, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
