'use strict';

var _ = require('lodash');
var async = require('async');
var child_process = require('child_process');
var config = require('./config');
var fs = require('fs-extra');
var packager = require('./packager');
var path = require('path');
var pbjs_target = require('protobufjs/cli/pbjs/targets/json');
var request = require('request');
var tmp = require('tmp');

var EventEmitter = require('events').EventEmitter;
var FindFiles = require('node-find-files');
var ProtoBuf = require('protobufjs');
var StreamZip = require('node-stream-zip');

exports.ApiRepo = ApiRepo;
exports.GOOGLE_APIS_REPO_ZIP = GOOGLE_APIS_REPO_ZIP;

var GOOGLE_APIS_REPO_ZIP =
    'https://github.com/google/googleapis/archive/master.zip';

var DEFAULT_LANGUAGES = [
  'go',
  'objc',
  'nodejs',
  'python',
  'ruby'
];

/**
 * ApiRepo represents a published repo containing API protos.
 */
function ApiRepo(opts) {
  opts = opts || {};
  this.depBins = {};
  this.opts = opts;
  this.languages = opts.languages || DEFAULT_LANGUAGES;
  this.outDir = opts.outDir || tmp.dirSync().name;
  this.repoDir = opts.repoDir;
  this.pkgPrefix = opts.pkgPrefix;
  this.zipUrl = opts.zipUrl;
  this.isGoogleApi = !!opts.isGoogleApi;
  if (!(this.repoDir || this.zipUrl)) {
    this.zipUrl = GOOGLE_APIS_REPO_ZIP; // default to download googleapis
    this.isGoogleApi = true;
  }
}
ApiRepo.prototype =
  Object.create(EventEmitter.prototype, { constructor: { value: ApiRepo } });

/**
 * setUp prepares an ApiRepo for use.
 *
 * After it is called, build packages in the repo's 'ready' event.
 * It ensures that
 * - the binaries needed to complete code generation are already available
 * - the configured api repository is valid and available.
 *
 * repo = new ApiRepo({
 *   isGoogleApi: true,
 *   languages: ['python', 'ruby']
 * });
 * repo.on('ready', function() {
 *   repo.buildPackages(name, version);
 * });
 * repo.on('err', function(err) {
 *   console.error('Could not build packages:', err);
 * });
 * repo.setUp();
 */
ApiRepo.prototype.setUp = function setUp() {
  var that = this;

  // checkDeps wraps this._checkDeps to include in the setUp async waterfall.
  var checkDeps = function checkDeps(next) {
    that._checkDeps(null /* use instance opts */, next);
  }

  // done is run when setUp completes.
  var done = function done(err) {
    if (!err) {
      that.emit('ready');
    } else {
      that.emit('error', err);
    }
  };
  async.waterfall([
    this._checkRepo.bind(this),
    checkDeps
  ], done);
};

/**
 * buildPackages builds the configured languages packages.
 *
 * It is to be called once the repo is 'ready' after setUp is called.
 *
 * repo = new ApiRepo({
 *   isGoogleApi: true,
 *   languages: ['python', 'ruby']
 * });
 * repo.on('ready', function() {
 *   repo.buildPackages(name, version);  // called then the repo is ready
 * });
 * repo.on('err', function(err) {
 *   console.error('Could not build packages:', err);
 * });
 * repo.setUp();
 */
ApiRepo.prototype.buildPackages =
  function buildPackages(name, version, opt_done) {
    var tasks = [];
    var that = this;
    var done = opt_done || _.noop;
    this.languages.forEach(function(l) {
      var innerTasks = [that._buildProtos.bind(that, name, version, l)];
      if (packager[l]) {
        var buildAPackage = function buildAPackage(generated, next) {
          var opts = {
            'top': path.join(that.outDir, l),
            'packageInfo': config.defaults,
            'generated': generated
          };
          opts.packageInfo.api.name = that.pkgPrefix + name;
          opts.packageInfo.api.version = version;
          packager[l](opts, next);
        };
        innerTasks.push(buildAPackage);
      }
      tasks.push(async.waterfall.bind(async, innerTasks));
    });
    async.parallel(tasks, done);
  }

/**
 * _buildProtos builds the protos for named api and version in the target languages.
 *
 * @param {string} name the api name
 * @param {string} version the api version
 * @param {string} language language to generate protos in
 * @param {function} done the function to run on protoc completion
 */
ApiRepo.prototype._buildProtos =
  function _buildProtos(name, version, language, done) {
    var that = this;
    /** findOutputs lists the files in the output directory */
    var findOutputs = function findOutputs(err) {
      if (err) {
        console.error('findOutputs:start:err', err);
        done(err);
        return;
      }
      var outputs = [];
      var langRoot = path.join(that.outDir, language)
      var finder = new FindFiles({
        rootFolder : langRoot,
        filterFunction : function (_unused, stat) {
          return stat.isFile();
        }
      });
      var finished = false;
      finder.on("complete", function() {
        if (!finished) {
          done(null, outputs);
          finished = true;
        }
      });
      finder.on("match", function(path) {
        var shortPath = path.replace(langRoot + '/', '');
        outputs.push(shortPath);
      });
      finder.on("error", function(err) {
        if (!finished) {
          console.error('findOutputs:err', err);
          done(err);
          finished = true;
        }
      });
      finder.startSearch();
    };
    if (language === 'nodejs') {
      this.opts.pbBuilder = ProtoBuf.newBuilder();

      /**
       * storeService writes a single JSON representation of all the protos
       * relevant to service in a format from which a gRPC client constructor
       * can be derived.
       */
      var storeService = function storeService(err) {
        if (err !== null) {
          findOutputs(err);
          return;
        }
        var outDir = path.join(that.outDir, language);
        fs.mkdirsSync(outDir);
        var servicePath = path.join(outDir, 'service.json');
        var pbjson = pbjs_target(that.opts.pbBuilder, {});
        fs.writeFile(servicePath, pbjson, findOutputs);
      }
      var loadPB = this._makePBFunc(this.opts);
      this._findProtos(name, version, storeService, loadPB);
    } else {
      var protoc = this._makeProtocFunc(this.opts, language);
      this._findProtos(name, version, findOutputs, protoc);
    }
  }

/**
 * _checkDeps confirms that the tools needed to generate the required protos
 * are present.
 */
ApiRepo.prototype._checkDeps = function _checkDeps(opts, done) {
  // If nodejs is the only language, there are no dependencies.
  if (this.languages.length === 1 && this.languages.indexOf('nodejs') !== -1) {
    done(null);
    return;
  }

  opts = opts || {};
  opts.env = opts.env || this.opts.env || process.env;
  var reqdBins = ['protoc'];
  this.languages.forEach(function(l) {
    if (l == 'nodejs') {
      return;  // nodejs builds using ProtoBuf.js
    }
    reqdBins.push('grpc_' + l + '_plugin');
  });

  var that = this;
  var isInPath = function isInPath(err, data) {
    if (!err) {
      var binPaths = data.split("\n");
      _.forEach(reqdBins, function(b) {
        _.forEach(binPaths, function(p) {
          if (_.endsWith(p, b)) {
            that.depBins[b] = p;
          }
        })
      });
      console.log('using the following required binaries:');
      console.log(that.depBins);
    };
    done(err, data);
  };
  child_process.execFile('which', reqdBins, {env: opts.env}, isInPath);
};

/**
 * newIsDirFunc creates a function isDir(callback) that asynchronouosly
 * confirms if dirName is a directory.
 *
 * @param dirName the directory to check.
 * @return function isDir(callback)
 */
function newIsDirFunc(dirName) {
  return function(done) {
    var statCb = function(err, stats) {
      if (err) {
        console.error('directory not found: ', dirName);
        return done(err);
      };
      if (!stats.isDirectory()) {
        console.error('file was not a directory: ', dirName);
        return done(new Error('not a directory'));
      }
      return done(null);
    };
    fs.stat(dirName, statCb);
  };
};

/**
 * _verifyRepo confirms that api repo source is available.
 *
 * if repoDir is set, it confirms that the directory exists
 *
 * if repoDir is not set, but zipUri is, it downloads the api zip to tmp dir and
 * sets that to repoDir
 *
 * if isGoogleApi is `true`, it confirms that repoDir has 'google' subdirectory
 */
ApiRepo.prototype._checkRepo = function _checkRepo(done) {
  var that = this;
  if (this.repoDir) {
    var checkDir = newIsDirFunc(this.repoDir);
    if (this.isGoogleApi) {
      var checkGoogleDir = newIsDirFunc(path.join(that.repoDir, 'google'));
      async.waterfall([checkDir, checkGoogleDir], done);
    } else {
      checkDir(done);
    }
    return;
  }
  var makeTmpDir = function makeTmpDir(next) {
    tmp.dir({}, next);
  };
  var makeTmpZip =  function makeTmpZip(dirName, _unused, next) {
    var fileCb = function fileCb(err, tmpPath, fd) {
      next(err, dirName, tmpPath, fd);
    };
    tmp.file({
      mode: 420 /* 0644 */,
      prefix: 'repo-',
      postfix: '.zip' }, fileCb);
  };
  var saveZip = function saveZip(dirname, tmpPath, fd, next) {
    console.log("writing", that.zipUrl, "to fd:", fd);
    var stm = request(that.zipUrl).pipe(fs.createWriteStream('', {fd: fd}));
    stm.on('close', function() {
      console.log('saved zip to ', tmpPath);
      next(null, dirname, tmpPath);
    });
  };
  var extractZip = function extractZip(dirname, tmpPath, next) {
    var zip = new StreamZip({
      file: tmpPath,
      storeEntries: true
    });
    zip.on('error', function(err) { next(err)});
    zip.on('ready', function() {
      zip.extract(null, dirname, function(err, count) {
        if (err) {
          console.error('extract failed:', err);
          return next(err);
        }
        return next(null, dirname);
      });
    });
  };
  var updateRepoDir = function updateRepoDir(dirName, next) {
    fs.readdir(dirName, function(err, files) {
      if (err) {
        return next(err);
      };
      if (files.length > 1) {
        console.error('Malformed zip had', files.length, 'top-level dirs');
        return next(new Error('Malformed zip: more than 1 top-level dir'))
      }
      that.repoDir = path.join(dirName, files[0]);
      console.log('repoDir is ', that.repoDir);
      return next(null);
    });
  };
  var checkNewSubDir = function checkNewSubDir(callback) {
    var checkGoogleDir = newIsDirFunc(path.join(that.repoDir, 'google'));
    checkGoogleDir(callback);
  };
  if (this.zipUrl) {
    var tasks = [
      makeTmpDir,   // make a tmp direcotry
      makeTmpZip,   // make a tmp file in which to save the zip
      saveZip,      // pull the zip archive and save it
      extractZip,   // extract the zip and save in the tmp directory
      updateRepoDir // set the top-level dir of the extracted zip as repoDir
    ];
    if (this.isGoogleApi) {
      tasks.push(checkNewSubDir);  // check that the google dir is present.
    }
    async.waterfall(tasks, done);
  }
};

var isProtoPath = /.proto$/;

/**
 * Finds the paths to the proto files with the given api name and version.
 *
 * If callback is set, it calls back on each of them.
 * @param {string} name the api name.
 * @param {string} version the api version
 * @param {function} done the cb called with all the protos or an error
 * @param {function} onProto the callback called on each proto
 */
ApiRepo.prototype._findProtos = function _findProtos(name, version, done,
                                                     onProto) {
  // Determine the top-level dir, verify it exists, then scan for protos in it.
  var parts = [this.repoDir];
  if (this.isGoogleApi) {
    parts.push('google');
  }
  parts.push(name, version);
  var protoDir = path.join.apply(path, parts);
  var checkProtoDir = newIsDirFunc(protoDir);
  var that = this;
  var eachProto = onProto || _.noop;
  var scanForProtos = function scanForProtos(next) {
    var protos = [];
    var finder = new FindFiles({
      rootFolder : protoDir,
      filterFunction : function (path) {
        return isProtoPath.test(path);
      }
    });
    var matchCount = 0;
    var matchDoneCount = 0;
    var checkMatches = function checkMatches() {
      if (matchDoneCount == matchCount) {
        next(null, protos);
      }
    };
    finder.on("match", function(path) {
      matchCount += 1;
      var shortPath = path.replace(that.repoDir + '/', '');
      protos.push(shortPath);
      eachProto(shortPath, function(err) {
        matchDoneCount += 1;
        if (err) {
          console.error('scanForProtos:eachProto:err', err);
          finder.emit('error', err);
        } else {
          checkMatches();
        }
      });
    });
    finder.on("error", function(err) {
      console.error('scanForProtos:err', err)
      next(err);
    });
    finder.startSearch();
  };
  async.waterfall([
    checkProtoDir,
    scanForProtos
  ], done);
};

/**
 * _makeProtocFunc makes a function that calls the protoc command line on
 * a proto in a given languages.
 *
 * @param {object} opts configure the call
 * @param {string} language the language to generate protos in.
 */
ApiRepo.prototype._makeProtocFunc = function _makeProtocFunc(opts, language) {
  var that = this;
  opts = opts || {};
  opts.env = opts.env || this.opts.env || process.env;
  // return a func that invokes protoc for the given language
  var callProtoc = function callProtoc(protoPath, done) {
    if (that.languages.indexOf(language) == -1) {
      console.error('language not setup -', language, 'is not in',
                    that.languages);
      done(new Error('invalid language'));
      return;
    }
    var outDir = path.join(that.outDir, language);
    fs.mkdirsSync(outDir);
    var args = [];
    if (language === 'go') {
      args.push(
        '--' + language + '_out=plugins=grpc:' + outDir,
        protoPath);
    } else {
      var pluginBin = that.depBins['grpc_' + language + '_plugin'];
      args.push(
        '--' + language + '_out=' + outDir,
        '-I.',
        '--grpc_out=' + outDir,
        '--plugin=protoc-gen-grpc=' + pluginBin,
        protoPath
      );
    }

    // Spawn the protoc command.
    console.log('Running protoc in ', that.repoDir);
    var proc = child_process.execFile('protoc', args, {
      cwd: that.repoDir,
      env: opts.env
    }, done);
  };
  return callProtoc;
};

/**
 * Helps construct a JSON representation each proto file for the nodejs build.
 *
 * The JSON representation is constructed via a opts.pbBuilder, a
 * ProtoBuf.Builder
 *
 * @param {object} opts provides configuration info
 * @param {object} opts.pbBuilder a ProtoBuf.Builder instance
 */
ApiRepo.prototype._makePBFunc = function _makePBFunc(opts) {
  var that = this;
  var loadPB = function loadPB(protoPath, done) {
    ProtoBuf.loadProtoFile({
      root: that.repoDir,
      file: protoPath
    }, opts.pbBuilder);
    done(null, opts.pbBuilder);
  };

  return loadPB;
};
