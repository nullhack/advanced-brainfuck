# Changelog

All notable changes to advanced-brainfuck will be documented in this file.

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