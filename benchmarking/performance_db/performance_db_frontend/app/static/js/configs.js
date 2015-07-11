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
 * Function to populate the user's config information in the tables
*/
function populateInfo() {
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
  } else {
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
}
