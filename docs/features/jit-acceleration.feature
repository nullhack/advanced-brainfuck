Feature: JIT Acceleration

  Programs containing only computation commands (+, -, >, <, ., [, ]) are executed
  through a Numba JIT-compiled path for significantly improved performance. Programs
  with I/O or extended commands fall back to interpreted execution.

  Status: BASELINED (2026-05-02)

  Rules (Business):
  - Programs without `,`, `*`, or `&` commands are automatically routed to the JIT path
  - Programs with `,`, `*`, or `&` commands use the interpreted fallback path
  - Both paths must produce identical output for identical input
  - The JIT path uses Numba's @jit(nopython=True) decorator
  - The IR is converted to NumPy int32 arrays before JIT execution
  - Cell state is transferred to/from the JIT tape transparently

  Constraints:
  - Performance: JIT path should achieve at least 2x speedup over interpreted path for programs > 1000 characters
  - Compatibility: both paths must produce byte-identical output
  - Numba and NumPy are required runtime dependencies

  ## Frozen Examples Rule

  After a feature is BASELINED, all `Example:` blocks are immutable.

  ## Questions

  | ID | Question | Status | Answer / Assumption |
  |----|----------|--------|---------------------|
  | Q1 | What happens if Numba is not installed? | Resolved | ImportError at import time; no silent fallback |
  | Q2 | What happens if JIT compilation fails? | Resolved | Falls back silently to interpreted execution |
  | Q3 | Should the JIT path have a different MAX_RECURSION? | Resolved | No — same limit applies |

  ## Changes

  | Session | Q-IDs | Change |
  |---------|-------|--------|
  | 2026-05-02 S1 | Q1-Q3 | Created: JIT acceleration feature |

  Rule: JIT path selection

    As a Python developer
    I want programs without I/O to execute faster
    So that long-running Brainfuck programs complete in reasonable time

@id:jit-pure-computation
    Example: Pure computation uses JIT path
      Given a BrainFuck instance
      When I execute '+++++++++++++++++++++++++++++++++++++++++++++++++++.' (no , * or &)
      Then the output is "3" (via JIT execution)

@id:jit-fallback-interpreted
    Example: Programs with input fall back to interpreted
      Given a BrainFuck instance
      When I execute a program containing ',' (input command)
      Then the interpreted path is used

@id:jit-output-correctness
    Example: JIT output matches interpreted output
      Given a BrainFuck instance
      When I execute '++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.'
      Then the output is "H" (identical to interpreted output)

  Rule: IR compilation

    As a Python developer
    I want consecutive commands to be collapsed into single operations
    So that the execution loop processes fewer operations

@id:jit-run-length-encoding
    Example: Consecutive increments are collapsed
      Given a BrainFuck instance
      When I execute '+++++' (five increments)
      Then the IR contains a single ('add', 5) operation instead of five add-1 operations

@id:jit-jump-patching
    Example: Jump targets are pre-resolved
      Given a BrainFuck instance
      When I compile '[-]'
      Then the IR contains jump_zero and jump_nz with pre-computed target indices