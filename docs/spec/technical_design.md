# Technical Design: advanced-brainfuck

> Technical design document for the current feature or initiative.

---

## Feature

N/A — this document describes the overall system architecture.

---

## Architectural Style

**Style:** Monolithic library with JIT acceleration

**Rationale:** Brainfuck is a single-threaded, sequential language. There is no concurrency, distribution, or messaging requirement. A monolithic library keeps the system simple while Numba provides native-code performance for the hot loop.

---

## Quality Attributes

| Attribute | Architectural Decision | ADR Ref |
|-----------|----------------------|---------|
| Performance | IR compilation with RLE + Numba JIT for hot path | ADR-20260502-ir-compilation, ADR-20260502-jit-acceleration |
| Correctness | Interpreted fallback path for I/O commands preserves spec compliance | ADR-20260502-jit-acceleration |
| Compatibility | Public API (`BrainFuck`, `Cells`, `main`) unchanged from v0.1.0 | — |

---

## Stack

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| Language | Python | >=3.13 | Numba dependency requirement |
| JIT Compiler | Numba | >=0.58.0 | Compiles Python to native code; zero-copy NumPy interop |
| Array Library | NumPy | >=1.24.0 | Required by Numba; provides typed arrays for JIT |
| CLI | argparse | stdlib | Lightweight, no additional dependency |

---

## Module Structure

```
brainfuck.py
  BrainFuck              # Main class: parse, compile, execute, import resolution
  Cells                  # Tape memory: list + sparse dict
  execute_jit()          # @jit(nopython=True) execution loop
  convert_ir_to_numeric() # IR → NumPy array conversion
  convert_ir_to_numeric_jit() # @jit helper for array construction
  main()                 # CLI entry point

bflib/
  sum.bf, copy.bf, ...  # Reusable Brainfuck library modules
```

---

## API Contracts

### `BrainFuck()`

**Constructor.** Creates a new interpreter instance with empty tape, pointer at 0.

```python
bf = BrainFuck()
```

### `BrainFuck.execute(cmd_line, MAX_RECURSION=100000)`

**Method.** Compiles and executes a Brainfuck program string.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `cmd_line` | `str` | required | Brainfuck source code (may include `{LIB}` imports) |
| `MAX_RECURSION` | `int` | 100000 | Maximum operations before halting |

**Raises:** `Exception("brackets not balanced!")` if brackets are mismatched.

**Side effects:** Prints output to stdout. Modifies internal `cells`, `pointer`, and `_cmd_parts`.

**JIT path:** If the program contains only `+`, `-`, `>`, `<`, `. commands, execution is delegated to `execute_jit()` via Numba. Otherwise, the interpreted path is used.

### `BrainFuck.interpreter(MAX_RECURSION=100000)`

**Method.** Starts an interactive REPL. Prompts with `>> ` (and `.. ` for incomplete brackets). Enter empty line to exit. Type `help` for command reference.

### `BrainFuck.is_balanced(cmd_line) -> bool`

**Static method.** Checks whether brackets (`[]`, `{}`) are balanced in the given string.

### `BrainFuck.import_lib(cmds) -> dict`

**Static method.** Resolves `{LIB}` imports in the given string. Returns a dict mapping library names to their resolved content.

### `BrainFuck.print_cells()`

**Method.** Prints all non-zero cells with the current pointer highlighted using `|value|` notation.

### `BrainFuck.print_cmd_history()`

**Method.** Prints the length and content of all commands executed so far.

---

## Interface Definitions

### Cells

```python
class Cells:
    def __init__(self) -> None: ...
    def __getitem__(self, key: int) -> int: ...     # Returns 0 for unset cells
    def __setitem__(self, key: int, value: int) -> None: ...  # Deletes key if value==0
    def backup(self) -> Cells: ...                    # Shallow copy
    def print_pos(self, pos: int) -> str: ...        # Formatted cell display
```

### JIT Execution

```python
@jit(nopython=True)
def execute_jit(program: np.ndarray, tape_size: int = 30000, max_iterations: int = 100000) -> tuple[np.ndarray, np.ndarray, int, int]: ...
    # Returns (output_values, final_tape, final_pointer, iterations)
```

---

## Dependencies

| Dependency | What it provides | Why not replaced |
|------------|------------------|-----------------|
| Numba | JIT compilation to native code | Only Python JIT library with NumPy interop and `nopython` mode |
| NumPy | Typed arrays for JIT | Required by Numba; provides O(1) array access |

---

## Configuration Keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `MAX_RECURSION` | int | 100000 | Maximum operations per `execute()` call |
| `tape_size` | int | 30000 | Pre-allocated tape size for JIT path |
| `bflib/` | path | `<package_dir>/bflib/` | Directory to resolve `{LIB}` imports from |

---

## Changes

| Date | Source | Change | Reason |
|------|--------|--------|--------|
| 2026-05-02 | ADR-20260502-ir-compilation | Added IR compilation phase | Performance |
| 2026-05-02 | ADR-20260502-jit-acceleration | Added JIT execution path | Performance |
| 2026-05-02 | Optimisation | Replaced Cells(dict) with list + sparse dict | Performance |