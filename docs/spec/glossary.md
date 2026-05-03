# Glossary: advanced-brainfuck

> Living glossary of domain terms used in this project.
> Code and tests take precedence over this glossary — if they diverge, refactor the code, not this file.

---

## BrainFuck

**Definition:** An esoteric programming language with 8 instructions (`><+-.,[]`) operating on a tape of cells with a movable pointer.

**Aliases:** BF, brainfuck

**Example:** `+++.` increments cell 0 three times and outputs the result (ASCII 3).

**Source:** core-interpreter

## Cell

**Definition:** A single integer storage location on the Brainfuck tape, addressable by index, defaulting to 0 when uninitialised.

**Aliases:** register

**Example:** In `+>++`, cell 0 holds 1 and cell 1 holds 2.

**Source:** core-interpreter

## Pointer

**Definition:** An integer index indicating which cell on the tape is currently active for reading, writing, or output.

**Aliases:** data pointer, cursor

**Example:** The `>` command increments the pointer; `<` decrements it.

**Source:** core-interpreter

## Tape

**Definition:** The virtual memory model of Brainfuck: a sequence of cells indexed by the pointer, with a pre-allocated region for positive indices and a sparse dict for negative indices.

**Aliases:** memory, cells

**Example:** The default tape pre-allocates 30,000 cells; negative indices are stored in a sparse dictionary.

**Source:** core-interpreter

## IR

**Definition:** Intermediate Representation — a compiled form of Brainfuck source where consecutive identical commands are collapsed into single operations with counts (e.g., `+++++` becomes `('add', 5)`), and jump targets are pre-resolved.

**Aliases:** intermediate representation, compiled program

**Example:** The IR for `+++>[-]<` is `[('add', 3), ('move', 1), ('jump_zero', 4), ('add', -1), ('jump_nz', 2), ('move', -1)]`.

**Source:** ir-compilation

## Library Import

**Definition:** The `{LIB}` syntax that inlines the contents of an external `.bf` file from the `bflib/` directory into the current program at parse time.

**Aliases:** lib import, include

**Example:** `{sum}` resolves to the contents of `bflib/sum.bf`.

**Source:** core-interpreter

## JIT Execution

**Definition:** A fast execution path that converts the IR program to NumPy arrays and runs it through Numba's `@jit(nopython=True)` compiled function, bypassing the Python interpreter loop.

**Aliases:** JIT path, fast path

**Example:** Programs containing only `+`, `-`, `>`, `<`, `.`, `[`, `]` are eligible for JIT execution.

**Source:** jit-acceleration

## Interpreted Execution

**Definition:** The fallback execution path that processes IR operations one at a time through Python, used when the program contains commands incompatible with JIT (input `,`, print cells `*`, print history `&`).

**Aliases:** slow path, fallback path

**Example:** A program containing `,` (input) falls back to interpreted execution.

**Source:** jit-acceleration

## Command History

**Definition:** A record of all expanded Brainfuck commands executed in a session, stored as a list of strings and joinable on demand for the `&` command.

**Aliases:** cmd_history

**Example:** After `bf.execute('+++')`, `bf.print_cmd_history()` prints the expanded command string.

**Source:** core-interpreter

## Run-Length Encoding

**Definition:** The IR compilation optimisation that collapses consecutive identical commands into a single operation with a count argument, reducing the number of operations the execution loop must process.

**Aliases:** RLE, command collapsing

**Example:** `+++++` is compiled to `('add', 5)` instead of five separate add-1 operations.

**Source:** ir-compilation

## Jump Table

**Definition:** A pre-computed mapping from each `[` to its matching `]` and vice versa, embedded in the IR as the second element of jump operations, enabling O(1) bracket navigation.

**Aliases:** bracket matching

**Example:** `[+]` compiles to `[('jump_zero', 2), ('add', 1), ('jump_nz', 0)]` where the numbers are jump targets.

**Source:** ir-compilation