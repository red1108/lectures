# Lectures

Lecture and research presentations authored with Beamer, Manim, and Slidev.

| Material | Source | Tool |
| --- | --- | --- |
| Quantum algorithms course | `Quantum-algorithms-QISCA/` | Beamer and Manim |
| Pebbling computations | [`pebble/`](pebble/) | Slidev with Bricks |

Authoring guidance starts in [`AGENTS.md`](AGENTS.md). Shared presentation
principles are in [`phillosophy.md`](phillosophy.md), with implementation guidance
in [`beamer.md`](beamer.md), [`manim.md`](manim.md), and [`slidev.md`](slidev.md).

For the pebbling talk:

```sh
cd pebble
npm ci
npm run dev -- --port 3039
```

Each deck owns its dependencies and build commands. Source, build helpers,
lockfiles, and required assets are tracked. Generated PDF/HTML presentations,
rendering intermediates, dependency directories, and local review files are
ignored.
