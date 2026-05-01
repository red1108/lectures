"""End-to-end build for the lecture deck.

Pipeline:
    1. ``manim-slides render main.py SCENE``        — renders MP4 per slide
    2. ``manim-slides convert --one-file --offline``— animated self-contained HTML
    3. patch ``main.html`` with backward-nav skip JS so reveal.js does not
       replay the slide animation when you press left arrow
    4. ``python build_static.py``                   — second HTML where every
       slide is a still image (used for browsing / distribution)

Run from inside the lecture folder:

    python build.py

The script is idempotent — re-running after no source change is fast (manim
cache is per-animation, and the patch step is a no-op if the JS is already
present).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCENE = "Lecture4"
VENV_BIN = Path(__file__).resolve().parents[2] / ".venv" / "bin"
MANIM_SLIDES = VENV_BIN / "manim-slides"


# Injected into ``main.html`` before ``</body>``. The handler hooks
# ``Reveal.on('slidechanged', ...)`` and, when the new slide index is lower
# than the previous one (i.e. left-arrow / backward navigation), seeks the
# slide background video to its end and pauses it. Forward navigation falls
# through to reveal.js's default behaviour, which plays the animation.
SKIP_REPLAY_JS = """\
<script>
(function () {
  if (typeof Reveal === 'undefined') return;

  function seekToEnd(video) {
    var doSeek = function () {
      if (!isFinite(video.duration)) return;
      try { video.currentTime = video.duration; } catch (e) {}
      video.pause();
    };
    if (video.readyState >= 1 && isFinite(video.duration)) {
      doSeek();
    } else {
      video.addEventListener('loadedmetadata', doSeek, { once: true });
    }
  }

  function skipVideoToEnd(slide) {
    if (!slide) return;
    var bg = slide.slideBackgroundElement;
    if (!bg) return;
    var existing = bg.querySelector('video');
    if (existing) {
      seekToEnd(existing);
      return;
    }
    var obs = new MutationObserver(function () {
      var v = bg.querySelector('video');
      if (v) {
        obs.disconnect();
        seekToEnd(v);
      }
    });
    obs.observe(bg, { childList: true, subtree: true });
  }

  Reveal.on('slidechanged', function (event) {
    if (event.indexh < event.previousIndexh) {
      skipVideoToEnd(event.currentSlide);
    }
  });
})();
</script>
"""


def run(*args: object) -> None:
    subprocess.run([str(a) for a in args], check=True)


def patch_main_html(path: Path) -> bool:
    """Enable reveal progress and inject the backward-skip ``<script>``.

    Uses ``rfind`` instead of ``str.replace(..., 1)`` because ``--offline``
    inlines reveal.js's notes plugin (marked.js), and marked's source contains
    string literals like ``"</body>"``. A first-occurrence replace lands inside
    that literal and breaks the bundled script — we'd see raw marked.js code
    rendered on the page instead of slides.
    """
    text = path.read_text()
    changed = False
    if "progress: false," in text:
        text = text.replace("progress: false,", "progress: true,", 1)
        changed = True
    if "skipVideoToEnd" not in text:
        idx = text.rfind("</body>")
        if idx == -1:
            raise RuntimeError(f"no </body> tag found in {path}")
        text = text[:idx] + SKIP_REPLAY_JS + text[idx:]
        changed = True
    if changed:
        path.write_text(text)
    return changed


def main() -> None:
    run(MANIM_SLIDES, "render", "main.py", SCENE)
    run(MANIM_SLIDES, "convert", "--one-file", "--offline", SCENE, "main.html")

    patched = patch_main_html(Path("main.html"))
    print(f"main.html patched={patched}")

    run(sys.executable, "build_static.py", SCENE, "main.static.html")


if __name__ == "__main__":
    main()
