var pathName = window.location.pathname;
pathName = pathName.replace(/\/configs\//g, '');
pathName = atob(pathName);

var pathNameParts = pathName.split('%');

var testName = document.getElementById('test-name');
/** Test name **/
testName.innerHTML = 'Test: ' + pathNameParts[0];

var testTag = document.getElementById('test-tag');

// Second part of split url pathname is the test tag
if (pathNameParts[1]) {
  /** Test tag **/
  testTag.innerHTML = 'Tag: ' + pathNameParts[1];
}
else {
  testTag.innerHTML = 'Tag: None';
}

var table = document.getElementById('client-configs-table');

// Third part of split url pathname is client config
fillTable(table, pathNameParts[2]);

table = document.getElementById('server-configs-table');
// Fourth part of split url pathname is server config
fillTable(table, pathNameParts[3]);

table = document.getElementById('sys-info-table');
// Fifth part of split url pathname is sys info
fillTable(table, pathNameParts[4]);

/**
 * Function to fill table
 * @constructor
 * @param {HTMLTableSectionElement} table - Table to populate
 * @param {JSON} info - Information to populate the table with
 */
function fillTable(table, info) {
  JSON.parse(info, function(k, v) {
    var row = table.insertRow(-1);
    var keyCell = row.insertCell(-1);
    var valCell = row.insertCell(-1);

    keyCell.innerHTML = k;
    valCell.innerHTML = v;

    keyCell.style.textAlign = 'center';
    valCell.style.textAlign = 'center';
  });
  table.deleteRow(-1);
}
