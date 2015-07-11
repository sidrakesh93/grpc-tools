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
 * Function to populate all users' information in the table
 * @param {Array} allUsersData - All user's data
 * @param {string} metricName - Name of the data metric
*/
function populateInfo(allUsersData, metricName) {
  window.allUsersData = allUsersData;
  window.metricName = metricName;
  window.dateFormat = 'YYYY-MM-DD HH:mm:ss';

  // Draw chart on load
  google.load('visualization', '1', {packages: ['corechart']});
  google.setOnLoadCallback(drawChartOnLoad);

  /** Function to draw charts on page load **/
  function drawChartOnLoad() {
    // Draw all data histogram
    drawChart(moment().subtract(1000, 'years'), moment());
  }

  /** String 'endswith' function **/
  if (typeof String.prototype.endsWith != 'function') {
    String.prototype.endsWith = function(suffix) {
      return this.indexOf(suffix, this.length - suffix.length) !== -1;
    };
  }

  /**
   * Function to format the date to ISO standard
   * @param {Date} date - Date object to format
   * @return {Date} formattedDate - Formatted date object
  */
  function formatDate(date) {
    formattedDate = moment(date).format(dateFormat);
    return formattedDate;
  }

  /**
   * Function to draw chart, gicen start and end time
   * @param {Date} start - The start date of data in the range
   * @param {Date} end - The end date of data in the range
  */
  function drawChart(start, end) {
    if (metricName.endsWith('Percentile Latency')) {
      metricName = metricName + ' (\u03BCs)';
    }

    var args = [[metricName]];

    var startDate = moment();
    var endDate = moment().subtract(1000, 'years');

    // Add data

    for (var i = 0; i < allUsersData.length; i++) {
      allUsersData[i] = allUsersData[i].replace(/'/g, '\"');
      allUsersData[i] = allUsersData[i].replace(/u"(?=[^:]+")/g, '\"');
      item = jQuery.parseJSON(allUsersData[i]);

      var metricDate = new Date(item.timestamp);

      if (start <= metricDate && end >= metricDate) {
        if (item.value != 0.0) {
          args.push([item.value]);
        }

        if (metricDate < startDate) {
          startDate = metricDate;
        }
        if (metricDate > endDate) {
          endDate = metricDate;
        }
      }
    }

    var errorHeader = document.getElementById('error-header');
    var chartDiv = document.getElementById('chart_div');

    if (args.length == 1) {
      // No data available
      errorHeader.innerHTML = 'Sorry, no data is available for the ' +
          'given time range';
      chartDiv.innerHTML = null;
    } else {
      errorHeader.innerHTML = null;
      var data = google.visualization.arrayToDataTable(args);

      // Options for chart
      var options = {
        legend: {position: 'none'},
        hAxis: {
          title: metricName,
          titleTextStyle: {
            fontSize: 25,
          },
        },
        vAxis: {
          title: 'Number of users',
          titleTextStyle: {
            fontSize: 25,
          },
        }
      };

      var chart = new google.visualization.Histogram(chartDiv);
      chart.draw(data, options);

      // Update date range in date range picker
      $('#report-range span').html(formatDate(startDate) + ' - ' +
          formatDate(endDate));
    }
  }

  /** Initializes date range picker **/
  $('#report-range').daterangepicker({
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
      'All Time': [moment().subtract(1000, 'years'), moment()]
    },
    opens: 'left',
    drops: 'down',
    buttonClasses: ['btn', 'btn-sm'],
    applyClass: 'btn-primary',
    cancelClass: 'btn-default',
    separator: ' to ',
  }, function(start, end, label) {
    drawChart(start, end);
  });
}
