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

from qualitylib import utils
from qualitylib.domain import LowerIsBetterMetric, HigherIsBetterMetric
from qualitylib.metric import NagiosMetricMixin
from qualitylib.metric.quality_attributes import AVAILABILITY, PERFORMANCE
import datetime


class ServiceAvailability(NagiosMetricMixin, HigherIsBetterMetric):
    ''' Metric for measuring the availability of a service. '''

    name = 'Service beschikbaarheid'
    norm_template = 'De beschikbaarheid van de dienst is minimaal ' \
        '%(target)d%%. Lager dan %(low_target)d%% is rood.'
    template = 'De beschikbaarheid van de dienst %(name)s ' \
        '%(time_period_description)s %(value)d%%.'
    target_value = 99
    low_target_value = 98
    quality_attribute = AVAILABILITY
    time_period_nagios = 'Subclass responsibility'

    @classmethod
    def can_be_measured(cls, service, project):
        return super(ServiceAvailability, cls).can_be_measured(service, 
                                                               project) and \
            service.nagios_server_id() and \
            (service.nagios() or project.nagios())

    def value(self):
        return self._nagios.service_availability(self.__nagios_server_id(),
                                        time_period=self.time_period_nagios)

    def url(self):
        return dict(Nagios=self._nagios.service_availability_url( \
                                        time_period=self.time_period_nagios))

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(ServiceAvailability, self)._parameters()
        parameters['time_period_description'] = \
            self.time_period_description().lower()
        return parameters

    @classmethod
    def time_period_description(cls):
        ''' Return a human readable form of the time period that this metric
            is reporting on. '''
        raise NotImplementedError  # pragma: no cover

    @staticmethod
    def _today():
        ''' Return the current date. Overrideable for unit test purposes. '''
        return datetime.date.today()

    def __nagios_server_id(self):
        ''' Return the Nagios id of the server. '''
        return self._subject.nagios_server_id()


class ServiceAvailabilityLastMonth(ServiceAvailability):
    ''' Metric for measuring the availability of a service last month. '''

    name = '%s vorige maand' % ServiceAvailability.name
    time_period_nagios = 'lastmonth'

    @classmethod
    def time_period_description(cls):
        return 'was vorige maand (%s)' % \
            utils.format_month(utils.month_ago(cls._today()))


class ServiceAvailabilityThisMonth(ServiceAvailability):
    ''' Metric for measuring the availability of a service this month. '''

    name = '%s deze maand' % ServiceAvailability.name
    time_period_nagios = 'thismonth'

    @classmethod
    def time_period_description(cls):
        return 'is deze maand (%s)' % utils.format_month(cls._today())


class ServiceResponseTimes(LowerIsBetterMetric):
    ''' Metric for measuring the response times of a service. '''

    name = 'Service responstijden'
    norm_template = 'De maximale gemiddelde responstijd is lager dan ' \
        '%(target)d ms. Hoger dan %(low_target)d ms is rood.'
    template = 'De maximale gemiddelde responstijd van de dienst %(name)s ' \
        '%(time_period_description)s %(value)d ms.'
    target_value = 2000  # milliseconds
    low_target_value = 3000  # milliseconds
    quality_attribute = PERFORMANCE

    @classmethod
    def can_be_measured(cls, service, project):
        return super(ServiceResponseTimes, cls).can_be_measured(service,
                                                                project) and \
            project.javamelody() and service.java_melody()

    def __init__(self, *args, **kwargs):
        super(ServiceResponseTimes, self).__init__(*args, **kwargs)
        self.__javamelody = self._project.javamelody()

    def value(self):
        start, end = self.__period()
        mean_request_times = self.__javamelody.mean_request_times( \
            self.__javamelody_id(), start, end)
        return max(mean_request_times) if mean_request_times else -1

    def url(self):
        return dict(JavaMelody=self.__javamelody.url(self.__javamelody_id(), 
                                                     *self.__period()))

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(ServiceResponseTimes, self)._parameters()
        parameters['time_period_description'] = \
            self.time_period_description().lower()
        return parameters

    @classmethod
    def time_period_description(cls):
        ''' Return a human readable form of the time period that this metric
            is reporting on. '''
        raise NotImplementedError  # pragma: no cover

    @staticmethod
    def _today():
        ''' Return the current date. Overrideable for unit test purposes. '''
        return datetime.date.today()

    @classmethod
    def __period(cls):
        ''' Return the reporting period to pass to JavaMelody. '''
        date = cls._date_in_period()
        start = date.replace(day=1)        
        end = date.replace(day=utils.last_day_of_month(date))
        return start, end

    @classmethod
    def _date_in_period(cls):
        ''' Return a date in the period (month) this metric is reporting on. '''
        raise NotImplementedError  # pragma: no cover

    def __javamelody_id(self):
        ''' Return the JavaMelody id of the product we're reporting on. '''
        return self._subject.java_melody()


class ServiceResponseTimesLastMonth(ServiceResponseTimes):
    ''' Metric for measuring the response times of a service last month. '''

    name = '%s vorige maand' % ServiceResponseTimes.name

    @classmethod
    def time_period_description(cls):
        return 'was vorige maand (%s)' % \
            utils.format_month(utils.month_ago(cls._today()))

    @classmethod
    def _date_in_period(cls):
        return utils.month_ago(cls._today())


class ServiceResponseTimesThisMonth(ServiceResponseTimes):
    ''' Metric for measuring the response times of a service this month. '''

    name = '%s deze maand' % ServiceResponseTimes.name

    @classmethod
    def time_period_description(cls):
        return 'is deze maand (%s)' % utils.format_month(cls._today())

    @classmethod
    def _date_in_period(cls):
        return cls._today()
