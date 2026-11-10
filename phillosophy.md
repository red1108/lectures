# Lecture Slide Philosophy

## Purpose

This file records the working principles for making lecture slides in this repository.
It is not a changelog.
When new instructions overlap with existing ones, integrate them into the relevant section instead of appending repetitive notes.

The goal is to gradually accumulate a consistent slide-making style so new lecture materials can be produced quickly and still feel like they were made by the same person.

This file covers presentation flow, narrative, and content style — concerns that apply regardless of which tool produces the slides. Tool-specific implementation details belong in companion files:

- `beamer.md` — LaTeX Beamer specifics (engine, theme, theorem environments, overlays, images, build, failure modes).
- `manim.md` — manim-slides specifics (Scene structure, animation discipline, layout, build, failure modes).
- `slidev.md` — Slidev specifics (Markdown, Vue components, interactive playback, KaTeX, build, export).

## Core Principle

Lecture slides are presentation material, not lecture notes.

- Prioritize speaking support over textual completeness.
- Keep only the key idea, key structure, and key visual cue on each slide.
- Do not dump full paragraphs when a short phrase or 3 to 5 bullets is enough.
- Overview, goals, and plan slides should be compressed into short presentation bullets.
- If a slide starts reading like a handout, it is too dense.

## Content Density

- Prefer concise bullets over explanatory paragraphs.
- Use full sentences only when tone matters, for example on welcome or personal introduction slides.
- Avoid stacking many boxed regions when plain headings plus bullets or columns read more cleanly.
- Keep formulas compact. A formula should be large enough to read, not so large that it dominates the frame or forces nearby text into the margins.
- Preserve visible whitespace. If a slide feels packed even without literal overlap, split it.
- If several equations or definitions are needed, do not keep all of them on screen just because they technically fit. Reveal and retire intermediate objects, or put each beat on its own page.
- Each slide should have one clear function:
  overview, goal, self-introduction, course logistics, schedule, concept, example, or references.
- Prefer several sparse slides over one dense slide.
  If a concept naturally splits into three beats, give it three slides with one beat each instead of stacking three sub-sections.
- Sub-slides that carry new conceptual content should count as real pages. Avoid hiding substantial proof steps as "animation-only" beats just to keep the page count low.

## Recommended Slide Flow

For a course-opening deck, the default early sequence should be:

1. Title page
2. Welcome
3. About me
4. About this course
5. Schedule
6. Outline

This can be adjusted, but the deck should establish:

- who is speaking
- what the course is about
- how the course will run
- what the audience should expect

## Visual Structure

- Prefer clean layouts with intentional hierarchy.
- Use columns when they help separate roles, such as image vs. biography or overview vs. goals.
- Use asymmetrical layouts when appropriate; they often read better than perfectly uniform boxes.
- Use one-column layouts for schedules, references, and concept-heavy slides.
- Use two-column layouts for profile and comparison slides.
- A "2 columns on top + 1 full-width section below" layout is a good pattern for self-introduction slides.

### Color as Identity

When a symbol recurs across a slide in different visual contexts — a variable that appears both inside a formula and inside a truth-value table, a register that shows up in a circuit and in an inline state, a clause referenced in two diagrams — color it consistently in every context.
The audience can then trace identity by eye instead of re-parsing notation each time it reappears.
Establish the color first (introduce `x_1` in cyan before showing any clause that mentions it), then keep it stable for the rest of the slide.
Use a small palette of distinct hues for the per-symbol track, and keep it disjoint from the palette used for true/false / pass/fail / on/off so a colored variable can sit inside any state without color-meaning collisions.
Tool-specific implementation (multi-color math, per-glyph color in text) lives in `beamer.md`, `manim.md`, or `slidev.md`.

## Text Style

- Use short, presentation-friendly wording.
- Favor phrases such as `Major ideas`, `Core techniques`, `Where speedups arise` over explanatory prose.
- Avoid writing everything the speaker will say.
- Let the spoken lecture carry the detail; let the slide carry the structure.
- Keep wording professional, direct, and compact.
- When citing papers or theorems, prefer a structured citation mechanism over manually typing author-year strings. (Tool-specific citation flow lives in `beamer.md`, `manim.md`, or `slidev.md`.)
- Avoid author-initial acronyms (e.g. BBHT, BBBV, HHL) in slide titles or first mentions. The audience will rarely have memorized them. Title slides by what the algorithm or result *does* (`Why Use Exponential Searching?`), not by who wrote it. The acronym, if useful at all, comes after the idea has been introduced.

## Narrative Flow

- A good slide should not only contain the right content; it should reveal it in the right order.
- The deeper version of this rule:
  write to follow the audience's mental flow, not the source paper's table of contents.
- Names should emerge from questions, not the other way around.
  Do not introduce a structural label like "Phase 1 / Phase 2" or "the three stages" before the audience can already see why those structures need to exist.
  Build bottom up: show the artifact, notice a property of it, realize what to do with it, and only then give the structure a name.
- When a concept is being introduced, prefer a short sequence of bullets that builds toward a punchline or transition.
- Progressive reveal is useful when the audience should follow one idea at a time. Use it only when the audience must absorb content in a specific order, or when a punchline genuinely needs to land after the setup.
- End important setup slides with a pivot line or question when it helps move naturally into the next topic.
- A rhetorical question is a good device when the next slide will answer or problematize the current one.
- Stronger than a pivot line:
  a slide can literally end with a one-line question, and the next slide opens with its answer.
  Use this when the answer is the whole point of the next slide.
- Example pattern:
  start with the familiar setup, add the key speedup/result, then end with the real conceptual question.
- When moving into a deeper issue, use a pair of slides:
  one slide raises the concern, the next slide receives that concern and redirects it.
- It is often effective to voice the audience's likely skepticism explicitly before resolving it.
- Do not introduce a new formal language abruptly. If the talk has been using discrete steps, and the next section needs a differential equation, first rewrite the familiar object in that language before quantizing or generalizing it.
- Likewise, do not introduce a spectral formula, oracle, or reduced subspace as if it were self-motivated. First make clear what question it answers.
- Before any algorithmic separation claim, state the problem model explicitly: input, goal, what is hidden, what can be queried, and whether classical and quantum algorithms receive the same information in different access modes.
- When a graph or construction looks arbitrary, ask the motivating question first. The audience should know what property the construction is meant to exploit before seeing the construction.
- When a structural grouping appears, say why it is being introduced. "Group by distance" should be motivated as exploiting hidden symmetry, not dropped as a new label.
- Do not dwell on alternatives the audience will not use.
  If a competing method is not the one being taught, dispatch it in one sentence on the intro slide
  ("the original 2006 paper is 19 pages and intricate; we will cover the cleaner 2019 version")
  rather than dedicating a comparison slide.
- Good lecture flow often follows:
  setup -> tension -> question -> reassurance -> next framework.
- Short conversational lines are acceptable when they sharpen the transition or keep the audience engaged.
- Recap, motivation, problem-statement, and stable definition slides should default to fully static. There is nothing to reveal in sequence, and forcing reveal makes the speaker click without purpose.
- When in doubt between static and progressive reveal, choose static. Removing an unnecessary reveal almost never hurts a slide; adding a needless one always slows the talk.
- The mechanics of progressive reveal are tool-specific (Beamer overlays vs. manim animations); see the relevant companion file for the exact conventions, including how to handle a transition line that should appear *after* a list is finished.

### Explanation ladder: intuition -> calculation -> proof

For mathematical content, do not stop at an intuition slide if the result will be used later. A strong sequence is:

1. show the intuition visually
2. do the rough calculation or scaling argument
3. give the precise recurrence / algebra / proof
4. return to the original algorithmic consequence

Use this especially when the final formula is not obvious from the picture. Examples from lecture 4:

- after showing a biased 3-SAT walk, solve the hitting-probability recurrence rather than only asserting a success probability
- after showing ballistic spreading, explain why packet velocity is a derivative of the dispersion relation before writing `d\omega/dp`
- after showing a column-state invariant subspace, derive where the coefficients such as `\sqrt{2}` and the middle coupling come from

If a proof is too dense for one slide, split it across pages. The proof should feel walked through, not pasted in.

### Orientation and audience position

For long lectures, help the audience locate themselves in the argument.

- Divide the talk into a small number of macro beats, roughly five to seven.
- Show the current beat consistently in a low-emphasis navigation area when the deck is long enough to need it.
- The macro beats should be semantic, not uniformly spaced by page count. A short transition section can be one beat; a long technical section can be another.
- The current slide's local section should still be visible, but it is secondary to the high-level lecture arc.
- Navigation should not compete with content. It is a thin orientation aid, not a second header.

### Pacing — fast for text, deliberate for visualization

Animation pacing should match the cognitive role of the content.

- Outline, title, recap, transition, and bullet-list reveals should be fast. The audience does not need to read along character-by-character — the speaker's voice carries the pace, and a slow reveal makes them wait for the slide to catch up. Avoid typewriter effects on TOC-style slides; a quick staggered fade is enough.
- Visualization beats — a walker stepping, a graph filling in, a value flipping, a state vector rotating — should be deliberate enough that each step lands before the next begins. The animation *is* the content here, so its tempo is what the audience is following.
- This split between "snappy text" and "deliberate visuals" is the principle; the mechanism (separate speed multipliers in code) is tool-specific and lives in `manim.md`.

### Auto-advance vs. arrow-key advance

Inside a single conceptual moment, decide which beats auto-play and which require an arrow-key click.

- Auto-play when the motion is one connected idea the audience absorbs as a whole (a walker traversing a path, a tree filling in level by level, a bullet list staggering in).
- Arrow-key advance when each sub-step is its own discrete observation the speaker wants to land separately (a variable's value flips → the formula re-evaluates → the audience notices a cycle). The pause forces the speaker to narrate each beat instead of letting the animation race past.
- A useful test: if you'd say "and now…" between two sub-steps, they probably belong on separate arrow-key advances. If they read as one continuous motion, auto-play.
- The mechanism (sub-slide segmentation) is tool-specific and lives in `beamer.md`, `manim.md`, or `slidev.md`.

## Reusable Building Blocks

- If a technique, inequality, or subroutine will be invoked more than once, hoist it into its own named slide *before* the first use.
- Later slides should *apply* the named result instead of re-deriving it.
- Naming once and applying many times keeps later slides slim and trains the audience to recognize the trick when it reappears.

## Welcome / Intro Slides

- After the title page, include a short welcome slide.
- Mention that the materials will be uploaded to the personal homepage and GitHub when relevant.
- Keep the welcome message brief and warm, not long.
- For continuing weeks (lecture 2+), skip the full Welcome / About Me / About This Course / Schedule sequence. Replace it with a single "Welcome back" slide that recaps the prior lectures in one line and previews the current one, then move directly to the today's-plan and outline slides.

## About Me Slide

Default structure:

- top area: 2 columns
- bottom area: 1 column

Recommended layout:

- left top: profile image
- right top: short personal introduction
- bottom: research interests or current study areas

Current preferred details:

- use a circular crop for the profile image when possible
- crop around the center of the face
- include personal homepage and LinkedIn below the short introduction
- keep the biography short, with no more than a few short lines

## About This Course Slides

- Spread course introduction across 2 to 3 slides rather than cramming it into one.
- Use one slide for `Overview` and `Goals`.
- Use one slide for `Plan` and `Notes`.
- Use one slide for the schedule table.
- Summarize `Overview` and `Goals` into short bullets.
- Do not paste full course descriptions verbatim into slides.

## Theorem / Definition Slides

- Important conceptual statements should often be framed as theorem-like objects rather than ordinary bullets.
- Use a labeled box such as `Definition`, `Claim`, `Observation`, `Proposition`, or `Result` when the structure helps the audience understand the role of the statement.
- The statement itself should stay short.
- Put intuition or explanation below the labeled statement rather than stuffing everything into it.
- If notation such as `D(f)` or `Q(f)` has not already been established, define it explicitly on the same slide.
- The mechanism for rendering these labeled boxes differs by tool; see `beamer.md` (theorem environments) and `manim.md` (helper boxes).

## Explaining Algorithms and Results

- Lead with the mechanism, not the citation. "Grover with the wrong iteration count overshoots and the success probability collapses" is more useful to the audience than "BBHT solved the unknown-$t$ case."
- When introducing a non-obvious algorithm, motivate it by what it *fixes* in the previous attempt. The audience must feel the gap before they will care about the solution.
- Spell out what an algorithm needs from the user (e.g. "Grover needs us to know $t$ in advance") before showing the workaround. The constraint is the hook.
- When a result is famous for being short or surprising, say so. Concrete trivia — "the paper is only 2 pages long", a year, an anecdote — grounds an abstract result and keeps the audience engaged.
- Name an algorithm by its descriptive function (`Exponential Searching`, `Minimum Finding`) on first introduction; let the bibliography carry the author tags.
- Imagine the audience as a stranger meeting the algorithm for the first time, and present like a math YouTuber who explains by walking through a concrete example end-to-end. The example should be small enough to fit on a slide and rich enough that every interesting case actually occurs.
- For an iterative or stochastic algorithm, *show the trial and error*. Walk through a concrete trace that includes a step that does not progress (a wrong move, a cycle, an unsatisfied check) before reaching success. Audiences trust mechanisms they have seen fail and recover. Skipping straight to a clean run hides the part the algorithm is actually solving.
- Color the working state (variables, registers, current candidate) consistently throughout the trace using the rule in *Color as Identity*, so the audience can follow what changed at each step without re-parsing.
- When an algorithm is defined through an oracle or query model, put the access model before the lower/upper bound story. The audience cannot evaluate a speedup until they know what both algorithms are allowed to ask.
- If the classical and quantum versions use the same hidden object differently, state both access modes explicitly. "Same information, different access mode" is often the core reason a separation is possible.

## Grover / Query-Complexity Lecture Flow

- If the audience is assumed to already know Grover at a basic level, do not over-explain the search problem from scratch.
- Use Grover as a familiar anchor, then quickly pivot to the real conceptual question:
  what are the limits of quantum speedup?
- A strong flow is:
  Grover recap -> promise problem examples -> total function limitation -> search as benchmark -> BBBV lower bound -> Grover optimality.
- The point of Theorem 3.3 is not just the formula; the point is that total functions allow at most quartic quantum advantage.
- The point of BBBV is to sharpen the message:
  even if quartic is allowed in general, unstructured search only allows quadratic improvement.
- This makes Grover important not just as an example, but as an optimal algorithm.
- Separate quantum work and classical post-processing onto different slides when both appear in an algorithm.
  The classical-work slide is also a natural place to reinforce the convention that classical work is not counted in query complexity.

## Schedule Slide

- Keep the schedule in a compact table.
- Optimize for scanability, not prose.
- Use short study-topic labels.
- Keep notes brief.
- If a cell becomes too long, shorten the wording instead of shrinking the whole deck too much.

## Images

- Store image assets in a per-lecture `imgs/` folder. Reference them by relative path from the lecture's source. Do not share one `imgs/` across lectures — when a deck is moved, extracted, or renamed, broken paths waste rebuild time.
- Prefer deliberate image treatment over raw insertion.
- For profile photos, use a circular crop when appropriate.
- Full-bleed image slides are useful when one picture carries the conceptual point on its own. Center the image, add at most a short bold caption beneath, and skip bullets.
- Check the image's aspect ratio first and size accordingly so nothing distorts or clips. Tool-specific sizing options live in `beamer.md` and `manim.md`.

## Build Policy

- Each deck owns its source, dependencies, assets, and build commands.
- Track authoring source, dependency manifests, lockfiles, build helpers, and
  assets referenced by the deck. Captured traces and circuit figures belong to
  these required assets even when they can be regenerated.
- Generated presentations remain local and ignored by Git. This includes Beamer
  PDFs, Manim HTML exports, and Slidev static sites and PDF exports.
- Keep rendering intermediates in `builds/` for Beamer and Manim. Slidev uses
  `dist/` for the static site and `.generated/` for review files and temporary tools.
- Keep dependency directories, caches, screenshots, logs, and `references/` ignored.
- Use each tool's preview workflow while editing. Rebuild and inspect final
  exports when preparing a presentation for sharing.
- Tool-specific commands are in `beamer.md`, `manim.md`, and `slidev.md`.

## Error Prevention

- For presentation work, the main goal is to eliminate fatal compile or render errors first, then worry about layout warnings.
- Check the output after every meaningful change rather than batching many edits.
- Tool-specific failure modes (TeX errors, manim animation pitfalls, Unicode handling, etc.) live in `beamer.md` and `manim.md`.

## Screenshot Feedback Loop

Layout, spacing, color contrast, and visual hierarchy can only be judged by looking at the rendered output, not by reading the source.
A clean compile is not the same as a clean slide — the source can be syntactically perfect while the result has overlapping text, off-frame mobjects, or a checkmark sitting on top of a caption.

The discipline:

- after any non-trivial change to a slide's layout, render the deck and **open the actual page image** before moving on
- look for: text overlapping another mobject, components touching the frame edge or footer, animations captured mid-state in the static frame, color contrast issues against the dark background, elements that fell off the visible area
- treat the image as the spec — if the rendered slide does not match the intent, fix it before continuing to the next change
- on a multi-beat slide (sub-slides, progressive reveal), inspect *each* beat — a layout that works on one sub-slide can break on the next when more elements are added
- when an issue is fixed, re-render and re-inspect the same image; do not assume the fix worked

Tool-specific paths to the rendered images live in `beamer.md` (PDF page snapshots) and `manim.md` (`builds/static_frames/<Scene>/slideNN.png`).

## Maintenance Rule For This File Set

When a new stylistic instruction appears:

- first decide which file it belongs in:
  - presentation flow / narrative / content density / pedagogical patterns -> `phillosophy.md`
  - Beamer-only mechanics -> `beamer.md`
  - manim-slides-only mechanics -> `manim.md`
  - Slidev-only mechanics -> `slidev.md`
- then check whether the idea already exists in that file
- if it overlaps, revise the existing section
- if it is genuinely new, add it to the right section
- do not write duplicate rules in a new place, and do not split a single rule across files unless the principle and the mechanism truly belong apart

Each of these files should stay organized by principle, not by conversation history.
