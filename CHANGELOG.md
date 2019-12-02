# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.4] - 2019-11-13
- automatically link frontend plugins for dynamic import
- various bugfixes and improvements

## [0.4.3] - 2019-11-01
- use Porterstemmer to get correct singular fontend plugin name
- ease package creation
- make license configureable at startplugin time

## [0.4.2] - 2019-10-16
- allow using variables in template file/dir names
- provide pluggable Javascript (and other) package manager support
- simple working syncplugin support
- improve frontend plugin creation
- generate frontend plugin names from entry point group by stemming

## [0.4.0] - 2019-10-12
- Change API to an easier one, following Marty Alchin's Simple Plugin Framework
- add some tests

## [0.3.5] - 2019-06-xx
### Added
- GDAPS plugins need to be Django AppConfig classes now.
