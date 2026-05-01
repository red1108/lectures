"""Build a static-image HTML deck from a manim-slides ``SCENE.json``.

For each slide, take the last frame of its rendered MP4 and embed it as a
``data-background-image`` data URI inside a reveal.js section. The result is
a single self-contained HTML file where navigation is instant — no video
playback, no flicker, no re-running the animation each time you visit a
slide. Use this for browsing, distribution, or just reviewing layout.

The animated HTML (built with ``manim-slides convert``) and this static HTML
are siblings; pick whichever fits the moment.

Prerequisite: ``manim-slides render`` has produced ``slides/SCENE.json``
and the underlying MP4s. ``ffmpeg`` is on PATH.

Usage:
    python build_static.py [SCENE] [OUTPUT.html]

Defaults: ``SCENE=Lecture4``, ``OUTPUT=main.static.html``.
"""
from __future__ import annotations

import base64
import json
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

REVEAL_BASE = "https://cdn.jsdelivr.net/npm/reveal.js@6.0.1"


def extract_last_frame(mp4: Path, cache_png: Path) -> bytes:
    """Cache last frame of ``mp4`` at ``cache_png`` and return its bytes.

    The cache key is the destination path. Delete the cache file (or the
    enclosing folder) to force a re-extract.
    """
    if not cache_png.exists() or cache_png.stat().st_mtime < mp4.stat().st_mtime:
        cache_png.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-sseof", "-0.2",
                "-i", str(mp4),
                "-vframes", "1",
                str(cache_png),
            ],
            check=True,
            capture_output=True,
        )
    return cache_png.read_bytes()


def main() -> None:
    scene = sys.argv[1] if len(sys.argv) > 1 else "Lecture4"
    out_path = Path(sys.argv[2] if len(sys.argv) > 2 else "main.static.html")

    cfg_path = Path(f"slides/{scene}.json")
    if not cfg_path.exists():
        sys.exit(
            f"missing {cfg_path} — run "
            f"'manim-slides render main.py {scene}' first"
        )
    cfg = json.loads(cfg_path.read_text())

    cache_dir = Path(f"builds/static_frames/{scene}")
    sections: list[str] = []
    for i, slide in enumerate(cfg["slides"], start=1):
        mp4 = Path(slide["file"])
        png = cache_dir / f"slide{i:02d}.png"
        png_bytes = extract_last_frame(mp4, png)
        b64 = base64.b64encode(png_bytes).decode()
        sections.append(
            f'<section data-background-color="black" '
            f'data-background-size="contain" '
            f'data-background-image="data:image/png;base64,{b64}"></section>'
        )

    sections_html = "\n            ".join(sections)
    html = dedent(
        f"""\
        <!doctype html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{scene} — Static</title>
            <link rel="stylesheet" href="{REVEAL_BASE}/dist/reveal.css">
            <link rel="stylesheet" href="{REVEAL_BASE}/dist/theme/black.css">
            <style>body {{ background: #000; }}</style>
        </head>
        <body>
            <div class="reveal"><div class="slides">
            {sections_html}
            </div></div>
            <script src="{REVEAL_BASE}/dist/reveal.js"></script>
            <script>
                Reveal.initialize({{
                    width: '100%', height: '100%', margin: 0.04,
                    transition: 'none', backgroundTransition: 'none',
                    controls: true, hash: true, slideNumber: true, progress: true,
                }});
            </script>
        </body>
        </html>
        """
    )
    out_path.write_text(html)
    size_kb = out_path.stat().st_size // 1024
    print(f"wrote {out_path}  ({len(cfg['slides'])} slides, {size_kb} KB)")


if __name__ == "__main__":
    main()
