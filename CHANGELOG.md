# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v0.1.8] - 2026-04-29

### Fixed

- Avoid inserting the user name twice in the `tmpUrl` variable of the `main` section

## [v0.1.7] - 2026-04-17

### Fixed

- Fix typo introduced in v0.1.6

## [v0.1.6] - 2026-04-17

### Changed

- Added support for generating a minimal STAC catalog for `File` outputs.

## [v0.1.5] - 2026-01-21

### Changed

- Adopted PEP 621 standard for project metadata in `pyproject.toml`

### Removed

- Removed unnecessary `__init__.py` file for cleaner package structure

## [v0.1.4] - 2026-01-19

### Changed

- `CommonExecutionHandler` now inherits from `zoo_runner_common.handlers.ExecutionHandler`

## [v0.1.3] - 2026-01-19

### Fixed

- Fixed import to enable use of `botocore.session`

## [v0.1.2] - 2026-01-19

### Changed

- Updated `zoo-runner-common` dependency from `>=0.1.0` to `>=0.1.2` to support the new package structure and import paths (`from zoo_runner_common import ...`)

## [v0.1.1] - 2026-01-18

### Added

- Package is now officially available on PyPI: `pip install zoo-template-common`
- Automated CI/CD pipeline for PyPI publication on new releases
- Added `zoo-runner-common` (>=0.1.0) as an official dependency
- Complete PyPI metadata: classifiers, keywords, and project URLs
- Enhanced documentation with real-world examples

### Changed

- License updated to Apache-2.0
- Minimum Python version raised to 3.10 (supports 3.10, 3.11, 3.12)
- Updated documentation to reflect latest service template patterns

### Fixed
- Multiple typos in codebase and documentation
- Package structure improvements for better imports

## [v0.1.0] - 2026-01-18

### Added

- Initial release of `zoo-template-common`
- `CommonExecutionHandler`: extensible base class for CWL workflow execution with pre/post-execution hooks, automatic STAC catalog output processing, Kubernetes pod environment variable and node selector management, secrets handling, and tool log integration
- `CustomStacIO`: STAC I/O class with S3 support via `boto3` for reading and writing STAC catalogs from/to S3 or local file systems
- MkDocs Material documentation site
- Core dependencies: `loguru>=0.7.0`, `pystac>=1.8.0`, `pyyaml>=6.0`, `boto3>=1.28.0`, `botocore>=1.31.0`

[Unreleased]: https://github.com/ZOO-Project/zoo-template-common/compare/v0.1.8...HEAD
[v0.1.8]: https://github.com/ZOO-Project/zoo-template-common/compare/v0.1.7...v0.1.8
[v0.1.7]: https://github.com/ZOO-Project/zoo-template-common/compare/v0.1.6...v0.1.7
[v0.1.6]: https://github.com/ZOO-Project/zoo-template-common/compare/v0.1.5...v0.1.6
[v0.1.5]: https://github.com/ZOO-Project/zoo-template-common/compare/v0.1.4...v0.1.5
[v0.1.4]: https://github.com/ZOO-Project/zoo-template-common/compare/v0.1.3...v0.1.4
[v0.1.3]: https://github.com/ZOO-Project/zoo-template-common/compare/v0.1.2...v0.1.3
[v0.1.2]: https://github.com/ZOO-Project/zoo-template-common/compare/v0.1.1...v0.1.2
[v0.1.1]: https://github.com/ZOO-Project/zoo-template-common/compare/v0.1.0...v0.1.1
[v0.1.0]: https://github.com/ZOO-Project/zoo-template-common/releases/tag/v0.1.0