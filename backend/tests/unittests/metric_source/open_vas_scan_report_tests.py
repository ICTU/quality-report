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
import unittest
import urllib.error

from hqlib.metric_source import OpenVASScanReport


class FakeUrlOpener(object):  # pylint: disable=too-few-public-methods
    """ Fake the url opener to return static html. """
    html = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html" />
<!-- CSS Tabs is licensed under Creative Commons Attribution 3.0 - http://creativecommons.org/licenses/by/3.0/ -->
<style type="text/css">

body {
font: 100% verdana, arial, sans-serif;
background-color: #fff;
}

/* begin css tabs */

ul#tabnav { /* general settings */
text-align: left; /* set to left, right or center */
margin: 8px 0 0 0; /* set margins as desired */
font: bold 11px verdana, arial, sans-serif; /* set font as desired */
border-bottom: 1px solid #6c6; /* set border COLOR as desired */
list-style-type: none;
padding: 3px 10px 3px 10px; /* THIRD number must change with respect to padding-top (X) below */
}

ul#tabnav li { /* do not change */
display: inline;
}

ul#tabnav li.selected { /* settings for selected tab */
border-bottom: 1px solid #fff; /* set border color to page background color */
background-color: #fff; /* set background color to match above border color */
}


ul#tabnav li { /* settings for all tab links */
padding: 3px 4px; /* set padding (tab size) as desired; FIRST number must change with respect to padding-top (X) above */
border: 1px solid #6c6; /* set border COLOR as desired; usually matches border color specified in #tabnav */
background-color: #cfc; /* set unselected tab background color as desired */
color: #666; /* set unselected tab link color as desired */
margin-right: 0px; /* set additional spacing between tabs as desired */
text-decoration: none;
border-bottom: none;
cursor: pointer;
}

ul#tabnav li:hover { /* settings for hover effect */
background: #afa; /* set desired hover color */
}

/* end css tabs */

/* FF 100% height iframe */
html, body, div, iframe { margin:0; padding:0; }
iframe { display:block; width:100%; border:none; }

h1
{
    display: inline;
    float: left;
    font-size: small;
    margin: 0;
    padding: 0 10px;
}

h2
{
    display: inline;
    float: right;
    font-size: small;
    margin: 0;
    padding: 0 10px;
}

</style>

<script type="text/javascript">
function updateBody(tabId, page) {
    document.getElementById(selectedTab).setAttribute("class", "unselected");
    tab = document.getElementById(tabId)
    tab.setAttribute("class", "selected");
    selectedTab = tabId;
    iframe = document.getElementById("myframe");
    iframe.src = tab.getAttribute("value");
}
function init(tabId){
	updateBody(tabId);
	updateViewport();
	
	window.onresize = updateViewport;
}

function updateViewport(){
	 var viewportheight;

	 // the more standards compliant browsers (mozilla/netscape/opera/IE7) use window.innerWidth and window.innerHeight

	 if (typeof window.innerWidth != 'undefined')
	 {
	      viewportheight = window.innerHeight
	 }

	// IE6 in standards compliant mode (i.e. with a valid doctype as the first line in the document)

	 else if (typeof document.documentElement != 'undefined'
	     && typeof document.documentElement.clientWidth !=
	     'undefined' && document.documentElement.clientWidth != 0)
	 {
	       viewportheight = document.documentElement.clientHeight
	 }
	// older versions of IE
	 else
	 { 
	       viewportheight = document.getElementsByTagName('body')[0].clientHeight
	 }
	
	iframe = document.getElementById("myframe");
	iframe.style.height = (viewportheight-30)+'px';
}
var selectedTab = "tab1"
</script>

</head>

<body onload="init('tab1');">

<h1><a id="hudson_link" href="#"></a></h1>
<h2><a id="zip_link" href="#">Zip</a></h2>

<ul id="tabnav">
<li id="tab1" class="unselected" onclick="updateBody('tab1')" value="openvas_scan.html">openvas_scan</li><script type="text/javascript">document.getElementById("hudson_link").innerHTML="Back to Security-OpenVAS";</script><script type="text/javascript">document.getElementById("hudson_link").href="/job/Security-OpenVAS/";</script><script type="text/javascript">document.getElementById("zip_link").href="*zip*/HTML_Report.zip";</script></ul>
<div>
<iframe id="myframe" height="100%" width="100%" frameborder="0"></iframe>
</div>

</body>
</html>
'''

    def url_open(self, url):
        """ Open a url. """
        if 'raise' in url:
            raise urllib.error.HTTPError(url, None, None, None, None)
        else:
            return self.html


class OpenVASScanReportTest(unittest.TestCase):
    """ Unit tests for the open VAS Scan report class. """

    def setUp(self):
        self.__opener = FakeUrlOpener()
        self.__report = OpenVASScanReport(url_open=self.__opener.url_open)

    def test_high_risk_alerts(self):
        """ Test the number of high risk alerts. """
        self.assertEqual(0, self.__report.alerts('high', 'url'))

    def test_medium_risk_alerts(self):
        """ Test the number of medium risk alerts. """
        self.assertEqual(2, self.__report.alerts('medium', 'url'))

    def test_low_risk_alerts(self):
        """ Test the number of low risk alerts. """
        self.assertEqual(1, self.__report.alerts('low', 'url'))

    def test_passed_raise(self):
        """ Test that the value is -1 when the report can't be opened. """
        self.assertEqual(-1, self.__report.alerts('high', 'raise'))

    def test_multiple_urls(self):
        """ Test the number of alerts for multiple urls. """
        self.assertEqual(4, self.__report.alerts('medium', 'url1', 'url2'))

    def test_datetime(self):
        """ Test that the date/time can be parsed. """
        self.assertEqual(datetime.datetime(2017, 10, 15, 19, 17, 50), self.__report.datetime('url'))

    def test_empty_report(self):
        """ Test that the value is -1 when the report is invalid. """
        opener = FakeUrlOpener()
        opener.html = ''
        report = OpenVASScanReport(url_open=opener.url_open)
        self.assertEqual(-1, report.alerts('high', 'url'))

    def test_date_time_of_empty_report(self):
        """ Test that the date time is datetime.min when the report is invalid. """
        opener = FakeUrlOpener()
        opener.html = ''
        report = OpenVASScanReport(url_open=opener.url_open)
        self.assertEqual(datetime.datetime.min, report.datetime('url'))
