/**
 * Function to populate all users' information in the table
 * @constructor
 * @param {Array} allUsersData - All user's data
*/
function populateInfo(allUsersData) {
  // Draw chart on load
  google.load('visualization', '1', {packages: ['corechart']});
  google.setOnLoadCallback(drawChartOnLoad);

  /**
   * Function to draw charts on page load
   * @constructor
  */
  function drawChartOnLoad() {
    // Draw all data histogram
    drawChart(allUsersData, moment().subtract(1000, 'years'), moment());
  }

  /** String 'endswith' function **/
  if (typeof String.prototype.endsWith != 'function') {
    String.prototype.endsWith = function(suffix) {
      return this.indexOf(suffix, this.length - suffix.length) !== -1;
    };
  }

  /**
   * Function to draw chart, gicen start and end time
   * @constructor
   * @param {Array} allUsersData - All user's data
   * @param {Date} start - The start date of data in the range
   * @param {Date} end - The end date of data in the range
  */
  function drawChart(allUsersData, start, end) {
    var metricName;
    if ('{{ metric }}'.endsWith('Percentile Latency')) {
      metricName = '{{ metric }} (\xB5s)';
    }
    else {
      metricName = '{{ metric }}';
    }

    var args = [[metricName]];

    var startDate = moment();
    var endDate = moment().subtract(1000, 'years');

    // Add data

    for (i = 0; i < allUsersData.length; i++) {
      allUsersData[i] = allUsersData[i].replace(/'/g, '\"');
      allUsersData[i] = allUsersData[i].replace(/u"(?=[^:]+")/g, '\"');
      item = jQuery.parseJSON(allUsersData[i]);

      var metricDate = new Date(
          item.year,
          item.month - 1,
          item.day,
          item.hour,
          item.min,
          item.sec,
          0);

      if (start <= metricDate && end >= metricDate) {
        if (item.value != 0.0)
          args.push([item.value]);

        if (metricDate < startDate) {
          startDate = metricDate;
        }
        if (metricDate > endDate) {
          endDate = metricDate;
        }
      }
    }


    if (args.length == 1) {
      // No data available
      var errorHeader = document.getElementById('error-header');
      errorHeader.innerHTML = 'Sorry, no data is available for the' +
          'given time range';
    }
    else {
      var data = google.visualization.arrayToDataTable(
        args
      );

      // Options for chart
      var options = {
        legend: { position: 'none' },
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

      var chart = new google.visualization.Histogram(
          document.getElementById('chart_div'));
      chart.draw(data, options);
      $('#reportrange span').html(moment(startDate).format(
          'MM/DD/YYYY, HH:mm:ss') + ' - ' + moment(endDate).format(
          'MM/DD/YYYY, HH:mm:ss'));
    }
  }

  /** Initializes date range picker **/
  $('#reportrange').daterangepicker({
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
