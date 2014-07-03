'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from qualitylib.formatting import base_formatter
import logging


class CSVFormatter(base_formatter.Formatter):
    ''' Format the report as one line that can be added to a CSV file. '''

    sep = ', '

    def prefix(self, report):
        return report.date().strftime('%c')

    def body(self, report):
        from qualitylib import metric
        result = []
        count_green = count_yellow = count_red = count_grey = 0
        for metric_instance in report.metrics():
            status = metric_instance.status()
            if status in metric.GreenMetaMetric.metric_statuses:
                count_green += 1
            elif status in metric.YellowMetaMetric.metric_statuses:
                count_yellow += 1
            elif status in metric.RedMetaMetric.metric_statuses:
                count_red += 1
            elif status in metric.GreyMetaMetric.metric_statuses:
                count_grey += 1
            else:
                logging.warn('Unknown metric status %s in CSV export', status)
            if isinstance(metric_instance, metric.TotalLOC):
                result.append(self.metric(metric_instance))
        result.extend([str(count) for count in (count_green, count_yellow, 
                                                count_red, count_grey)])
        return self.sep.join(result) + '\n'

    def metric(self, metric_instance):
        return '%s' % metric_instance.value()
