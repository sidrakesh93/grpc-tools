'use strict';

var _ = require('lodash');
var async = require('async');
var fs = require('fs-extra');
var path = require('path');

var Mustache = require('mustache');

exports.go = makeGolangPackage;
exports.objc = makeObjcPackage;
exports.python = makePythonPackage;
exports.ruby = makeRubyPackage;
exports.nodejs = makeNodejsPackage;

var settings = {
  'go': {
    'copyables': [
      'PUBLISHING.md',
      'LICENSE'
    ],
    'templateDir': path.join(__dirname, '..', 'templates', 'go')
  },
  'objective_c': {
    'copyables': [
      'PUBLISHING.md',
      'LICENSE'
    ],
    'templates': [
      'podspec.mustache'
    ],
    'templateDir': path.join(__dirname, '..', 'templates', 'objc')
  },
  'python': {
    'copyables': [
      'PUBLISHING.rst',
      'LICENSE'
    ],
    'templates': [
      'setup.py.mustache'
    ],
    'templateDir': path.join(__dirname, '..', 'templates', 'python')
  },
  'ruby': {
    'copyables': [
      'Gemfile',
      'PUBLISHING.md',
      'LICENSE',
      'Rakefile'
    ],
    'templates': [
      'gemspec.mustache'
    ],
    'templateDir': path.join(__dirname, '..', 'templates', 'ruby')
  },
  'nodejs': {
    'copyables': [
      'PUBLISHING.md',
      'LICENSE',
      'index.js'
    ],
    'templates': [
      'package.json.mustache'
    ],
    'templateDir': path.join(__dirname, '..', 'templates', 'nodejs')
  }
}

/**
 * makeGolangPackage creates a Go package.
 *
 * @param {object} opts contains settings used to configure the package.
 * @param {function} done is called once the package is created.
 */
function makeGolangPackage(opts, done) {
  opts = opts || {};
  _.merge(opts, settings.go);
  var tasks = [];

  // Move copyable files to the top-level dir.
  opts.copyables.forEach(function(f) {
    var src = path.join(opts.templateDir, f)
      , dst = path.join(opts.top, f);
    tasks.push(fs.copy.bind(fs, src, dst));
  });

  var packageName = opts.packageInfo.api.name + '-'
                  + opts.packageInfo.api.version;
  async.parallel(tasks, function(err) {
    if (!err && opts.copyables.indexOf('PUBLISHING.md') != -1) {
      console.log('The golang package', packageName, 'was created in',
                  opts.top);
      console.log('To publish it, read', path.join(opts.top, 'PUBLISHING.md'),
                  'for the next steps');
    }
    done(err);
  });
};

/**
 * makePythonPackage creates a new python package.
 *
 * @param {object} opts contains settings used to configure the package.
 * @param {function} done is called once the package is created.
 */
function makePythonPackage(opts, done) {
  opts = opts || {};
  _.merge(opts, settings.python);
  var tasks = [];

  // Move copyable files to the top-level dir.
  opts.copyables.forEach(function(f) {
    var src = path.join(opts.templateDir, f)
      , dst = path.join(opts.top, f);
    tasks.push(fs.copy.bind(fs, src, dst));
  });

  // Move the expanded files to the top-level dir.
  var packageName = opts.packageInfo.api.name + '-'
                  + opts.packageInfo.api.version;
  opts.templates.forEach(function(f) {
    var dstBase = f;
    if (dstBase == 'setup.py.mustache') {
      dstBase = 'setup.py';
    }
    var tmpl = path.join(opts.templateDir, f)
      , dst = path.join(opts.top, dstBase);
    tasks.push(expand.bind(null, tmpl, dst, opts.packageInfo));
  });

  async.parallel(tasks, function(err) {
    if (!err && opts.copyables.indexOf('PUBLISHING.rst') != -1) {
      console.log('The python package', packageName, 'was created in',
                  opts.top);
      console.log('To publish it, read', path.join(opts.top, 'PUBLISHING.rst'),
                  'for the next steps');
    }
    done(err);
  });
};

/**
 * makeNodejsPackage creates a new nodejs package.
 *
 * @param {object} opts contains settings used to configure the package.
 * @param {function} done is called once the package is created.
 */
function makeNodejsPackage(opts, done) {
  opts = opts || {};
  _.merge(opts, settings.nodejs);
  var tasks = [];

  // Move copyable files to the top-level dir.
  opts.copyables.forEach(function(f) {
    var src = path.join(opts.templateDir, f)
      , dst = path.join(opts.top, f);
    tasks.push(fs.copy.bind(fs, src, dst));
  });

  // Move the expanded files to the top-level dir.
  var packageName = opts.packageInfo.api.name + '-'
                  + opts.packageInfo.api.version;
  opts.templates.forEach(function(f) {
    var dstBase = f;
    if (dstBase == 'package.json.mustache') {
      dstBase = 'package.json';
    }
    var tmpl = path.join(opts.templateDir, f)
      , dst = path.join(opts.top, dstBase);
    tasks.push(expand.bind(null, tmpl, dst, opts.packageInfo));
  });

  async.parallel(tasks, function(err) {
    if (!err && opts.copyables.indexOf('PUBLISHING.md') != -1) {
      console.log('The nodejs package', packageName, 'was created in',
                  opts.top);
      console.log('To publish it, read', path.join(opts.top, 'PUBLISHING.md'),
                  'for the next steps');
    }
    done(err);
  });
};

/**
 * makeObjcPackage creates a new objective-c package.
 *
 * @param {object} opts contains settings used to configure the package.
 * @param {function} done is called once the package is created.
 */
function makeObjcPackage(opts, done) {
  opts = opts || {};
  _.merge(opts, settings.objective_c);
  var tasks = [];

  // Move copyable files to the top-level dir.
  opts.copyables.forEach(function(f) {
    var src = path.join(opts.templateDir, f)
      , dst = path.join(opts.top, f);
    tasks.push(fs.copy.bind(fs, src, dst));
  });

  // Move the expanded files to the top-level dir.
  var packageName = opts.packageInfo.api.name + '-'
                  + opts.packageInfo.api.version;
  opts.templates.forEach(function(f) {
    var dstBase = f;
    if (dstBase == 'podspec.mustache') {
      dstBase = packageName + '.podspec';
    }
    var tmpl = path.join(opts.templateDir, f)
      , dst = path.join(opts.top, dstBase);
    tasks.push(expand.bind(null, tmpl, dst, opts.packageInfo));
  });

  async.parallel(tasks, function(err) {
    if (!err && opts.copyables.indexOf('PUBLISHING.md') != -1) {
      console.log('The objective-c package', packageName, 'was created in',
                  opts.top);
      console.log('To publish it, read', path.join(opts.top, 'PUBLISHING.md'),
                  'for the next steps');
    }
    done(err);
  });
};

/**
 * makeRubyPackage creates a new ruby package.
 *
 * @param {object} opts contains settings used to configure the package.
 * @param {function} done is called once the package is created.
 */
function makeRubyPackage(opts, done) {
  opts = opts || {};
  _.merge(opts, settings.ruby);
  fs.mkdirsSync(path.join(opts.top, 'lib'));
  var tasks = [];

  // Move the generated files to the lib dir.
  opts.generated = opts.generated || [];
  opts.generated.forEach(function(f) {
    var src = path.join(opts.top, f)
      , dst = path.join(opts.top, 'lib', f);
    tasks.push(fs.move.bind(fs, src, dst));
  });

  // Move copyable files to the top-level dir.
  opts.copyables.forEach(function(f) {
    var src = path.join(opts.templateDir, f)
      , dst = path.join(opts.top, f);
    tasks.push(fs.copy.bind(fs, src, dst));
  });

  // Move the expanded files to the top-level dir.
  var packageName = opts.packageInfo.api.name + '-'
                  + opts.packageInfo.api.version;
  opts.templates.forEach(function(f) {
    var dstBase = f;
    if (dstBase == 'gemspec.mustache') {
      dstBase = packageName + '.gemspec';
    }
    var tmpl = path.join(opts.templateDir, f)
      , dst = path.join(opts.top, dstBase);
    tasks.push(expand.bind(null, tmpl, dst, opts.packageInfo));
  });

  async.parallel(tasks, function(err) {
    if (!err && opts.copyables.indexOf('PUBLISHING.md') != -1) {
      console.log('The ruby package', packageName, 'was created in',
                  opts.top);
      console.log('To publish it, read', path.join(opts.top, 'PUBLISHING.md'),
                  'for the next steps');
    }
    done(err);
  });
};

/**
 * Expands the contents of a template file, saving it to an output file.
 *
 * @param {string} template the path to the template file
 * @param {string} dst the path of the expanded output
 * @param {Object} params object containing the named parameter values
 * @param {function(Error, string)} done is called with the rendered template
 */
function expand(template, dst, params, done) {
  // renders and saves the output file
  var render = function render(err, renderable) {
    if (err) {
      done(err);
    } else {
      fs.writeFile(dst, Mustache.render(renderable, params), done);
    }
  }
  fs.readFile(template, {encoding: 'utf-8'}, render);
}
