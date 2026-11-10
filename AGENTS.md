# Lecture authoring

Read `phillosophy.md` for presentation flow, content density, and visual review.
Then read the document for the deck's tool:

- `main.tex` uses `beamer.md`.
- Manim Python scenes use `manim.md`.
- `slides.md` with a Slidev `package.json` uses `slidev.md`.

Use the commands and dependencies in the individual deck. Keep its assets inside
its folder and use relative paths. Preserve existing author edits.

Track source, dependency manifests, lockfiles, build helpers, and assets consumed
by the deck. Keep generated presentations, dependencies, caches, screenshots,
logs, and temporary executables ignored. Check the staged file list before a
commit. Files already tracked require an index change to become ignored.

After layout or interaction changes, inspect the rendered slide and the relevant
states. Build success alone does not establish layout or interaction correctness.
