# System Overview: advanced-brainfuck

> Current-state description of the production system.

---

## Summary

advanced-brainfuck is a Python-based Brainfuck language interpreter with JIT acceleration. It compiles Brainfuck source code to an intermediate representation (IR) with run-length encoding and pre-resolved jumps, then executes it either through a Numba JIT-compiled path (for pure computation) or a Python interpreted path (for I/O operations). Users interact via a Python API (`BrainFuck` class) or a CLI (`brainfuck` command).

---

## Delivery

**Mechanism:** CLI / Library

- **CLI:** `brainfuck` command installed via pip, accepts Brainfuck code as positional argument or opens an interactive REPL.
- **Library:** `from brainfuck import BrainFuck` — instantiate and call `.execute()` or `.interpreter()`.

---

## Context (C4 Level 1)

### Actors

| Actor | Description |
|-------|-------------|
| Language Enthusiast | Runs Brainfuck programs interactively or via CLI for learning and experimentation |
| Python Developer | Imports BrainFuck into Python projects needing a Brainfuck execution engine |
| Library Author | Creates `.bf` files in `bflib/` and references them via `{libname}` syntax |

### Systems

| System | Kind | Description |
|--------|------|-------------|
| advanced-brainfuck | Internal | The Brainfuck interpreter, compiler, and library system |

### Interactions

| Interaction | Behaviour | Technology |
|-------------|-----------|------------|
| User → advanced-brainfuck | Submits Brainfuck code via CLI or Python API | Python / argparse |
| advanced-brainfuck → bflib | Resolves `{LIB}` imports by reading `.bf` files from disk | Python filesystem |
| advanced-brainfuck → Numba | Compiles IR to native machine code for fast execution | Numba JIT |

---

## Container (C4 Level 2)

### Boundary: advanced-brainfuck

| Container | Technology | Responsibility |
|-----------|------------|----------------|
| brainfuck.py | Python | Interpreter core: parsing, IR compilation, execution, Cells, CLI |
| bflib/ | Brainfuck files | Reusable library modules (sum, copy, mul, etc.) |
| Numba JIT | Numba / LLVM | Just-in-time compilation of IR to native code |

### Interactions

| Interaction | Behaviour |
|-------------|-----------|
| brainfuck.py → Numba JIT | Converts IR to NumPy arrays and calls `execute_jit()` for fast execution |
| brainfuck.py → bflib/ | Reads `.bf` files and inlines their contents during import resolution |

---

## Module Structure

| Module | Responsibility | Bounded Context |
|--------|----------------|-----------------|
| `BrainFuck` class | Parsing, compilation, execution orchestration, import resolution | Execution |
| `Cells` class | Tape memory model (list + sparse dict) | Memory |
| `execute_jit()` | Numba JIT-compiled execution of IR programs | Execution |
| `convert_ir_to_numeric()` | Converts IR tuples to NumPy arrays for JIT | Compilation |
| `main()` | CLI argument parsing and entry point | Delivery |

---

## Domain Model Documentation

### Why Each Context Exists

| Bounded Context | Business Capability | Why It's Separate |
|-----------------|---------------------|-------------------|
| Execution | Run Brainfuck programs correctly and fast | Distinct because compilation, JIT dispatch, and interpreted fallback have different performance profiles |
| Memory | Manage the Brainfuck tape efficiently | Distinct because the tape data structure is optimised independently (list + sparse dict) |
| Library | Resolve and inline external Brainfuck modules | Distinct because import resolution is a compile-time concern separate from runtime execution |
| Delivery | Expose the interpreter via CLI and Python API | Distinct because delivery format does not affect execution semantics |

### Aggregate Boundary Rationale

| Aggregate | Why These Entities Are Grouped | Transactional Invariant |
|-----------|-------------------------------|------------------------|
| Program | Source code → IR → execution is a single compilation-then-run pipeline | A program must compile successfully before it can execute |
| Tape | Cells and pointer are always accessed together | Pointer must always reference a valid cell index |

---

## Active Constraints

- Python >= 3.13 required (for Numba compatibility)
- Numba and NumPy are required runtime dependencies
- JIT path only available for programs without `,`, `*`, or `&` commands
- Tape pre-allocated to 30,000 cells; sparse dict used for negative indices
- MAX_RECURSION (default 100,000) limits execution to prevent infinite loops

---

## Key Decisions

- IR compilation with run-length encoding chosen over character-by-character interpretation for performance (ADR-20260502-ir-compilation)
- Numba JIT chosen as acceleration backend for its Python integration and zero-copy NumPy support (ADR-20260502-jit-acceleration)
- Cells implemented as list + sparse dict rather than pure dict for O(1) positive-index access
- Library files filtered to valid BF commands only during import (non-BF text treated as comments)

---

## ADRs

See `docs/adr/` for the full decision record.

---

## Completed Features

See `docs/features/` for accepted features.

---

## Changes

| Date | Source | Change | Reason |
|------|--------|--------|--------|
| 2026-05-02 | ADR-20260502-ir-compilation | Added IR compilation with RLE | Performance |
| 2026-05-02 | ADR-20260502-jit-acceleration | Added Numba JIT execution path | Performance |
| 2026-05-02 | Optimisation pass | Replaced Cells(dict) with list + sparse dict | Performance |