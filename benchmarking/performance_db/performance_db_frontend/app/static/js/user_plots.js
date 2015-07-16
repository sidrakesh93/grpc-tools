/*
 *
 * Copyright 2015, Google Inc.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met:
 *
 *     * Redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above
 * copyright notice, this list of conditions and the following disclaimer
 * in the documentation and/or other materials provided with the
 * distribution.
 *     * Neither the name of Google Inc. nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 */


/**
 * Function to populate all users' information in the plots
 * @param {string} userDataStr - user data in string format
*/
function populateInfo(userDataStr) {
  userDataStr = userDataStr.replace(/'/g, '\"');
  userDataStr = userDataStr.replace(/u"(?=[^:]+")/g, '\"');

  window.userData = jQuery.parseJSON(userDataStr);
  window.dateFormat = 'YYYY-MM-DD HH:mm:ss';
  window.earliestTime = new Date(2000, 0, 1);

  google.load('visualization', '1', {packages: ['corechart']});
  google.setOnLoadCallback(drawChartsOnLoad);

  /**
   * Function to draw charts on page load
  */
  function drawChartsOnLoad() {
    drawQpsChart(moment().subtract(1000, 'years'), moment());
    drawQpsPerCoreChart(moment().subtract(1000, 'years'), moment());
    drawLatChart(moment().subtract(1000, 'years'), moment());
    drawServerTimesChart(moment().subtract(1000, 'years'), moment());
    drawClientTimesChart(moment().subtract(1000, 'years'), moment());
  }

  /* Base options for charts */
  var baseOptions = {
    pointSize: 7,
    titleTextStyle: {
      fontSize: 30,
    },
    legend: {position: 'none'},
    curveType: 'function',
    hAxis: {
      title: 'Time',
      titleTextStyle: {
        fontSize: 25,
      },
    },
    vAxis: {
      titleTextStyle: {
        fontSize: 25,
      },
      viewWindowMode: 'explicit',
      viewWindow: {
        min: 0,
      }
    },
    explorer: {
      axis: 'horizontal',
      maxZoomIn: '0.001',
      maxZoomOut: '10',
    },
  };

  /**
   * Function to open the configuration information page
   * @param {Object} chart - Chart in which element has been selected
   * @param {Array} configs - Contains configuration information
  */
  function configOpener(chart, configs) {
    var selection = chart.getSelection();
    chart.setSelection([]);
    var row = selection[0].row;
    if (row != null) {
      window.open(
          '/configs/' +
          btoa(
              configs[row][0] + '%' +
              configs[row][1] + '%' +
              JSON.stringify(configs[row][2]) + '%' +
              JSON.stringify(configs[row][3]) + '%' +
              JSON.stringify(configs[row][4])),
          '_blank');
    }
  }

  /**
   * Function to get configuration array
   * @param {Array} item - Object containing config information
   * @return {Array} configArr - Array of config information
  */
  function getConfigArr(item) {
    var configArr = [
      item.test_name,
      item.tag,
      item.client_config,
      item.server_config,
      item.sys_info
    ];

    return configArr;
  }

  /**
   * Function to update date range in specified element
   * @param {string} element - Name of element to update the date range in
   * @param {Date} startDate - Start date in the range
   * @param {Date} endDate - End date in the range
   * @param {int} argsLen - Length of the arguments array
  */
  function updateRange(element, startDate, endDate, argsLen) {
    if (argsLen == 1) {
      $('#' + element).html('');
    } else {
      $('#' + element).html(startDate.toLocaleString() + ' - ' +
          endDate.toLocaleString());
    }
  }

  /**
   * Function for rendering the QPS chart
   * @param {Date} start - Start date of data
   * @param {Date} end - End date of data
  */
  function drawQpsChart(start, end) {
    var qpsArgs = [[{label: 'Time'}, {type: 'number', label: 'QPS'}]];

    // Earliest data date in given time range
    var startDate = new Date();
    // Latest data date in given time range
    var endDate = earliestTime;

    var configs = [];

    // Add data
    for (var i = 0; i < (userData.qpsData).length; i++) {
      item = (userData.qpsData)[i];

      var metricDate = new Date(item.timestamp);

      if (start <= metricDate && end >= metricDate) {
        qpsArgs.push([metricDate, item.qps]);
        configs.push(getConfigArr(item));

        if (metricDate < startDate) {
          startDate = metricDate;
        }
        if (metricDate > endDate) {
          endDate = metricDate;
        }
      }
    }

    // Data for the QPS chart
    var qpsData = google.visualization.arrayToDataTable(qpsArgs);

    var qpsOptions = jQuery.extend(true, {}, baseOptions);
    qpsOptions.title = 'Queries Per Second';
    qpsOptions.vAxis.title = 'Queries Per Second';

    // Draw QPS chart
    var chart = new google.visualization.LineChart(
        document.getElementById('chart-div-qps'));
    chart.draw(qpsData, qpsOptions);

    google.visualization.events.addListener(chart, 'select', function() {
      configOpener(chart, configs);
    });

    // Adding mouse events to change cursor
    google.visualization.events.addListener(chart, 'onmouseover', function() {
      $('#chart-div-qps').css('cursor', 'pointer');
    });

    google.visualization.events.addListener(chart, 'onmouseout', function() {
      $('#chart-div-qps').css('cursor', 'auto');
    });

    updateRange('qps-report-range span', startDate, endDate, qpsArgs.length);
  }

  /**
   * Function for rendering the QPS Per Core chart
   * @param {Date} start - Start date of data
   * @param {Date} end - End date of data
  */
  function drawQpsPerCoreChart(start, end) {
    var qpsPerCoreArgs = [[
      {label: 'Time'},
      {type: 'number', label: 'QPS Per Core'}
    ]];

    // Earliest data date in given time range
    var startDate = new Date();
    // Latest data date in given time range
    var endDate = earliestTime;

    var configs = [];

    // Add data

    for (var i = 0; i < (userData.qpsPerCoreData).length; i++) {
      item = (userData.qpsPerCoreData)[i];

      var metricDate = new Date(item.timestamp);

      if (start <= metricDate && end >= metricDate) {
        qpsPerCoreArgs.push([metricDate, item.qps_per_core]);
        configs.push(getConfigArr(item));

        if (metricDate < startDate) {
          startDate = metricDate;
        }
        if (metricDate > endDate) {
          endDate = metricDate;
        }
      }
    }

    // Data for QPS per core chart
    var qpsPerCoreData = google.visualization.arrayToDataTable(qpsPerCoreArgs);

    var qpsPerCoreOptions = jQuery.extend(true, {}, baseOptions);
    qpsPerCoreOptions.title = 'QPS Per Core';
    qpsPerCoreOptions.vAxis.title = 'QPS Per Core';

    // Draw QPS per core chart
    var chart = new google.visualization.LineChart(
        document.getElementById('chart-div-qps-per-core'));
    chart.draw(qpsPerCoreData, qpsPerCoreOptions);

    google.visualization.events.addListener(chart, 'select', function() {
      configOpener(chart, configs);
    });

    // Adding mouse events to change cursor
    google.visualization.events.addListener(chart, 'onmouseover', function() {
      $('#chart-div-qps-per-core').css('cursor', 'pointer');
    });

    google.visualization.events.addListener(chart, 'onmouseout', function() {
      $('#chart-div-qps-per-core').css('cursor', 'auto');
    });

    updateRange('qps-per-core-report-range span', startDate, endDate,
        qpsPerCoreArgs.length);
  }

  /**
   * Function for rendering the Latencies chart
   * @param {Date} start - Start date of data
   * @param {Date} end - End date of data
  */
  function drawLatChart(start, end) {
    var latArgs = [[
      {label: 'Time'},
      {type: 'number', label: '50th Percentile Latency'},
      {type: 'number', label: '90th Percentile Latency'},
      {type: 'number', label: '95th Percentile Latency'},
      {type: 'number', label: '99th Percentile Latency'},
      {type: 'number', label: '99.9th Percentile Latency'}
    ]];

    // Earliest data date in given time range
    var startDate = new Date();
    // Latest data date in given time range
    var endDate = earliestTime;

    var configs = [];

    // Add data

    for (var i = 0; i < (userData.latData).length; i++) {
      item = (userData.latData)[i];

      var metricDate = new Date(item.timestamp);

      if (start <= metricDate && end >= metricDate) {
        latArgs.push([
          metricDate,
          item.lat.perc_lat_50,
          item.lat.perc_lat_90,
          item.lat.perc_lat_95,
          item.lat.perc_lat_99,
          item.lat.perc_lat_99_point_9
        ]);
        configs.push(getConfigArr(item));

        if (metricDate < startDate) {
          startDate = metricDate;
        }
        if (metricDate > endDate) {
          endDate = metricDate;
        }
      }
    }

    // Data for the latencies chart
    var latData = google.visualization.arrayToDataTable(latArgs);

    var latOptions = jQuery.extend(true, {}, baseOptions);
    latOptions.title = 'Percentile Latencies';
    latOptions.legend.position = 'right';
    latOptions.vAxis.title = 'Percentile Latencies (in \u03BCs)';
    latOptions.vAxis.logScale = true;

    // Draw latencies chart
    var chart = new google.visualization.LineChart(
        document.getElementById('chart-div-percentile-latencies'));
    chart.draw(latData, latOptions);

    google.visualization.events.addListener(chart, 'select', function() {
      configOpener(chart, configs);
    });

    //Adding mouse events to change cursor
    google.visualization.events.addListener(chart, 'onmouseover', function() {
      $('#chart-div-percentile-latencies').css('cursor', 'pointer');
    });

    google.visualization.events.addListener(chart, 'onmouseout', function() {
      $('#chart-div-percentile-latencies').css('cursor', 'auto');
    });

    updateRange('perc-lat-report-range span', startDate, endDate,
        latArgs.length);
  }

  var timesOptions = jQuery.extend(true, {}, baseOptions);
  timesOptions.legend.position = 'right';
  timesOptions.vAxis.title = 'Percentage Time';
  timesOptions.vAxis.format = '0.0%';

  var configs = [];

  /**
   * Function for rendering the Server times chart
   * @param {Date} start - Start date of data
   * @param {Date} end - End date of data
  */
  function drawServerTimesChart(start, end) {
    var serverTimesArgs = [[
      {label: 'Time'},
      {type: 'number', label: 'Server System Time'},
      {type: 'number', label: 'Server User Time'}
    ]];

    // Earliest data date in given time range
    var startDate = new Date();
    // Latest data date in given time range
    var endDate = earliestTime;

    var configs = [];

    // Add data

    for (var i = 0; i < (userData.timesData).length; i++) {
      item = (userData.timesData)[i];

      var metricDate = new Date(item.timestamp);

      if (start <= metricDate && end >= metricDate) {
        serverTimesArgs.push([
          metricDate,
          item.times.server_system_time / 100.0,
          item.times.server_user_time / 100.0
        ]);
        configs.push(getConfigArr(item));

        if (metricDate < startDate) {
          startDate = metricDate;
        }
        if (metricDate > endDate) {
          endDate = metricDate;
        }
      }
    }

    // Data for server times chart
    var serverTimesData = google.visualization.arrayToDataTable(
        serverTimesArgs);

    var serverTimesOptions = jQuery.extend(true, {}, timesOptions);
    serverTimesOptions.title = 'Server Times';

    var formatter = new google.visualization.NumberFormat({pattern: '0.0%'});
    formatter.format(serverTimesData, 1);
    formatter.format(serverTimesData, 2);

    // Draw server times chart
    var chart = new google.visualization.LineChart(
        document.getElementById('chart-div-server-times'));
    chart.draw(serverTimesData, serverTimesOptions);

    google.visualization.events.addListener(chart, 'select', function() {
      configOpener(chart, configs);
    });

    // Adding mouse events to change cursor
    google.visualization.events.addListener(chart, 'onmouseover', function() {
      $('#chart-div-server-times').css('cursor', 'pointer');
    });

    google.visualization.events.addListener(chart, 'onmouseout', function() {
      $('#chart-div-server-times').css('cursor', 'auto');
    });

    updateRange('server-times-report-range span', startDate, endDate,
        serverTimesArgs.length);
  }

  /**
   * Function for rendering the Client times chart
   * @param {Date} start - Start date of data
   * @param {Date} end - End date of data
  */
  function drawClientTimesChart(start, end) {
    var clientTimesArgs = [[
      {label: 'Time'},
      {type: 'number', label: 'Client System Time'},
      {type: 'number', label: 'Client User Time'}
    ]];

    // Earliest data date in given time range
    var startDate = new Date();
    // Latest data date in given time range
    var endDate = earliestTime;

    var configs = [];

    for (var i = 0; i < (userData.timesData).length; i++) {
      item = (userData.timesData)[i];

      var metricDate = new Date(item.timestamp);

      if (start <= metricDate && end >= metricDate) {
        clientTimesArgs.push([
          metricDate,
          item.times.client_system_time / 100.0,
          item.times.client_user_time / 100.0
        ]);
        configs.push([
          item.test_name,
          item.tag,
          item.client_config,
          item.server_config,
          item.sys_info
        ]);

        if (metricDate < startDate) {
          startDate = metricDate;
        }
        if (metricDate > endDate) {
          endDate = metricDate;
        }
      }
    }

    // Data for client times chart
    var clientTimesData = google.visualization.arrayToDataTable(
        clientTimesArgs);

    var clientTimesOptions = jQuery.extend(true, {}, timesOptions);
    clientTimesOptions.title = 'Client Times';

    var formatter = new google.visualization.NumberFormat({pattern: '0.0%'});
    formatter.format(clientTimesData, 1);
    formatter.format(clientTimesData, 2);

    // Draw client times chart
    var chart = new google.visualization.LineChart(
        document.getElementById('chart-div-client-times'));
    chart.draw(clientTimesData, clientTimesOptions);

    google.visualization.events.addListener(chart, 'select', function() {
      configOpener(chart, configs);
    });

    // Adding mouse events to change cursor
    google.visualization.events.addListener(chart, 'onmouseover', function() {
      $('#chart-div-client-times').css('cursor', 'pointer');
    });

    google.visualization.events.addListener(chart, 'onmouseout', function() {
      $('#chart-div-client-times').css('cursor', 'auto');
    });

    updateRange('client-times-report-range span', startDate, endDate,
        clientTimesArgs.length);
  }

  /* Date range picker settings */
  var dateRangePickerSettings = {
    format: dateFormat,
    showDropdowns: true,
    timePicker: true,
    timePickerIncrement: 1,
    timePicker12Hour: false,
    timePickerSeconds: true,
    ranges: {
      'Today': [moment().startOf('day'), moment()],
      'Yesterday': [
        moment().subtract(1, 'days').startOf('day'),
        moment().subtract(1, 'days').endOf('day')
      ],
      'Last 7 Days': [moment().subtract(6, 'days'), moment()],
      'Last 30 Days': [moment().subtract(29, 'days'), moment()],
      'This Month': [moment().startOf('month'), moment().endOf('month')],
      'Last Month': [
        moment().subtract(1, 'month').startOf('month'),
        moment().subtract(1, 'month').endOf('month')
      ],
      'All Time': [moment().subtract(29, 'days'), moment()]
    },
    opens: 'left',
    drops: 'down',
    buttonClasses: ['btn', 'btn-sm'],
    applyClass: 'btn-primary',
    cancelClass: 'btn-default',
    separator: ' to ',
  };

  // Date range picker functionality
  $('#qps-report-range').daterangepicker(dateRangePickerSettings,
      function(start, end, label) {
        drawQpsChart(start, end);
      });
  $('#qps-per-core-report-range').daterangepicker(dateRangePickerSettings,
      function(start, end, label) {
        drawQpsPerCoreChart(start, end);
      });
  $('#perc-lat-report-range').daterangepicker(dateRangePickerSettings,
      function(start, end, label) {
        drawLatChart(start, end);
      });
  $('#server-times-report-range').daterangepicker(dateRangePickerSettings,
      function(start, end, label) {
        drawServerTimesChart(start, end);
      });
  $('#client-times-report-range').daterangepicker(dateRangePickerSettings,
      function(start, end, label) {
        drawClientTimesChart(start, end);
      });
}
