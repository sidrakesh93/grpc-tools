'use strict';

var _ = require('lodash');
var async = require('async');
var child_process = require('child_process');
var diff = require('diff');
var expect = require('chai').expect;
var fs = require('fs-extra');
var path = require('path');
var tmp = require('tmp');

var packager = require('../lib/packager');


function filesEqual(file1, file2, done) {
  fs.readFile(file1, 'utf-8', function(err, file1Data) {
    if (err) {
      done(err);
      return;
    }
    fs.readFile(file2, 'utf-8', function(err, file2Data) {
      if (err) {
        done(err);
        return;
      }
      var diffs = diff.diffTrimmedLines(file1Data, file2Data);
      var diffCount = 0;
      diffs.forEach(function(d) {
        if (!!d.added || !!d.removed) {
          diffCount += 1;
        }
      });
      if (diffCount == 0) {
        done(null)
      } else {
        console.log(diffs);
        if (diffCount == 1) {
          done(new Error('There was a difference'));
        } else {
          done(new Error('There were ' + diffCount + ' differences'));
        }
      }
    });
  });
}

function genFixtureCompareFunc(top) {
  return function compareWithFixture(c) {
    var want = path.join(__dirname, 'fixtures', c);
    var got = path.join(top, c);
    return filesEqual.bind(null, want, got);
  }
}

function genCopyCompareFunc(top, language) {
  return function checkACopy(c) {
    var want = path.join(__dirname, '..', 'templates', language, c);
    var got = path.join(top, c);
    return filesEqual.bind(null, want, got);
  }
}

var testPackageInfo = {
  api: {
    'author': 'Google Inc',
    'description': 'a unittest api',
    'email': 'googleapis-packages@google.com',
    'github_user_uri': 'https://github.com/google',
    'homepage': 'https://github.com/google/googleapis',
    'license': 'Apache',
    'name': 'packager-unittest',
    'version': 'v2',
    'semantic_version': '1.0.0'
  },
  dependencies: {
    protobuf: {
      version: '3.0.0-alpha-3'
    },
    grpc: {
      core: {
        version: '0.9.0'
      },
      objc: {
        ios: {
          deployment_target: '6.0'
        },
        osx: {
          deployment_target: '10.8'
        },
        version: '0.5.0'
      },
      python: {
        version: '0.9.0a0'
      },
      ruby: {
        version: '0.9.3'
      },
      nodejs: {
        version: '0.10.0'
      }
    },
    auth: {
      python: {
        version: '0.4.1'
      },
      ruby: {
        version: '0.4.1'
      },
      nodejs: {
        version: '0.9.2'
      }
    }
  }
}

describe('the go package builder', function() {
  var top;
  beforeEach(function() {
    top = tmp.dirSync().name;
  });

  it ('should construct a go package', function(done) {
    var opts = {
      packageInfo: testPackageInfo,
      top: top
    }
    var copies = [
      'LICENSE',
      'PUBLISHING.md'
    ];
    var checkCopies = function checkCopies(next) {
      var checkACopy = genCopyCompareFunc(top, 'go');
      var copyTasks = _.map(copies, checkACopy);
      async.parallel(copyTasks, next);
    }
    async.series([
      packager.go.bind(null, opts),
      checkCopies
    ], done);
  });
});

describe('the objective c package builder', function() {
  var top;
  beforeEach(function() {
    top = tmp.dirSync().name;
  });

  it ('should construct a objc package', function(done) {
    var opts = {
      packageInfo: testPackageInfo,
      top: top
    }
    var copies = [
      'LICENSE',
      'PUBLISHING.md'
    ];
    var checkCopies = function checkCopies(next) {
      var checkACopy = genCopyCompareFunc(top, 'objc');
      var copyTasks = _.map(copies, checkACopy);
      async.parallel(copyTasks, next);
    }
    var expanded = [
      'packager-unittest-v2.podspec'
    ];
    var compareWithFixture = genFixtureCompareFunc(top);
    var checkExpanded = function checkExpanded(next) {
      var expandTasks = _.map(expanded, compareWithFixture);
      async.parallel(expandTasks, next);
    }
    async.series([
      packager.objc.bind(null, opts),
      checkCopies,
      checkExpanded
    ], done);
  });
});

describe('the python package builder', function() {
  var top;
  beforeEach(function() {
    top = tmp.dirSync().name;
  });
  it ('should construct a python package', function(done) {
    var opts = {
      packageInfo: testPackageInfo,
      top: top
    }
    var copies = [
      'LICENSE',
      'PUBLISHING.rst'
    ];
    var checkCopies = function checkCopies(next) {
      var checkACopy = genCopyCompareFunc(top, 'python');
      var copyTasks = _.map(copies, checkACopy);
      async.parallel(copyTasks, next);
    }
    var expanded = [
      'setup.py'
    ];
    var compareWithFixture = genFixtureCompareFunc(top);
    var checkExpanded = function checkExpanded(next) {
      var expandTasks = _.map(expanded, compareWithFixture);
      async.parallel(expandTasks, next);
    }
    async.series([
      packager.python.bind(null, opts),
      checkCopies,
      checkExpanded
    ], done);
  });
});

describe('the ruby package builder', function() {
  var top;
  beforeEach(function() {
    top = tmp.dirSync().name;
  });

  it ('should construct a ruby package', function(done) {
    var opts = {
      packageInfo: testPackageInfo,
      top: top
    }
    var copies = [
      'Gemfile',
      'LICENSE',
      'PUBLISHING.md',
      'Rakefile'
    ];
    var checkCopies = function checkCopies(next) {
      var checkACopy = genCopyCompareFunc(top, 'ruby');
      var copyTasks = _.map(copies, checkACopy);
      async.parallel(copyTasks, next);
    }
    var expanded = [
      'packager-unittest-v2.gemspec'
    ];
    var compareWithFixture = genFixtureCompareFunc(top);
    var checkExpanded = function checkExpanded(next) {
      var expandTasks = _.map(expanded, compareWithFixture);
      async.parallel(expandTasks, next);
    }
    async.series([
      packager.ruby.bind(null, opts),
      checkCopies,
      checkExpanded
    ], done);
  });
});

describe('the nodejs package builder', function() {
  var top;
  beforeEach(function() {
    top = tmp.dirSync().name;
  });

  it ('should construct a nodejs package', function(done) {
    var opts = {
      packageInfo: testPackageInfo,
      top: top
    }
    var copies = [
      'index.js',
      'LICENSE',
      'PUBLISHING.md'
    ];
    var checkCopies = function checkCopies(next) {
      var checkACopy = genCopyCompareFunc(top, 'nodejs');
      var copyTasks = _.map(copies, checkACopy);
      async.parallel(copyTasks, next);
    }
    var expanded = [
      'package.json'
    ];
    var compareWithFixture = genFixtureCompareFunc(top);
    var checkExpanded = function checkExpanded(next) {
      var expandTasks = _.map(expanded, compareWithFixture);
      async.parallel(expandTasks, next);
    }
    async.series([
      packager.nodejs.bind(null, opts),
      checkCopies,
      checkExpanded
    ], done);
  });
});
