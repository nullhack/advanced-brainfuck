# Domain Model: advanced-brainfuck

> Current understanding of the business domain.

---

## Summary

The Brainfuck domain is a single bounded context: a program (source text) is compiled to an intermediate representation (IR) and executed against a tape (memory model). The tape is a sequence of integer cells addressed by a movable pointer. Library modules extend programs through textual inclusion at compile time.

---

## Event Map

### Domain Events

| Event | Description | Trigger | Bounded Context |
|-------|-------------|---------|-----------------|
| `ProgramSubmitted` | User provides Brainfuck source code for execution | CLI argument or `.execute()` call | Execution |
| `ProgramCompiled` | Source code parsed and converted to IR | `BrainFuck.execute()` compile phase | Execution |
| `ImportResolved` | Library `{LIB}` reference replaced with file contents | `BrainFuck._resolve_imports()` | Library |
| `CellModified` | A cell value on the tape is changed | `+`, `-` commands | Memory |
| `PointerMoved` | The data pointer changes position | `>`, `<` commands | Memory |
| `ValueOutput` | A cell value is printed to stdout | `.` command | Execution |
| `ValueInput` | A value is read from stdin into a cell | `,` command | Execution |
| `ProgramCompleted` | Execution finishes (end of program or MAX_RECURSION) | End of IR program or limit reached | Execution |

### Commands

| Command | Description | Produces Event | Actor |
|---------|-------------|----------------|-------|
| `Execute` | Compile and run a Brainfuck program | `ProgramSubmitted` → `ProgramCompiled` → `ProgramCompleted` | User |
| `ImportLib` | Resolve `{LIB}` references in source | `ImportResolved` | BrainFuck |
| `StartInterpreter` | Begin interactive REPL session | `ProgramSubmitted` (per line) | User |

### Read Models

| Read Model | Description | Consumes Event | Used By |
|------------|-------------|----------------|---------|
| CellDisplay | Shows all cells with pointer highlight | `CellModified`, `PointerMoved` | User (`*` command) |
| CommandHistory | Shows all executed commands | `ProgramCompleted` | User (`&` command) |
| Output | Character or integer printed to stdout | `ValueOutput` | User |

---

## Context Candidates

| Candidate | Responsibility | Grouped Aggregates | Notes |
|-----------|---------------|--------------------|-------|
| Execution | Compile and run programs | Program | Core interpreter loop |
| Memory | Manage tape state | Tape (Cells + Pointer) | List + sparse dict implementation |
| Library | Resolve and inline external modules | Library | Filesystem-based .bf resolution |

---

## Aggregate Candidates

| Candidate | Events Grouped | Tentative Root Entity | Notes |
|-----------|---------------|-----------------------|-------|
| Program | `ProgramSubmitted`, `ProgramCompiled`, `ProgramCompleted` | BrainFuck | Single compilation-then-execution pipeline |
| Tape | `CellModified`, `PointerMoved` | Cells | Cell value and pointer always accessed together |

---

## Bounded Contexts

| Context | Responsibility | Key Entities | Integration Points |
|---------|----------------|--------------|-------------------|
| Execution | Parse, compile, and execute Brainfuck programs | BrainFuck (aggregate root), IR | Delegates to Memory context for cell operations |
| Memory | Store and retrieve cell values | Cells (aggregate root), Pointer | Called by Execution context |
| Library | Resolve and inline external code | bflib files | Called by Execution context at compile time |

---

## Entities

| Name | Type | Description | Bounded Context | Aggregate Root? |
|------|------|-------------|-----------------|-----------------|
| BrainFuck | Entity | Main interpreter: parses, compiles, and executes programs | Execution | Yes |
| Cells | Entity | Tape memory model: pre-allocated list + sparse dict | Memory | Yes |
| IR Operation | Value Object | Compiled instruction tuple: `(op_name, arg)` or `(op_name,)` | Execution | No |
| Pointer | Value Object | Integer index into the tape | Memory | No |
| Library File | Value Object | `.bf` file contents loaded from `bflib/` | Library | No |

---

## Relationships

| Subject | Relation | Object | Cardinality | Notes |
|---------|----------|--------|-------------|-------|
| BrainFuck | owns | Cells | 1:1 | Each interpreter instance has exactly one tape |
| BrainFuck | produces | IR | 1:N | One program compiles to many IR operations |
| BrainFuck | resolves | Library File | 0:N | Programs may import zero or more libraries |
| Cells | contains | Cell Values | 1:N | One tape holds many cell values |
| Cells | tracks | Pointer | 1:1 | One tape has one current pointer |

---

## Aggregate Boundaries

| Aggregate | Root Entity | Invariants | Bounded Context |
|-----------|-------------|------------|-----------------|
| Program | BrainFuck | A program must compile (balanced brackets) before execution; MAX_RECURSION bounds execution length | Execution |
| Tape | Cells | Unset cells default to 0; cells set to 0 are removed from storage | Memory |

---

## Changes

| Date | Source | Change | Reason |
|------|--------|--------|--------|
| 2026-05-02 | Optimisation pass | Added IR as domain concept | Performance |
| 2026-05-02 | Optimisation pass | Changed Cells from dict-subclass to list + sparse dict | Performance |