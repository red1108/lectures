# Beamer Implementation Notes

This file collects Beamer-specific implementation details. For presentation flow, narrative, and content style that apply regardless of tool, see `phillosophy.md`.

Lectures 1 and 3 are built with Beamer. The conventions below are what those decks use.

## Engine and Theme

- Engine is `pdflatex`. Pin it at the top of `main.tex` with `% !TEX program = pdflatex`.
- Theme: `Madrid`. Color theme: `default`.
- Remove navigation symbols: `\setbeamertemplate{navigation symbols}{}`.
- Preserve section overview slides via `\AtBeginSection` for longer talks.
- Keep a consistent footer across decks. Current split:
  author (15%) | title (40%) | section (35%) | page (10%).
- Prefer a small set of dependable packages. Only add extras when a concrete slide need arises.
- Keep common quantum notation available in the template:
  `\ket`, `\bra`, `\braket`, `\ketbra`, `\proj`.
- Prefer custom-safe macros over package-heavy rewrites unless there is a clear need.
- Use `\setbeamercovered{transparent}` so still-hidden overlays remain faintly visible.

## Theorem-Like Environments

- Numbered environments registered alongside `theorem`:
  `claim`, `proposition`, `observation`, `result`.
- Unnumbered remark via `\theoremstyle{remark}` then `\newtheorem*{remark}{Remark}`, then switch back with `\theoremstyle{plain}`.
- Use these to mark statements that the audience should treat as the slide's anchor (`Definition`, `Claim`, etc.). Keep the statement short; place intuition below.

## Citations and Bibliography

- Each lecture has its own `citation.bib` next to `main.tex`.
- Cite with `\cite{...}` rather than typing author-year strings by hand.
- Use `\setbeamertemplate{bibliography item}[text]` so bibliography entries read as text rather than icons.
- The build script runs `bibtex` automatically when the aux file shows `\bibdata{}` and `\citation{}`.

## Overlays and Progressive Reveal

The principle (use sparingly, default to static) is in `phillosophy.md`. The Beamer mechanics:

- For sequential reveal of a list, put `[<+->]` on the list environment.
- For a transition line that should appear *after* a list is fully revealed, do not default to `\pause`, and do not write `<n->` on that line.
  Use `\only<k->{...}` where `k` is one step past the last bullet, so the line stays completely hidden until the next click.
- Use `<n->` only when a line is intentionally meant to appear together with the bullet at step `n`.
- Recap, motivation, problem-statement, and stable definition slides should be fully static — no overlay specifiers at all.

## Images

- Reference images by per-lecture relative path from `main.tex`, e.g. `\includegraphics[width=\textwidth]{imgs/file.png}`.
- For wide images use `width=\textwidth`; for tall ones cap with `height=...`.
- Always include `keepaspectratio` so nothing distorts.

## Build System

Folder layout per lecture:

- source: `lectureN/main.tex`, `lectureN/citation.bib`, `lectureN/imgs/`
- aux artifacts: `lectureN/builds/`
- final output: `lectureN/main.pdf`

The build is driven by `scripts/build-tex.sh`, which:

- reads `% !TEX program = ...` from the first 20 lines of the file (defaults to `xelatex` when absent — the lectures pin `pdflatex`)
- finds the nearest `main.tex` walking up from the edited file
- runs the engine three times (with `bibtex` in between when needed) into `builds/`
- copies the final pdf to the lecture root
- cleans stray aux files left in the lecture root

VS Code is wired through `.vscode/settings.json` so save triggers `build-tex.sh` automatically. `latex-workshop.latex.outDir` and `auxDir` both point at `%DIR%/builds`.

`references/` (PDFs of source papers), `builds/`, and the generated `main.pdf` are git-ignored. Track the TeX source, bibliography, assets, and build helpers.

## Common TeX Failure Modes

- Unescaped special characters: `#`, `%`, `_`, `&`.
- Missing `\end{frame}`.
- Mismatched math delimiters.
- Bad image paths after a deck is moved or renamed (the per-lecture `imgs/` rule prevents this).
- Duplicate theorem or environment definitions.
- Raw Unicode under `pdflatex`, especially Korean text and emoji. The current template registers `\DeclareUnicodeCharacter{1F914}{\thinkingemoji}` to handle the thinking-face emoji explicitly. Extend this pattern when more Unicode characters appear.
- For presentation work, eliminate fatal compile errors first, then worry about layout warnings such as overfull boxes.
