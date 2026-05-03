Feature: Library Import System

  The {LIB} syntax allows Brainfuck programs to include external code from .bf files
  in the bflib/ directory. Imports are resolved at compile time and inlined into the
  program text. Nested imports are supported recursively.

  Status: BASELINED (2026-05-02)

  Rules (Business):
  - {LIB} in source code is replaced with the contents of bflib/LIB.bf (or LIB without extension)
  - Library files can contain only valid Brainfuck commands; description text is filtered out
  - Nested imports ({LIB} inside a .bf file) are resolved recursively
  - Import cycles are prevented by tracking visited libraries
  - Missing libraries raise an exception: "Could not import: <lib>"
  - The resolved source (with imports expanded) is stored in command history

  Constraints:
  - Import resolution must be recursive but cycle-safe
  - Library content must be filtered to valid BF commands (><+-.,[]) before inlining
  - The bflib/ directory is searched relative to the brainfuck.py module location

  ## Questions

  | ID | Question | Status | Answer / Assumption |
  |----|----------|--------|---------------------|
  | Q1 | Can libraries import other libraries? | Resolved | Yes — recursive resolution is supported |
  | Q2 | What happens with library description text? | Resolved | Non-BF characters are stripped during import |
  | Q3 | Can {LIB} appear inside brackets? | Resolved | Yes — imports are resolved before bracket balancing |

  ## Changes

  | Session | Q-IDs | Change |
  |---------|-------|--------|
  | 2026-05-02 S1 | Q1-Q3 | Created: library import system feature |

  Rule: Library resolution

    As a library author
    I want to import external Brainfuck code
    So that I can reuse common operations without copy-pasting

@id:lib-simple-import
    Example: Import and use a library
      Given a new BrainFuck instance
      When I execute '{toint}*'
      Then the output shows "importing: bflib/toint.bf" followed by a cell display

@id:lib-nested-import
    Example: Import a library that uses other libraries
      Given a new BrainFuck instance
      When I execute a program containing nested {LIB} references
      Then all nested imports are resolved before execution

@id:lib-missing-import
    Example: Import a non-existent library
      Given a new BrainFuck instance
      When I execute '{nonexistent}'
      Then an exception is raised with message "Could not import: nonexistent"

@id:lib-command-history
    Example: Imported code appears in command history
      Given a new BrainFuck instance
      When I execute '+++++++++++++++++++++++++++++++++++++++++++++++++++.' then execute '[-]' then execute '{p10}*{tochar}'
      And I execute '&'
      Then the output shows the expanded command history with library contents inlined