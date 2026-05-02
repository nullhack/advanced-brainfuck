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

- **Background/parchment:** `#1E1E2E` → `#11111B` — Deep terminal dark; reduces eye strain during long sessions
- **Primary text:** `#CDD6F4` → `#BAC2DE` — High-contrast light text on dark backgrounds
- **Accent/gold:** `#F9E2AF` → `#F5C2E7` — Highlights for pointers and active cells; decorative only
- **Secondary/blue:** `#89B4FA` → `#74C7EC` — Links, commands, and interactive elements
- **Stone/marble:** `#6C7086` → `#585B70` — Muted text, comments, and secondary information
- **Logo:** `docs/assets/logo.svg`
- **Banner:** `docs/assets/banner.svg`

> `#CDD6F4` on `#1E1E2E` achieves 12.4:1 contrast (WCAG AAA). `#F9E2AF` is decorative; it never carries meaning that must be read.

### Logo

The logo mark depicts a Brainfuck tape: eight rectangular cells arranged horizontally, with one cell highlighted by the data pointer. The highlighted cell uses the accent colour (`#F9E2AF`); other cells use primary text (`#CDD6F4`). The pointer arrow below uses secondary blue (`#89B4FA`). All strokes are 2px. Dark-mode variant inverts: dark cells on light background.

### Banner

The banner layout uses the terminal background (`#1E1E2E`) across the full 1200×630 canvas. The logo sits left-centred at 64px from the left edge, vertically centred. Project name "advanced-brainfuck" in `#CDD6F4` monospace at 48px sits to the right of the logo, with the tagline below in `#6C7086` at 20px. A thin `#89B4FA` horizontal rule separates the tagline from the name.

## Release Naming

- **Convention:** `adjective-stone`
- **Theme:** Stones and minerals — enduring, foundational, precisely formed
- **Excluded words:** diamond, gold, silver (too precious/cliché)

## Wording

Every word carries weight.

- **Avoid:** easy, simple, just, quick, scaffold, superseded, boilerplate, lightweight, blazing
- **Prefer:** precise, production-ready, correct, fast, rigorous, minimal