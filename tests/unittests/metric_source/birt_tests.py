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
import urllib2

import bs4

from hqlib.metric_source import Birt
from hqlib.metric_source.birt import SprintProgressReport

TEST_DESIGN_HTML = """
<html>
    <body class="style_0" style=" margin:0px;">
        <table cellpadding="0" style="empty-cells: show; border-collapse:collapse; width:100%;">
            <col></col>
            <tr>
                <td></td>
            </tr>
            <tr>
                <td valign="top">
                    <div id="__bookmark_1">
                        <table class="style_1" style="border-collapse: collapse; empty-cells: show; width: 4.24in;" id="AUTOGENBOOKMARK_1_09021f92-9b5c-4954-8540-c857b9b99ce7">
                            <col style=" width: 300px;"></col>
                            <col style=" width: 142px;"></col>
                            <tr class="style_2" valign="top">
                                <td>
                                    <div class="style_3" id="AUTOGENBOOKMARK_2_a1534fa9-8bf2-4f94-a4a9-6f05e2b40d88">Aantal stories</div>
                                </td>
                                <td>
                                    <div class="style_4" style=" text-align:right;">23</div>
                                </td>
                            </tr>
                            <tr class="style_2" valign="top">
                                <td>
                                    <div class="style_3" id="AUTOGENBOOKMARK_3_854ce0a0-67f9-4b5e-accc-51f51fc6d82e">Aantal stories met LTCs</div>
                                </td>
                                <td>
                                    <div class="style_4" style=" text-align:right;">20</div>
                                </td>
                            </tr>
                            <tr class="style_2" valign="top">
                                <td>
                                    <div class="style_3" id="AUTOGENBOOKMARK_4_0ec27541-c30c-4f75-a5f3-21d8cb0ef193">Aantal stories met te weinig LTCs</div>
                                </td>
                                <td>
                                    <div class="style_4" style=" text-align:right;">1</div>
                                </td>
                            </tr>
                        </table>
                    </div>
                    <div id="__bookmark_2">
                        <table class="style_5" style="border-collapse: collapse; empty-cells: show; width: 4.24in;" id="AUTOGENBOOKMARK_5_eda145ca-ac28-4328-95c8-a0a6c7775059">
                            <col style=" width: 300px;"></col>
                            <col style=" width: 142px;"></col>
                            <tr class="style_2" valign="top">
                                <td>
                                    <div class="style_3" id="AUTOGENBOOKMARK_6_10245332-19f1-436d-94c8-332b8ebf791b">Aantal stories gereviewd</div>
                                </td>
                                <td class="style_2">
                                    <div class="style_4" style=" text-align:right;">23</div>
                                </td>
                            </tr>
                            <tr class="style_2" valign="top">
                                <td class="style_2">
                                    <div class="style_3" id="AUTOGENBOOKMARK_7_cc77e1ab-6ea5-442d-9315-1b304f192469">Aantal stories goedgekeurd</div>
                                </td>
                                <td class="style_2">
                                    <div class="style_4" style=" text-align:right;">23</div>
                                </td>
                            </tr>
                            <tr class="style_2" valign="top">
                                <td class="style_2">
                                    <div class="style_3" id="AUTOGENBOOKMARK_8_1313ade1-1f00-4830-bcb0-807dbf09593f">Aantal stories afgekeurd</div>
                                </td>
                                <td class="style_2">
                                    <div class="style_4" style=" text-align:right;">0</div>
                                </td>
                            </tr>
                            <tr class="style_2" valign="top">
                                <td class="style_2">
                                    <div class="style_3" id="AUTOGENBOOKMARK_9_d1dfa975-ab2b-4741-8cd7-c9712f2b55e1">Aantal LTCs</div>
                                </td>
                                <td class="style_2">
                                    <div class="style_4" style=" text-align:right;">182</div>
                                </td>
                            </tr>
                            <tr class="style_2" valign="top">
                                <td class="style_2">
                                    <div class="style_3" id="AUTOGENBOOKMARK_10_75bdaaaa-27fb-474d-a660-e9d2eafdde4e">Aantal LTCs gereviewd</div>
                                </td>
                                <td class="style_2">
                                    <div class="style_4" style=" text-align:right;">182</div>
                                </td>
                            </tr>
                            <tr class="style_2" valign="top">
                                <td class="style_6">
                                    <div class="style_3" id="AUTOGENBOOKMARK_11_aaf0840d-f80e-4d98-bec4-22ae572fa3de">Aantal LTCs goedgekeurd</div>
                                </td>
                                <td>
                                    <div class="style_4" style=" text-align:right;">182</div>
                                </td>
                            </tr>
                            <tr class="style_2" valign="top">
                                <td>
                                    <div class="style_3" id="AUTOGENBOOKMARK_12_48a92b7f-6400-4cdb-aed4-306038b9b70b">Aantal LTCs afgekeurd</div>
                                </td>
                                <td>
                                    <div class="style_4" style=" text-align:right;">0</div>
                                </td>
                            </tr>
                        </table>
                    </div>
                    <div id="__bookmark_3">
                        <table class="style_7" style="border-collapse: collapse; empty-cells: show; width: 4.229in;" id="AUTOGENBOOKMARK_13_64637aea-619a-4075-bbb2-a637ec73fdf8">
                            <col style=" width: 300px;"></col>
                            <col style=" width: 142px;"></col>
                            <tr class="style_2" valign="top">
                                <td class="style_2">
                                    <div class="style_3" id="AUTOGENBOOKMARK_14_a5e2c383-e2ab-4936-908f-648b387a9749">Aantal LTCs dat geimplementeerd moeten zijn</div>
                                </td>
                                <td class="style_2">
                                    <div class="style_4" style=" text-align:right;">165</div>
                                </td>
                            </tr>
                            <tr class="style_2" valign="top">
                                <td class="style_2">
                                    <div class="style_3" id="AUTOGENBOOKMARK_15_9089a210-503d-4b7f-bc2c-1a0e46e9b75e">Aantal geimplementeerde LTCs</div>
                                </td>
                                <td class="style_2">
                                    <div class="style_4" style=" text-align:right;">111</div>
                                </td>
                            </tr>
                            <tr class="style_2" valign="top">
                                <td class="style_2">
                                    <div class="style_3" id="AUTOGENBOOKMARK_16_b05ae0ae-fab2-496c-a768-18f96ae76118">Aantal niet geimplementeerde LTCs</div>
                                </td>
                                <td class="style_2">
                                    <div class="style_4" style=" text-align:right;">71</div>
                                </td>
                            </tr>
                            <tr class="style_2" valign="top">
                                <td class="style_2">
                                    <div class="style_3" id="AUTOGENBOOKMARK_17_b20001aa-23c5-47ea-a837-ad24bbc94fd8">Aantal LTCs met missende implementatie</div>
                                </td>
                                <td class="style_2">
                                    <div class="style_4" style=" text-align:right;">54</div>
                                </td>
                            </tr>
                            <tr class="style_2" valign="top">
                                <td class="style_6">
                                    <div class="style_3" id="AUTOGENBOOKMARK_18_f4e8f298-99a6-4700-a17e-eee3d20b3827">Aantal 'onnodige' implementaties</div>
                                </td>
                                <td>
                                    <div class="style_4" style=" text-align:right;">0</div>
                                </td>
                            </tr>
                            <tr class="style_2" valign="top">
                                <td>
                                    <div class="style_3" id="AUTOGENBOOKMARK_19_a256ae79-3286-429c-afb5-89494b96d00a">Aantal handmatige LTCs</div>
                                </td>
                                <td>
                                    <div class="style_4" style=" text-align:right;">12</div>
                                </td>
                            </tr>
                            <tr class="style_2" valign="top">
                                <td>
                                    <div class="style_3" id="AUTOGENBOOKMARK_20_cee749e8-b95b-49e7-bb1d-718c97acb3d3">Aantal nooit geteste handmatige LTCs</div>
                                </td>
                                <td>
                                    <div class="style_4" style=" text-align:right;">12</div>
                                </td>
                            </tr>
                        </table>
                    </div>
                    <div style=" overflow:hidden;">REPORT_URL=[jdbc:mysql://mysql:3306/report]</div>
                </td>
            </tr>
            <tr>
                <td>
                    <div style=" overflow:hidden;">1 sep. 2015 16:03</div>
                </td>
            </tr>
        </table>
    </body>
</html>
"""

SPRINT_PROGRESS_REPORT_HTML = """
<table>
    <table>
        <table>
            <tr>
                <td><div>Gerealiseerde punten in sprint:</div></td>
                <td><div>20</div></td>
            </tr>
            <tr>
                <td><div>Geplande punten in sprint:</div></td>
                <td><div>23,5</div></td>
            </tr>
            <tr>
                <td><div>Startdatum sprint:</div></td>
                <td><div>01-02-2013</div></td>
            </tr>
            <tr>
                <td><div>Einddatum sprint:</div></td>
                <td><div>21-02-2013</div></td>
            </tr>
            <tr>
                <td><div>Vandaag is dag:</div></td>
                <td><div>14</div></td>
            </tr>
            <tr>
                <td><div>Prognose sprint:</div></td>
                <td><div>21</div></td>
            </tr>
        </table>
    </table>
</table>
"""

SPRINT_PROGRESS_REPORT_HTML_MISSING_DATA = """
<html>
    <body class="style_0" style=" margin:0px;">
        <table cellpadding="0" style="empty-cells: show; border-collapse:collapse; width:284.29999999999995mm; overflow: hidden; table-layout:fixed;">
            <col></col>
            <tr>
                <td></td>
            </tr>
            <tr>
                <td valign="top">
                    <table class="style_1" style="border-collapse: collapse; empty-cells: show; width: 100%; overflow:hidden; table-layout:fixed;" id="__bookmark_1">
                        <col style=" width: 2%;"></col>
                        <col style=" width: 10%;"></col>
                        <col style=" width: 61%;"></col>
                        <col style=" width: 22%;"></col>
                        <col style=" width: 10%;"></col>
                        <tr valign="top" align="center">
                            <th colspan="3" style=" overflow:hidden;">
                                <div class="style_3" style=" text-align:left; overflow:hidden;">Voortgang sprint 'null'</div>
                            </th>
                            <th colspan="2" style=" overflow:hidden;">
                                <table class="style_1" style="border-collapse: collapse; empty-cells: show; width: 100%; overflow:hidden; table-layout:fixed;" id="AUTOGENBOOKMARK_1_510b0e9b-1ffe-44ea-b3ed-ebca46dd9a2d">
                                    <col style=" width: 69%;"></col>
                                    <col style=" width: 31%;"></col>
                                    <tr valign="top">
                                        <td class="style_4" style=" overflow:hidden;">
                                            <div class="style_5" id="AUTOGENBOOKMARK_2_7273e4ed-51e4-4ccc-aba5-60b7b6ab13e2" style=" text-align:left;">Gerealiseerde punten in sprint:</div>
                                        </td>
                                        <td class="style_4" style=" overflow:hidden;">
                                            <div class="style_6" style=" text-align:right;">
                                                <div style="visibility:hidden">&#xa0;</div>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr valign="top">
                                        <td class="style_4" style=" overflow:hidden;">
                                            <div class="style_5" id="AUTOGENBOOKMARK_3_9f190811-e3aa-4216-9c35-88ce99fe6ef0" style=" text-align:left;">Geplande punten in sprint:</div>
                                        </td>
                                        <td class="style_4" style=" overflow:hidden;">
                                            <div class="style_6" style=" text-align:right;">
                                                <div style="visibility:hidden">&#xa0;</div>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr valign="top">
                                        <td class="style_4" style=" overflow:hidden;">
                                            <div class="style_7" id="AUTOGENBOOKMARK_4_83cae1b8-fee6-4493-b684-174ac426ae66" style=" text-align:left;">Startdatum sprint:</div>
                                        </td>
                                        <td class="style_4" style=" overflow:hidden;">
                                            <div class="style_6" style=" text-align:right;">null-null-null</div>
                                        </td>
                                    </tr>
                                    <tr valign="top">
                                        <td class="style_4" style=" overflow:hidden;">
                                            <div class="style_7" id="AUTOGENBOOKMARK_5_31d4501b-9a5b-45cb-a783-8adbb621d6a7" style=" text-align:left;">Einddatum sprint:</div>
                                        </td>
                                        <td class="style_8" style=" overflow:hidden;">
                                            <div class="style_9" style=" text-align:right;">null-null-null</div>
                                        </td>
                                    </tr>
                                    <tr valign="top">
                                        <td class="style_4" style=" overflow:hidden;">
                                            <div class="style_7" id="AUTOGENBOOKMARK_6_588c7460-0f93-483a-9f68-374f98621dda" style=" text-align:left;">Vandaag is dag:</div>
                                        </td>
                                        <td class="style_4" style=" overflow:hidden;">
                                            <div class="style_6" style=" text-align:right;">
                                                <div style="visibility:hidden">&#xa0;</div>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr valign="top">
                                        <td class="style_4" style=" overflow:hidden;">
                                            <div class="style_7" id="AUTOGENBOOKMARK_7_b7adfece-0388-4107-bef4-db669dbd2ff5" style=" text-align:left;">Prognose sprint:</div>
                                        </td>
                                        <td class="style_4" style=" overflow:hidden;">
                                            <div class="style_6" style=" text-align:right;">NaN</div>
                                        </td>
                                    </tr>
                                </table>
                            </th>
                        </tr>
                        <tr valign="top" align="center">
                            <th style=" overflow:hidden;"></th>
                            <th style=" overflow:hidden;"></th>
                            <th style=" overflow:hidden;">
                                <div id="AUTOGENBOOKMARK_8_e3203f33-e867-4c16-bb34-8c92b1d195ad">&#xa0;</div>
                            </th>
                            <th style=" overflow:hidden;"></th>
                            <th style=" overflow:hidden;"></th>
                        </tr>
                        <tr valign="top" align="center">
                            <th style=" overflow:hidden;"></th>
                            <th class="style_4" style=" overflow:hidden;">
                                <div class="style_10" id="AUTOGENBOOKMARK_9_e6d73e14-3aa3-4912-b1f8-a0c5ddb3905a" style=" text-align:left;">Nummer</div>
                            </th>
                            <th class="style_4" style=" overflow:hidden;">
                                <div class="style_10" id="AUTOGENBOOKMARK_10_f7bdd47c-baef-47e0-a5ac-ca54c96f3ecc" style=" text-align:left;">Functie</div>
                            </th>
                            <th class="style_4" style=" overflow:hidden;">
                                <div class="style_11" id="AUTOGENBOOKMARK_11_008f645d-f1ff-4335-8f06-8618d0e8bfee" style=" text-align:right;">Voortgang (taken)</div>
                            </th>
                            <th class="style_4" style=" overflow:hidden;">
                                <div class="style_11" id="AUTOGENBOOKMARK_12_a5beefb2-c414-4608-afc6-b38167430bd5" style=" text-align:right;">Punten</div>
                            </th>
                        </tr>
                        <tr valign="top">
                            <td style=" overflow:hidden;"></td>
                            <td style=" overflow:hidden;"></td>
                            <td style=" overflow:hidden;"></td>
                            <td style=" overflow:hidden;"></td>
                            <td style=" overflow:hidden;"></td>
                        </tr>
                    </table>
                    <div style=" overflow:hidden;">REPORT_URL=[jdbc:mysql://mysql:3306/report]</div>
                </td>
            </tr>
            <tr>
                <td>
                    <div style="overflow:hidden; height:0.5in">
                        <div style=" overflow:hidden;">1 sep. 2015 19:14</div>
                    </div>
                </td>
            </tr>
        </table>
    </body>
</html>"""

MANUAL_TEST_EXECUTION_HTML_NEVER_EXECUTED = """
<html>
    <body class="style_0" style=" margin:0px;">
        <table cellpadding="0" style="empty-cells: show; border-collapse:collapse; width:100%;">
            <col></col>
            <tr>
                <td>
                    <table style="border-collapse: collapse; empty-cells: show; width: 100%;" id="AUTOGENBOOKMARK_1_9d7aa414-e6db-4225-afd1-419c590f4948">
                        <col></col>
                        <tr valign="top">
                            <td class="style_1" align="center" valign="top">
                                <div>
                                    <img class="style_2" id="AUTOGENBOOKMARK_2_7c2753d2-5a5b-48e7-b4cd-bbea6f086bc3" src="/birt/preview?__sessionId=20150901_201252_235&amp;__imageid=design3dd5095814f83cd057312.png" alt="" style=" width: 45px; height: 76px;display: block;"></img>
                                </div>
                            </td>
                        </tr>
                        <tr class="style_3" style=" height: 0.5in;" valign="top">
                            <td></td>
                        </tr>
                        <tr valign="top">
                            <td>
                                <div class="style_4" id="AUTOGENBOOKMARK_3_30e5bcb5-2413-438b-9969-9860aff0830a" style=" text-align:center;">Handmatige testuitvoering</div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr>
                <td valign="top">
                    <div style=" overflow:hidden;">De versies in de dropdown zijn alle versies waarvoor handmatige testen uitgevoerd zijn. Logische testgevallen komen voor in de rapportage wanneer ze een story, die voldoet aan de volgende voorwaarden, testen (Issue Link: Logical Test Case tests Story): <ul><li>De story is geen bugfix (Bug fix: No)</li><li>Er wordt aan de story gewerkt of de story is in een eerdere sprint opgeleverd: <ul><li>De story is onderhanden werk (Status: In Progress) <i>of</i></li><li>De story is afgerond (Status: Resolved, Closed en Resolution: Fixed)</li></ul></li></ul>
                    </div>
                    <table class="style_5" style="border-collapse: collapse; empty-cells: show; width: 3.885in;" id="__bookmark_1">
                        <col style=" width: 1.25in;"></col>
                        <col style=" width: 1.25in;"></col>
                        <col style=" width: 1.385in;"></col>
                        <tr valign="top" align="center">
                            <th class="style_7">
                                <div class="style_8" id="AUTOGENBOOKMARK_4_d9eeb2e1-d50e-4be2-843a-e4caea4c7817" style=" text-align:left;">LTC</div>
                            </th>
                            <th class="style_7">
                                <div class="style_8" id="AUTOGENBOOKMARK_5_20669bb1-e077-4cbd-abb4-34b106e771a1" style=" text-align:left;">Aanmaakdatum</div>
                            </th>
                            <th class="style_7">
                                <div class="style_8" id="AUTOGENBOOKMARK_6_fb50b59e-8477-4bef-984f-e2c8e20c22cd" style=" text-align:left;">Laatst geslaagd</div>
                            </th>
                        </tr>
                        <tr valign="top">
                            <td class="style_7">
                                <div>BSNKEID-387</div>
                            </td>
                            <td class="style_7">
                                <div>2015-8-4</div>
                            </td>
                            <td class="style_7">
                                <div>
                                    <div style="visibility:hidden">&#xa0;</div>
                                </div>
                            </td>
                        </tr>
                        <tr valign="top">
                            <td class="style_7">
                                <div>BSNKEID-547</div>
                            </td>
                            <td class="style_7">
                                <div>2015-8-27</div>
                            </td>
                            <td class="style_7">
                                <div>
                                    <div style="visibility:hidden">&#xa0;</div>
                                </div>
                            </td>
                        </tr>
                        <tr valign="top">
                            <td class="style_7">
                                <div>BSNKEID-548</div>
                            </td>
                            <td class="style_7">
                                <div>2015-8-27</div>
                            </td>
                            <td class="style_7">
                                <div>
                                    <div style="visibility:hidden">&#xa0;</div>
                                </div>
                            </td>
                        </tr>
                        <tr valign="top">
                            <td class="style_7">
                                <div>BSNKEID-549</div>
                            </td>
                            <td class="style_7">
                                <div>2015-8-27</div>
                            </td>
                            <td class="style_7">
                                <div>
                                    <div style="visibility:hidden">&#xa0;</div>
                                </div>
                            </td>
                        </tr>
                        <tr valign="top">
                            <td class="style_7">
                                <div>BSNKEID-550</div>
                            </td>
                            <td class="style_7">
                                <div>2015-8-27</div>
                            </td>
                            <td class="style_7">
                                <div>
                                    <div style="visibility:hidden">&#xa0;</div>
                                </div>
                            </td>
                        </tr>
                        <tr valign="top">
                            <td class="style_7">
                                <div>BSNKEID-551</div>
                            </td>
                            <td class="style_7">
                                <div>2015-8-27</div>
                            </td>
                            <td class="style_7">
                                <div>
                                    <div style="visibility:hidden">&#xa0;</div>
                                </div>
                            </td>
                        </tr>
                        <tr valign="top">
                            <td class="style_7">
                                <div>BSNKEID-552</div>
                            </td>
                            <td class="style_7">
                                <div>2015-8-27</div>
                            </td>
                            <td class="style_7">
                                <div>
                                    <div style="visibility:hidden">&#xa0;</div>
                                </div>
                            </td>
                        </tr>
                        <tr valign="top">
                            <td class="style_7">
                                <div>BSNKEID-553</div>
                            </td>
                            <td class="style_7">
                                <div>2015-8-27</div>
                            </td>
                            <td class="style_7">
                                <div>
                                    <div style="visibility:hidden">&#xa0;</div>
                                </div>
                            </td>
                        </tr>
                        <tr valign="top">
                            <td class="style_7">
                                <div>BSNKEID-554</div>
                            </td>
                            <td class="style_7">
                                <div>2015-8-27</div>
                            </td>
                            <td class="style_7">
                                <div>
                                    <div style="visibility:hidden">&#xa0;</div>
                                </div>
                            </td>
                        </tr>
                        <tr valign="top">
                            <td class="style_7">
                                <div>BSNKEID-555</div>
                            </td>
                            <td class="style_7">
                                <div>2015-8-27</div>
                            </td>
                            <td class="style_7">
                                <div>
                                    <div style="visibility:hidden">&#xa0;</div>
                                </div>
                            </td>
                        </tr>
                        <tr valign="top">
                            <td class="style_7">
                                <div>BSNKEID-556</div>
                            </td>
                            <td class="style_7">
                                <div>2015-8-27</div>
                            </td>
                            <td class="style_7">
                                <div>
                                    <div style="visibility:hidden">&#xa0;</div>
                                </div>
                            </td>
                        </tr>
                        <tr valign="top">
                            <td class="style_7">
                                <div>BSNKEID-557</div>
                            </td>
                            <td class="style_7">
                                <div>2015-8-28</div>
                            </td>
                            <td class="style_7">
                                <div>
                                    <div style="visibility:hidden">&#xa0;</div>
                                </div>
                            </td>
                        </tr>
                        <tr valign="top">
                            <td></td>
                            <td></td>
                            <td></td>
                        </tr>
                    </table>
                    <div style=" overflow:hidden;">REPORT_URL=[jdbc:mysql://mysql:3306/report]</div>
                </td>
            </tr>
            <tr>
                <td>
                    <div style=" overflow:hidden;">1 sep. 2015 20:12</div>
                </td>
            </tr>
        </table>
    </body>
</html>
"""

MANUAL_TEST_EXECUTION_HTML = """
<html>
    <body class="style_0" style=" margin:0px;">
        <table cellpadding="0" style="empty-cells: show; border-collapse:collapse; width:100%;">
            <col></col>
            <tr>
                <td>
                    <table style="border-collapse: collapse; empty-cells: show; width: 100%;" id="AUTOGENBOOKMARK_1_e31e0d58-a361-401b-ac5c-489087be0029">
                        <col></col>
                        <tr valign="top">
                            <td class="style_1" align="center" valign="top">
                                <div>
                                    <img class="style_2" id="AUTOGENBOOKMARK_2_dc56fb6a-c976-48b7-89d1-bc8ab0bb97a2" src="/birt/preview?__sessionId=20150902_070128_741&amp;__imageid=design6c65238d14f838712cd2.png" alt="" style=" width: 45px; height: 76px;display: block;"></img>
                                </div>
                            </td>
                        </tr>
                        <tr class="style_3" style=" height: 0.5in;" valign="top">
                            <td></td>
                        </tr>
                        <tr valign="top">
                            <td>
                                <div class="style_4" id="AUTOGENBOOKMARK_3_238c7265-c09c-4037-a2c0-e247773d7f09" style=" text-align:center;">Handmatige testuitvoering</div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr>
                <td valign="top">
                    <div style=" overflow:hidden;">De versies in de dropdown zijn alle versies waarvoor handmatige testen uitgevoerd zijn. Logische testgevallen komen voor in de rapportage wanneer ze een story, die voldoet aan de volgende voorwaarden, testen (Issue Link: Logical Test Case tests Story): <ul><li>De story is geen bugfix (Bug fix: No)</li><li>Er wordt aan de story gewerkt of de story is in een eerdere sprint opgeleverd: <ul><li>De story is onderhanden werk (Status: In Progress) <i>of</i></li><li>De story is afgerond (Status: Resolved, Closed en Resolution: Fixed)</li></ul></li></ul>
                    </div>
                    <table class="style_5" style="border-collapse: collapse; empty-cells: show; width: 3.885in;" id="__bookmark_1">
                        <col style=" width: 1.25in;"></col>
                        <col style=" width: 1.25in;"></col>
                        <col style=" width: 1.385in;"></col>
                        <tr valign="top" align="center">
                            <th class="style_7">
                                <div class="style_8" id="AUTOGENBOOKMARK_4_fc44f98c-0129-40d0-9166-453bd163a77c" style=" text-align:left;">LTC</div>
                            </th>
                            <th class="style_7">
                                <div class="style_8" id="AUTOGENBOOKMARK_5_e2a2253d-32a3-4864-bd46-50f8fe56e6c0" style=" text-align:left;">Aanmaakdatum</div>
                            </th>
                            <th class="style_7">
                                <div class="style_8" id="AUTOGENBOOKMARK_6_d988c87c-cf0a-493a-a197-3361aa3f03f1" style=" text-align:left;">Laatst geslaagd</div>
                            </th>
                        </tr>
                        <tr valign="top">
                            <td class="style_7">
                                <div>ISZW-2117</div>
                            </td>
                            <td class="style_7">
                                <div>2015-7-20</div>
                            </td>
                            <td class="style_7">
                                <div>2015-8-19</div>
                            </td>
                        </tr>
                        <tr valign="top">
                            <td class="style_7">
                                <div>ISZW-2230</div>
                            </td>
                            <td class="style_7">
                                <div>2015-7-23</div>
                            </td>
                            <td class="style_7">
                                <div>2015-8-19</div>
                            </td>
                        </tr>
                        <tr valign="top">
                            <td class="style_7">
                                <div>ISZW-2232</div>
                            </td>
                            <td class="style_7">
                                <div>2015-7-23</div>
                            </td>
                            <td class="style_7">
                                <div>2015-8-19</div>
                            </td>
                        </tr>
                        <tr valign="top">
                            <td></td>
                            <td></td>
                            <td></td>
                        </tr>
                    </table>
                    <div style=" overflow:hidden;">REPORT_URL=[jdbc:mysql://mysql:3306/report]</div>
                </td>
            </tr>
            <tr>
                <td>
                    <div style=" overflow:hidden;">2 sep. 2015 07:01</div>
                </td>
            </tr>
        </table>
    </body>
</html>"""


class BirtUnderTest(Birt):  # pylint: disable=too-few-public-methods
    """ Override the soup method to return a fixed HTML fragment. """
    html = ''

    def soup(self, url):  # pylint: disable=unused-argument
        """ Return the static html. """
        if self.html == 'raise':
            raise urllib2.URLError('Birt down')
        else:
            return bs4.BeautifulSoup(self.html, "html.parser")


class BirtTest(unittest.TestCase):
    """ Unit tests for the Birt class. """

    def setUp(self):
        self.__birt = BirtUnderTest('http://birt/')

    def test_url(self):
        """ Test the url. """
        self.assertEqual('http://birt/birt/', self.__birt.url())

    def test_test_design_url(self):
        """ Test the test design url. """
        self.assertEqual('http://birt/birt/preview?__report=reports/test_design.rptdesign',
                         self.__birt.test_design_url())

    def test_whats_missing_url(self):
        """ Test the what's missing report url. """
        self.assertEqual('http://birt/birt/preview?__report=reports/whats_missing.rptdesign',
                         self.__birt.whats_missing_url())

    def test_manual_test_url_trunk(self):
        """ Test the manual test execution url for the trunk. """
        self.assertEqual(
            'http://birt/birt/preview?__report=reports/manual_test_execution_report.rptdesign&version=trunk',
            self.__birt.manual_test_execution_url())

    def test_manual_test_url_version(self):
        """ Test the manual test execution url with a specific version. """
        self.assertEqual('http://birt/birt/preview?__report=reports/manual_test_execution_report.rptdesign&version=1',
                         self.__birt.manual_test_execution_url('1'))

    def test_sprint_progress_url(self):
        """ Test the sprint progress url. """
        self.assertEqual('http://birt/birt/preview?__report=reports/sprint_voortgang.rptdesign',
                         self.__birt.sprint_progress_url())

    def test_nr_user_stories_with_sufficient_ltcs(self):
        """ Test that the number of user stories with sufficient number of logical test cases is correct. """
        self.__birt.html = TEST_DESIGN_HTML
        self.assertEqual(22, self.__birt.nr_user_stories_with_sufficient_ltcs())

    def test_nr_user_stories_with_sufficient_ltcs_on_error(self):
        """ Test that the number of user stories is -1 when Birt is unavailable. """
        self.__birt.html = 'raise'
        self.assertEqual(-1, self.__birt.nr_user_stories_with_sufficient_ltcs())

    def test_nr_automated_ltcs(self):
        """ Test the number of automated logical test cases is correct. """
        self.__birt.html = TEST_DESIGN_HTML
        self.assertEqual(111, self.__birt.nr_automated_ltcs())

    def test_nr_automated_ltcs_on_error(self):
        """ Test that the number of automated logical test cases is -1 when Birt is unavailable. """
        self.__birt.html = 'raise'
        self.assertEqual(-1, self.__birt.nr_automated_ltcs())

    def test_nr_user_stories(self):
        """ Test that the number of user stories is correct. """
        self.__birt.html = TEST_DESIGN_HTML
        self.assertEqual(23, self.__birt.nr_user_stories())

    def test_reviewed_user_stories(self):
        """ Test that the number of reviewed user stories is correct. """
        self.__birt.html = TEST_DESIGN_HTML
        self.assertEqual(23, self.__birt.reviewed_user_stories())

    def test_approved_user_stories(self):
        """ Test that the number of approved user stories is correct. """
        self.__birt.html = TEST_DESIGN_HTML
        self.assertEqual(23, self.__birt.approved_user_stories())

    def test_not_approved_user_stories(self):
        """ Test that the number of not approved user stories is correct. """
        self.__birt.html = TEST_DESIGN_HTML
        self.assertEqual(0, self.__birt.not_approved_user_stories())

    def test_nr_ltcs(self):
        """ Test that the number of logical test cases is correct. """
        self.__birt.html = TEST_DESIGN_HTML
        self.assertEqual(182, self.__birt.nr_ltcs())

    def test_reviewed_ltcs(self):
        """ Test that the number of reviewed logical test cases is correct. """
        self.__birt.html = TEST_DESIGN_HTML
        self.assertEqual(182, self.__birt.reviewed_ltcs())

    def test_approved_ltcs(self):
        """ Test that the number of approved logical test cases is correct. """
        self.__birt.html = TEST_DESIGN_HTML
        self.assertEqual(182, self.__birt.approved_ltcs())

    def test_not_approved_ltcs(self):
        """ Test that the number of not approved logical test cases is correct. """
        self.__birt.html = TEST_DESIGN_HTML
        self.assertEqual(0, self.__birt.not_approved_ltcs())

    def test_nr_ltcs_to_be_automated(self):
        """ Test that the number of logical test cases to be automated is correct. """
        self.__birt.html = TEST_DESIGN_HTML
        self.assertEqual(165, self.__birt.nr_ltcs_to_be_automated())

    def test_nr_manual_ltcs(self):
        """ Test that the number of manual logical test cases is correct. """
        self.__birt.html = MANUAL_TEST_EXECUTION_HTML
        self.assertEqual(3, self.__birt.nr_manual_ltcs('bulk'))

    def test_nr_manual_ltcs_on_error(self):
        """ Test that the number of manual logical test cases is -1 when Birt is not available. """
        self.__birt.html = 'raise'
        self.assertEqual(-1, self.__birt.nr_manual_ltcs('bulk'))

    def test_nr_manual_ltcs_too_old(self):
        """ Test that the number of manual logical test cases that have not been tested recently is correct. """
        self.__birt.html = MANUAL_TEST_EXECUTION_HTML
        self.assertEqual(3, self.__birt.nr_manual_ltcs_too_old('trunk', 7))

    def test_nr_manual_ltcs_too_old_on_error(self):
        """ Test that the number of manual logical test cases is -1 whe Birt is not available. """
        self.__birt.html = 'raise'
        self.assertEqual(-1, self.__birt.nr_manual_ltcs_too_old('trunk', 7))

    def test_no_date_manual_tests(self):
        """ Test that the date of the last manual test execution is correct. """
        self.__birt.html = MANUAL_TEST_EXECUTION_HTML_NEVER_EXECUTED
        date = self.__birt.date_of_last_manual_test()
        self.assertEqual(datetime.datetime(2015, 8, 4), date)

    def test_late_date_manual_tests(self):
        """ Test that the date of the last manual test execution is correct. """
        self.__birt.html = MANUAL_TEST_EXECUTION_HTML
        date = self.__birt.date_of_last_manual_test()
        self.assertEqual(datetime.datetime(2015, 8, 19), date)

    def test_date_of_last_manual_test_on_error(self):
        """ Test that the date of the last manual test execution is the min date when Birt is unavailable. """
        self.__birt.html = 'raise'
        self.assertEqual(-1, self.__birt.date_of_last_manual_test())


class BirtSprintProgressReportUnderTest(SprintProgressReport):  # pylint: disable=too-few-public-methods
    """ Override the soup method to return a fixed HTML fragment. """
    html = ''

    def soup(self, url):  # pylint: disable=unused-argument
        """ Return the static html. """
        return bs4.BeautifulSoup(self.html, "html.parser")


class BirtSprintProgressReportTest(unittest.TestCase):
    """ Unit tests for the Birt sprint progress report. """

    def setUp(self):
        self.__birt = BirtSprintProgressReportUnderTest('http://birt/')
        self.__birt.html = SPRINT_PROGRESS_REPORT_HTML

    def test_actual_velocity(self):
        """ Test that the actual velocity is the number of points realized per day so far. """
        self.assertEqual(20 / 14., self.__birt.actual_velocity())

    def test_planned_velocity(self):
        """ Test that the planned velocity is correct. """
        self.assertEqual(23.5 / 15, self.__birt.planned_velocity())

    def test_required_velocity(self):
        """ Test that the required velocity is correct. """
        self.assertEqual(3.5 / 2, self.__birt.required_velocity())

    def test_days_in_sprint_no_end_date(self):
        """ Test that the days in the sprint is zero when the end date is unknown. """
        self.__birt.html = SPRINT_PROGRESS_REPORT_HTML_MISSING_DATA
        self.assertEqual(0, self.__birt.days_in_sprint())

    def test_missing_velocity(self):
        """ Test that the actual velocity is zero when the data is missing. """
        self.__birt.html = SPRINT_PROGRESS_REPORT_HTML_MISSING_DATA
        self.assertEqual(0., self.__birt.actual_velocity())
