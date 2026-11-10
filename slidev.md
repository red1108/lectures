# Slidev implementation notes

Read `phillosophy.md` for shared presentation principles. The pebbling talk in
`pebble/` uses Slidev and the Bricks theme.

## Source and dependencies

- Keep `slides.md`, `package.json`, and `package-lock.json` in the deck folder.
- Put reusable Vue visuals in `components/` and replay logic in `lib/`.
- Put required assets in `public/` and import source snippets by relative path.
- Track recorded trace fixtures and their provenance so the deck runs without
  the external algorithm repository.
- Use `npm ci` for a clean installation. Node 24 LTS is the recommended runtime.
- Keep theme and dependency versions in the individual deck.

## Development and export

Run commands from the deck folder:

```sh
npm ci
npm run dev -- --port 3039
npm test
npm run build
npm run export
```

The development server provides live preview and a built-in Markdown editor.
Edits in that editor save to `slides.md`. Static HTML output is in `dist/`.
PDF export captures static states. Use the live deck for interactive demos.
Use the export command in the deck's package file, including its font/render
wait settings. Inspect exported pages before sharing them.

## Interaction

- Arrow keys navigate the presentation. Playback controls own simulation steps.
- Do not use the slide click counter as a simulation clock.
- Keep code highlighting synchronized with the simulation's local step.
- Provide reset, previous/next, play/pause, and 1x/2x/4x controls for recorded traces.
- Stop playback when the slide becomes inactive.
- Release pointer focus after using demo controls so Slidev navigation continues
  to work. Preserve keyboard activation of controls.
- Use Slidev click reveals when successive equations need to appear in order.
- Use `disabled: true` in slide frontmatter to retain an omitted slide's source.

## Mathematics and validation

Put KaTeX expressions in Markdown blocks with blank lines around them when
nesting them inside HTML containers. Inline dollar expressions inside a raw
HTML paragraph may remain literal text. Check the rendered result.

Keep sources and detailed reasoning in presenter notes. Verify theorem numbers
against the cited manuscript PDF. Explain any simplification in the notes.
Inspect every relevant reveal and the beginning, middle, and end of a simulation.
Check navigation after clicking a control or dragging a slider.

For `pebble/`, `npm run test:browser` accepts `SLIDEV_URL` and an optional
`CHROME_PATH`. Its screenshots go in `.generated/`. The server must already be
running. See the deck README for regeneration and browser installation commands.

## Git policy

Ignore `node_modules/`, `dist/`, `.generated/`, and exported presentations.
Track the assets used by the slides, including generated SVG/PNG circuit figures
and captured JSON traces, together with their generating scripts. Rebuilds should
not add dependency trees, logs, temporary executables, or review screenshots to Git.
