# manim-slides Implementation Notes

This file collects manim-slides specific implementation details. For presentation flow, narrative, and content style that apply regardless of tool, see `phillosophy.md`.

Lecture 4 is the first deck built with manim-slides. The conventions below are what that deck currently uses.

## Why manim-slides

- Beamer remains the default when slides are mostly typeset content.
- manim-slides earns its weight when a lecture leans on motion: state vectors evolving, geometric arguments unfolding, algorithm steps traced over time, success-probability curves filling in.
- The presentation-flow rules in `phillosophy.md` still apply. Animation is a stronger version of progressive reveal — use it only when motion itself carries meaning, not as decoration.

## Stack

- Manim Community Edition (`manim`).
- `manim-slides` for slide segmentation, presentation, and HTML conversion.
- Python ≥ 3.10 (lecture 4 uses 3.10 from a repo-root `.venv`).
- The exact installed versions live in each lecture's `requirements.txt`. After a working render, lock with `pip freeze > requirements.lock` if reproducibility matters.

## File and Folder Layout

Each lecture stays in its own folder, parallel to the Beamer lectures:

- source: `lectureN/main.py` (deck entry) and `lectureN/lecture_base.py` (theme + footer + `LectureScene` base class)
- shared Manim helpers: `shared/`, for reusable primitives that should look identical across lectures
- config: `lectureN/manim.cfg` (output dir, quality), `lectureN/requirements.txt`
- assets: `lectureN/imgs/` (per-lecture, do not share across lectures)
- intermediate artifacts: `lectureN/builds/` (manim media), `lectureN/slides/` (manim-slides JSON + concatenated MP4s), `lectureN/main_assets/` (only when `convert` is run without `--one-file`), `lectureN/__pycache__/`
- final output: `lectureN/main.html`, self-contained (videos embedded as data URIs, reveal.js bundled offline) — parallel to Beamer's `main.pdf`

`references/`, `builds/`, `slides/`, `main_assets/`, `__pycache__/`, and the repo-root `.venv/` are git-ignored. `main.html` is a generated export and is git-ignored.

`lecture_base.py` still lives next to `main.py` because the footer roadmap and section map are lecture-specific. Reusable visual primitives that should stay consistent across lectures live under `Quantum-algorithms-QISCA/shared/`.

### Shared Quantum-Circuit Primitives

Circuit symbols should not be redrawn ad hoc inside slide methods. Put reusable circuit drawing in `Quantum-algorithms-QISCA/shared/quantum_circuit.py` and import it from the lecture file. This keeps notation stable across decks and prevents mistakes such as rendering a measurement as a text box.

Current primitives include:

- `wire(...)` and `wire_bundle(...)` for horizontal quantum wires.
- `single_qubit_gate(...)`, plus `h_gate()`, `pauli_gate("X"|"Y"|"Z")`, `x_gate()`, `y_gate()`, `z_gate()`, `s_gate()`, `t_gate()`, and `phase_gate("S"|"T")`.
- `measurement_gate(...)`, drawn as a boxed meter symbol with an arc and diagonal pointer.
- `swap_gate(...)` and `controlled_swap_gate(...)`, using real crossed-wire markers instead of a text `x`.

Lecture files should still own placement and animation. For example:

```python
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.quantum_circuit import controlled_swap_gate, h_gate, measurement_gate, wire_bundle

wires = wire_bundle(-4.4, 4.2, [1.05, 0.05, -0.95], color=TEXT_MUTED)
h1 = h_gate(stroke_color=TEXT_PRIMARY, text_color=TEXT_PRIMARY).move_to([-2.8, 1.05, 0])
meas = measurement_gate(stroke_color=TEXT_ACCENT).move_to([3.55, 1.05, 0])
```

## Authoring Model

- A deck is one or more `Scene` subclasses written in Python (lecture 4 uses one Scene). Subclass `LectureScene` (defined in `lecture_base.py`), which itself inherits from `manim_slides.Slide`.
- Slide boundaries are `self.next_slide()`. Everything between two `next_slide()` calls plays as one advance step.
- End every slide segment with `self.wait(0.5)` (a real-time literal — *not* `self.wait(0.5 / ANIM_SPEED)`). This holds the final frame steady long enough for `build_static.py`'s last-frame extraction (`ffmpeg -sseof -0.2`) to land after any FadeIn / typewriter / move-to has completed; without it the static PNG can capture mid-animation (faded headings, truncated last word, half-flipped values). The buffer must be absolute because dividing by the speed constant collapses to ~0.17s — too short for the 0.2s seek-back.
- Reserve `self.play(...)` for slides where the audience must absorb steps in a specific order. Mirror Beamer's `\only` discipline: do not animate just to "make something appear later."
- Prefer one Scene per logical section over one giant Scene per deck once decks grow — easier to re-render and easier to reorder. Lecture 4 is short enough to keep as one Scene.

### Sub-slides within one method (arrow-key beats)

When *Auto-advance vs. arrow-key advance* in `phillosophy.md` calls for separate beats inside a single conceptual moment (a value flip → re-evaluation → cycle observation), use sub-slides instead of splitting the work across separate methods:

```python
def _slide_two_sat_assignment(self) -> None:
    self.begin_slide(section="2-SAT")
    # ... build the formula and the value boxes ...
    self.next_slide()                 # arrow-key boundary
    self.begin_slide(clear=False)     # keep current mobjects on screen
    # ... animate the flip ...
    self.next_slide()
    self.begin_slide(clear=False)
    # ... animate the re-evaluation ...
```

`begin_slide(clear=False)` skips the default FadeOut so the previous beat's mobjects stay visible. Use this when a proof or visual argument continues from the previous frame but still needs a new presenter click.

Page-count convention after lecture 4:

- If the sub-slide carries new conceptual content, it is a real page and should advance the visible footer page counter.
- If the sub-slide is only a micro-animation inside the same spoken beat, keep it off the page count with `advance_page=False`.
- If the sub-slide keeps previous mobjects but should count as a page, call `begin_slide(..., clear=False, advance_page=True)`.
- If a method contains counted proof pages, include them in `TOTAL_PAGES` explicitly, for example with an `EXTRA_PROOF_PAGES` constant.

The goal is honest audience orientation. Do not hide substantial proof or derivation steps as "animation-only" beats to make the page count look smaller.

## Theme and Footer

- Dark theme: pure black background, off-white primary text, muted gray for secondary text, soft blue accent. The constants live near the top of `lecture_base.py`.
- The `LectureScene` base class auto-manages a 4-cell footer in the same proportions as the Beamer Madrid footer used in lectures 1 and 3:
  author 15% | major section 40% | current section 35% | page 10%.
- Subclasses call `setup_lecture(author=..., title=..., total_pages=...)` once at the top of `construct`, then `begin_slide(section=..., major_section=...)` at the start of every slide segment. `begin_slide` fades out the previous slide's content, advances the visible page counter only for logical slides, optionally updates the section labels, and refreshes the footer.

### Roadmap strip

Long manim decks should include a thin roadmap strip above the footer. Lecture 4 uses this to show the high-level arc without turning the footer into a second title bar.

- Use about six semantic beats, not one label per subsection. Lecture 4 uses: Intro, Diffusion, 2-SAT, 3-SAT, Quantum Walk, Glued Trees.
- Connect the beats with a thin arrow line and highlight only the current beat.
- Positions do not need to be evenly spaced; place them by narrative weight and label length.
- Use the same body font as the main slide text. Footer and roadmap typography must not look like a different UI system.
- Keep the strip shallow. It should help the audience locate themselves, not compete with the slide.
- Map detailed section names to roadmap beats in one helper such as `roadmap_step_for(...)`, so new slides inherit the right highlight automatically.

## Animations

- Use `FadeIn(mobject, shift=0.2 * UP)` for entrance animations. Adds a small upward drift so the appearance has direction without being noisy.
- Use `LaggedStart(*[FadeIn(b) for b in bullets], lag_ratio=0.3..0.5)` for bullet lists, including outline / TOC / "today's plan" reveals. This is the default for any list-shaped reveal where the audience does not need to read along character-by-character.
- Avoid `AddTextLetterByLetter` (typewriter) for outline-style reveals. Even at high `ANIM_SPEED` the per-character pacing reads as cinematic and makes the audience wait for the slide to catch up to the speaker. Reserve typewriter for moments where the speaker is genuinely walking through a single phrase as it lands — a punchline, a one-line rhetorical question, a status verdict — not for bullet lists.
- Avoid `Write` for plain `Text` — its progressive-stroke effect produces visible cursor artifacts on the final frame and reads as gimmicky for prose.
- Reserve `Write` and stroke-based animations for math (`MathTex`) and figures, where the construction motion carries meaning.

### Two speed multipliers — `ANIM_SPEED` vs `VISUAL_SPEED`

`lecture_base.py` exposes two animation speed constants, both used as divisors on `run_time` (and on `wait` durations between beats):

```python
ANIM_SPEED   = 3.0   # snappy — text, headings, lists, transitions
VISUAL_SPEED = 1.0   # deliberate — walkers, trees, value flips, state animations
```

This is the mechanism for the "fast text, deliberate visualization" pacing rule in `phillosophy.md`. Pick the divisor by what the audience is meant to track:

- `run_time=0.4 / ANIM_SPEED` — heading FadeIn, bullet stagger, section transitions. The audience should see the text appear and immediately read it; the animation is just delivering the text, not carrying meaning.
- `run_time=0.4 / VISUAL_SPEED` — a node lighting up in a graph, a walker stepping, a clause re-evaluating. The animation *is* the content; each step needs time to land.

Tune both per deck if needed (lecture 4 settled at 3.0 / 1.0). When in doubt, use `ANIM_SPEED` — the worst case is the audience reads a beat slightly faster than they expected.

**Do not divide the static-frame buffer by either constant.** The end-of-slide `self.wait(0.5)` is a real-time literal so the ffmpeg seek lands on a settled frame; see *Authoring Model* and *Common Failure Modes*.

## Layout and Spacing

Lecture 4 exposed the main Manim failure mode: the source can be "correct" while the rendered frame feels cramped. Treat the visible frame as the design surface, not the coordinate plane.

- Reserve the bottom band for roadmap + footer. Do not place final formulas or captions so low that they fight this reserved area.
- Prefer a content-safe vertical range. Headings live near the top, conclusions near the lower middle, and the footer/roadmap area is off-limits except for navigation.
- Use the full horizontal width when it helps. If the center is crowded, move explanation text into left/right columns instead of stacking everything vertically.
- When many values must appear on one topic, make them appear and disappear in stages. Do not leave setup equations, intermediate substitutions, reminders, and final results all visible at once.
- A proof slide may be sparse. It is better to spend four pages on setup → recurrence → boundary → conclusion than one page that contains all four.
- If a rendered slide feels like it is "barely not overlapping", it is still too dense. Add whitespace or split the beat.
- Visual metaphors must match the idea. Do not use an arbitrary shape just because it is easy to draw; for example, a diffusion scaling slide should visually communicate "farther distance costs quadratically more time", not just show nested ellipses.

### Formula sizing

- Default formulas should be medium sized and fitted with `max_width`; do not scale math up until it nearly touches the margins.
- Reserve very large math for one-line conclusions only, such as a boxed runtime or a final recurrence solution.
- Labels that are mathematical symbols should be rendered as math, not as Unicode-subscript prose. Use `math(r"a_n", ...)` or `math(r"a_{n-1}", ...)` for labels on boxes, arrows, and diagrams.
- Avoid mixing prose and math in a single oversized expression when the same idea can be shown as a small formula plus a short caption.
- If a formula introduces a non-obvious operator or derivative, add a preceding visual/intuitive slide rather than making the formula bigger.

## Math, Text, and Notation

Three font slots, intentionally distinct so the role (prose / math / code) is legible at a glance:

| Role | Font | How it's set |
| --- | --- | --- |
| Body, headings | **Apple SD Gothic Neo** | `FONT_BODY` constant in `lecture_base.py`; ships with macOS, supports Korean |
| Math | **Computer Modern** (LaTeX default) | Inherited via `MathTex` — no Python-side constant |
| Code, monospace | **Monaco** | `FONT_MONO` constant in `lecture_base.py` |

Pretendard was the first pick (visually pleasant on its own) but produced visible inter-letter gaps inside words like "manim-slides", "current", "MarkupText" at body and footer sizes. The cause is manim Text's per-glyph placement combined with Pretendard's wide sidebearings at small sizes; `disable_ligatures=True` and the `MarkupText` route did not fix it. Apple SD Gothic Neo has tighter, more uniform metrics in manim's pipeline and renders cleanly at 18–48pt across the deck. If a future deck wants Pretendard back, render at ≥36pt and scale down with `.scale()` — that mostly hides the gaps.

`lecture_base.py` exposes two helpers — `body_text(s, ...)` and `mono_text(s, ...)` — that wrap `Text` with the right font slot pre-applied. Use them rather than re-typing `font=...` everywhere. For inline tokens that need the contrast (a single variable name, a short keyword), keep them in body font; only switch fonts when the inline span carries a clear "this is code" or "this is math" signal.

Pango on macOS only resolves fonts that show up in `fc-list`, and **silently falls back** to a default for missing names. Always probe before adding a candidate:

```bash
fc-list : family | sort -u | grep -i '<name>'
```

If the name is not in that list, manim will accept it without complaint and produce identical-looking output to your default — which makes side-by-side font comparisons silently useless. Many "obvious" choices on macOS are not exposed to fontconfig (Inter, IBM Plex, Source Sans, JetBrains Mono, SF Pro, SF Mono, Menlo's italic styles, …). The verified-working set on the current Mac includes: Pretendard, Helvetica Neue, Avenir Next, Lucida Grande, Seravek, Futura, Optima, Geneva, PT Sans, PT Mono, Monaco, Menlo, Andale Mono.

Use `MathTex` for math, `Tex` for prose with TeX features, plain `Text` only when LaTeX is unnecessary. Reuse the Beamer notation conventions (`\ket`, `\bra`, `\braket`, `\ketbra`, `\proj`) — define them in `lecture_base.py` (or the eventual shared module) and import where used. Treat `MathTex` strings exactly like LaTeX source: same escaping rules, same care with `_`, `#`, `%`, `&`.

Pretendard already supports Korean, so prose-side Korean works out of the box. Korean inside `Tex` / `MathTex` would still need a Korean-capable LaTeX setup; defer that decision until the first equation needs it.

### Multi-color math (xcolor)

`lecture_base.math(...)` renders LaTeX through `pdflatex` + `pdftocairo` because TeX Live "basic" lacks dvisvgm. The renderer loads `xcolor` and wraps the snippet in `\(\color[HTML]{F0F0F0} ... \)` so operators and parens stay legible on the dark theme.

To track a per-symbol color (the *Color as Identity* pattern in `phillosophy.md`) into the math expression itself, embed `{\color[HTML]{HEX} ...}` groups inside the LaTeX string and call `math(latex, color=None)` so the helper does not flatten the SVG to the default color after import:

```python
expr = math(
    r"({\color[HTML]{06B6D4} x_1} \vee {\color[HTML]{A78BFA} \neg x_2}) "
    r"\wedge ({\color[HTML]{A78BFA} x_2} \vee {\color[HTML]{FB923C} \neg x_3})",
    color=None,
)
```

Match the hex codes to the `COLOR_VAR1/2/3` constants in `lecture_base.py` so the same symbol carries the same hue inside math, value boxes, and any other place it appears on the slide. Keep the per-symbol palette disjoint from `COLOR_TRUE` / `COLOR_FALSE` / `COLOR_HIGHLIGHT` — the audience reads "this is the variable named X" from the per-symbol palette and "this evaluated to true/false" from the verdict palette, and overlap collapses both signals.

## Theorem-Like Statements

- manim-slides has no built-in theorem environment. Mirror the Beamer feel with a small helper that produces a labeled box (`Definition`, `Claim`, `Observation`, `Proposition`, `Result`) — title bar plus body. Put this helper in `lecture_base.py` so labels look identical across slides.
- Keep the statement short; place intuition below the box, exactly as in Beamer.

## Citations

- Keep a per-lecture `citation.bib` as the source of truth, even though manim-slides does not consume it directly.
- For inline citation marks on slides, render the cite key (or a short author-year tag) as a small `Tex` element — do not retype author-year strings by hand.
- For a final references slide, decide between formatting bib entries through a helper or rendering a Beamer-built bibliography to image and including it. Lecture 4 has no references slide; pin the choice here once exercised.

## Build, Preview, Present

Run from inside a lecture folder, with the repo-root venv on PATH (or by calling its binaries directly).

### Two HTML outputs

One command runs the whole pipeline:

```bash
python build.py
```

`build.py` runs four steps and is idempotent (manim cache is per-animation, the patch step is a no-op once injected):

1. `manim-slides render main.py SCENE` — renders one MP4 per slide.
2. `manim-slides convert --one-file --offline SCENE main.html` — animated self-contained HTML (videos embedded as data URIs, reveal.js bundled).
3. **patches `main.html`** to enable Reveal's progress bar and to inject a small `Reveal.on('slidechanged', ...)` handler that, on backward navigation, seeks the slide's background video to its end and pauses it. Forward navigation still plays animations as usual; backward is now instant. Without this patch, reveal.js auto-plays the forward MP4 from frame 0 on every visit, including left-arrow nav, which feels like the deck "scrubs back through the previous animations." Keep the progress bar enabled in both `main.html` and `main.static.html` so the two outputs have the same slide-position affordance.
4. `python build_static.py SCENE main.static.html` — second HTML where every slide is a still image (last frame of each MP4, embedded as data URI). Use for browsing, distribution, or layout review when even the first-time forward animation is more than you need.

Both `main.html` (animated, with backward-skip patch) and `main.static.html` (still images, instant nav) are local generated exports and stay git-ignored. `builds/static_frames/` and the manim-slides intermediates (`slides/`, `main_assets/` when not `--one-file`) stay git-ignored.

The patch JS lives inside `build.py` as a string constant — open `build.py` and edit the `SKIP_REPLAY_JS` block if you want to change the navigation behaviour (e.g. "play once per slide and never again", or "always play forward, always skip backward"). The current rule is the second one: `event.indexh < event.previousIndexh` ⇒ skip.

### Dev preview workflow

Full `build.py` renders the whole deck, converts the animated HTML, then builds the static HTML. For a lecture-4-sized deck this can take minutes even with cache. Do not use full build as the inner loop.

Use the `Preview` Scene in `main.py` when you only need to inspect one slide's final frame:

```bash
SLIDE=2 manim -s -ql main.py Preview
```

`Preview` is a subclass of the main lecture scene that runs `_slide_*` methods up to `SLIDE` and then stops. Manim's `-s` flag skips animation playback and saves only the final frame as PNG; `-ql` drops quality for speed. The PNG lands at `builds/images/main/Preview_ManimCE_v0.19.1.png`. Open it for a tight inner loop on layout, text, math size, and footer.

For lecture decks whose slide methods are self-contained, add a single-slide fast path to `Preview` and use it during review:

```bash
FAST_PREVIEW=1 SLIDE=15 manim -s -ql main.py Preview
```

This should call only `SLIDE_METHODS[SLIDE - 1]`, set the page counter to `SLIDE - 1` before that method calls `begin_slide`, and write the same preview PNG. Use this for the normal edit → screenshot → visual review loop. Reserve the cumulative `SLIDE=N` preview for cases where a slide intentionally depends on objects created by earlier slide methods.

For multi-beat methods, `SLIDE=N` previews the final state of that top-level method, not every internal arrow-key beat. If the layout risk is inside an internal beat, either temporarily render the method in isolation, inspect the static frames after a full build, or add a local preview target while developing.

For animation iteration (the typewriter timing, fade durations, etc.), run the full `manim-slides render` and then `manim-slides present Lecture4` for the Qt fullscreen player. The Qt player respects manim's cache and navigates with arrow keys, so it's the closest thing to a "real" presentation review without rebuilding HTML. (Requires the `pyside6` extra: `pip install 'manim-slides[pyside6]'`.)

### Visual feedback loop — inspect the rendered PNG

Per the *Screenshot Feedback Loop* rule in `phillosophy.md`, the source compiling cleanly is not enough — the rendered image is the spec.

During editing, first use the `Preview` scene for the changed top-level slide. Before committing or publishing, run `python build.py` and open the per-slide PNG that `build_static.py` extracts:

```
builds/static_frames/<Scene>/slideNN.png
```

`NN` is the manim-slides segment index, zero-padded to two digits. Inspect every segment of a multi-beat slide. Footer page numbers should advance whenever the beat carries new conceptual content; repeated footer numbers are acceptable only for micro-animation beats intentionally marked `advance_page=False`. Things to look for:

- text overlapping another mobject (a checkmark sitting on a caption, two captions stacking, a heading touching the formula below it)
- elements touching the frame edge or hidden behind the footer band
- last-frame extraction artifacts (faded headings, half-typed text, mid-flip values) — see *Common Failure Modes*
- color contrast against `BG_COLOR` (off-white over dark = good; muted gray text on a low-opacity blue ellipse = often illegible)
- bidirectional arrow pairs that visually fused into one line because the perpendicular offset was too small

When a problem is found, edit, preview or rebuild, and **open the same image again** to confirm the fix landed. Do not declare the slide done by reading the source diff; it is done when the image matches intent.

### Config and ignored files

`manim.cfg` redirects manim's media output to `./builds/`. The intermediate directories `slides/`, `main_assets/`, `builds/`, `__pycache__/`, and the repo-root `.venv/` are git-ignored. Source (`main.py`, `lecture_base.py`, `build_static.py`, `manim.cfg`, `requirements.txt`, `imgs/`) is tracked. The two generated HTML outputs (`main.html`, `main.static.html`) are git-ignored.

A save-triggered build (analogous to `scripts/build-tex.sh` for Beamer) is not wired yet — explicit commands keep iteration choices visible.

## Common Failure Modes (and lessons from lecture 4)

- **Background color must be set via `config.background_color = "#000000"` at module load,** not via `self.camera.background_color = "#000000"` inside `construct`. On manim 0.19 + manim-slides 5.6, the latter leaves the value as a `str`, and manim-slides later calls `.to_hex()` on it and crashes. Setting `config.background_color` at the top of `lecture_base.py` makes the renderer pick it up at construction time. As a belt-and-suspenders, also assign `self.camera.background_color = ManimColor(BG_COLOR)` in `setup_lecture`.
- **`self.mobjects` may contain `Group` (not `VGroup`) entries** — `manim-slides`'s internal markers are plain `Group`. Wrapping them in `VGroup(*to_fade)` raises `TypeError: Only values of type VMobject can be added as submobjects of VGroup`. Use `self.play(*[FadeOut(m) for m in to_fade])` instead.
- Default font is serif. Always pass `font=FONT_BODY` (or another explicit font) to `Text` for a sans-serif slide look — or use the `body_text` / `mono_text` helpers in `lecture_base.py`.
- **`MathTex` needs `dvisvgm`,** which TeX Live "basic" does not ship. Do *not* `brew install dvisvgm` — Homebrew's bottle pulls full TeX Live (~4 GB). When dvisvgm is missing, render math via the existing `pdflatex` + `pdftocairo` instead: emit a `\documentclass[border=2pt]{standalone}` snippet, compile to PDF, convert PDF to SVG with `pdftocairo -svg`, and load the SVG with `SVGMobject(...).set_color(WHITE)`. Cache by destination path so re-renders are cheap. (`standalone.cls` itself is in the `standalone` TL package; install via `tlmgr --usermode install standalone preview varwidth` — no root needed.)
- Forgetting `self.next_slide()` between intended slides — the whole scene becomes one continuous animation with no advance points.
- Calling `self.play(...)` for a slide meant to be static. Use `self.add(...)` and a short `self.wait()` instead.
- Re-using the same `Mobject` across scenes without copying — manim mutates state.
- Stale media cache: after notation or font changes, clear `builds/` (or pass `--flush_cache`) before re-rendering.
- **Static-frame extraction races a still-running animation.** `build_static.py` calls `ffmpeg -sseof -0.2` to grab the last frame of each slide MP4. If the slide's terminal animation (FadeIn of a status line, typewriter on a final phrase, FadeOut of a highlight box) is still playing 0.2 s before the MP4 ends, the captured PNG is mid-animation: a faded heading, a truncated last word, a half-flipped value, a ghost of a box that was supposed to be gone. Defensive rule: every slide segment ends with `self.wait(0.5)` — a *real-time* literal, never `0.5 / ANIM_SPEED` (which collapses to ~0.17 s and re-introduces the race). When this artifact appears, look for a closing `wait` that was divided by a speed constant.

## Open Decisions

These will be resolved as decks need them and the answers recorded here:

- Korean text rendering path (when the first Korean-bearing slide arrives).
- Citation rendering strategy on a references slide (when one is needed).
- Whether to wire a save-triggered render hook similar to the Beamer flow.
- When to factor `lecture_base.py` out of `lecture4/` into a shared module — trigger is "lecture 5 also goes manim."
