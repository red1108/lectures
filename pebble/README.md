# Pebbling computations

A 34-slide, 15–20 minute introductory talk using Slidev and the
[Bricks theme](https://github.com/slidevjs/themes/tree/main/packages/theme-bricks).
The slides are in English and presenter notes are in Korean.

## Present

Use Node 24 LTS and npm. From this folder:

```sh
npm ci
npm run dev -- --port 3039
```

Open the printed URL. The navigation toolbar opens the built-in Markdown editor,
which saves edits to `slides.md`. Arrow keys navigate the presentation. Each trace
has its own playback buttons, slider, and 1x/2x/4x speed controls. Playback stops
when leaving the slide. The first demo supports clicking individual pebbles.

## Build and check

```sh
npm test
npm run build
```

The static site is generated in `dist/`. To run the browser checks against an
already running development server:

```sh
npx playwright install chromium
SLIDEV_URL=http://localhost:3039 npm run test:browser
```

Set `CHROME_PATH` to use an existing Chrome or Chromium executable instead of the
bundled browser. Screenshots and review files are generated in `.generated/`.

```sh
npm run export
```

For a single HTML file that opens directly in a browser, including offline fonts
and interactive demos:

```sh
npm run build:standalone
```

The file is generated at `.generated/pebble-talk.html`.

PDF export creates `pebble-talk.pdf`. It captures static states. Present the
interactive animations from the browser. An existing browser can be selected
with `npm run export -- --executable-path /path/to/chrome`.

## Trace provenance

Recorded schedules in `traces/native.json` come from the
[paper's C++ implementation](https://github.com/red1108/pebble) at commit
`d5081286aaa1b99c6caa220ce05966b308cbd2ed`. The fixture includes source hashes and records any tracked source changes. It lets the presentation run without that
repository or a C++ compiler. Replay validates dependencies, register occupancy,
parallel active sets, work, and final states.

To regenerate the fixtures and the C++ reference snippet, supply a source
checkout explicitly. A C++17 compiler and Git are required:

```sh
PEBBLE_REPO=/path/to/pebble npm run traces:generate
npm test
```

Set `CXX` to select the compiler. Regeneration records the selected checkout's
revision, source hashes, and tracked changes, so inspect the resulting diff.

Line strategies are adapted from
[Gidney's 2019 article](https://algassert.com/post/1905), with explicit ghost
recomputation and cleanup. The block-cleanup idea diagram is a conceptual
illustration. The algorithm trace slides replay recorded implementation actions.
The KMRV demo uses a length-16 path with a fixed anchor and retained endpoint.
An older short path slide is retained with `disabled: true`.
Detailed mathematical explanations and source references are in presenter notes.
The root-computation pseudocode follows Algorithm 1, `SequentialPebble(T)`,
in the submitted manuscript; its action lines follow the recorded trace.
The boundary-expansion demo follows Algorithm 2, `Boundary(T, m)`, and the
`build_boundary` recursion in `sequential.cpp`. It draws a four-level tree
with a target boundary size of six. Its frontier marks subtree roots being
split during construction, rather than occupied quantum registers.

## Circuit figures

The slides use the SVG and PNG files in `public/figures/`. To redraw them:

```sh
uv run --with matplotlib python scripts/draw_measurement_circuit.py
```

## Research plots

`sequential-work-and-memory.svg` and `associative-reduction-depth.svg` are
vector conversions of the submitted `numerical_tradeoffs.pdf` and
`associative_reduction_depth.pdf`, respectively. Convert each with
`pdftocairo -svg input.pdf output.svg`.

## Tracked files

Source, dependency manifests and lockfiles, required figure assets, recorded
traces, and generation/validation scripts are tracked. `node_modules/`, `dist/`,
`.generated/`, and `pebble-talk.pdf` are ignored. Authoring conventions are in the
repository's `AGENTS.md`, `phillosophy.md`, and `slidev.md`.

The parallel-computation circuit is drawn with LaTeX Quantikz. To regenerate
its SVG and PNG assets, install Quantikz and its TeX dependencies, then run:

```sh
bash scripts/build_parallel_circuit.sh
```

The script requires `pdflatex` and `pdftocairo`. Intermediate TeX/PDF files stay
in `.generated/parallel-circuit/`.
