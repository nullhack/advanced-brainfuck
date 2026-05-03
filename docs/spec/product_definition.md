# Product Definition: advanced-brainfuck

> **Status:** BASELINED (2026-05-02)

---

## What advanced-brainfuck IS

- A Brainfuck language interpreter that executes Brainfuck programs from Python code or the command line
- A JIT-accelerated execution engine that compiles Brainfuck programs to an intermediate representation and runs them via Numba, with segmented checkpoint/resume for I/O operations
- A library system that allows importing external Brainfuck code modules into running programs

## What advanced-brainfuck IS NOT

- Does NOT compile Brainfuck to standalone executables or machine code
- Does NOT provide a graphical IDE or debugger for Brainfuck programs
- Does NOT implement Brainfuck extensions beyond the documented additional commands (`{LIB}`, `*`, `&`)

## Why does this exist

Brainfuck is a minimal Turing-complete language used for computational theory exercises and code golf. Existing Python interpreters are unacceptably slow for non-trivial programs. advanced-brainfuck fills this gap by combining an easy-to-use Python API with JIT-accelerated execution, making it practical to run real Brainfuck programs at meaningful speed while retaining the language's educational value.

## Users

- **Language enthusiast** — Runs Brainfuck programs interactively or from the command line for learning and experimentation
- **Python developer** — Imports the `BrainFuck` class into Python projects that need a Brainfuck execution engine (e.g., testing, code golf bots, esoteric language toolchains)
- **Library author** — Creates `.bf` files in `bflib/` and imports them via `{libname}` syntax

## Quality Attributes

| Attribute | Scenario | Target | Priority |
|-----------|----------|--------|----------|
| Performance | When a user executes a 10,000+ character Brainfuck program, the interpreter completes in under 1 second | < 1s for 10K-char programs | Must |
| Correctness | When a user runs any valid Brainfuck program, the output matches the language specification exactly | 100% spec compliance | Must |
| Compatibility | When a user runs existing code written for v0.1.0, it produces identical results | Zero breaking changes | Must |
| Usability | When a user imports BrainFuck from Python, the API is self-documenting and requires no configuration | < 2 min to first execution | Should |

---

## Out of Scope

- Standalone binary compilation of Brainfuck programs
- Graphical debugger or IDE
- Brainfuck extensions beyond `{LIB}`, `*`, `&`
- Multi-threading or concurrent execution of multiple Brainfuck instances

## Delivery Order

1 → 2 (Core interpreter must exist before JIT acceleration can be applied)

---

## Project Conventions

### Definition of Done

All criteria must be met before a feature is considered done.

**Development:**

- [ ] All BDD scenarios from the .feature file pass
- [ ] Quality Gate passes all three tiers (Design → Structure → Conventions)
- [ ] Test coverage meets project threshold (≥ 80%)
- [ ] No test coupling — tests verify behavior, not structure
- [ ] Production code follows priority order: YAGNI > DRY > KISS > OC > SOLID > Design Patterns
- [ ] Code uses ubiquitous language from glossary.md

**Review:**

- [ ] CI pipeline passes all three tiers (Design → Structure → Conventions)
- [ ] Code Review approved by R (independent reviewer)
- [ ] Acceptance Testing passed — PO verifies BDD scenarios behave as expected

**Deployment:**

- [ ] Version bumped in pyproject.toml
- [ ] CHANGELOG.md updated with version and delivered scenarios
- [ ] Git tag created (format: `v<semver>`)

### Deployment

**Deployment type:** CLI / Library

#### CLI / Library

- [ ] Package builds without errors (`python -m build`)
- [ ] Package published to PyPI (`twine upload dist/*`)
- [ ] Installable from PyPI in clean environment

#### Rollback Plan

Revert to previous Git tag and republish. No database migrations required.

### Branch Strategy

- **Convention:** Trunk-based (short-lived feature branches from trunk, PR before merge)
- **Branch naming:** `<type>/<short-description>` (e.g., `feature/jit-acceleration`)
- **Merge policy:** Squash merge to trunk after approval

---

## Scope Changes

| Date | Session | Change | Reason |
|------|---------|--------|--------|
| 2026-05-02 | Optimization pass | Added JIT acceleration via Numba | Performance requirement for long programs |