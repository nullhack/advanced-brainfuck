# Changelog

All notable changes to advanced-brainfuck will be documented in this file.

## [2.2.0] - 20260503 — Memory Consolidation

### Added

- `quit` and `exit` commands in REPL to exit the interpreter
- `save [FILE]` command in REPL to save tape state to JSON (default: `tape.json`)
- `--load FILE` CLI flag to restore tape state from a JSON file before execution
- `--output FILE` CLI flag to redirect program output to a file instead of stdout
- `--dump FILE` CLI flag to save tape state to a JSON file after execution
- `save_tape(path)` and `load_tape(path)` methods on `BrainFuck` class for programmatic tape persistence
- Tape state JSON format: `{"pointer": int, "cells": {"index": value, ...}}` (sparse, non-zero cells only)

### Fixed

- Cell values now wrap to 0-255 (8-bit unsigned) in both JIT and interpreted paths — standard Brainfuck requires `255+1=0` and `0-1=255`
- `EOFError` in `_read_input_direct()` and `_read_value()` now returns -1 instead of crashing when stdin is exhausted
- `_read_value()` and `_read_input_direct()` now take only the first character of string input (`ord(ui[0])`)

## [2.1.3] - 20260503

### Fixed

- CLI entry point now correctly parses arguments (`main()` was using default `args=[]` instead of `sys.argv`)

## [2.1.2] - 20260503

### Added

- GitHub Pages documentation site (`docs/index.html`) with project branding
- Static documentation landing page linking to specs, ADRs, source, and PyPI

## [2.1.1] - 20260503

### Removed

- `.travis.yml` — obsolete CI config (project uses GitHub Actions)
- `conftest.py` — unnecessary sys.path hack (package imports work natively)
- `how-to-use.md` — content covered by README.md

### Changed

- Default branch renamed from `master` to `main`
- Added GitHub Pages, PyPI, and Changelog links to README
- Cleaned up `.gitignore` (removed stale entries, added build artifacts)

## [2.1.0] - 20260503

### Added

- Proper Python package structure (`brainfuck/` package with `__init__.py`, `__main__.py`, `core.py`)
- 16 new bflib programs: `div`, `mod`, `zero`, `move`, `swap`, `not`, `and`, `or`, `eq`, `if`, `sqrt`, `p5`, `p32`, `p48`, `p65`, `newline`
- `python -m brainfuck` entry point for running the interpreter
- PyPI-compatible packaging with `setuptools` build backend and `package-data` for bflib inclusion
- `-f`/`--file` flag for loading large Brainfuck programs from files (fixes #2: "Argument list too long" for large programs)
- `pyproject.toml` build configuration with `[tool.setuptools.packages.find]` and `[tool.setuptools.package-data]`

### Changed

- Restructured from single `brainfuck.py` module to `brainfuck/` package directory
- bflib directory moved inside `brainfuck/bflib/` for installed-package compatibility
- Library import path resolution now uses `__file__`-relative paths for wheel compatibility
- Version bumped to 2.1.0
- `pyproject.toml` updated: removed `agents-smith` dependency, added `build` to dev deps, added setuptools config

### Fixed

- **#2**: Large Brainfuck programs can now be loaded via `-f FILE` flag instead of shell argument expansion
- PyPI package now includes bflib data files and installs as a proper importable package
- Feature test discovery fixed (`*_test.py` pattern added to pytest config)

## [2.0.0] - 20260503 — Neuroplasticity

### Added

- Segmented JIT execution with checkpoint/resume for I/O operations — all programs now use the JIT path, not just pure-computation ones
- I/O checkpoint handling: `execute_jit()` returns status codes (NEED_INPUT, PRINT_CELLS, PRINT_HISTORY, OUTPUT_OVERFLOW) and Python handles I/O at each checkpoint before resuming
- Pre-allocated output buffer for accumulating `.` outputs during JIT execution, flushed at checkpoints or on overflow
- `_execute_segmented_jit()` orchestration loop that drives the JIT → flush → checkpoint → resume cycle
- `_read_input_direct()` for reading input without Cells object dependency during segmented execution
- `_sync_cells_from_tape()` to copy tape state back to Cells for I/O operations that need it

### Changed

- Tape size increased from 30,000 to 65,536 cells (64K) to match Brainfuck convention
- JIT execution now uses mutable state array (`[pointer, pc, output_count]`) instead of return tuples
- All programs — including those with `,`, `*`, and `&` commands — now execute through the JIT path instead of falling back to interpreted execution
- `execute_jit()` signature changed to accept `program, tape, state, output_buf, max_iterations` and return `(status, iterations)`
- Interpreted path is now a fallback only for JIT compilation failures, not for I/O programs

### Fixed

- Programs with input (`,`) now benefit from JIT acceleration between input checkpoints
- Programs with cell display (`*`) and command history (`&`) now execute at JIT speed between I/O checkpoints

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