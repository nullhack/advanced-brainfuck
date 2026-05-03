# Changelog

All notable changes to advanced-brainfuck will be documented in this file.

## [0.2.0] - 20260502

### Added

- IR compilation with run-length encoding for 2-3x speedup on long programs
- Numba JIT-compiled execution engine for pure-computation programs
- List-backed tape with sparse dict fallback replacing Cells(dict)
- Inline library loading without throwaway BrainFuck instance execution
- O(1) command history accumulation using list append instead of string concatenation
- Direct IR dispatch loop eliminating per-character dictionary lookups
- CLI entry point in pyproject.toml (`brainfuck` command)
- NumPy and Numba as runtime dependencies

### Changed

- Python version requirement raised to >=3.13
- `_resolve_imports` now filters library files to valid BF commands only
- `import_lib` delegates to `_resolve_imports` for backward compatibility
- Exception handling in `_read_value` changed from bare `except:` to `except (ValueError, TypeError)`
- Removed `from __future__ import print_function` (Python 3 only)
- `cmd_history` string replaced by `_cmd_parts` list for efficient accumulation
- `_cmd_pointer` replaced by local `pc` variable in `execute()`

### Fixed

- Library files containing description text no longer pollute command history
- Import resolution no longer double-resolves nested imports

## [0.1.0] - 20160101

### Added

- Initial release: BrainFuck interpreter with library import, cell display, and command history