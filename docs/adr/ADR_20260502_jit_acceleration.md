# ADR_20260502_jit_acceleration

## Status

Accepted

## Context

Even with IR compilation and run-length encoding, the execution loop still runs in Python — each IR operation involves a Python `if/elif` chain, attribute access, and method call. For programs with thousands of operations, this Python overhead dominates. Numba's `@jit(nopython=True)` compiles Python functions to native machine code, eliminating interpreter overhead entirely for tight numeric loops.

However, not all Brainfuck operations can run in Numba's `nopython` mode: input (`,`), cell display (`*`), and command history (`&`) require Python I/O and object access. This creates a bifurcated execution path.

## Interview

| Question | Answer |
|---|---|
| Should all programs use JIT or only compatible ones? | Only programs without I/O commands (`,`, `*`, `&`) use JIT; others fall back to interpreted execution |
| Should JIT compilation happen lazily or eagerly? | Eagerly — compile on each `execute()` call since programs change between calls |
| What happens if JIT compilation fails? | Fall back silently to interpreted execution |

## Decision

Implement a Numba JIT-compiled execution path (`execute_jit()`) that handles programs containing only `+`, `-`, `>`, `<`, `. `[`, and `]` commands. Programs with `,`, `*`, or `&` fall back to the interpreted IR execution path.

## Reason

Numba provides 3-5x speedup over interpreted Python for tight numeric loops. The JIT path handles the vast majority of Brainfuck programs (which rarely use `,` or the extended commands). The fallback path preserves full compatibility. The bifurcated design avoids compromising correctness for speed.

## Alternatives Considered

- **Cython extension module:** Rejected — requires compilation step, C knowledge, and build tooling; Numba is pure-Python-decorated
- **PyPy compatibility:** Rejected — would limit to pure Python; Numba is the standard JIT for CPython scientific computing
- **Full LLVM IR generation (llvmlite):** Rejected — would give maximum performance but requires managing LLVM IR directly; Numba abstracts this away
- **C extension via ctypes/cffi:** Rejected — same build complexity as Cython without the ergonomics

## Consequences

- (+) 3-5x speedup for pure-computation Brainfuck programs
- (+) Zero behavioral changes — JIT and interpreted paths produce identical results
- (+) Numba is well-maintained and widely used in scientific Python
- (-) Programs with `,`, `*`, or `&` commands bypass JIT (no speedup)
- (-) First JIT call has compilation overhead (~0.5s); subsequent calls are fast
- (-) Numba and NumPy become required runtime dependencies (large install size)
- (-) Python version constrained to Numba's supported range (currently >=3.9, effectively >=3.13 for our stack)

## Risk Assessment

| Risk | Probability | Impact | Mitigation | Accepted? |
|------|------------|--------|------------|-----------|
| Numba incompatibility with future Python | Medium | High | Interpreted fallback always available | Yes |
| JIT path produces different results than interpreted | Low | High | Doctests verify both paths; cells/pointer state compared after JIT execution | Yes |
| Install size bloated by NumPy/Numba | Medium | Low | Acceptable for a development/scientific tool | Yes |