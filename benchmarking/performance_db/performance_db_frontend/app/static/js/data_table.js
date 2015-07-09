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
 * @constructor
 * @param {Array} allUsersData - All user's data
*/
function populateInfo(allUsersData) {
  // Add data to table on load
  addDataToTable(allUsersData, moment().subtract(1000, 'years'), moment());

  /**
   * Function to add data to table
   * @constructor
   * @param {Array} allUsersData - All user's data
   * @param {Date} start - Start date of range of requested data
   * @param {Date} end - End date of range of requested data
  */
  function addDataToTable(allUsersData, start, end) {
    $('#metrics-table').bootstrapTable({});

    data = getData(allUsersData, start, end);
    $('#metrics-table').bootstrapTable('load', data);
  }

  /**
   * Custom sorter for time
   * @constructor
   * @param {string} a - First time string
   * @param {string} b - Second time string
  */
  function timeSorter(a, b) {
    var timeArr1 = a.split(/[ :\/]+/);
    var timeArr2 = b.split(/[ :\/]+/);

    var time1 = new Date(timeArr1[2], timeArr1[0], timeArr1[1],
                         timeArr1[3], timeArr1[4], timeArr1[5], 0);
    var time2 = new Date(timeArr2[2], timeArr2[0], timeArr2[1],
                         timeArr2[3], timeArr2[4], timeArr2[5], 0);

    if (time1 > time2) {
      return 1;
    }
    if (time1 < time2) {
      return -1;
    }
    return 0;
  }

  /**
   * Returns user records array
   * @constructor
   * @param {Array} allUsersData - All users' data
   * @param {Date} start - The start date of data in the range
   * @param {Date} end - The end date of data in the range
  */
  function getData(allUsersData, start, end) {
    var dataArr = [];

    // Earliest data date in given time range
    var startDate = moment();
    // Latest data date in given time range
    var endDate = moment().subtract(1000, 'years');

    for (i = 0; i < allUsersData.length; i++) {
      allUsersData[i] = allUsersData[i].replace(/'/g, '\"');
      allUsersData[i] = allUsersData[i].replace(/u"(?=[^:]+")/g, '\"');
      row = jQuery.parseJSON(allUsersData[i]);

      var rowDate = new Date(
          row.timestamp.year,
          row.timestamp.month - 1,
          row.timestamp.day,
          row.timestamp.hour,
          row.timestamp.min,
          row.timestamp.sec,
          0);

      // If in valid time range
      if (rowDate > start && rowDate < end) {
        dataArr.push({
          userId: '<a href="/plot-user/' + row.hashed_id + '">' +
              row.username + '</a>',
          timestamp: row.timestamp.month + '/' + row.timestamp.day + '/' +
              row.timestamp.year + ' ' + row.timestamp.hour + ':' +
              row.timestamp.min + ':' + row.timestamp.sec,
          testName: '<a id="config" href="/configs/' +
              btoa(row.test_name + '%' + row.tag + '%' +
                   JSON.stringify(row.client_config) + '%' +
                   JSON.stringify(row.server_config) + '%' +
                   JSON.stringify(row.sys_info)) +
              '" target="_blank">' + row.test_name + '</a>',
          qps: row.qps,
          qpsPerCore: row.qps_per_core,
          p50: row.perc_lat_50,
          p90: row.perc_lat_90,
          p95: row.perc_lat_95,
          p99: row.perc_lat_99,
          p99point9: row.perc_lat_99_point_9,
          serverSystemTime: row.server_system_time,
          serverUserTime: row.server_user_time,
          clientSystemTime: row.client_system_time,
          clientUserTime: row.client_user_time,
          tag: row.tag
        });
        if (rowDate < startDate) {
          startDate = rowDate;
        }
        if (rowDate > endDate) {
          endDate = rowDate;
        }
      }
    }

    // Update date range in date range picker
    $('#report-range span').html(moment(startDate).format(
        'MM/DD/YYYY, HH:mm:ss') + ' - ' + moment(endDate).format(
        'MM/DD/YYYY, HH:mm:ss'));

    return dataArr;
  }

  // Initializing date range picker
  $('#report-range').daterangepicker({
      format: 'MM/DD/YYYY, HH:mm:ss',
      showDropdowns: true,
      timePicker: true,
      timePickerIncrement: 1,
      timePicker12Hour: false,
      timePickerSeconds: true,
      ranges: {
          'Today': [moment().startOf('day'), moment()],
          'Yesterday': [moment().subtract(1, 'days').startOf('day'),
              moment().subtract(1, 'days').endOf('day')],
          'Last 7 Days': [moment().subtract(6, 'days'), moment()],
          'Last 30 Days': [moment().subtract(29, 'days'), moment()],
          'This Month': [moment().startOf('month'), moment().endOf('month')],
          'Last Month': [moment().subtract(1, 'month').startOf('month'),
              moment().subtract(1, 'month').endOf('month')],
          'All Time': [moment().subtract(29, 'days'), moment()]
      },
      opens: 'left',
      drops: 'down',
      buttonClasses: ['btn', 'btn-sm'],
      applyClass: 'btn-primary',
      cancelClass: 'btn-default',
      separator: ' to ',
  }, function(start, end, label) {
    addDataToTable(start, end);
  });
}
