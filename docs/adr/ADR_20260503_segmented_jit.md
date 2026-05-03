# ADR_20260503_segmented_jit

## Status

Accepted

## Context

The original JIT implementation used a bifurcated execution model: programs without I/O commands (`,`, `*`, `&`) ran through the fast Numba JIT path, while programs containing any of these commands fell back entirely to the slow interpreted Python loop. This meant that real-world Brainfuck programs — which commonly use `,` for input — received zero JIT acceleration, even though the I/O operations represent a tiny fraction of total execution time.

The core problem is that Numba's `nopython` mode cannot call Python functions or access Python objects. Input requires `input()`, cell display requires `Cells.print_pos()`, and history requires `Cells` state. Previously, this meant the entire program had to run in Python if it contained even a single `,` command.

## Interview

| Question | Answer |
|---|---|
| Should all programs use JIT or only compatible ones? | All programs — segmented execution lets I/O commands act as checkpoints while the rest runs at native speed |
| How should state be preserved across checkpoints? | Use a mutable NumPy state array `[pointer, pc, output_count]` that Numba modifies in-place |
| What happens when the output buffer fills? | Flush accumulated outputs and resume JIT from the saved PC |
| What if JIT compilation fails? | Fall back to interpreted IR execution (unchanged behavior) |

## Decision

Replace the bifurcated execution model with segmented JIT execution. `execute_jit()` runs at native Numba speed until it hits an I/O operation, then returns a status code and saves execution state. Python handles the I/O at each checkpoint, then resumes JIT execution from the saved program counter.

Status codes: STATUS_COMPLETE (0), STATUS_NEED_INPUT (1), STATUS_PRINT_CELLS (2), STATUS_PRINT_HISTORY (3), STATUS_OUTPUT_OVERFLOW (4).

## Reason

Real Brainfuck programs almost always contain input commands. The previous design penalised these programs with 100% interpreted execution even though I/O operations represent <1% of total operations. Segmented execution gives all programs JIT acceleration for the compute-heavy segments between I/O checkpoints.

The mutable state array approach solves Numba's limitation of not being able to return multiple values or pass Python objects — the array is modified in-place and the status code is the return value.

## Alternatives Considered

- **Keep bifurcated model:** Rejected — programs with `,` are the common case and get no speedup
- **Callback-based I/O in JIT:** Rejected — Numba `nopython` mode cannot call Python callbacks
- **Two-pass execution (JIT for compute, Python for I/O):** Rejected — would require splitting the program into segments at compile time, duplicating jump resolution logic
- **Cython extension for I/O programs:** Rejected — adds build complexity; segmented JIT achieves the same goal within the existing Numba infrastructure

## Consequences

- (+) All programs now benefit from JIT acceleration, including those with input
- (+) I/O operations still execute correctly with full Python access to Cells state
- (+) Programs like LostKingdom.b (188K IR ops, 9 input commands) now execute via segmented JIT
- (-) Slight overhead at each checkpoint (Python ↔ JIT transition, ~microseconds)
- (-) Output buffer size (64K) limits buffered output before flush-and-resume cycle
- (-) More complex execution orchestration (`_execute_segmented_jit` loop)

## Risk Assessment

| Risk | Probability | Impact | Mitigation | Accepted? |
|------|------------|--------|------------|-----------|
| Checkpoint overhead degrades performance on I/O-heavy programs | Low | Low | Checkpoint cost is microseconds; typical programs have few I/O ops | Yes |
| Output buffer overflow causes data loss | Very Low | High | STATUS_OUTPUT_OVERFLOW triggers flush-and-resume; no data is lost | Yes |
| State array mutation causes correctness bugs | Low | High | State is a simple 3-element int64 array; tested with input, display, and history ops | Yes |