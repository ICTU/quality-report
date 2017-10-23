"""
Copyright 2012-2017 Ministerie van Sociale Zaken en Werkgelegenheid

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
import io
import unittest
import urllib.error

from hqlib.metric_source import SpiritSplunkCSVPerformanceLoadTestReport


CSV = b""";KEI Performance-acceptatiecriteria;;;;;;;;;;;;;;;;;;;;;;;
Nr.;Criterium;Applicatie;"Zakelijk/
Prive";Eindgebruikershandeling;Bestandsgrootte (MB);"10-05-2017 (S1718)
Baseline Test (PT03)";;"11-06-2017 (S1720)
Baseline Test (PT06)";;"12-06-2017 (S1720)
Baseline Test (PT07)";;;"% Verbetering
(laatste vs voorlaatste)";;;;;;;;;;;%
;;;;;;0;;0;;0;;;;;;;;;;;Totaal requirements;37;;100
;;;;;;Gemiddeld;90e percentiel;Gemiddeld;90e percentiel;Gemiddeld;90e percentiel;;Gemiddeld;90e percentiel;Requirement;Verschil (s) laatste en voorlaatste;"significantie (of een verschil betekenisvol is) 
(minder of meer dan 1s)";"Overdrachtsnelheid
(bij download/upload)";Result;;;;;
1;Nieuwe aankoop starten (Zakelijk);XYZ;Zakelijk (1a);Upload bijlage (2,5 MB);2,5;6,01;6,25;6,09;6,36;6,06;6,42;;0,51;-0,97;3,13;0,03;;0,39;Failed;;#Getest;36;97%;97
;;XYZ;Zakelijk (1b);Naar aankoopoverzicht (na indienen);;6,57;9,17;0,62;0,65;0,54;0,59;;15,08;10,87;5;0,08;;;Passed;;#Nog te testen;1;3%;3
2;Nieuwe aankoop starten (Prive);XYZ;Prive (2a);Upload Bijlage (1 MB);1;4,08;4,16;4,24;4,36;4,3;4,4;0;-1,41;-1,02;1,25;-4,3;Significante verslechtering;0,23;Failed;;;;;
;;XYZ;Prive (2b);Knop indienen klikken;;5,21;5,92;4,62;5,68;4,38;4,46;;-1,02;0,57;5;-0,05;;;Passed;;#Passed;11;31%;30
3;Indienen factuur bij bestaande aankoop (Prive) (taak indienen);XYZ;Prive (3a);Upload Bijlage  (2,5 MB);2,5;5,17;5,18;5,47;5,55;5,53;5,62;;-2,72;-6,16;3,13;-0,11;;0,45;Failed;;#Failed;25;69%;68
;;XYZ;Prive (3b);Knop indienen klikken;;2,32;3,15;2,6;4;2,81;3,64;;-2,54;-4,71;5;-0,11;;;Passed;;;;;
4;Zoeken van een aankoop (Zakelijk en Prive);XYZ;Zakelijk (4a);Zoeken op aankoopnummer;;0,38;0,47;0,5;0,64;0,52;0,61;;-3,64;4,91;3;-0,02;;;Passed;;;;;
;;XYZ;Prive (4b);Zoeken op aankoopnummer;;0,42;0,6;0,44;0,67;0,38;0,52;;15,53;27,83;3;0,06;;;Passed;;;;;
5;Stukken indienen bij een bestaande aankoop (Zakelijk);XYZ;Zakelijk (5a);Uploaden zelf (2,5MB);2,5;5,31;5,5;5,48;5,71;5,6;5,85;;-2,16;-2,36;3,13;-0,12;;0,43;Failed;;;;;
6;Downloaden dossier (Zakelijk);XYZ;Zakelijk (6a);Downloadsnelheid (MB/s) (60MB);60;1,22;1,3;1,3;1,39;1;1,1;0;29,78;25,88;1;-1,98;Significante verslechtering;1,1;Passed;x;let op downloadsnelheid, hoe meer hoe beter;;;
7;Downloaden dossier (Prive);XYZ;Prive (7a);Downloadsnelheid (MB/s) (16MB);16;0,78;1,3;0,85;1,2;0,67;0,91;;27,73;32,43;1;0,19;;0,91;Failed;x;let op downloadsnelheid, hoe meer hoe beter;;;
8;Makelaar opent bericht en daarna 10 onderliggende stukken een voor een;XYZ;Zakelijk (8a);Openen bericht;;10,21;14,72;8,37;10,15;10,22;14,48;;-18,05;-29,9;3;-1,84;Significante verslechtering;;Failed;;;;;
;;XYZ;Zakelijk (8b);Openen stuk;;1,64;1,95;1,9;3,41;2,02;3,36;;-5,52;1,5;3;-0,11;;;Failed;;;;;
;;XYZ;Prive (8c);Openen bericht;;8,16;10,53;6,95;8,44;8,8;12,55;;-20,98;-32,74;3;-1,85;Significante verslechtering;;Failed;;;;;
;;XYZ;Prive (8d);Openen stuk;;1,52;2,37;1,5;2,53;1,61;2,62;;-7,17;-3,21;3;-0,12;;;Passed;;;;;
9;Zoeken van een aankoop op nummer  (Zakelijk en Prive);ABC;Zakelijk (9a);Zoeken op aankoopnummer;;2,95;3,56;3,32;3,79;4,24;5,45;;-21,6;-30,48;5;-0,92;;;Failed;;;;;
;;ABC;Prive (9b);Zoeken op aankoopnummer;;3,05;3,62;3,71;5,39;6,2;6,43;;-40,17;-16,18;5;-2,49;Significante verslechtering;;Failed;;;;;
10;Samenstellen factuur  (Zakelijk en Prive);ABC;Zakelijk (10a);Opstarten boekhoudapp;;7,74;11,09;8,09;12,01;8,5;12,26;0;-4,78;-2,08;5;-0,41;;;Failed;;;;;
;;ABC;Zakelijk (10b);Afronden boekhoudapp;;;;;;;;;;;;;;;;;;;;
;;ABC;Prive (10c);Opstarten boekhoudapp;;1,58;2,24;3,37;5,88;7,16;15,25;;-52,9;-61,42;5;-3,79;Significante verslechtering;;Failed;;;;;
;;ABC;Prive (10d);Afronden boekhoudapp;;0,35;0,51;0,73;0,77;1,11;1,67;;-34,08;-53,72;5;-0,38;;;Passed;;;;;
11;Aanmaken van een herinnering (alleen Zakelijk);ABC;Zakelijk (11a);Indienen herinnering;;0,38;0,38;2,62;2,88;2,58;2,58;;1,71;11,64;5;0,04;;;Passed;;;;;
12;Plannen aankoop op herinnering (Zakelijk en Prive);ABC;Zakelijk (12a);Indienen (plannen herinnering);;7,63;9,14;8,91;10,62;10,26;11,07;;-13,13;-4,1;5;-1,35;Significante verslechtering;;Failed;;;;;
;;ABC;Prive (12b);Indienen (plannen herinnering);;2,2;2,29;2,9;3,17;3,19;3,19;0;-9,12;-0,69;5;-0,29;;;Passed;;;;;
13;Toevoegen document (alleen Zakelijk);ABC;Zakelijk (13a);Toevoegen document (2,5MB);2,5;4,53;4,59;7,33;9,19;6,85;7,37;;7,1;24,73;3,13;0,49;;0,34;Failed;;;;;
14;Stukken controleren inclusief openen document (stuk openen vanuit aankoop);ABC;Zakelijk (14a);Drop down Stukken-menu;;0,65;0,76;1,79;2,55;4,46;3;;-59,83;-14,79;1;-2,67;Significante verslechtering;;Failed;;;;;
;;ABC;Zakelijk (14b);Openen document;;0,73;1,71;1,1;1,38;1,12;1,46;;-1,88;-5,49;3;-0,02;;;Passed;;;;;
15;"Taken/Zaken openen (vanuit een link)
";ABC;Zakelijk (15a);Openen Taak_Nieuwe manier;;4,9;6,05;5,62;6,98;7,39;10,22;;-24,02;-31,68;0;-1,78;Significante verslechtering;;Failed;;;;;
;;ABC;Zakelijk (15b);Openen Taak_Oude manier;;6,68;8,43;6,08;7,29;9,44;12,35;0;-35,58;-40,92;3;-3,36;Significante verslechtering;;Failed;;;;;
;;ABC;Zakelijk (15c);Uitvoeren van taak ;;1,47;1,73;2,3;3,61;3,05;4,82;0;-24,39;-25,16;3;-0,74;;;Failed;;;;;
16;"Taken/Zaken openen (vanuit een link): Bv controleren factuur

";ABC;Prive (16a);Openen Taak_Nieuwe manier;;4,72;4,72;9,19;9,19;8,84;8,84;;3,98;3,98;0;0,35;;;Failed;;;;;
;;ABC;Prive (16b);Openen Taak_Oude manier;;13,47;21,29;9,97;10,89;10,18;10,37;0;-2,01;5,04;3;-0,21;;;Failed;;;;;
;;ABC;Prive (16c);Uitvoeren van taak ;;1,73;1,86;3,68;4,78;4,65;4,96;;-20,72;-3,61;3;-0,96;;;Failed;;;;;
17;Navigeren en aantekeningen maken in aankoopdossierviewer;ABC;Zakelijk (17a);Openen viewer;;5,036;9,475;4,728;9,715;4,535;9,262;;4,26;4,89;1;0,19;;;Failed;;;;;
;;ABC;Zakelijk (17b);Openen 1 doc in viewer;;0,925;1,032;1,154;1,385;1,15;1,38;;0,35;0,36;1;0;;;Failed;;;;;
;;ABC;Prive (17c);Openen viewer;;5,024;9,767;4,448;9,528;4,697;9,457;;-5,3;0,75;1;-0,25;;;Failed;;;;;
;;ABC;Prive (17d);Openen 1 doc in viewer;;0,93;1,03;1,163;1,392;1,181;1,449;;-1,52;-3,93;1;-0,02;;;Failed;;;;;
"""


class ReportUnderTest(SpiritSplunkCSVPerformanceLoadTestReport):  # pylint: disable=too-few-public-methods
    """ Override the performance report to return the url as report contents. """

    def url_open(self, url):  # pylint: disable=no-self-use
        """ Return the static html. """
        if 'error' in url:
            raise urllib.error.URLError('reason')
        else:
            return io.BytesIO(CSV)


class SpiritSplunkCSVPerformanceReportTest(unittest.TestCase):
    """ Unit tests for the Spirit Splunk CSV performance report metric source. """
    expected_queries = 22
    expected_queries_violating_max_responsetime = 17

    def setUp(self):
        ReportUnderTest.queries.cache_clear()
        self._performance_report = ReportUnderTest('http://report/')

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual('http://report/', self._performance_report.url())

    def test_queries_non_existing(self):
        """ Test that the number of queries for a product/version that is not found is zero. """
        self.assertEqual(0, self._performance_report.queries('product'))

    def test_queries(self):
        """ Test the total number of queries for a product/version that is in the report. """
        self.assertEqual(self.expected_queries, self._performance_report.queries('ABC'))

    def test_queries_re(self):
        """ Test that the total number of queries for a product/version that is in the report can be found using a
            regular expression. """
        self.assertEqual(self.expected_queries, self._performance_report.queries('AB.*'))

    def test_queries_violating_max_responsetime(self):
        """ Test that the number of queries violating the maximum response times is zero. """
        self.assertEqual(self.expected_queries_violating_max_responsetime,
                         self._performance_report.queries_violating_max_responsetime('ABC'))

    def test_queries_violating_wished_reponsetime(self):
        """ Test that the number of queries violating the wished response times is zero. """
        self.assertEqual(self.expected_queries_violating_max_responsetime,
                         self._performance_report.queries_violating_wished_responsetime('ABC'))

    def test_date_of_last_measurement(self):
        """ Test that the date of the last measurement is correctly parsed from the report. """
        self.assertEqual(datetime.datetime(2017, 6, 12), self._performance_report.datetime('ABC'))

    def test_date_without_urls(self):
        """ Test that the min date is passed if there are no report urls to consult. """
        class SpiritSplunkCSVReportWithoutUrls(ReportUnderTest):
            """ Simulate missing urls. """
            def urls(self, product):  # pylint: disable=unused-argument
                return []

        self.assertEqual(datetime.datetime.min,
                         SpiritSplunkCSVReportWithoutUrls('http://report').datetime('ABC'))


class SpiritSplunkCSVPerformanceReportMultipleReportsTest(SpiritSplunkCSVPerformanceReportTest):
    """ Unit tests for a performance report metric source with multiple reports. """

    expected_queries = 2 * SpiritSplunkCSVPerformanceReportTest.expected_queries
    expected_queries_violating_max_responsetime = \
        2 * SpiritSplunkCSVPerformanceReportTest.expected_queries_violating_max_responsetime

    def setUp(self):
        self._performance_report = ReportUnderTest('http://report/',
                                                   report_urls=['http://report/1', 'http://report/2'])


class SpiritSplunkCSVPerformanceReportMissingTest(unittest.TestCase):
    """ Unit tests for a missing performance report metric source. """

    def test_queries_with_missing_report(self):
        """ Test that the value of a missing report is -1. """
        self.assertEqual(-1, ReportUnderTest('http://error/').queries('p1'))

    def test_queries_max_responsetime_with_missing_report(self):
        """ Test that the value of a missing report is -1. """
        self.assertEqual(-1, ReportUnderTest('http://error/').queries_violating_max_responsetime('p2'))

    def test_queries_wished_reponsetime_with_missing_report(self):
        """ Test that the value of a missing report is -1. """
        self.assertEqual(-1, ReportUnderTest('http://error/').queries_violating_wished_responsetime('p3'))

    def test_date_with_missing_report(self):
        """ Test that the date of a missing report is the min date. """
        self.assertEqual(datetime.datetime.min, ReportUnderTest('http://error/').datetime('p4'))
