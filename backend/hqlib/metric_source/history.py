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
import datetime
from typing import Type, Callable, List, Dict, Union

from hqlib.persistence import JsonPersister, FilePersister
from .. import domain
from ..typing import DateTime, Number


class CompactHistory(domain.MetricSource):
    """ Class for reading and writing history JSON files. """
    __long_history_count = 2000
    __persister = FilePersister

    def __init__(self, history_filename: str, recent_history: int = 100) -> None:
        self.__history_filename = history_filename
        self.__recent_history = recent_history
        self.__history = self.__persister.read_json(history_filename) or dict(dates=[], statuses=[], metrics={})
        super().__init__()

    @classmethod
    def set_persister(cls, new_persister: Type[JsonPersister]):
        """ Method injects non-default persister class instead of FilePersister. """
        cls.__persister = new_persister

    def filename(self) -> str:
        """ Return the history filename """
        return self.__history_filename

    def recent_history(self, metric_id: str) -> List[Number]:
        """ Retrieve the recent history for the metric_ids. """
        return self.__history_records(metric_id, self.__recent_history)

    def long_history(self, metric_id) -> List[Number]:
        """ Retrieve longer history for the metric_ids. """
        return self.__history_records(metric_id, self.__long_history_count)

    def __history_records(self, metric_id: str, number_of_records: int) -> List[Number]:
        """ Retrieve the given number of history records for the metric_id. """
        measurements = self.__history['metrics'].get(metric_id, [])
        dates = self.__history['dates'][-number_of_records:]
        values = self.__get_prehistory(dates, measurements)

        for date in dates:
            for measurement in reversed(measurements):
                if measurement['start'] <= date <= measurement['end']:
                    values.append(measurement.get('value', None))
                    break  # Next date

        return values

    @classmethod
    def __get_prehistory(cls, dates, measurements) -> List[Number]:
        values = []
        if dates and measurements:
            i = 0
            while dates[i] < measurements[0]['start'] and i < len(dates):
                values.append(None)
                i += 1
        return values

    def get_dates(self, long_history: bool = False) -> str:
        """ Retrieve the list of report dates concatenated in comma separated string. """
        number_of_records = self.__long_history_count if long_history else self.__recent_history
        return ','.join(self.__history['dates'][-number_of_records:])

    def status_start_date(self, metric_id: str, current_status: str,
                          now: Callable[[], DateTime] = datetime.datetime.now) -> DateTime:
        """ Return the start date of the current status of the metric. """
        measurements = self.__history['metrics'].get(metric_id, [])
        if measurements:
            last_status, date_string = measurements[-1]['status'], measurements[-1]['start']
            start_date = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
            return start_date if last_status == current_status else now()
        return now()

    def statuses(self) -> List[Dict[str, Union[str, int]]]:
        """ Return the statuses for each measurement. """
        status_records = []
        for (date, statuses) in zip(self.__history['dates'], self.__history['statuses']):
            status_record = dict(date=date)
            status_record.update(statuses)
            status_records.append(status_record)
        return status_records

    def add_report(self, quality_report):
        """ Add the report to the history file. """
        self.add_metrics(quality_report.date(), quality_report.metrics())

    def add_metrics(self, date_time, metrics):
        """ Add the metrics to the history file. """
        date = date_time.strftime('%Y-%m-%d %H:%M:%S')
        self.__history['dates'].append(date)
        self.__history['statuses'].append(dict())
        for metric in metrics:
            measurements = self.__history['metrics'].setdefault(metric.stable_id(), [])
            value = metric.numerical_value()
            status = metric.status()
            if measurements and measurements[-1].get('value', -1) == value and measurements[-1].get('status') == status:
                measurements[-1]['end'] = date
            else:
                new_measurement = dict(start=date, end=date, status=status)
                if value != -1:
                    new_measurement['value'] = value
                measurements.append(new_measurement)
            self.__history['statuses'][-1][status] = self.__history['statuses'][-1].get(status, 0) + 1
        self.__persister.write_json(self.__history, self.__history_filename)


class History(CompactHistory):
    """ Class representing the obsolete history file. Substituted by CompactHistory."""
