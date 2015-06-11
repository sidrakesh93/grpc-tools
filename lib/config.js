'use strict';

var fs = require('fs');
var path = require('path');
var yaml = require('js-yaml');

var defaultDepPath = path.join(__dirname, '..', 'config', 'dependencies.yml');
var defaultApiPath = path.join(__dirname, '..', 'config', 'api_defaults.yml');

exports.defaults = {
  api: yaml.safeLoad(fs.readFileSync(defaultApiPath, 'utf8')),
  dependencies:  yaml.safeLoad(fs.readFileSync(defaultDepPath, 'utf8'))
}
