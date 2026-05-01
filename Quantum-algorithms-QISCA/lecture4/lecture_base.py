"""Base scene + footer template for QISCA lecture decks rendered with manim-slides.

This file plays the same role as the Beamer preamble in lectures 1 and 3:

- defines the dark theme constants
- builds the 4-cell footer (author / major section / section / page)
- exposes a ``LectureScene`` subclass of ``manim_slides.Slide`` that auto-manages
  the footer text and the page counter as the deck advances

A subclass calls ``setup_lecture(...)`` once at the top of ``construct``, then
``begin_slide(section=...)`` at the start of each new slide segment.
"""
from __future__ import annotations

import hashlib
import subprocess
import tempfile
from pathlib import Path

from manim import (
    Arrow,
    Circle,
    Line,
    ManimColor,
    Rectangle,
    SVGMobject,
    Text,
    VGroup,
    FadeOut,
    config,
)
from manim_slides import Slide

# === Theme ============================================================
BG_COLOR = "#000000"
TEXT_PRIMARY = "#f0f0f0"
TEXT_MUTED = "#9aa0a6"
TEXT_ACCENT = "#79b8ff"

# True/false palette for binary visuals (assignments, clauses, pass/fail).
# Picked to read clearly on the dark theme.
COLOR_TRUE = "#4ade80"       # bright green — satisfied / on
COLOR_FALSE = "#f87171"      # soft red — unsatisfied / off
COLOR_HIGHLIGHT = "#fbbf24"  # amber — current focus / variable being flipped

# Per-variable palette for slides where individual symbols get tracked
# across an expression (e.g. each x_i in 2-SAT). Distinct from the
# true/false eval colors so a colored variable can sit inside any clause.
COLOR_VAR1 = "#06b6d4"  # cyan
COLOR_VAR2 = "#a78bfa"  # purple
COLOR_VAR3 = "#fb923c"  # orange
COLOR_VAR4 = "#ec4899"  # pink (introduced for the 3-SAT trace's 4th variable)

# Set the renderer-default background here so the Camera picks it up at
# construction time. Setting ``self.camera.background_color`` from inside
# ``construct`` arrives too late on manim 0.19 + manim-slides 5.6.
config.background_color = BG_COLOR

FOOTER_BG = "#0f0f0f"
FOOTER_BORDER = "#2a2a2a"
FOOTER_TEXT = "#cfcfcf"
FOOTER_HEIGHT = 0.5
FOOTER_FONT_SIZE = 18
ROADMAP_HEIGHT = 0.28
ROADMAP_FONT_SIZE = 10
ROADMAP_STEPS = (
    "Intro",
    "Diffusion",
    "2-SAT",
    "3-SAT",
    "Quantum Walk",
    "Glued Trees",
)
ROADMAP_POSITIONS = (0.07, 0.22, 0.35, 0.49, 0.67, 0.86)

# Three font slots, intentionally distinct so role (prose / math / code) is
# legible at a glance. Math has no Python-side constant — it goes through
# ``MathTex`` and inherits the LaTeX default (Computer Modern serif).
FONT_BODY = "Apple SD Gothic Neo"  # prose, headings; tight metrics, ships with macOS
FONT_MONO = "Monaco"               # code, terminal-style snippets

# Two animation speed multipliers — higher = faster. Every ``run_time`` /
# ``time_per_char`` / ``wait`` is divided by one of these. Text/list slides
# use ``ANIM_SPEED`` so reveals feel snappy; visualization-heavy beats
# (random walk tree, walker, 2-SAT flip animations) use ``VISUAL_SPEED`` so
# the audience can follow each step deliberately.
ANIM_SPEED = 3.0
VISUAL_SPEED = 1.0

# Cell widths as fractions of frame width (must sum to 1.0).
# Mirrors the Beamer Madrid footer used in lectures 1 and 3.
CELL_FRACTIONS = (0.15, 0.40, 0.35, 0.10)


def roadmap_step_for(major_section: str, section: str) -> str:
    """Collapse detailed section names into the six high-level lecture beats."""
    if major_section == "Intro" or section in {"", "Welcome", "Today"}:
        return "Intro"
    if section == "Motivation":
        return "Diffusion"
    if section == "2-SAT":
        return "2-SAT"
    if section == "3-SAT":
        return "3-SAT"
    if section in {"Bridge", "CTQW", "Ballistic"}:
        return "Quantum Walk"
    if section in {"Glued Trees", "Column Subspace", "Closing"}:
        return "Glued Trees"
    return major_section if major_section in ROADMAP_STEPS else "Intro"


def body_text(
    s: str,
    *,
    color: str = TEXT_PRIMARY,
    size: int = 26,
    weight: str = "NORMAL",
) -> Text:
    """Prose / heading text in the deck's body font (Pretendard)."""
    return Text(s, font=FONT_BODY, font_size=size, color=color, weight=weight)


def mono_text(
    s: str,
    *,
    color: str = TEXT_PRIMARY,
    size: int = 22,
) -> Text:
    """Inline or block code in the deck's monospace font (Monaco)."""
    return Text(s, font=FONT_MONO, font_size=size, color=color)


# === Math rendering ===================================================
# Bypass MathTex (which needs dvisvgm — not in TeX Live "basic"). Render
# LaTeX through pdflatex → pdf → svg via pdftocairo, then load the SVG with
# manim's SVGMobject. Cached on disk; re-renders are instant.
_MATH_CACHE = Path(tempfile.gettempdir()) / "qisca-math-svg"


def _render_math_svg(latex: str) -> Path:
    _MATH_CACHE.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha1(latex.encode("utf-8")).hexdigest()[:16]
    out = _MATH_CACHE / f"{digest}.svg"
    if out.exists():
        return out
    # xcolor lets a caller embed `{\color[HTML]{HEX} ...}` groups inside the
    # latex string to color individual sub-expressions (used by slides where a
    # single variable needs to be tracked across multiple occurrences). The
    # `\color[HTML]{F0F0F0}` at math entry sets the *base* color so operators
    # and parens stay visible on the dark theme even when caller passes
    # color=None to math().
    tex = (
        r"\documentclass[preview,border=2pt]{standalone}"
        "\n"
        r"\usepackage{amsmath,amssymb,xcolor}"
        "\n"
        r"\begin{document}"
        "\n"
        r"\(\color[HTML]{F0F0F0} " + latex + r"\)"
        "\n"
        r"\end{document}"
        "\n"
    )
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        (tmpdir / "m.tex").write_text(tex, encoding="utf-8")
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory", str(tmpdir), "m.tex"],
            cwd=tmpdir,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            ["pdftocairo", "-svg", str(tmpdir / "m.pdf"), str(out)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    return out


def math(
    latex: str,
    *,
    color: str | None = TEXT_PRIMARY,
    scale: float = 1.0,
) -> SVGMobject:
    """Render a LaTeX math expression as an SVGMobject.

    Bypasses ``MathTex`` (which needs dvisvgm) by going through pdflatex +
    pdftocairo. ``color`` is applied to the whole result after import; pass
    ``color=None`` to preserve per-element colors baked in via ``\\color``
    commands inside ``latex``.
    """
    svg = _render_math_svg(latex)
    obj = SVGMobject(str(svg))
    if color is not None:
        obj.set_color(color)
    obj.scale(scale)
    return obj


def make_footer(
    author: str,
    major_section: str,
    section: str,
    page_text: str,
) -> VGroup:
    """Build the 4-cell footer at the bottom of the frame.

    Each cell is a flat rectangle with its label centered. Empty labels render
    as a blank cell. The footer has a thin separator line along its top edge.
    """
    fw = config.frame_width
    fh = config.frame_height
    h = FOOTER_HEIGHT
    roadmap_h = ROADMAP_HEIGHT
    footer_y = -fh / 2 + h / 2
    roadmap_y = -fh / 2 + h + roadmap_h / 2

    cells_text = [author, major_section, section, page_text]

    group = VGroup()
    roadmap_bg = Rectangle(
        width=fw,
        height=roadmap_h,
        stroke_width=0,
        fill_color=BG_COLOR,
        fill_opacity=1,
    ).move_to([0, roadmap_y, 0])
    group.add(roadmap_bg)

    active_step = roadmap_step_for(major_section, section)
    active_idx = ROADMAP_STEPS.index(active_step)
    xs = [-fw / 2 + frac * fw for frac in ROADMAP_POSITIONS]
    arrow_y = roadmap_y - 0.060
    label_y = roadmap_y + 0.055
    for i in range(len(xs) - 1):
        color = TEXT_ACCENT if i < active_idx else FOOTER_BORDER
        opacity = 0.55 if i < active_idx else 1.0
        arrow = Arrow(
            [xs[i] + 0.33, arrow_y, 0],
            [xs[i + 1] - 0.33, arrow_y, 0],
            buff=0,
            color=color,
            stroke_width=1.4,
            max_tip_length_to_length_ratio=0.08,
        )
        arrow.set_opacity(opacity)
        group.add(arrow)

    for i, (step, x) in enumerate(zip(ROADMAP_STEPS, xs)):
        is_active = i == active_idx
        dot = Circle(
            radius=0.035 if not is_active else 0.046,
            stroke_color=TEXT_ACCENT if is_active else TEXT_MUTED,
            stroke_width=1.4,
            fill_color=TEXT_ACCENT if is_active else BG_COLOR,
            fill_opacity=1 if is_active else 0,
        ).move_to([x, arrow_y, 0])
        label = body_text(
            step,
            size=ROADMAP_FONT_SIZE if step != "Quantum Walk" else ROADMAP_FONT_SIZE - 1,
            color=TEXT_ACCENT if is_active else TEXT_MUTED,
            weight="BOLD" if is_active else "NORMAL",
        )
        label.move_to([x, label_y, 0])
        group.add(dot, label)

    roadmap_border = Line(
        start=[-fw / 2, roadmap_y + roadmap_h / 2, 0],
        end=[fw / 2, roadmap_y + roadmap_h / 2, 0],
        stroke_color=FOOTER_BORDER,
        stroke_width=0.8,
    )
    group.add(roadmap_border)

    x_left = -fw / 2
    for frac, txt in zip(CELL_FRACTIONS, cells_text):
        cw = frac * fw
        rect = Rectangle(
            width=cw,
            height=h,
            stroke_width=0,
            fill_color=FOOTER_BG,
            fill_opacity=1,
        )
        rect.move_to([x_left + cw / 2, footer_y, 0])
        cell = VGroup(rect)
        if txt:
            label = body_text(
                txt,
                size=FOOTER_FONT_SIZE,
                color=FOOTER_TEXT,
                weight="NORMAL",
            )
            max_w = cw * 0.92
            if label.width > max_w:
                label.scale(max_w / label.width)
            label.move_to(rect.get_center())
            cell.add(label)
        group.add(cell)
        x_left += cw

    border = Line(
        start=[-fw / 2, footer_y + h / 2, 0],
        end=[fw / 2, footer_y + h / 2, 0],
        stroke_color=FOOTER_BORDER,
        stroke_width=1.0,
    )
    group.add(border)
    return group


class LectureScene(Slide):
    """Base scene for QISCA lecture decks.

    Sets the dark background, manages the footer, and tracks slide page
    numbers. Subclasses call ``setup_lecture(...)`` once, then ``begin_slide``
    at the start of every slide segment.
    """

    def setup_lecture(self, *, author: str, title: str, total_pages: int) -> None:
        self.camera.background_color = ManimColor(BG_COLOR)
        self._lecture_author = author
        self._lecture_title = title
        self._total_pages = total_pages
        self._current_page = 0
        self._current_major_section = title
        self._current_section = ""
        self._footer: VGroup | None = None

    def begin_slide(
        self,
        *,
        section: str | None = None,
        major_section: str | None = None,
        clear: bool = True,
        advance_page: bool | None = None,
    ) -> None:
        """Open a new slide segment.

        If ``clear`` is true, fade out everything except the footer. By default,
        only clear/full-slide transitions advance the visible page counter;
        ``clear=False`` beats are animation segments inside the same logical
        page.
        """
        if clear:
            to_fade = [m for m in self.mobjects if m is not self._footer]
            if to_fade:
                self.play(*[FadeOut(m) for m in to_fade], run_time=0.3 / ANIM_SPEED)
        if advance_page is None:
            advance_page = clear
        if advance_page:
            self._current_page += 1
        if major_section is not None:
            self._current_major_section = major_section
        if section is not None:
            self._current_section = section
        self._refresh_footer()

    def _refresh_footer(self) -> None:
        page_text = f"{self._current_page}/{self._total_pages}"
        new_footer = make_footer(
            self._lecture_author,
            self._current_major_section,
            self._current_section,
            page_text,
        )
        if self._footer is not None:
            self.remove(self._footer)
        self.add(new_footer)
        self._footer = new_footer
