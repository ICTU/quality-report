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

from qualitylib import metric, domain
import datetime
import unittest


class FakeNagios(object):
    ''' Provide for a fake Nagios object so that unit tests don't need access
        to a real Nagios instance. '''
    @staticmethod
    def service_availability(server, time_period):  
        # pylint: disable=unused-argument
        ''' Assume all services were available. '''
        return 100

    @staticmethod
    def availability_url(time_period):  # pylint: disable=unused-argument
        ''' Return fake url. '''
        return 'http://nagios'

    service_availability_url = availability_url


class FakeJavaMelody(object):  # pylint: disable=too-few-public-methods
    ''' Provide for a fake JavaMelody object so that unit tests don't need 
        access to a real JavaMelody instance. '''
    mean_request_times_list = [1, 2, 3]

    def mean_request_times(self, *args):  # pylint: disable=unused-argument
        ''' Return a list of mean request times. '''
        return self.mean_request_times_list

    @staticmethod  # pylint: disable=unused-argument
    def url(*args):
        ''' Return a fake url. '''
        return 'http://javamelody/'


class FakeService(object):
    ''' Fake service that only implements methods needed for the unit tests. '''

    def __init__(self, nagios_id=True, nagios=None, java_melody_id=True):
        self.__nagios_id = nagios_id
        self.__nagios = nagios
        self.__java_melody_id = java_melody_id

    def java_melody(self):
        ''' Return the JavaMelody id of this subject. '''
        return 'java_melody_id' if self.__java_melody_id else ''

    def nagios(self):
        ''' Return the Nagios instance of the service. '''
        return self.__nagios

    def nagios_server_id(self):
        ''' Return the Nagios server id of this subject. '''
        return 'nagios_id' if self.__nagios_id else ''

    def __str__(self):
        return 'FakeService'


class ServiceAvailabilityTestsMixin(object):  
    ''' Unit tests for the abstract ServiceAvailability metrics. '''
    def setUp(self):  # pylint: disable=invalid-name
        ''' Create the text fixture. '''
        self.__project = domain.Project(nagios=FakeNagios())
        self.__service = FakeService()
        self._metric = self.metric_class(subject=self.__service, 
                                         project=self.__project)

    def set_today(self, year, month, day):
        ''' Fake the current date. '''
        # pylint: disable=protected-access
        self.metric_class._today = \
            staticmethod(lambda: datetime.date(year, month, day))

    def test_value(self):
        ''' Test that the value matches what Nagios provides. '''
        self.assertEqual(100, self._metric.value())

    def test_report_availability(self):
        ''' Test that the metric report contains the availability. '''
        self.failUnless('100%' in self._metric.report())

    def test_url(self):
        ''' Test that the metric returns the correct url. '''
        self.assertEqual(dict(Nagios='http://nagios'), self._metric.url())

    def test_can_be_measured(self):
        ''' Test that the metric can be measured when the project has Nagios
            and the service has a Nagios id. '''
        self.failUnless(self.metric_class.can_be_measured(self.__service,
                                                          self.__project))

    def test_service_nagios(self):
        ''' Test that the metric can be measured when the service has Nagios
            instead of the project. '''
        service = FakeService(nagios=FakeNagios())
        project = domain.Project()
        self.failUnless(self.metric_class.can_be_measured(service, project))

    def test_need_nagios(self):
        ''' Test that the metric cannot be measured if the project or the 
            service doesn't have Nagios. ''' 
        project = domain.Project()
        self.failIf(self.metric_class.can_be_measured(self.__service, project))

    def test_need_nagios_id(self):
        ''' Test that the metric cannot be measured if the service has no 
            Nagios id. '''
        service = FakeService(nagios_id=False)
        self.failIf(self.metric_class.can_be_measured(service, self.__project))


class ServiceAvailabilityLastMonthTest(ServiceAvailabilityTestsMixin, 
                                       unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the ServiceAvailabilityLastMonth metric. '''
    metric_class = metric.ServiceAvailabilityLastMonth

    def test_report_month_januari(self):
        ''' Test that the metric report contains the right month. '''
        self.set_today(2000, 1, 1)
        self.failUnless('december 1999' in self._metric.report())

    def test_report_month_june(self):
        ''' Test that the metric report contains the right month. '''
        self.set_today(2010, 6, 30)
        self.failUnless('mei 2010' in self._metric.report())


class ServiceAvailabilityThisMonthTest(ServiceAvailabilityTestsMixin, 
                                       unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the ServiceAvailabilityThisMonth metric. '''
    metric_class = metric.ServiceAvailabilityThisMonth

    def test_report_month_januari(self):
        ''' Test that the metric report contains the right month. '''
        self.set_today(2000, 1, 1)
        self.failUnless('januari 2000' in self._metric.report())

    def test_report_month_june(self):
        ''' Test that the metric report contains the right month. '''
        self.set_today(2010, 6, 30)
        self.failUnless('juni 2010' in self._metric.report())


class ServiceResponseTimesTestsMixin(object):
    ''' Unit tests for the service response times metrics. '''

    def setUp(self):  # pylint: disable=invalid-name
        ''' Create the text fixture. '''
        self.__javamelody = FakeJavaMelody()
        self.__service = FakeService()
        self.__project = domain.Project(javamelody=self.__javamelody)
        self._metric = self.metric_class(subject=self.__service, 
                                         project=self.__project)

    def set_today(self, year, month, day):
        ''' Fake the current date. '''
        # pylint: disable=protected-access
        self.metric_class._today = \
            staticmethod(lambda: datetime.date(year, month, day))

    def test_value(self):
        ''' Test that the metric value is the maximum mean response time as
            reported by JavaMelody. '''
        self.assertEqual(3, self._metric.value())

    def test_no_measurements(self):
        ''' Test that the value is -1 when JavaMelody reports no mean request
            times (e.g. because the monitored application hasn't been used 
            yet. '''
        self.__javamelody.mean_request_times_list = [] 
        self.assertEqual(-1, self._metric.value())

    def test_report(self):
        ''' Test that the report contains the value. '''
        self.failUnless('3 ms.' in self._metric.report())

    def test_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual(dict(JavaMelody='http://javamelody/'), 
                         self._metric.url())

    def test_can_be_measured(self):
        ''' Test that the metric can be measured when JavaMelody is 
            available and the service has a JavaMelody id. '''
        self.failUnless(self.metric_class.can_be_measured(self.__service,
                                                          self.__project))

    def test_needs_java_melody(self):
        ''' Test that the metric cannot be measured if the project has no
            JavaMelody. '''
        project = domain.Project()
        self.failIf(self.metric_class.can_be_measured(self.__service, project))

    def test_needs_java_melody_id(self):
        ''' Test that the metric cannot be measured if the service has no
            JavaMelody id. '''
        service = FakeService(java_melody_id=False)
        self.failIf(self.metric_class.can_be_measured(service, self.__project))


class ServiceResponseTimesLastMonthTest(ServiceResponseTimesTestsMixin, 
                                        unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the ServiceResponseTimesLastMonth metric. '''
    metric_class = metric.ServiceResponseTimesLastMonth

    def test_report_month_januari(self):
        ''' Test that the metric report contains the right month. '''
        self.set_today(2000, 1, 1)
        self.failUnless('december 1999' in self._metric.report())

    def test_report_month_june(self):
        ''' Test that the metric report contains the right month. '''
        self.set_today(2010, 6, 30)
        self.failUnless('mei 2010' in self._metric.report())


class ServiceResponseTimesThisMonthTest(ServiceResponseTimesTestsMixin, 
                                        unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the ServiceResponseTimesThisMonth metric. '''
    metric_class = metric.ServiceResponseTimesThisMonth

    def test_report_month_januari(self):
        ''' Test that the metric report contains the right month. '''
        self.set_today(2000, 1, 1)
        self.failUnless('januari 2000' in self._metric.report())

    def test_report_month_june(self):
        ''' Test that the metric report contains the right month. '''
        self.set_today(2010, 6, 30)
        self.failUnless('juni 2010' in self._metric.report())
