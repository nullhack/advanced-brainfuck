Feature: Core Brainfuck Interpreter

  The interpreter executes standard Brainfuck programs (`><+-.,[]`) correctly and
  efficiently, supporting both one-shot execution from Python and an interactive REPL.
  This feature covers the fundamental language semantics: tape memory, pointer movement,
  cell increment/decrement, I/O, and loop control.

  Status: BASELINED (2026-05-02)

  Rules (Business):
  - The tape consists of cells that default to 0
  - The pointer starts at cell 0
  - `>` increments the pointer; `<` decrements the pointer
  - `+` increments the current cell; `-` decrements the current cell
  - `.` outputs the current cell: if 0, newline; if 1-255, the ASCII character; otherwise the integer
  - `,` reads input: accepts integer or single character, blank line exits input mode
  - `[` jumps forward past the matching `]` if the current cell is 0
  - `]` jumps back to the matching `[` if the current cell is non-zero
  - Brackets must be balanced; unbalanced programs raise an exception
  - Execution halts after MAX_RECURSION operations (default 100,000)

  Constraints:
  - Correctness: output must match the Brainfuck language specification exactly
  - Performance: programs up to 10,000 characters should complete in under 1 second

  ## Frozen Examples Rule

  After a feature is BASELINED, all `Example:` blocks are immutable. Changes require
  `@deprecated` on the old Example (preserving the original @id) and a new Example
  with a new @id.

  ## Questions

  | ID | Question | Status | Answer / Assumption |
  |----|----------|--------|---------------------|
  | Q1 | Should negative pointer positions be supported? | Resolved | Yes — sparse dict stores negative indices |
  | Q2 | What happens when a cell value overflows an integer? | Resolved | Python ints are unbounded; no overflow |
  | Q3 | Should empty input on `,` set cell to 0 or leave it unchanged? | Resolved | Empty input exits input mode; cell is unchanged |

  ## Changes

  | Session | Q-IDs | Change |
  |---------|-------|--------|
  | 2026-05-02 S1 | Q1-Q3 | Created: core interpreter semantics |

  Rule: Basic command execution

    As a language enthusiast
    I want to execute standard Brainfuck commands
    So that I can run any valid Brainfuck program

@id:core-execute
    Example: Execute simple increment and output
      Given a new BrainFuck instance
      When I execute '++++++++++++++++++++++++++++++++++++++++++++++++++.'
      Then the output is "2"

@id:core-balance-true
    Example: Balanced brackets pass validation
      Given a new BrainFuck instance
      When I check if '[[-][-][][{sum}+++.>]]' is balanced
      Then the result is True

@id:core-balance-false-missing-close
    Example: Unbalanced brackets (missing close) fail validation
      Given a new BrainFuck instance
      When I check if '[.[>>>[+++{sum]<<+++.]*]' is balanced
      Then the result is False

@id:core-balance-false-extra-close
    Example: Unbalanced brackets (extra close) fail validation
      Given a new BrainFuck instance
      When I check if '[.[>>>[+++[{sum}<<+++.]*]' is balanced
      Then the result is False

  Rule: Extended commands

    As a language enthusiast
    I want to inspect the tape and command history
    So that I can debug my Brainfuck programs

@id:core-print-cells
    Example: Print all cells with pointer
      Given a new BrainFuck instance with cell 0 set to 50
      When I execute '*'
      Then the output shows "|50|"

@id:core-print-history
    Example: Print command history
      Given a new BrainFuck instance that has executed commands
      When I execute '&'
      Then the output shows the length and content of all executed commands

  Rule: Interactive REPL

    As a language enthusiast
    I want to use an interactive shell
    So that I can experiment with Brainfuck commands incrementally

@id:core-repl
    Example: Start interpreter
      Given a new BrainFuck instance
      When I call interpreter()
      Then an interactive REPL starts with ">> " prompt
      And incomplete bracket lines prompt with ".. "
      And typing "help" shows command reference
      And an empty line exits the REPL