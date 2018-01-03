/* Copyright 2012-2018 Ministerie van Sociale Zaken en Werkgelegenheid
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

import Chart from 'chart.js';

// Derived from https://github.com/y-takey/chartjs-plugin-stacked100

(function(Chart) {
  var StackedLine100Plugin = {
    id: 'stackedline100',

    beforeInit: function(chartInstance, pluginOptions) {
      if (!pluginOptions.enable) return;

      var yAxes = chartInstance.options.scales.yAxes;

      yAxes.forEach(function(hash) { hash.stacked = true; hash.ticks.min = 0; hash.ticks.max = 100 });

      chartInstance.options.tooltips.callbacks.label = function(tooltipItem, data) {
        var datasetIndex = tooltipItem.datasetIndex,
          index = tooltipItem.index,
          yLabel = tooltipItem.yLabel;
        var datasetLabel = data.datasets[datasetIndex].label || '';

        return '' + datasetLabel + ': ' + yLabel + '% (' + data.originalData[datasetIndex][index] + ')';
      };
    },

    beforeUpdate: function(chartInstance, pluginOptions) {
      if (!pluginOptions.enable) return;

      var datasets = chartInstance.data.datasets;
      var allData = datasets.map(function(dataset) { return dataset.data });
      chartInstance.data.originalData = allData;

      var totals = Array.apply(null, new Array(allData[0].length)).map(function(el, i) {
        return allData.reduce(function(sum, data) { return sum + data[i] }, 0);
      });
      datasets.forEach(function(dataset) {
        dataset.data = dataset.data.map(function(val, i) {
          return Math.round(val * 1000 / totals[i]) / 10;
        });
      });
    }
  };

  Chart.pluginService.register(StackedLine100Plugin);
}).call(this, Chart);
