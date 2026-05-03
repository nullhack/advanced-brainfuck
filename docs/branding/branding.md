# Branding — advanced-brainfuck

> *High-performance Brainfuck interpreter for Python*

Agents read this file before generating release names, C4 diagrams, README banners, or any document with visual or copy identity. All fields are optional; absent or blank fields fall back to defaults (adjective-animal release names, Mermaid default colours, no wording constraints).

**Ownership**: The stakeholder owns this file. The design agent proposes changes; the stakeholder approves them. No other agent edits this file.

---

## Identity

- **Project name:** advanced-brainfuck
- **Tagline:** Run Brainfuck programs at native speed from Python
- **Mission:** Make Brainfuck execution practical for real programs by combining an easy Python API with JIT-accelerated performance
- **Vision:** The de facto Python Brainfuck interpreter — fast, correct, and extensible
- **Tone of voice:** direct, precise, minimal

## Visual

The palette is drawn from terminal aesthetics — dark backgrounds, bright accents, monospace precision. Every colour choice serves legibility first; decoration is secondary.

- **Background:** `#0B1026` — Deep navy terminal dark; reduces eye strain during long sessions
- **Primary text:** `#F0F0F0` — High-contrast light text on dark backgrounds
- **Accent gold:** `#FFB800` — Highlights for pointers and active cells; decorative only
- **Secondary blue:** `#6A7AA0` — Links, commands, and interactive elements
- **Logo:** `docs/assets/logo.svg`
- **Banner:** `docs/assets/banner.svg`

> `#F0F0F0` on `#0B1026` achieves high contrast (WCAG AAA). `#FFB800` is decorative; it never carries meaning that must be read.

### Logo

The logo depicts Brainfuck command syntax: heavy brackets `[ ]` enclosing stylized directional arrows `< >` and a central dot `.` representing output. The brackets use secondary blue (`#6A7AA0`), arrows use primary white (`#F0F0F0`), and the dot uses accent gold (`#FFB800`). All elements maintain geometric precision with rounded corners. Dark-mode variant uses the same colors on navy background.

### Banner

The banner (1280×320) uses navy background (`#0B1026`) with a subtle code pattern. The logo sits left at 120px from edge, vertically centered and scaled to 0.35x. Project name "advanced-brainfuck" in white at 48px sits center-right, with tagline "JIT-Accelerated Brainfuck Interpreter" below in blue-gray (`#6A7AA0`) at 18px. Key command highlight `[ < . > ]` appears in gold within a rounded blue-gray background.

## Release Naming

- **Pattern:** Release codenames reference phenomena that alter how the brain operates — neurological conditions, cognitive effects, brain injuries, or mental states. Multi-word phrases are welcome. The name should metaphorically echo what the release changes about the interpreter.
- **Format:** `v<semver>` tag with codename in release notes (e.g., `v0.3.0 — Syncope`).
- **Existing releases:**
  - `v0.1.0` — **Amnesia** (the interpreter forgets nothing, but the name nods to Brainfuck's memory tape)
  - `v0.2.0` — *(no codename assigned)*
  - `v2.0.0` — **Neuroplasticity** (the brain's ability to reorganize — the interpreter dynamically adapts between JIT and I/O operations)
  - `v2.1.0` — *(no codename assigned)*
  - `v2.2.0` — **Memory Consolidation** (the brain's process of stabilizing a memory trace — the interpreter now persists tape state)
- **Examples:** Aphasia, Transient Global Amnesia, Frontal Lobe Syndrome, Absence Seizure, Hemispheric Neglect, Brain Injury

## Wording

Every word carries weight.

- **Avoid:** easy, simple, just, quick, scaffold, superseded, boilerplate, lightweight, blazing
- **Prefer:** precise, production-ready, correct, fast, rigorous, minimal