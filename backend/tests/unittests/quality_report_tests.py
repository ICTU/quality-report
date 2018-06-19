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

import pathlib
import unittest
from unittest.mock import MagicMock, patch, call, ANY
import pkg_resources
import quality_report
from hqlib import formatting, report, filesystem
from hqlib.metric_source import CompactHistory


@patch.object(quality_report.configuration, 'project')
class ReporterTest(unittest.TestCase):
    """ Test case of Reporter class"""
    def test_init(self, mock_project):
        """ Test if configuration project function is called """
        reporter = quality_report.Reporter('folder')
        mock_project.assert_called_once_with('folder')
        self.assertTrue(reporter)

    @patch.object(filesystem, 'create_dir')
    @patch.object(filesystem, 'write_file')
    @patch.object(pkg_resources.ResourceManager, 'resource_listdir')
    @patch.object(formatting.json_formatter.MetricsFormatter, 'process')
    @patch.object(report.QualityReport, 'metrics')
    @patch.object(report.QualityReport, 'name')
    def test_create_report_with_empty_history(  # pylint: disable=too-many-arguments
            self, mock_name, mock_metrics, mock_process, mock_resource_listdir, mock_write_file, mock_create_dir,
            mock_project):
        """ Tests if it creates all report files and directories."""
        mock_name.return_value = 'QR Name'
        mock_metrics.return_value = MagicMock()
        mock_process.return_value = 'formatted report'
        mock_resource_listdir.return_value = []
        mock_create_dir.return_value = 'unimportant'
        mock_write_file.return_value = 'unimportant'
        mock_project.metric_sources.return_value = []

        reporter = quality_report.Reporter('folder').create_report('report_dir', True)
        report_dir = pathlib.Path('report_dir').resolve()

        self.assertTrue(all(b in mock_create_dir.call_args_list for b in [
            call(report_dir),
            call(report_dir / 'json'),
            call(report_dir / 'img'),
            call(report_dir / 'dist'),
            call(report_dir / 'chart'),
        ]))
        mock_resource_listdir.assert_has_calls([
            call('hqlib.app', 'img'),
            call('hqlib.app', 'dist'),
            call('hqlib.app', 'html')
        ])
        mock_write_file.assert_has_calls([
            call('formatted report', report_dir / 'json' / 'metrics.json', 'w', 'utf-8'),
            call('[]\n', report_dir / 'json' / 'meta_history.json', 'w', 'utf-8'),
            call(ANY, report_dir / 'json' / 'meta_data.json', 'w', 'utf-8'),
            call('', report_dir / 'json' / 'dates.txt', encoding=None, mode='w')
        ])
        self.assertEqual('QR Name', reporter.name())

    @patch.object(filesystem, 'create_dir')
    @patch.object(filesystem, 'write_file')
    @patch.object(pkg_resources.ResourceManager, 'resource_listdir')
    @patch.object(formatting.json_formatter.MetricsFormatter, 'process')
    @patch.object(report.QualityReport, 'metrics')
    @patch.object(report.QualityReport, 'name')
    def test_create_report_without_frontend(  # pylint: disable=too-many-arguments
            self, mock_name, mock_metrics, mock_process, mock_resource_listdir, mock_write_file, mock_create_dir,
            mock_project):
        """ Tests if it creates json report files and needed directories, but not frontend."""
        mock_name.return_value = 'QR Name'
        mock_metrics.return_value = MagicMock()
        mock_process.return_value = 'formatted report'
        mock_resource_listdir.return_value = []
        mock_create_dir.return_value = 'unimportant'
        mock_write_file.return_value = 'unimportant'
        mock_project.metric_sources.return_value = []

        reporter = quality_report.Reporter('folder').create_report('report_dir', False)
        report_dir = pathlib.Path('report_dir').resolve()

        mock_create_dir.assert_has_calls([
            call(report_dir),
            call(report_dir / 'json'),
            call(report_dir / 'chart'),
        ])

        self.assertTrue(report_dir / 'img' not in mock_create_dir.call_args_list)

        mock_resource_listdir.assert_not_called()

        mock_write_file.assert_has_calls([
            call('formatted report', report_dir / 'json' / 'metrics.json', 'w', 'utf-8'),
            call('[]\n', report_dir / 'json' / 'meta_history.json', 'w', 'utf-8'),
            call(ANY, report_dir / 'json' / 'meta_data.json', 'w', 'utf-8'),
            call('', report_dir / 'json' / 'dates.txt', encoding=None, mode='w')
        ])
        self.assertEqual('QR Name', reporter.name())

    @patch.object(filesystem, 'create_dir')
    @patch.object(filesystem, 'write_file')
    @patch.object(pkg_resources.ResourceManager, 'resource_listdir')
    @patch.object(formatting.json_formatter.MetricsFormatter, 'process')
    @patch.object(CompactHistory, 'filename')
    @patch.object(CompactHistory, 'add_report')
    def test_create_report_with_history_without_file_name(  # pylint: disable=too-many-arguments
            self, mock_add_report, mock_filename, mock_process, mock_resource_listdir, mock_write_file,
            mock_create_dir, mock_project):
        """ Tests if it does not add a history record when it has no history file name."""
        mock_filename.return_value = None
        mock_resource_listdir.return_value = []
        mock_process.return_value = 'formatted report'
        mock_project.return_value = MagicMock(metric_sources=MagicMock(return_value=[CompactHistory('')]))

        reporter = quality_report.Reporter('folder').create_report('report_dir')

        mock_filename.assert_called_once()
        mock_add_report.assert_not_called()
        mock_write_file.assert_called()
        mock_create_dir.assert_called()
        self.assertTrue(reporter)

    @patch.object(filesystem, 'create_dir')
    @patch.object(filesystem, 'write_file')
    @patch.object(pkg_resources.ResourceManager, 'resource_listdir')
    @patch.object(formatting.json_formatter.MetricsFormatter, 'process')
    @patch.object(CompactHistory, 'filename')
    @patch.object(CompactHistory, 'add_report')
    def test_create_report_with_valid_history(  # pylint: disable=too-many-arguments
            self, mock_add_report, mock_filename, mock_process, mock_resource_listdir, mock_write_file,
            mock_create_dir, mock_project):
        """ Tests if it does add a history record when it has history file name."""
        mock_filename.return_value = 'history.json'
        mock_process.return_value = 'formatted report'
        mock_resource_listdir.return_value = []
        mock_project.return_value = MagicMock(metric_sources=MagicMock(return_value=[CompactHistory('')]))

        reporter = quality_report.Reporter('folder').create_report('report_dir')

        mock_filename.assert_called_once()
        mock_add_report.assert_called_once_with(reporter)
        mock_write_file.assert_called()
        mock_create_dir.assert_called()
        self.assertTrue(reporter)
