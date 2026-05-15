"""Lecture 5 - tomography-free quantum state classification.

Render and convert (run from this directory):

    python build.py

For per-slide preview during dev:

    SLIDE=8 ../../.venv/bin/manim -s -ql main.py Preview

For faster iteration when a slide does not depend on previous slide state:

    FAST_PREVIEW=1 SLIDE=8 ../../.venv/bin/manim -s -ql main.py Preview
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from math import cos, pi, sin

from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    Arc,
    Arrow,
    Circle,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    Flash,
    Indicate,
    LaggedStart,
    Line,
    Rectangle,
    ReplacementTransform,
    SurroundingRectangle,
    Transform,
    VGroup,
    ValueTracker,
    linear,
)

from lecture_base import (
    ANIM_SPEED,
    COLOR_FALSE,
    COLOR_HIGHLIGHT,
    COLOR_TRUE,
    COLOR_VAR1,
    COLOR_VAR2,
    COLOR_VAR3,
    COLOR_VAR4,
    LectureScene,
    TEXT_ACCENT,
    TEXT_MUTED,
    TEXT_PRIMARY,
    VISUAL_SPEED,
    body_text,
    math as tex_math,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.quantum_circuit import (
    controlled_swap_gate,
    h_gate,
    measurement_gate,
    wire_bundle,
)

AUTHOR = "Mingyu Lee"
TITLE = "Lecture 5"
DATE = "2026 May 13"

LABEL_COLORS = {
    "cat": COLOR_VAR3,
    "dog": COLOR_VAR1,
    "bird": "#34d399",
    "Unknown": COLOR_HIGHLIGHT,
}

TRAINING_DATA = [
    ("0", "dog", 0.71),
    ("1", "bird", 0.34),
    ("2", "dog", 0.67),
    ("3", "cat", 0.92),
    ("4", "dog", 0.61),
    ("5", "cat", 0.88),
    ("6", "bird", 0.40),
    ("7", "cat", 0.84),
]

SLIDE_METHODS = (
    "_slide_title",
    "_slide_question",
    "_slide_classification_not_tomography",
    "_slide_training_library",
    "_slide_single_best_rule",
    "_slide_brittle_one_neighbor",
    "_slide_knn_definition",
    "_slide_bridge",
    "_slide_one_pair",
    "_slide_swap_circuit",
    "_slide_swap_state_evolution",
    "_slide_swap_split",
    "_slide_swap_probability",
    "_slide_swap_caveat",
    "_slide_repeat_every_j",
    "_slide_classical_postprocessing",
    "_slide_skepticism",
    "_slide_why_coherent_cost",
    "_slide_superposition_indices",
    "_slide_desired_oracle",
    "_slide_swap_not_enough",
    "_slide_analog_to_digital",
    "_slide_amplitude_view",
    "_slide_qpe_operator",
    "_slide_qpe_circuit",
    "_slide_qpe_eigenphase",
    "_slide_theta_parameter",
    "_slide_digital_register",
    "_slide_central_oracle",
    "_slide_comparisons",
    "_slide_comparator_construction",
    "_slide_topk_machinery",
    "_slide_majority_vote",
    "_slide_topk_enough",
    "_slide_why_ranking",
    "_slide_all_pairs_rank",
    "_slide_sorting_caveat",
    "_slide_warning_detector",
    "_slide_binning",
    "_slide_labeled_collision",
    "_slide_element_distinctness",
    "_slide_collision_oracle_model",
    "_slide_collision_subset_idea",
    "_slide_collision_registers",
    "_slide_collision_setup",
    "_slide_collision_marking",
    "_slide_johnson_walk_update",
    "_slide_walk_search_operator",
    "_slide_collision_query_complexity",
    "_slide_pipeline_summary",
    "_slide_final_sentence",
)
TOTAL_PAGES = len(SLIDE_METHODS)

MAJOR_SECTION_BY_SECTION = {
    "": "Hook",
    "Question": "Hook",
    "Library": "Hook",
    "One pick": "k-NN",
    "k-NN": "k-NN",
    "Swap Test": "Swap Test",
    "Baseline": "Baseline",
    "Coherent": "QADC",
    "QADC": "QADC",
    "Comparator": "Comparator",
    "Top-k": "Comparator",
    "Primitives": "Primitive Algorithms",
    "Ranking": "Primitive Algorithms",
    "Collision": "Primitive Algorithms",
    "Closing": "Closing",
}


def fit_math(
    latex: str,
    *,
    scale: float = 0.28,
    max_width: float = 8.0,
    max_height: float | None = None,
    color: str | None = TEXT_PRIMARY,
) -> object:
    obj = tex_math(latex, scale=scale, color=color)
    if obj.width > max_width:
        obj.scale(max_width / obj.width)
    if max_height is not None and obj.height > max_height:
        obj.scale(max_height / obj.height)
    return obj


def label_chip(
    label: str,
    *,
    color: str,
    width: float = 1.0,
    height: float = 0.32,
    font_size: int = 15,
) -> VGroup:
    rect = Rectangle(
        width=width,
        height=height,
        stroke_width=1.4,
        stroke_color=color,
        fill_color=color,
        fill_opacity=0.12,
    )
    txt = body_text(label, size=font_size, color=color, weight="BOLD")
    if txt.width > width * 0.82:
        txt.scale((width * 0.82) / txt.width)
    if txt.height > height * 0.68:
        txt.scale((height * 0.68) / txt.height)
    txt.move_to(rect.get_center())
    return VGroup(rect, txt)


def state_card(
    idx: str,
    label: str,
    *,
    width: float = 1.34,
    height: float = 1.04,
    show_value: bool = False,
    value: float | None = None,
) -> VGroup:
    color = LABEL_COLORS[label]
    rect = Rectangle(
        width=width,
        height=height,
        stroke_color=TEXT_MUTED,
        stroke_width=1.2,
        fill_color="#101010",
        fill_opacity=1,
    )
    compact = height < 0.90
    idx_size = max(8, min(14, int(height * 13.5)))
    chip_height = min(0.32, height * 0.28)
    chip_font_size = max(8, min(15, int(chip_height * 47)))
    ket_scale = 0.19 if compact else 0.21
    idx_text = body_text(f"j={idx}", size=idx_size, color=TEXT_MUTED)
    ket = fit_math(
        rf"\left|\phi_{{{idx}}}\right\rangle",
        scale=ket_scale,
        max_width=width * 0.72,
        max_height=height * 0.34,
        color=TEXT_PRIMARY,
    )
    chip = label_chip(
        label,
        color=color,
        width=width * 0.74,
        height=chip_height,
        font_size=chip_font_size,
    )
    idx_y = height / 2 - max(0.13, height * 0.14)
    ket_y = height * 0.12
    chip_y = -height / 2 + chip_height / 2 + max(0.08, height * 0.11)
    idx_text.move_to(rect.get_center() + idx_y * UP)
    ket.move_to(rect.get_center() + ket_y * UP)
    chip.move_to(rect.get_center() + chip_y * UP)
    group = VGroup(rect, idx_text, ket, chip)
    if show_value and value is not None:
        val = fit_math(
            rf"F={value:.2f}",
            scale=0.12,
            max_width=width * 0.78,
            color=TEXT_ACCENT,
        )
        val.next_to(rect, DOWN, buff=0.10)
        group.add(val)
    return group


def test_state_card() -> VGroup:
    circ = Circle(
        radius=0.52,
        stroke_color=COLOR_HIGHLIGHT,
        stroke_width=3.0,
        fill_color=COLOR_HIGHLIGHT,
        fill_opacity=0.10,
    )
    dot = Dot(radius=0.09, color=COLOR_HIGHLIGHT).move_to(circ.get_center())
    ket = fit_math(
        r"\left|\psi\right\rangle",
        scale=0.30,
        max_width=1.15,
        color=COLOR_HIGHLIGHT,
    )
    ket.next_to(circ, DOWN, buff=0.16)
    unknown = body_text("test state", size=15, color=TEXT_MUTED).next_to(
        ket, DOWN, buff=0.08
    )
    return VGroup(circ, dot, ket, unknown)


def make_library_grid(*, show_values: bool = False) -> VGroup:
    cards = [
        state_card(idx, label, show_value=show_values, value=value)
        for idx, label, value in TRAINING_DATA
    ]
    grid = VGroup(*cards).arrange_in_grid(rows=2, cols=4, buff=(0.35, 0.35))
    return grid


def small_register(name: str, value: str | None = None, *, width: float = 1.35) -> VGroup:
    rect = Rectangle(
        width=width,
        height=0.50,
        stroke_color=TEXT_ACCENT,
        stroke_width=1.6,
        fill_color=TEXT_ACCENT,
        fill_opacity=0.06,
    )
    txt = body_text(name if value is None else value, size=17, color=TEXT_PRIMARY)
    if txt.width > width * 0.84:
        txt.scale((width * 0.84) / txt.width)
    txt.move_to(rect.get_center())
    return VGroup(rect, txt)


def math_register(expr: str, *, width: float = 1.35, scale: float = 0.18) -> VGroup:
    rect = Rectangle(
        width=width,
        height=0.50,
        stroke_color=TEXT_ACCENT,
        stroke_width=1.6,
        fill_color=TEXT_ACCENT,
        fill_opacity=0.06,
    )
    txt = fit_math(expr, scale=scale, max_width=width * 0.84, color=TEXT_PRIMARY)
    txt.move_to(rect.get_center())
    return VGroup(rect, txt)


def bit_register(bits: str, *, bit_color: str = TEXT_ACCENT) -> VGroup:
    boxes = []
    for bit in bits:
        rect = Rectangle(
            width=0.34,
            height=0.44,
            stroke_color=bit_color,
            stroke_width=1.4,
            fill_color=bit_color,
            fill_opacity=0.08,
        )
        txt = body_text(bit, size=17, color=TEXT_PRIMARY, weight="BOLD")
        txt.move_to(rect.get_center())
        boxes.append(VGroup(rect, txt))
    return VGroup(*boxes).arrange(RIGHT, buff=0.06)


def oracle_box(
    label: str,
    *,
    width: float = 1.75,
    height: float = 1.05,
    math_label: bool | None = None,
) -> VGroup:
    rect = Rectangle(
        width=width,
        height=height,
        stroke_color=TEXT_ACCENT,
        stroke_width=2.0,
        fill_color=TEXT_ACCENT,
        fill_opacity=0.07,
    )
    if math_label is None:
        math_label = any(token in label for token in ("_", "^", "\\"))
    if math_label:
        txt = fit_math(
            label,
            scale=0.30,
            max_width=width * 0.70,
            max_height=height * 0.42,
            color=TEXT_ACCENT,
        )
    else:
        txt = body_text(label, size=24, color=TEXT_ACCENT, weight="BOLD")
    txt.move_to(rect.get_center())
    return VGroup(rect, txt)


def bar_chart(
    values: list[float],
    *,
    labels: list[str] | None = None,
    class_labels: list[str] | None = None,
    width: float = 8.30,
    max_height: float = 2.72,
    chip_height: float = 0.40,
    chip_font_size: int = 15,
    selected: set[int] | None = None,
) -> tuple[VGroup, list[VGroup]]:
    selected = selected or set()
    labels = labels or [str(i) for i in range(len(values))]
    n = len(values)
    bar_w = width / n * 0.58
    gap = width / n * 0.42
    bars: list[VGroup] = []
    x0 = -width / 2 + bar_w / 2
    for i, value in enumerate(values):
        h = max_height * value
        color = COLOR_HIGHLIGHT if i in selected else TEXT_ACCENT
        rect = Rectangle(
            width=bar_w,
            height=h,
            stroke_width=1.4,
            stroke_color=color,
            fill_color=color,
            fill_opacity=0.18 if i in selected else 0.10,
        )
        rect.move_to([x0 + i * (bar_w + gap), -max_height / 2 + h / 2, 0])
        idx = body_text(labels[i], size=17, color=TEXT_MUTED).next_to(
            rect, DOWN, buff=0.08
        )
        val = body_text(f"{value:.2f}", size=16, color=color).next_to(
            rect, UP, buff=0.08
        )
        bar_parts: list[Mobject] = [rect, idx, val]
        if class_labels is not None and i < len(class_labels):
            class_label = class_labels[i]
            chip = label_chip(
                class_label,
                color=LABEL_COLORS.get(class_label, TEXT_MUTED),
                width=max(1.02, min(1.28, bar_w * 1.62)),
                height=chip_height,
                font_size=chip_font_size,
            ).next_to(idx, DOWN, buff=0.04)
            bar_parts.append(chip)
        bars.append(VGroup(*bar_parts))
    baseline = Line(
        [-width / 2 - 0.15, -max_height / 2, 0],
        [width / 2 + 0.15, -max_height / 2, 0],
        stroke_color=TEXT_MUTED,
        stroke_width=1.0,
    )
    return VGroup(baseline, *bars), bars


def swap_test_circuit_diagram(
    *,
    center_y: float = 0.0,
    x_left: float = -4.35,
    x_right: float = 4.25,
    spacing: float = 1.0,
    include_measurement: bool = True,
) -> tuple[VGroup, dict[str, object]]:
    """Reusable Swap Test circuit drawing with keyed gate/cut positions."""
    y0, y1, y2 = center_y + spacing, center_y, center_y - spacing
    width = x_right - x_left
    x_h1 = x_left + 0.19 * width
    x_cswap = x_left + 0.50 * width
    x_h2 = x_left + 0.80 * width
    x_meas = x_left + 0.91 * width

    wires = wire_bundle(x_left, x_right, [y0, y1, y2], color=TEXT_MUTED)
    anc_ket = fit_math(
        r"\left|0\right\rangle",
        scale=0.21,
        max_width=0.72,
        color=TEXT_MUTED,
    ).move_to([x_left - 0.60, y0, 0])
    anc_name = body_text("ancilla", size=14, color=TEXT_MUTED).next_to(
        anc_ket, UP, buff=0.05
    )
    labels = VGroup(
        VGroup(anc_name, anc_ket),
        fit_math(
            r"\left|\psi\right\rangle",
            scale=0.20,
            max_width=0.88,
            color=COLOR_HIGHLIGHT,
        ).move_to([x_left - 0.60, y1, 0]),
        fit_math(
            r"\left|\phi_j\right\rangle",
            scale=0.18,
            max_width=1.04,
            color=TEXT_ACCENT,
        ).move_to([x_left - 0.60, y2, 0]),
    )
    h1 = h_gate(stroke_color=TEXT_PRIMARY, text_color=TEXT_PRIMARY).move_to([x_h1, y0, 0])
    h2 = h_gate(stroke_color=TEXT_PRIMARY, text_color=TEXT_PRIMARY).move_to([x_h2, y0, 0])
    cswap = controlled_swap_gate(x_cswap, y0, y1, y2, color=TEXT_PRIMARY)
    objects = [labels, wires, h1, cswap, h2]
    meas = None
    if include_measurement:
        meas = measurement_gate(stroke_color=TEXT_ACCENT).move_to([x_meas, y0, 0])
        objects.append(meas)

    group = VGroup(*objects)
    meta = {
        "labels": labels,
        "wires": wires,
        "h1": h1,
        "cswap": cswap,
        "h2": h2,
        "meas": meas,
        "ys": (y0, y1, y2),
        "cut_initial": x_left + 0.06 * width,
        "cut_after_h": x_h1 + 0.48,
        "cut_after_cswap": x_cswap + 0.48,
        "cut_after_h2": x_h2 + 0.48,
    }
    return group, meta


def pipeline_node(label: str, *, color: str = TEXT_ACCENT, width: float = 1.78) -> VGroup:
    rect = Rectangle(
        width=width,
        height=0.70,
        stroke_color=color,
        stroke_width=1.5,
        fill_color=color,
        fill_opacity=0.08,
    )
    if "\n" in label:
        txt = VGroup(
            *[
                body_text(part, size=18, color=color, weight="BOLD")
                for part in label.split("\n")
            ]
        ).arrange(DOWN, buff=0.02)
    else:
        txt = body_text(label, size=18, color=color, weight="BOLD")
    if txt.width > width * 0.85:
        txt.scale((width * 0.85) / txt.width)
    txt.move_to(rect.get_center())
    return VGroup(rect, txt)


class Lecture5(LectureScene):
    def begin_slide(
        self,
        *,
        section: str | None = None,
        major_section: str | None = None,
        clear: bool = True,
        advance_page: bool | None = None,
    ) -> None:
        if major_section is None and section is not None:
            major_section = MAJOR_SECTION_BY_SECTION.get(section, section or "Hook")
        super().begin_slide(
            section=section,
            major_section=major_section,
            clear=clear,
            advance_page=advance_page,
        )

    def construct(self) -> None:
        self.setup_lecture(author=AUTHOR, title=TITLE, total_pages=TOTAL_PAGES)
        for i, name in enumerate(SLIDE_METHODS):
            getattr(self, name)()
            if i < len(SLIDE_METHODS) - 1:
                self.next_slide()

    def _heading(self, text: str, *, size: int = 44) -> object:
        heading = body_text(text, size=size, weight="BOLD")
        if heading.width > 12.0:
            heading.scale(12.0 / heading.width)
        return heading.to_edge(UP, buff=0.70)

    # === 1. Title =======================================================
    def _slide_title(self) -> None:
        self.begin_slide(section="")

        lecture = body_text("Lecture 5", size=42, color=TEXT_MUTED)
        title = body_text(
            "Quantum k-NN",
            size=76,
            color=TEXT_ACCENT,
            weight="BOLD",
        )
        subtitle = body_text(
            "Tomography-Free Quantum State Classification",
            size=34,
            color=TEXT_PRIMARY,
            weight="BOLD",
        )
        detail = body_text(
            "Swap Test, QADC, comparator oracles, and collision detection",
            size=23,
            color=TEXT_MUTED,
        )
        title_block = (
            VGroup(lecture, title, subtitle, detail)
            .arrange(DOWN, buff=0.24)
            .move_to([0, 0.62, 0])
        )

        author = body_text(AUTHOR, size=25)
        affiliation = body_text("Seoul National University", size=20, color=TEXT_MUTED)
        date = body_text(DATE, size=19, color=TEXT_MUTED)
        author_block = (
            VGroup(author, affiliation, date)
            .arrange(DOWN, buff=0.16)
            .move_to([0, -1.75, 0])
        )

        self.play(FadeIn(title_block), run_time=0.55 / ANIM_SPEED)
        self.play(FadeIn(author_block), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

    # === 2. Question ====================================================
    def _slide_question(self) -> None:
        self.begin_slide(section="Question")

        heading = self._heading("What does tomography ask for?")
        q = fit_math(
            r"\text{Can we classify } \left|\psi\right\rangle "
            r"\text{ without full tomography?}",
            scale=0.26,
            max_width=9.2,
            color=TEXT_ACCENT,
        ).move_to([0, 1.50, 0])

        intro = fit_math(
            r"\text{For two qubits, full tomography reconstructs }"
            r"\rho=\left|\psi\right\rangle\left\langle\psi\right|\in\mathbb{C}^{4\times4}.",
            scale=0.19,
            max_width=8.4,
            color=TEXT_PRIMARY,
        ).move_to([0, 0.92, 0])

        def density_grid(entries: list[list[str]], *, accent: str) -> VGroup:
            cells = VGroup()
            size = 0.34
            for r, row in enumerate(entries):
                for c, value in enumerate(row):
                    active = value not in {"0", ""}
                    rect = Rectangle(
                        width=size,
                        height=size,
                        stroke_color=accent if active else TEXT_MUTED,
                        stroke_width=1.0 if active else 0.6,
                        fill_color=accent if active else "#101010",
                        fill_opacity=0.16 if active else 1.0,
                    )
                    txt = body_text(
                        value,
                        size=12 if value == "1/2" else 14,
                        color=TEXT_PRIMARY if active else TEXT_MUTED,
                        weight="BOLD" if active else "NORMAL",
                    ).move_to(rect.get_center())
                    cell = VGroup(rect, txt)
                    cell.move_to([c * size, -r * size, 0])
                    cells.add(cell)
            cells.move_to(ORIGIN)
            return cells

        def tomography_example(
            title_text: str,
            state_latex: str,
            entries: list[list[str]],
            *,
            color: str,
        ) -> VGroup:
            box = Rectangle(
                width=4.15,
                height=2.25,
                stroke_color=TEXT_MUTED,
                stroke_width=1.0,
                fill_color="#101010",
                fill_opacity=1.0,
            )
            title = body_text(title_text, size=17, color=color, weight="BOLD")
            state = fit_math(state_latex, scale=0.15, max_width=3.65, color=color)
            rho_label = fit_math(r"\rho=", scale=0.16, max_width=0.50, color=TEXT_PRIMARY)
            rho = density_grid(entries, accent=color)
            rho_row = VGroup(rho_label, rho).arrange(RIGHT, buff=0.10)
            content = VGroup(title, state, rho_row).arrange(DOWN, buff=0.13)
            content.move_to(box.get_center())
            return VGroup(box, content)

        examples = VGroup(
            tomography_example(
                "product state",
                r"\left|\psi\right\rangle=\left|00\right\rangle",
                [
                    ["1", "0", "0", "0"],
                    ["0", "0", "0", "0"],
                    ["0", "0", "0", "0"],
                    ["0", "0", "0", "0"],
                ],
                color=COLOR_HIGHLIGHT,
            ),
            tomography_example(
                "Bell state",
                r"\left|\psi\right\rangle=\frac{\left|00\right\rangle+\left|11\right\rangle}{\sqrt2}",
                [
                    ["1/2", "0", "0", "1/2"],
                    ["0", "0", "0", "0"],
                    ["0", "0", "0", "0"],
                    ["1/2", "0", "0", "1/2"],
                ],
                color=COLOR_VAR3,
            ),
        ).arrange(RIGHT, buff=0.42).move_to([0, -0.92, 0])

        pivot = body_text(
            "For classification, reconstructing all 16 entries may be the wrong question.",
            size=23,
            color=TEXT_PRIMARY,
        ).move_to([0, -2.50, 0])

        self.play(FadeIn(heading), FadeIn(q), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(intro), run_time=0.40 / ANIM_SPEED)
        self.play(
            LaggedStart(*[FadeIn(example) for example in examples], lag_ratio=0.14),
            run_time=0.80 / VISUAL_SPEED,
        )
        self.play(FadeIn(pivot), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

    # === 3. Classification not tomography ==============================
    def _slide_classification_not_tomography(self) -> None:
        self.begin_slide(section="Question")

        heading = self._heading("Classification only needs similarities")
        psi = test_state_card().move_to([-4.25, -0.2, 0])
        grid = make_library_grid(show_values=False).scale(0.74).move_to([1.45, -0.2, 0])

        lines = []
        for card in grid:
            lines.append(
                Line(
                    psi[0].get_center(),
                    card[0].get_center(),
                    stroke_color=TEXT_MUTED,
                    stroke_width=0.8,
                ).set_opacity(0.55)
            )
        similarity = fit_math(
            r"F_j=\left|\left\langle\psi|\phi_j\right\rangle\right|^2",
            scale=0.29,
            max_width=4.7,
            color=TEXT_ACCENT,
        ).move_to([0, 2.0, 0])
        question = body_text(
            "Which labeled reference states is it close to?",
            size=24,
            color=TEXT_PRIMARY,
        ).move_to([0, -2.55, 0])

        self.play(FadeIn(heading), FadeIn(similarity), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(psi), FadeIn(grid), run_time=0.45 / ANIM_SPEED)
        self.play(LaggedStart(*[Create(l) for l in lines], lag_ratio=0.08), run_time=0.8 / VISUAL_SPEED)
        self.play(FadeIn(question), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

    # === 4. Training library ===========================================
    def _slide_training_library(self) -> None:
        self.begin_slide(section="Library")

        heading = self._heading("Reference states come with labels")
        formula = fit_math(
            r"\mathcal{D}=\{(\left|\phi_j\right\rangle,\ell_j)\}_{j=0}^{M-1}",
            scale=0.30,
            max_width=6.2,
        ).move_to([0, 1.82, 0])
        grid = make_library_grid(show_values=False).scale(1.12).move_to([0, -0.32, 0])
        access = body_text(
            "Access assumption: state preparation or many copies are available.",
            size=20,
            color=TEXT_MUTED,
        ).move_to([0, -2.65, 0])

        self.play(FadeIn(heading), FadeIn(formula), run_time=0.45 / ANIM_SPEED)
        self.play(LaggedStart(*[FadeIn(c) for c in grid], lag_ratio=0.08), run_time=0.8 / ANIM_SPEED)
        self.play(FadeIn(access), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

    # === 5. Single best rule ===========================================
    def _slide_single_best_rule(self) -> None:
        self.begin_slide(section="One pick")

        heading = self._heading("Obvious rule: choose the largest fidelity")
        values = [v for _, _, v in TRAINING_DATA]
        chart, bars = bar_chart(
            values,
            labels=[idx for idx, _, _ in TRAINING_DATA],
            class_labels=[label for _, label, _ in TRAINING_DATA],
            width=8.75,
            max_height=3.02,
            selected={3},
        )
        chart.move_to([0, -0.55, 0])
        eq = fit_math(
            r"\hat{j}=\arg\max_j F_j=3",
            scale=0.30,
            max_width=5.2,
            color=TEXT_ACCENT,
        ).move_to([0, 2.02, 0])
        chosen = VGroup(
            body_text("chosen index", size=18, color=TEXT_MUTED),
            fit_math(r"\hat{j}=3", scale=0.27, max_width=1.6, color=COLOR_HIGHLIGHT),
        ).arrange(DOWN, buff=0.12).move_to([4.85, 1.05, 0])
        box = SurroundingRectangle(bars[3], color=COLOR_HIGHLIGHT, buff=0.10, stroke_width=2.2)

        self.play(FadeIn(heading), FadeIn(eq), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(chart), run_time=0.55 / ANIM_SPEED)
        self.play(Create(box), FadeIn(chosen), run_time=0.55 / VISUAL_SPEED)
        self.wait(0.5)

    # === 6. Brittle one neighbor =======================================
    def _slide_brittle_one_neighbor(self) -> None:
        self.begin_slide(section="One pick")

        heading = self._heading("One noisy neighbor can flip the answer")
        values = [0.52, 0.49, 0.47, 0.91, 0.88, 0.86, 0.84, 0.31]
        noisy_labels = ["dog", "bird", "dog", "dog", "cat", "cat", "cat", "bird"]
        chart, bars = bar_chart(
            values,
            labels=[str(i) for i in range(8)],
            class_labels=noisy_labels,
            width=8.75,
            max_height=2.62,
            selected={3, 4, 5, 6},
        )
        chart.move_to([0, -0.20, 0])

        outlier = body_text("noisy outlier", size=19, color=COLOR_FALSE).next_to(
            bars[3], UP, buff=0.62
        )
        outlier_arrow = Arrow(
            outlier.get_bottom() + 0.06 * RIGHT,
            bars[3][0].get_corner(UP + RIGHT) + 0.03 * (UP + RIGHT),
            buff=0,
            stroke_color=COLOR_FALSE,
            max_tip_length_to_length_ratio=0.12,
        )
        neighborhood = VGroup(
            body_text("nearest one:", size=20, color=TEXT_MUTED),
            label_chip("dog", color=LABEL_COLORS["dog"], width=0.90, height=0.30, font_size=13),
            body_text("top-4 neighborhood:", size=20, color=TEXT_MUTED),
            label_chip("cat", color=LABEL_COLORS["cat"], width=0.90, height=0.30, font_size=13),
        ).arrange(RIGHT, buff=0.14).move_to([0, -2.50, 0])

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(chart), run_time=0.55 / ANIM_SPEED)
        self.play(FadeIn(outlier), Create(outlier_arrow), Flash(bars[3], color=COLOR_FALSE, flash_radius=0.55), run_time=0.8 / VISUAL_SPEED)
        self.play(FadeIn(neighborhood), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

    # === 7. k-NN definition ============================================
    def _slide_knn_definition(self) -> None:
        self.begin_slide(section="k-NN")

        heading = self._heading("k-NN votes over nearby states")
        values = [v for _, _, v in TRAINING_DATA]
        top = {3, 5, 7}
        chart, _ = bar_chart(
            values,
            labels=[idx for idx, _, _ in TRAINING_DATA],
            class_labels=[label for _, label, _ in TRAINING_DATA],
            width=7.85,
            max_height=3.04,
            selected=top,
        )
        chart.scale(0.90).move_to([-2.95, -0.55, 0])

        set_eq = fit_math(
            r"S_k(\psi)=\operatorname{TopK}_{j}\{F_j\}",
            scale=0.26,
            max_width=3.9,
            color=TEXT_ACCENT,
        ).move_to([3.25, 1.25, 0])
        vote_eq = fit_math(
            r"\hat{\ell}=\operatorname{majority}\{\ell_j:j\in S_k(\psi)\}",
            scale=0.21,
            max_width=4.7,
        ).move_to([3.10, 0.45, 0])

        vote_cards = VGroup(
            label_chip("cat", color=LABEL_COLORS["cat"], width=1.05),
            label_chip("cat", color=LABEL_COLORS["cat"], width=1.05),
            label_chip("cat", color=LABEL_COLORS["cat"], width=1.05),
        ).arrange(DOWN, buff=0.16).move_to([3.10, -0.82, 0])
        vote_caption = body_text(
            "labels of top 3",
            size=17,
            color=TEXT_MUTED,
        ).next_to(vote_cards, UP, buff=0.14)
        winner = VGroup(
            body_text("vote result", size=18, color=TEXT_MUTED),
            fit_math(
                r"\hat{\ell}=\mathrm{cat}",
                scale=0.23,
                max_width=2.5,
                color=LABEL_COLORS["cat"],
            ),
        ).arrange(DOWN, buff=0.07).move_to([3.10, -2.08, 0])

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(chart), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(set_eq), FadeIn(vote_eq), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(vote_caption), LaggedStart(*[FadeIn(c) for c in vote_cards], lag_ratio=0.18), run_time=0.55 / VISUAL_SPEED)
        self.play(FadeIn(winner), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

    # === 8. Bridge ======================================================
    def _slide_bridge(self) -> None:
        self.begin_slide(section="k-NN")

        heading = self._heading("Roadmap: turn similarity into a decision")
        labels = ["pairwise\nfidelity", "similarity\ntable", "top-k", "label"]
        nodes = VGroup(*[pipeline_node(label, width=1.75) for label in labels]).arrange(RIGHT, buff=0.75)
        nodes.move_to([0, 0.25, 0])
        arrows = VGroup(
            *[
                Arrow(
                    nodes[i].get_right() + 0.08 * RIGHT,
                    nodes[i + 1].get_left() + 0.08 * LEFT,
                    buff=0,
                    stroke_color=TEXT_MUTED,
                    max_tip_length_to_length_ratio=0.12,
                )
                for i in range(len(nodes) - 1)
            ]
        )
        caption = body_text(
            "This is why Swap Test, QADC, and comparators appear in this order.",
            size=22,
            color=TEXT_ACCENT,
        ).move_to([0, -1.7, 0])

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        for i, node in enumerate(nodes):
            self.play(FadeIn(node), run_time=0.25 / ANIM_SPEED)
            if i < len(arrows):
                self.play(Create(arrows[i]), run_time=0.25 / ANIM_SPEED)
        self.play(FadeIn(caption), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

    # === 9. One pair ====================================================
    def _slide_one_pair(self) -> None:
        self.begin_slide(section="Swap Test")

        heading = self._heading("Now ask: how do we get one fidelity?")
        psi = test_state_card().move_to([-2.35, 0.10, 0])
        phi = state_card("j", "cat", width=1.65, height=1.20).move_to([2.35, 0.10, 0])
        sim = fit_math(
            r"F_j=\left|\left\langle\psi|\phi_j\right\rangle\right|^2",
            scale=0.32,
            max_width=5.2,
            color=TEXT_ACCENT,
        ).move_to([0, -1.55, 0])
        arrow = Arrow(
            psi.get_right() + 0.25 * RIGHT,
            phi.get_left() + 0.25 * LEFT,
            buff=0,
            stroke_color=TEXT_MUTED,
        )
        question = body_text("How do we get this fidelity?", size=24, color=TEXT_PRIMARY).move_to([0, 1.55, 0])

        self.play(FadeIn(heading), FadeIn(question), run_time=0.40 / ANIM_SPEED)
        self.play(FadeIn(psi), FadeIn(phi), Create(arrow), run_time=0.55 / VISUAL_SPEED)
        self.play(FadeIn(sim), run_time=0.40 / ANIM_SPEED)
        self.wait(0.5)

    # === 10. Swap circuit ==============================================
    def _slide_swap_circuit(self) -> None:
        self.begin_slide(section="Swap Test")

        heading = self._heading("Swap Test estimates one fidelity")
        _, circuit = swap_test_circuit_diagram(center_y=0.05)
        labels = circuit["labels"]
        wires = circuit["wires"]
        h1 = circuit["h1"]
        h2 = circuit["h2"]
        cswap = circuit["cswap"]
        meas = circuit["meas"]

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(labels), Create(wires), run_time=0.55 / ANIM_SPEED)
        self.play(FadeIn(h1), run_time=0.30 / ANIM_SPEED)
        self.play(Create(cswap), run_time=0.65 / VISUAL_SPEED)
        self.play(FadeIn(h2), FadeIn(meas), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

    # === 11. Swap state evolution ======================================
    def _slide_swap_state_evolution(self) -> None:
        self.begin_slide(section="Swap Test")

        heading = self._heading("Follow the state through each gate")
        circuit, meta = swap_test_circuit_diagram(
            center_y=0.88,
            x_left=-4.30,
            x_right=4.05,
            spacing=0.60,
            include_measurement=False,
        )

        cut_bottom = -0.10
        cut_top = 1.95
        cut_style = dict(stroke_color=TEXT_ACCENT, stroke_width=1.4, dash_length=0.08)
        cuts = [
            DashedLine([meta["cut_initial"], cut_bottom, 0], [meta["cut_initial"], cut_top, 0], **cut_style),
            DashedLine([meta["cut_after_h"], cut_bottom, 0], [meta["cut_after_h"], cut_top, 0], **cut_style),
            DashedLine([meta["cut_after_cswap"], cut_bottom, 0], [meta["cut_after_cswap"], cut_top, 0], **cut_style),
            DashedLine([meta["cut_after_h2"], cut_bottom, 0], [meta["cut_after_h2"], cut_top, 0], **cut_style),
        ]
        cut_labels = [
            body_text("input", size=15, color=TEXT_MUTED),
            body_text("after H", size=15, color=TEXT_ACCENT),
            body_text("after swap", size=15, color=TEXT_ACCENT),
            body_text("after H", size=15, color=TEXT_ACCENT),
        ]
        for cut, label in zip(cuts, cut_labels):
            label.next_to(cut, UP, buff=0.06)

        def ket_token(expr: str, *, color: str = TEXT_PRIMARY, max_width: float = 1.10) -> object:
            return fit_math(expr, scale=0.23, max_width=max_width, color=color)

        def payload_pair(first: str, second: str) -> VGroup:
            mapping = {
                "psi": ket_token(r"\left|\psi\right\rangle", color=COLOR_HIGHLIGHT),
                "phi": ket_token(r"\left|\phi_j\right\rangle", color=TEXT_ACCENT),
            }
            return VGroup(mapping[first], mapping[second]).arrange(RIGHT, buff=0.12)

        def sign_token(sign: str) -> object:
            return fit_math(sign, scale=0.22, max_width=0.34, color=TEXT_PRIMARY)

        def ancilla_combo(sign: str) -> VGroup:
            return VGroup(
                body_text("(", size=24, color=TEXT_PRIMARY),
                ket_token(r"\left|0\right\rangle", color=COLOR_TRUE, max_width=0.70),
                sign_token(sign),
                ket_token(r"\left|1\right\rangle", color=COLOR_FALSE, max_width=0.70),
                body_text(")", size=24, color=TEXT_PRIMARY),
            ).arrange(RIGHT, buff=0.05)

        def term(ancilla: object, first: str, second: str) -> VGroup:
            return VGroup(ancilla, payload_pair(first, second)).arrange(RIGHT, buff=0.14)

        def ket_term(label: str, first: str, second: str, *, color: str) -> VGroup:
            return term(ket_token(label, color=color, max_width=0.72), first, second)

        def coefficient(expr: str) -> object:
            return fit_math(expr, scale=0.23, max_width=0.70, color=TEXT_PRIMARY)

        def place_row(group: VGroup, y: float, *, max_width: float = 10.8) -> VGroup:
            group.arrange(RIGHT, buff=0.18)
            if group.width > max_width:
                group.scale(max_width / group.width)
            group.move_to([0, y, 0])
            return group

        def make_after_h(first_second: tuple[str, str] = ("psi", "phi")) -> dict[str, object]:
            first, second = first_second
            coef = coefficient(r"\frac{1}{\sqrt2}")
            t0 = ket_term(r"\left|0\right\rangle", "psi", "phi", color=COLOR_TRUE)
            plus = sign_token(r"+")
            t1 = ket_term(r"\left|1\right\rangle", first, second, color=COLOR_FALSE)
            group = place_row(VGroup(coef, t0, plus, t1), -1.44)
            return {"group": group, "coef": coef, "t0": t0, "plus": plus, "t1": t1}

        def make_decomposed() -> dict[str, object]:
            coef = coefficient(r"\frac12")
            t0 = term(ancilla_combo(r"+"), "psi", "phi")
            plus = sign_token(r"+")
            t1 = term(ancilla_combo(r"-"), "phi", "psi")
            group = place_row(VGroup(coef, t0, plus, t1), -1.44)
            return {"group": group, "coef": coef, "t0": t0, "plus": plus, "t1": t1}

        def make_expanded() -> dict[str, object]:
            coef = coefficient(r"\frac12")
            t00 = ket_term(r"\left|0\right\rangle", "psi", "phi", color=COLOR_TRUE)
            plus_a = sign_token(r"+")
            t10 = ket_term(r"\left|1\right\rangle", "psi", "phi", color=COLOR_FALSE)
            plus_b = sign_token(r"+")
            t01 = ket_term(r"\left|0\right\rangle", "phi", "psi", color=COLOR_TRUE)
            minus = sign_token(r"-")
            t11 = ket_term(r"\left|1\right\rangle", "phi", "psi", color=COLOR_FALSE)
            group = place_row(VGroup(coef, t00, plus_a, t10, plus_b, t01, minus, t11), -1.44)
            return {
                "group": group,
                "coef": coef,
                "t00": t00,
                "plus_a": plus_a,
                "t10": t10,
                "plus_b": plus_b,
                "t01": t01,
                "minus": minus,
                "t11": t11,
            }

        def make_collected_targets() -> dict[str, object]:
            coef = coefficient(r"\frac12")
            t00 = ket_term(r"\left|0\right\rangle", "psi", "phi", color=COLOR_TRUE)
            plus_a = sign_token(r"+")
            t01 = ket_term(r"\left|0\right\rangle", "phi", "psi", color=COLOR_TRUE)
            plus_b = sign_token(r"+")
            t10 = ket_term(r"\left|1\right\rangle", "psi", "phi", color=COLOR_FALSE)
            minus = sign_token(r"-")
            t11 = ket_term(r"\left|1\right\rangle", "phi", "psi", color=COLOR_FALSE)
            group = place_row(VGroup(coef, t00, plus_a, t01, plus_b, t10, minus, t11), -1.44, max_width=10.4)
            return {
                "group": group,
                "coef": coef,
                "t00": t00,
                "plus_a": plus_a,
                "t01": t01,
                "plus_b": plus_b,
                "t10": t10,
                "minus": minus,
                "t11": t11,
            }

        def make_factored() -> dict[str, object]:
            def factored_chunk(label: str, sign: str, *, color: str) -> VGroup:
                return VGroup(
                    coefficient(r"\frac12"),
                    ket_token(label, color=color, max_width=0.72),
                    body_text("(", size=24, color=TEXT_PRIMARY),
                    payload_pair("psi", "phi"),
                    sign_token(sign),
                    payload_pair("phi", "psi"),
                    body_text(")", size=24, color=TEXT_PRIMARY),
                ).arrange(RIGHT, buff=0.12)

            zero = factored_chunk(r"\left|0\right\rangle", r"+", color=COLOR_TRUE)
            plus = sign_token(r"+")
            one = factored_chunk(r"\left|1\right\rangle", r"-", color=COLOR_FALSE)
            group = place_row(VGroup(zero, plus, one), -1.44, max_width=10.6)
            return {"group": group, "zero": zero, "plus": plus, "one": one}

        state_title = body_text("initial state", size=20, color=TEXT_MUTED).move_to([0, -0.58, 0])
        initial_term = ket_term(r"\left|0\right\rangle", "psi", "phi", color=COLOR_TRUE).move_to([0, -1.42, 0])

        title_after_h = body_text("H splits the ancilla basis state", size=20, color=TEXT_ACCENT).move_to(state_title)
        title_after_cswap = body_text("controlled-SWAP changes only the red branch", size=20, color=TEXT_ACCENT).move_to(state_title)
        title_after_h2 = body_text("final H expands the ancilla terms", size=20, color=TEXT_ACCENT).move_to(state_title)
        title_expand = body_text("expand into four terms", size=20, color=TEXT_ACCENT).move_to(state_title)
        title_collect = body_text("move matching ancilla terms next to each other", size=20, color=TEXT_ACCENT).move_to(state_title)
        title_factor = body_text("factor the common ancilla state", size=20, color=TEXT_ACCENT).move_to(state_title)

        note = body_text(
            "Now the ancilla-zero branch contains the symmetric part.",
            size=22,
            color=COLOR_HIGHLIGHT,
        ).move_to([0, -2.45, 0])

        self.play(FadeIn(heading), FadeIn(circuit), run_time=0.45 / ANIM_SPEED)
        self.next_slide()
        self.play(Create(cuts[0]), FadeIn(cut_labels[0]), run_time=0.45 / VISUAL_SPEED)
        self.play(FadeIn(state_title), FadeIn(initial_term), run_time=0.65 / VISUAL_SPEED)
        self.wait(0.15)
        self.next_slide()

        after_h = make_after_h()
        self.play(Create(cuts[1]), FadeIn(cut_labels[1]), run_time=0.45 / VISUAL_SPEED)
        self.play(
            ReplacementTransform(state_title, title_after_h),
            ReplacementTransform(initial_term, after_h["t0"]),
            FadeIn(after_h["coef"], shift=0.12 * LEFT),
            FadeIn(after_h["plus"], shift=0.06 * UP),
            FadeIn(after_h["t1"], shift=0.10 * DOWN),
            run_time=0.78 / VISUAL_SPEED,
        )
        state_title = title_after_h
        self.play(Flash(meta["h1"], color=COLOR_HIGHLIGHT, flash_radius=0.48), run_time=0.45 / VISUAL_SPEED)
        self.wait(0.15)
        self.next_slide()

        self.play(Create(cuts[2]), FadeIn(cut_labels[2]), run_time=0.45 / VISUAL_SPEED)
        self.play(ReplacementTransform(state_title, title_after_cswap), run_time=0.35 / VISUAL_SPEED)
        state_title = title_after_cswap
        row1_payload = after_h["t1"][1]
        left_pos = row1_payload[0].get_center()
        right_pos = row1_payload[1].get_center()
        self.play(
            row1_payload[0].animate.move_to(right_pos),
            row1_payload[1].animate.move_to(left_pos),
            Flash(meta["cswap"], color=COLOR_HIGHLIGHT, flash_radius=0.48),
            run_time=0.85 / VISUAL_SPEED,
        )
        self.wait(0.15)
        self.next_slide()

        decomposed = make_decomposed()
        self.play(Create(cuts[3]), FadeIn(cut_labels[3]), run_time=0.45 / VISUAL_SPEED)
        self.play(ReplacementTransform(state_title, title_after_h2), run_time=0.35 / VISUAL_SPEED)
        self.play(
            Flash(meta["h2"], color=COLOR_HIGHLIGHT, flash_radius=0.48),
            Indicate(VGroup(after_h["t0"][0], after_h["t1"][0]), color=COLOR_HIGHLIGHT),
            run_time=0.65 / VISUAL_SPEED,
        )
        self.play(FadeOut(after_h["group"], shift=0.05 * DOWN), run_time=0.22 / VISUAL_SPEED)
        self.play(FadeIn(decomposed["group"], shift=0.05 * UP), run_time=0.36 / VISUAL_SPEED)
        state_title = title_after_h2
        self.wait(0.15)
        self.next_slide()

        expanded = make_expanded()
        self.play(ReplacementTransform(state_title, title_expand), run_time=0.35 / VISUAL_SPEED)
        self.play(FadeOut(decomposed["group"], shift=0.05 * DOWN), run_time=0.22 / VISUAL_SPEED)
        self.play(FadeIn(expanded["group"], shift=0.05 * UP), run_time=0.42 / VISUAL_SPEED)
        state_title = title_expand
        self.wait(0.15)
        self.next_slide()

        collected = make_collected_targets()
        self.play(ReplacementTransform(state_title, title_collect), run_time=0.35 / VISUAL_SPEED)
        self.play(
            Indicate(VGroup(expanded["t00"], expanded["t01"]), color=COLOR_TRUE),
            Indicate(VGroup(expanded["t10"], expanded["t11"]), color=COLOR_FALSE),
            run_time=0.65 / VISUAL_SPEED,
        )
        self.play(FadeOut(expanded["group"], shift=0.05 * DOWN), run_time=0.22 / VISUAL_SPEED)
        self.play(FadeIn(collected["group"], shift=0.05 * UP), run_time=0.36 / VISUAL_SPEED)
        state_title = title_collect
        self.wait(0.15)
        self.next_slide()

        factored = make_factored()
        self.play(ReplacementTransform(state_title, title_factor), run_time=0.35 / VISUAL_SPEED)
        self.play(FadeOut(collected["group"], scale=0.98), run_time=0.22 / VISUAL_SPEED)
        self.play(FadeIn(factored["group"], shift=0.05 * UP), run_time=0.42 / VISUAL_SPEED)
        state_title = title_factor
        self.play(FadeIn(note), run_time=0.35 / VISUAL_SPEED)
        self.wait(0.5)

    # === 12. Swap split ================================================
    def _slide_swap_split(self) -> None:
        self.begin_slide(section="Swap Test")

        heading = self._heading("The ancilla records overlap information")
        zero = fit_math(
            r"\frac{1}{2}\left|0\right\rangle"
            r"(\left|\psi\right\rangle\left|\phi_j\right\rangle"
            r"+\left|\phi_j\right\rangle\left|\psi\right\rangle)",
            scale=0.24,
            max_width=7.2,
            color=COLOR_TRUE,
        ).move_to([0, 0.95, 0])
        one = fit_math(
            r"\frac{1}{2}\left|1\right\rangle"
            r"(\left|\psi\right\rangle\left|\phi_j\right\rangle"
            r"-\left|\phi_j\right\rangle\left|\psi\right\rangle)",
            scale=0.24,
            max_width=7.2,
            color=COLOR_FALSE,
        ).move_to([0, -0.55, 0])
        plus = body_text("symmetric", size=22, color=COLOR_TRUE).move_to([-4.35, 0.95, 0])
        minus = body_text("antisymmetric", size=22, color=COLOR_FALSE).move_to([-4.35, -0.55, 0])
        note = body_text(
            "The overlap controls how much weight lands in the ancilla-zero branch.",
            size=23,
            color=TEXT_ACCENT,
        ).move_to([0, -2.25, 0])

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(plus), FadeIn(zero), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(minus), FadeIn(one), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(note), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

    # === 12. Probability ===============================================
    def _slide_swap_probability(self) -> None:
        self.begin_slide(section="Swap Test")

        heading = self._heading("Repeated shots estimate the probability")
        relation = fit_math(
            r"F_j=0.70\quad\Longrightarrow\quad "
            r"p_j=\Pr[0\mid j]=\frac{1+F_j}{2}=0.85",
            scale=0.24,
            max_width=8.2,
            color=TEXT_ACCENT,
        ).move_to([0, 1.62, 0])

        one_indices = {3, 8, 14, 21, 28, 34, 41, 49, 57, 66, 72, 79, 86, 93, 98}
        outcomes = [0 if i not in one_indices else 1 for i in range(100)]
        cells = []
        cell_size = 0.23
        gap = 0.035
        for i, outcome in enumerate(outcomes):
            row = i // 10
            col = i % 10
            is_zero = outcome == 0
            color = COLOR_TRUE if is_zero else COLOR_FALSE
            rect = Rectangle(
                width=cell_size,
                height=cell_size,
                stroke_color=color,
                stroke_width=0.8,
                fill_color=color,
                fill_opacity=0.24 if is_zero else 0.32,
            )
            txt = body_text("0" if is_zero else "1", size=8, color=TEXT_PRIMARY)
            txt.move_to(rect.get_center())
            cell = VGroup(rect, txt).move_to(
                [col * (cell_size + gap), -row * (cell_size + gap), 0]
            )
            cells.append(cell)
        grid = VGroup(*cells)
        grid.move_to([-2.75, -0.35, 0])
        grid_title = body_text("100 measurement shots", size=18, color=TEXT_MUTED).next_to(
            grid, UP, buff=0.22
        )

        tracker = ValueTracker(0)
        for i, cell in enumerate(cells):
            cell.set_opacity(0)

            def reveal_cell(mob, i=i):
                mob.set_opacity(1.0 if i < int(tracker.get_value()) else 0.0)

            cell.add_updater(reveal_cell)

        def current_n() -> int:
            return max(0, min(100, int(tracker.get_value())))

        def current_zeros() -> int:
            n = current_n()
            return sum(1 for value in outcomes[:n] if value == 0)

        def current_p() -> float:
            n = current_n()
            return current_zeros() / n if n else 0.0

        def current_f() -> float:
            return 2 * current_p() - 1 if current_n() else 0.0

        table_title = body_text("running estimate", size=18, color=TEXT_MUTED).move_to(
            [2.60, 0.86, 0]
        )
        row_y = [0.36, -0.14, -0.64, -1.14]
        label_x = 1.35
        value_x = 2.45
        estimate_labels = VGroup(
            body_text("n", size=24, color=TEXT_MUTED).move_to([label_x, row_y[0], 0]),
            body_text("#0", size=24, color=COLOR_TRUE).move_to([label_x, row_y[1], 0]),
            fit_math(r"\hat p", scale=0.23, max_width=0.65, color=TEXT_PRIMARY).move_to([label_x, row_y[2], 0]),
            fit_math(r"\hat F", scale=0.23, max_width=0.65, color=TEXT_PRIMARY).move_to([label_x, row_y[3], 0]),
        )
        equals = VGroup(
            *[body_text("=", size=24, color=TEXT_MUTED).move_to([1.85, y, 0]) for y in row_y]
        )

        def live_text(getter, position, *, color=TEXT_PRIMARY, size=28):
            state = {"text": getter()}
            mob = body_text(state["text"], size=size, color=color, weight="BOLD").move_to(position)

            def updater(m):
                new_text = getter()
                if new_text != state["text"]:
                    state["text"] = new_text
                    m.become(body_text(new_text, size=size, color=color, weight="BOLD").move_to(position))

            mob.add_updater(updater)
            return mob

        n_value = live_text(lambda: f"{current_n():3d}", [value_x, row_y[0], 0])
        zero_value = live_text(lambda: f"{current_zeros():3d}", [value_x, row_y[1], 0], color=COLOR_TRUE)
        p_value = live_text(lambda: f"{current_p():.2f}", [value_x, row_y[2], 0])
        f_value = live_text(lambda: f"{current_f():.2f}", [value_x, row_y[3], 0], color=COLOR_HIGHLIGHT)
        estimate_panel = VGroup(
            estimate_labels,
            equals,
            n_value,
            zero_value,
            p_value,
            f_value,
        )
        truth = VGroup(
            body_text("true p=0.85", size=18, color=TEXT_MUTED),
            body_text("true F=0.70", size=18, color=TEXT_MUTED),
        ).arrange(RIGHT, buff=0.35).move_to([2.60, -1.78, 0])
        final_note = body_text(
            "More shots make the classical estimates of p and F concentrate.",
            size=21,
            color=COLOR_HIGHLIGHT,
            ).move_to([0, -2.43, 0])

        self.play(FadeIn(heading), FadeIn(relation), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(grid_title), FadeIn(table_title), FadeIn(estimate_panel), FadeIn(truth), run_time=0.35 / ANIM_SPEED)
        self.add(grid)
        self.play(tracker.animate.set_value(100), run_time=5.2 / VISUAL_SPEED, rate_func=linear)
        for cell in cells:
            cell.clear_updaters()
        for value in (n_value, zero_value, p_value, f_value):
            value.clear_updaters()
        self.play(FadeIn(final_note), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

    # === 13. Caveat =====================================================
    def _slide_swap_caveat(self) -> None:
        self.begin_slide(section="Swap Test")

        heading = self._heading("What assumptions are hiding here?")
        mixed_row = VGroup(
            body_text("Mixed states:", size=24),
            fit_math(
                r"\operatorname{Tr}(\rho\sigma)",
                scale=0.22,
                max_width=2.0,
                color=TEXT_PRIMARY,
            ),
        ).arrange(RIGHT, buff=0.16)
        bullets = VGroup(
            body_text("Pure states:  Swap Test gives fidelity.", size=24),
            mixed_row,
            body_text("Estimation needs repeated preparations or many copies.", size=24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.48).move_to([0, 0.35, 0])
        formula = fit_math(
            r"\Pr[0]=\frac{1+\operatorname{Tr}(\rho\sigma)}{2}",
            scale=0.28,
            max_width=5.2,
            color=TEXT_MUTED,
        ).move_to([0, -1.72, 0])

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(LaggedStart(*[FadeIn(b) for b in bullets], lag_ratio=0.22), run_time=0.75 / ANIM_SPEED)
        self.play(FadeIn(formula), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

    # === 14. Repeat every j ============================================
    def _slide_repeat_every_j(self) -> None:
        self.begin_slide(section="Baseline")

        heading = self._heading("Baseline: measure every F_j")
        grid = make_library_grid(show_values=False).scale(0.78).move_to([0, 0.15, 0])
        swap_icon = oracle_box("SWAP", width=1.12, height=0.58).scale(0.72)
        estimates = []
        for card, (_, _, value) in zip(grid, TRAINING_DATA):
            est = body_text(f"{value:.2f}", size=14, color=TEXT_ACCENT)
            est.next_to(card[0], DOWN, buff=0.08)
            estimates.append(est)
        caption = body_text(
            "Repeat Swap Test many times for each index j.",
            size=23,
            color=TEXT_ACCENT,
        ).move_to([0, -2.55, 0])

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(grid), run_time=0.45 / ANIM_SPEED)
        for card, est in zip(grid, estimates):
            icon = swap_icon.copy().move_to(card[0].get_center() + 0.56 * UP)
            self.play(FadeIn(icon), FadeIn(est), run_time=0.12 / VISUAL_SPEED)
            self.play(FadeOut(icon), run_time=0.08 / VISUAL_SPEED)
        self.play(FadeIn(caption), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

    # === 15. Classical post-processing =================================
    def _slide_classical_postprocessing(self) -> None:
        self.begin_slide(section="Baseline")

        heading = self._heading("Classically, top-k is post-processing")
        qbox = Rectangle(width=2.75, height=1.25, stroke_color=TEXT_ACCENT, fill_color=TEXT_ACCENT, fill_opacity=0.06).move_to([-3.25, 0.35, 0])
        cbox = Rectangle(width=2.95, height=1.25, stroke_color=COLOR_HIGHLIGHT, fill_color=COLOR_HIGHLIGHT, fill_opacity=0.06).move_to([3.25, 0.35, 0])
        qtext = VGroup(
            body_text("Quantum", size=21, color=TEXT_ACCENT, weight="BOLD"),
            body_text("estimate fidelities", size=17, color=TEXT_PRIMARY),
        ).arrange(DOWN, buff=0.18).move_to(qbox.get_center())
        ctext = VGroup(
            body_text("Classical", size=21, color=COLOR_HIGHLIGHT, weight="BOLD"),
            body_text("sort / top-k / vote", size=17, color=TEXT_PRIMARY),
        ).arrange(DOWN, buff=0.18).move_to(cbox.get_center())

        table = VGroup(
            *[
                fit_math(
                    rf"\widetilde F_{{{idx}}}\approx {value:.2f}",
                    scale=0.18,
                    max_width=1.55,
                    color=TEXT_PRIMARY,
                )
                for idx, _, value in TRAINING_DATA[:5]
            ]
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([0, 0.35, 0])
        arrow1 = Arrow(qbox.get_right(), table.get_left() + 0.12 * LEFT, buff=0.08, stroke_color=TEXT_MUTED)
        arrow2 = Arrow(table.get_right() + 0.12 * RIGHT, cbox.get_left(), buff=0.08, stroke_color=TEXT_MUTED)
        eq = fit_math(r"\operatorname{TopK}_{j}\widetilde F_j", scale=0.32, max_width=4.0, color=TEXT_ACCENT).move_to([0, -1.85, 0])

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(qbox), FadeIn(qtext), run_time=0.35 / ANIM_SPEED)
        self.play(Create(arrow1), FadeIn(table), Create(arrow2), run_time=0.55 / ANIM_SPEED)
        self.play(FadeIn(cbox), FadeIn(ctext), FadeIn(eq), run_time=0.45 / ANIM_SPEED)
        self.wait(0.5)

    # === 16. Skepticism ================================================
    def _slide_skepticism(self) -> None:
        self.begin_slide(section="Baseline")

        question = body_text(
            "Why not just measure everything and run classical k-NN?",
            size=38,
            color=TEXT_ACCENT,
            weight="BOLD",
        ).move_to([0, 0.40, 0])
        sub = body_text(
            "This is the right baseline.  Now ask what a coherent quantum algorithm needs.",
            size=22,
            color=TEXT_MUTED,
        ).move_to([0, -0.75, 0])
        self.play(FadeIn(question), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(sub), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

    # === 17. Why coherent cost =========================================
    def _slide_why_coherent_cost(self) -> None:
        self.begin_slide(section="Baseline")

        heading = self._heading("Why bother with the coherent route?")

        left_panel = Rectangle(
            width=4.95,
            height=2.95,
            stroke_color=TEXT_ACCENT,
            stroke_width=1.8,
            fill_color=TEXT_ACCENT,
            fill_opacity=0.05,
        ).move_to([-3.05, 0.10, 0])
        right_panel = Rectangle(
            width=4.95,
            height=2.95,
            stroke_color=COLOR_HIGHLIGHT,
            stroke_width=1.8,
            fill_color=COLOR_HIGHLIGHT,
            fill_opacity=0.05,
        ).move_to([3.05, 0.10, 0])

        left_title = body_text("Sampling + classical top-k", size=23, color=TEXT_ACCENT, weight="BOLD").move_to(left_panel.get_top() + 0.35 * DOWN)
        left_lines = VGroup(
            body_text("estimate all M fidelities", size=18, color=TEXT_PRIMARY),
            fit_math(r"O(1/\epsilon^2)\text{ shots per candidate}", scale=0.16, max_width=4.0, color=TEXT_PRIMARY),
            body_text("then classical top-k", size=18, color=TEXT_MUTED),
            fit_math(r"\sim O(M/\epsilon^2)", scale=0.28, max_width=3.7, color=TEXT_ACCENT),
        ).arrange(DOWN, buff=0.22).next_to(left_title, DOWN, buff=0.24)

        right_title = body_text("Coherent QADC + k-maxima", size=23, color=COLOR_HIGHLIGHT, weight="BOLD").move_to(right_panel.get_top() + 0.35 * DOWN)
        right_lines = VGroup(
            fit_math(r"\text{precision: }O(1/\epsilon)", scale=0.17, max_width=4.0, color=TEXT_PRIMARY),
            body_text("coherent comparator oracle", size=18, color=TEXT_PRIMARY),
            fit_math(r"\text{quantum }k\text{-maxima: }O(\sqrt{kM})", scale=0.17, max_width=4.3, color=TEXT_PRIMARY),
            fit_math(r"\sim O(\sqrt{kM}/\epsilon)", scale=0.28, max_width=4.1, color=COLOR_HIGHLIGHT),
        ).arrange(DOWN, buff=0.22).next_to(right_title, DOWN, buff=0.24)

        arrow = Arrow(left_panel.get_right() + 0.18 * RIGHT, right_panel.get_left() + 0.18 * LEFT, buff=0, stroke_color=TEXT_MUTED)
        note = body_text(
            "Rough oracle-model scaling: speedup comes from both candidate search and precision.",
            size=20,
            color=TEXT_MUTED,
        ).move_to([0, -2.30, 0])

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(left_panel), FadeIn(left_title), FadeIn(left_lines), run_time=0.55 / ANIM_SPEED)
        self.play(Create(arrow), run_time=0.30 / VISUAL_SPEED)
        self.play(FadeIn(right_panel), FadeIn(right_title), FadeIn(right_lines), FadeIn(note), run_time=0.60 / ANIM_SPEED)
        self.wait(0.5)

    # === 17. Superposition indices =====================================
    def _slide_superposition_indices(self) -> None:
        self.begin_slide(section="Coherent")

        heading = self._heading("Keep j coherent while attaching a score")
        in_state = fit_math(
            r"\frac{1}{\sqrt{M}}\sum_{j=0}^{M-1}\left|j\right\rangle\left|0\right\rangle_{\mathrm{score}}",
            scale=0.27,
            max_width=5.7,
            color=TEXT_ACCENT,
        ).move_to([-3.05, 1.35, 0])
        out_state = fit_math(
            r"\frac{1}{\sqrt{M}}\sum_{j=0}^{M-1}\left|j\right\rangle\left|s_j\right\rangle",
            scale=0.27,
            max_width=5.4,
            color=TEXT_ACCENT,
        ).move_to([3.05, 1.35, 0])
        attach = oracle_box("compute", width=1.65, height=0.80).move_to([0, 0.25, 0])
        attach_sub = body_text("similarity score", size=16, color=TEXT_MUTED).next_to(attach, DOWN, buff=0.10)

        def branch_row(idx: int, evidence: str) -> VGroup:
            return VGroup(
                small_register("j", str(idx), width=0.55),
                math_register(evidence, width=0.92, scale=0.12),
            ).arrange(RIGHT, buff=0.08)

        left_rows = VGroup(
            branch_row(0, r"\left|0\right\rangle"),
            branch_row(1, r"\left|0\right\rangle"),
            branch_row(2, r"\left|0\right\rangle"),
            body_text(r"...", size=18, color=TEXT_MUTED),
            branch_row(7, r"\left|0\right\rangle"),
        ).arrange(DOWN, buff=0.10).move_to([-3.05, -0.48, 0])
        right_rows = VGroup(
            branch_row(0, r"\left|s_0\right\rangle"),
            branch_row(1, r"\left|s_1\right\rangle"),
            branch_row(2, r"\left|s_2\right\rangle"),
            body_text(r"...", size=18, color=TEXT_MUTED),
            branch_row(7, r"\left|s_7\right\rangle"),
        ).arrange(DOWN, buff=0.10).move_to([3.05, -0.48, 0])
        left_label = body_text("same blank score register", size=16, color=TEXT_MUTED).next_to(left_rows, UP, buff=0.16)
        right_label = body_text("one score per branch", size=16, color=TEXT_MUTED).next_to(right_rows, UP, buff=0.16)
        arrows = VGroup(
            Arrow(in_state.get_right() + 0.10 * RIGHT, out_state.get_left() + 0.10 * LEFT, buff=0, stroke_color=TEXT_MUTED),
            Arrow(left_rows.get_right() + 0.16 * RIGHT, attach.get_left() + 0.12 * LEFT, buff=0, stroke_color=TEXT_MUTED),
            Arrow(attach.get_right() + 0.12 * RIGHT, right_rows.get_left() + 0.16 * LEFT, buff=0, stroke_color=TEXT_MUTED),
        )
        note = body_text(
            "Do not measure j first; compute the similarity score on every branch.",
            size=22,
            color=TEXT_PRIMARY,
        ).move_to([0, -2.45, 0])

        self.play(FadeIn(heading), FadeIn(in_state), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(left_label), LaggedStart(*[FadeIn(r) for r in left_rows], lag_ratio=0.05), run_time=0.55 / VISUAL_SPEED)
        self.play(Create(arrows[1]), FadeIn(attach), FadeIn(attach_sub), run_time=0.40 / VISUAL_SPEED)
        self.play(Create(arrows[0]), FadeIn(out_state), Create(arrows[2]), FadeIn(right_label), LaggedStart(*[FadeIn(r) for r in right_rows], lag_ratio=0.05), run_time=0.75 / VISUAL_SPEED)
        self.play(FadeIn(note), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

    # === 18. Desired oracle ============================================
    def _slide_desired_oracle(self) -> None:
        self.begin_slide(section="Coherent")

        heading = self._heading("We want a coherent fidelity oracle")
        eq = fit_math(
            r"O_F:\left|j\right\rangle\left|0\right\rangle"
            r"\mapsto \left|j\right\rangle\left|\widetilde F_j\right\rangle",
            scale=0.31,
            max_width=7.4,
            color=TEXT_ACCENT,
        ).move_to([0, 1.65, 0])
        left = VGroup(small_register("j", "j"), small_register("0", "0")).arrange(DOWN, buff=0.18).move_to([-3.15, 0.05, 0])
        box = oracle_box("O_F", width=1.6, height=1.25).move_to([0, 0.05, 0])
        right = VGroup(small_register("j", "j"), bit_register("101101")).arrange(DOWN, buff=0.18).move_to([3.2, 0.05, 0])
        a1 = Arrow(left.get_right() + 0.12 * RIGHT, box.get_left() + 0.12 * LEFT, buff=0, stroke_color=TEXT_MUTED)
        a2 = Arrow(box.get_right() + 0.12 * RIGHT, right.get_left() + 0.12 * LEFT, buff=0, stroke_color=TEXT_MUTED)
        caption = body_text("This is a coherent fidelity-value oracle.", size=23, color=TEXT_PRIMARY).move_to([0, -2.15, 0])

        self.play(FadeIn(heading), FadeIn(eq), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(left), Create(a1), FadeIn(box), Create(a2), FadeIn(right), run_time=0.75 / VISUAL_SPEED)
        self.play(FadeIn(caption), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

    # === 19. Swap not enough ===========================================
    def _slide_swap_not_enough(self) -> None:
        self.begin_slide(section="Coherent")

        heading = self._heading("Swap Test alone is not that oracle")
        gauge = Rectangle(width=2.65, height=0.45, stroke_color=COLOR_TRUE, fill_color="#111111", fill_opacity=1).move_to([-2.95, 0.35, 0])
        fill = Rectangle(width=1.95, height=0.45, stroke_width=0, fill_color=COLOR_TRUE, fill_opacity=0.45).align_to(gauge, LEFT).move_to([gauge.get_left()[0] + 1.95 / 2, 0.35, 0])
        gauge_label = fit_math(r"p_j=\frac{1+F_j}{2}", scale=0.25, max_width=2.6, color=COLOR_TRUE).next_to(gauge, UP, buff=0.25)

        comp = oracle_box("compare", width=2.0, height=1.05).move_to([2.95, 0.35, 0])
        needed = bit_register("101101").next_to(comp, UP, buff=0.32)
        arrow = DashedLine(gauge.get_right() + 0.15 * RIGHT, comp.get_left() + 0.15 * LEFT, stroke_color=COLOR_FALSE)
        x = body_text("type mismatch", size=22, color=COLOR_FALSE, weight="BOLD").move_to([0, -0.85, 0])
        line = body_text(
            "A probability is not a reversible comparator input.",
            size=24,
            color=TEXT_ACCENT,
        ).move_to([0, -2.12, 0])

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(gauge_label), FadeIn(gauge), FadeIn(fill), FadeIn(comp), FadeIn(needed), run_time=0.55 / ANIM_SPEED)
        self.play(Create(arrow), FadeIn(x), run_time=0.45 / VISUAL_SPEED)
        self.play(FadeIn(line), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

    # === 20. Analog to digital =========================================
    def _slide_analog_to_digital(self) -> None:
        self.begin_slide(section="QADC")

        heading = self._heading("QADC turns probability evidence into bits")
        analog = Rectangle(width=2.65, height=0.48, stroke_color=COLOR_TRUE, fill_color="#111111", fill_opacity=1).move_to([-3.15, 0.35, 0])
        fill = Rectangle(width=1.72, height=0.48, stroke_width=0, fill_color=COLOR_TRUE, fill_opacity=0.48).align_to(analog, LEFT).move_to([analog.get_left()[0] + 1.72 / 2, 0.35, 0])
        analog_text = body_text("amplitude / probability", size=18, color=COLOR_TRUE).next_to(analog, UP, buff=0.25)
        qadc = oracle_box("QADC", width=1.72, height=1.08).move_to([0, 0.35, 0])
        digital = bit_register("101101", bit_color=TEXT_ACCENT).move_to([3.20, 0.35, 0])
        digital_text = body_text("qubit string", size=18, color=TEXT_ACCENT).next_to(digital, UP, buff=0.25)
        a1 = Arrow(analog.get_right() + 0.12 * RIGHT, qadc.get_left() + 0.12 * LEFT, buff=0, stroke_color=TEXT_MUTED)
        a2 = Arrow(qadc.get_right() + 0.12 * RIGHT, digital.get_left() + 0.12 * LEFT, buff=0, stroke_color=TEXT_MUTED)
        cite = body_text("Mitarai, Kitagawa, Fujii: Quantum Analog-Digital Conversion", size=18, color=TEXT_MUTED).move_to([0, -2.35, 0])

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(analog_text), FadeIn(analog), FadeIn(fill), run_time=0.35 / ANIM_SPEED)
        self.play(Create(a1), FadeIn(qadc), Create(a2), FadeIn(digital), FadeIn(digital_text), run_time=0.70 / VISUAL_SPEED)
        self.play(FadeIn(cite), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

    # === 21. Amplitude view ============================================
    def _slide_amplitude_view(self) -> None:
        self.begin_slide(section="QADC")

        heading = self._heading("QADC starts from amplitude information")
        eq = fit_math(
            r"A_j\left|0\right\rangle="
            r"\sqrt{p_j}\left|0\right\rangle\left|\mathrm{good}_j\right\rangle"
            r"+\sqrt{1-p_j}\left|1\right\rangle\left|\mathrm{bad}_j\right\rangle",
            scale=0.22,
            max_width=8.7,
            color=TEXT_PRIMARY,
        ).move_to([0, 1.55, 0])
        start = Dot([-3.9, -0.25, 0], radius=0.08, color=TEXT_PRIMARY)
        good = Dot([2.65, 0.50, 0], radius=0.10, color=COLOR_TRUE)
        bad = Dot([2.65, -0.98, 0], radius=0.10, color=COLOR_FALSE)
        gline = Line(start.get_center(), good.get_center(), stroke_color=COLOR_TRUE, stroke_width=5.0)
        bline = Line(start.get_center(), bad.get_center(), stroke_color=COLOR_FALSE, stroke_width=2.7)
        glabel = fit_math(
            r"\sqrt{p_j}\;\text{good branch}",
            scale=0.20,
            max_width=2.3,
            color=COLOR_TRUE,
        ).next_to(good, RIGHT, buff=0.2)
        blabel = fit_math(
            r"\sqrt{1-p_j}\;\text{bad branch}",
            scale=0.20,
            max_width=2.3,
            color=COLOR_FALSE,
        ).next_to(bad, RIGHT, buff=0.2)
        note = body_text("QADC acts on this amplitude-encoded information.", size=23, color=TEXT_ACCENT).move_to([0, -2.25, 0])

        self.play(FadeIn(heading), FadeIn(eq), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(start), Create(gline), Create(bline), FadeIn(good), FadeIn(bad), run_time=0.75 / VISUAL_SPEED)
        self.play(FadeIn(glabel), FadeIn(blabel), FadeIn(note), run_time=0.45 / ANIM_SPEED)
        self.wait(0.5)

    # === 22. QPE operator ==============================================
    def _slide_qpe_operator(self) -> None:
        self.begin_slide(section="QADC")

        heading = self._heading("Amplitude estimation runs QPE")
        prep = fit_math(
            r"A_j|0\rangle=\sqrt{p_j}\,|\mathrm{good}\rangle"
            r"+\sqrt{1-p_j}\,|\mathrm{bad}\rangle",
            scale=0.22,
            max_width=8.5,
            color=TEXT_PRIMARY,
        ).move_to([0, 1.42, 0])

        q_block = oracle_box("Q_j", width=1.25, height=0.90).move_to([-2.95, 0.15, 0])
        q_def = fit_math(
            r"Q_j=-A_jS_0A_j^\dagger S_{\mathrm{good}}",
            scale=0.20,
            max_width=3.6,
            color=TEXT_ACCENT,
        ).next_to(q_block, DOWN, buff=0.22)
        q_note = body_text("Grover iterate", size=19, color=TEXT_MUTED).next_to(q_block, UP, buff=0.20)

        plane = Circle(radius=0.95, stroke_color=TEXT_MUTED, stroke_width=1.2).move_to([0.15, 0.10, 0])
        center = plane.get_center()
        good_axis = Line(center + 0.82 * LEFT, center + 0.82 * RIGHT, stroke_color=COLOR_TRUE, stroke_width=2.0)
        bad_axis = Line(center + 0.82 * DOWN, center + 0.82 * UP, stroke_color=COLOR_FALSE, stroke_width=2.0)
        rot = Arc(radius=0.48, start_angle=0.15, angle=0.95, arc_center=center, color=TEXT_ACCENT)
        rot_label = fit_math(r"2\pi\theta_j", scale=0.17, max_width=1.1, color=TEXT_ACCENT).move_to(center + 0.75 * UP + 0.18 * RIGHT)
        plane_label = body_text("rotation in good/bad subspace", size=19, color=TEXT_MUTED).next_to(plane, DOWN, buff=0.26)

        qpe = oracle_box("QPE", width=1.35, height=0.90).move_to([3.05, 0.15, 0])
        phase = bit_register("011010", bit_color=TEXT_ACCENT).next_to(qpe, RIGHT, buff=0.36)
        phase_label = fit_math(r"\widetilde\theta_j", scale=0.16, max_width=0.9, color=TEXT_ACCENT).next_to(phase, UP, buff=0.15)
        a1 = Arrow(q_block.get_right() + 0.15 * RIGHT, plane.get_left() + 0.08 * LEFT, buff=0, stroke_color=TEXT_MUTED)
        a2 = Arrow(plane.get_right() + 0.12 * RIGHT, qpe.get_left() + 0.12 * LEFT, buff=0, stroke_color=TEXT_MUTED)

        note = body_text(
            "QPE reads the eigenphase of this iterate, not repeated measurement shots.",
            size=22,
            color=COLOR_HIGHLIGHT,
        ).move_to([0, -2.25, 0])

        self.play(FadeIn(heading), FadeIn(prep), run_time=0.40 / ANIM_SPEED)
        self.play(FadeIn(q_note), FadeIn(q_block), FadeIn(q_def), run_time=0.45 / ANIM_SPEED)
        self.play(Create(a1), Create(plane), Create(good_axis), Create(bad_axis), Create(rot), FadeIn(rot_label), FadeIn(plane_label), run_time=0.70 / VISUAL_SPEED)
        self.play(Create(a2), FadeIn(qpe), FadeIn(phase), FadeIn(phase_label), FadeIn(note), run_time=0.60 / VISUAL_SPEED)
        self.wait(0.5)

    # === 23. QPE circuit ===============================================
    def _slide_qpe_circuit(self) -> None:
        self.begin_slide(section="QADC")

        heading = self._heading("QPE writes the eigenphase into bits")

        eig = fit_math(
            r"U|\Psi\rangle=e^{2\pi i\varphi}|\Psi\rangle",
            scale=0.30,
            max_width=5.5,
            color=TEXT_ACCENT,
        ).move_to([0, 1.45, 0])
        message = body_text(
            "For an eigenstate, QPE estimates the phase.",
            size=20,
            color=TEXT_PRIMARY,
        ).move_to([0, 0.82, 0])

        y_phase = -0.12
        y_state = -1.18
        x0 = -4.35
        x1 = -2.70
        x2 = -0.70
        x3 = 1.45
        x4 = 3.55

        phase_label = body_text("phase register", size=17, color=TEXT_MUTED).move_to([x0, y_phase + 0.48, 0])
        state_label = body_text("eigenstate", size=17, color=TEXT_MUTED).move_to([x0, y_state + 0.48, 0])
        phase_in = bit_register("000000", bit_color=TEXT_ACCENT).move_to([x0, y_phase, 0])
        state_in = fit_math(r"|\Psi\rangle", scale=0.24, max_width=1.2, color=TEXT_PRIMARY).move_to([x0, y_state, 0])

        h_box = oracle_box("H", width=0.78, height=0.68).move_to([x1, y_phase, 0])
        h_note = body_text("superpose", size=15, color=TEXT_MUTED).next_to(h_box, UP, buff=0.12)

        ctrl = oracle_box(r"U^{2^t}", width=2.25, height=0.78, math_label=True).move_to([x2, (y_phase + y_state) / 2, 0])
        ctrl_note = body_text("controlled powers", size=15, color=TEXT_MUTED).next_to(ctrl, UP, buff=0.12)
        iqft = oracle_box(r"\mathrm{QFT}^{-1}", width=1.25, height=0.68, math_label=True).move_to([x3, y_phase, 0])
        phase_out = bit_register("011010", bit_color=TEXT_ACCENT).move_to([x4, y_phase, 0])
        out_label = fit_math(r"|\widetilde\varphi\rangle", scale=0.18, max_width=1.2, color=TEXT_ACCENT).next_to(phase_out, UP, buff=0.16)
        state_out = fit_math(r"|\Psi\rangle", scale=0.24, max_width=1.2, color=TEXT_MUTED).move_to([x4, y_state, 0])

        arrows = VGroup(
            Arrow(phase_in.get_right() + 0.08 * RIGHT, h_box.get_left() + 0.08 * LEFT, buff=0, stroke_color=TEXT_MUTED),
            Arrow(h_box.get_right() + 0.08 * RIGHT, ctrl.get_left() + 0.08 * LEFT + 0.26 * UP, buff=0, stroke_color=TEXT_MUTED),
            Arrow(ctrl.get_right() + 0.08 * RIGHT + 0.26 * UP, iqft.get_left() + 0.08 * LEFT, buff=0, stroke_color=TEXT_MUTED),
            Arrow(iqft.get_right() + 0.08 * RIGHT, phase_out.get_left() + 0.08 * LEFT, buff=0, stroke_color=TEXT_MUTED),
            Arrow(state_in.get_right() + 0.08 * RIGHT, ctrl.get_left() + 0.08 * LEFT + 0.28 * DOWN, buff=0, stroke_color=TEXT_MUTED),
            Arrow(ctrl.get_right() + 0.08 * RIGHT + 0.28 * DOWN, state_out.get_left() + 0.08 * LEFT, buff=0, stroke_color=TEXT_MUTED),
        )

        note = fit_math(
            r"\text{For amplitude estimation, }U=Q_j,\quad \varphi=\theta_j\text{ or }1-\theta_j.",
            scale=0.17,
            max_width=8.4,
            color=COLOR_HIGHLIGHT,
        ).move_to([0, -2.28, 0])

        self.play(FadeIn(heading), FadeIn(eig), FadeIn(message), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(phase_label), FadeIn(state_label), FadeIn(phase_in), FadeIn(state_in), run_time=0.40 / ANIM_SPEED)
        self.play(Create(arrows[0]), FadeIn(h_box), FadeIn(h_note), run_time=0.35 / VISUAL_SPEED)
        self.play(Create(arrows[1]), Create(arrows[4]), FadeIn(ctrl), FadeIn(ctrl_note), run_time=0.45 / VISUAL_SPEED)
        self.play(Create(arrows[2]), Create(arrows[5]), FadeIn(iqft), FadeIn(state_out), run_time=0.45 / VISUAL_SPEED)
        self.play(Create(arrows[3]), FadeIn(phase_out), FadeIn(out_label), FadeIn(note), run_time=0.45 / VISUAL_SPEED)
        self.wait(0.5)

    # === 24. QPE eigenphase ============================================
    def _slide_qpe_eigenphase(self) -> None:
        self.begin_slide(section="QADC")

        heading = self._heading("QPE sees two eigenphases")
        eig_plus = fit_math(
            r"Q_j|\Psi_+\rangle=e^{+2\pi i\theta_j}|\Psi_+\rangle",
            scale=0.28,
            max_width=6.0,
            color=TEXT_ACCENT,
        ).move_to([0, 1.20, 0])
        eig_minus = fit_math(
            r"Q_j|\Psi_-\rangle=e^{-2\pi i\theta_j}|\Psi_-\rangle"
            r"=e^{2\pi i(1-\theta_j)}|\Psi_-\rangle",
            scale=0.24,
            max_width=8.6,
            color=TEXT_ACCENT,
        ).move_to([0, 0.42, 0])
        decomp = fit_math(
            r"A_j|0\rangle=\alpha_+|\Psi_+\rangle+\alpha_-|\Psi_-\rangle",
            scale=0.26,
            max_width=7.2,
            color=TEXT_PRIMARY,
        ).move_to([0, -0.42, 0])
        qpe_out = fit_math(
            r"\mathrm{QPE}\;\Rightarrow\;\theta_j\;\text{or}\;1-\theta_j",
            scale=0.26,
            max_width=6.8,
            color=COLOR_HIGHLIGHT,
        ).move_to([0, -1.20, 0])
        harmless = fit_math(
            r"\sin^2(\pi\theta_j)=\sin^2(\pi(1-\theta_j))",
            scale=0.25,
            max_width=6.8,
            color=COLOR_TRUE,
        ).move_to([0, -1.88, 0])
        note = body_text(
            "We do not need to know the eigenvectors; QPE acts branch by branch.",
            size=20,
            color=TEXT_MUTED,
        ).move_to([0, -2.55, 0])

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(eig_plus), FadeIn(eig_minus), run_time=0.55 / ANIM_SPEED)
        self.play(FadeIn(decomp), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(qpe_out), FadeIn(harmless), FadeIn(note), run_time=0.55 / ANIM_SPEED)
        self.wait(0.5)

    # === 24. Theta parameter ===========================================
    def _slide_theta_parameter(self) -> None:
        self.begin_slide(section="QADC")

        heading = self._heading("The phase encodes the probability")
        circle = Circle(radius=1.15, stroke_color=TEXT_MUTED, stroke_width=1.4).move_to([-2.2, -0.15, 0])
        center_point = circle.get_center()
        center = Dot(center_point, radius=0.04, color=TEXT_MUTED)
        theta_angle = 0.78
        radius = Line(center_point, center_point + 1.15 * RIGHT, stroke_color=TEXT_MUTED)
        endpoint = center_point + 1.15 * (cos(theta_angle) * RIGHT + sin(theta_angle) * UP)
        arm = Line(center_point, endpoint, stroke_color=TEXT_ACCENT, stroke_width=3.0)
        arc = Arc(radius=0.42, start_angle=0, angle=theta_angle, arc_center=center_point, color=TEXT_ACCENT)
        theta = fit_math(r"\theta_j", scale=0.20, max_width=0.75, color=TEXT_ACCENT).move_to(
            center_point + 0.68 * (cos(theta_angle / 2) * RIGHT + sin(theta_angle / 2) * UP) + 0.08 * UP
        )

        eq1 = fit_math(r"p_j=\sin^2(\pi\theta_j)", scale=0.33, max_width=4.4, color=TEXT_ACCENT).move_to([2.45, 0.78, 0])
        eq2 = fit_math(r"p_j=\sin^2(\pi(1-\theta_j))", scale=0.25, max_width=4.9, color=COLOR_TRUE).move_to([2.45, 0.05, 0])
        eq3 = fit_math(r"F_j=2p_j-1", scale=0.28, max_width=3.3).move_to([2.45, -0.72, 0])
        note = body_text("Either QPE phase branch gives the same probability.", size=22, color=TEXT_MUTED).move_to([0, -2.25, 0])

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(Create(circle), FadeIn(center), Create(radius), run_time=0.40 / ANIM_SPEED)
        self.play(Create(arm), Create(arc), FadeIn(theta), run_time=0.60 / VISUAL_SPEED)
        self.play(FadeIn(eq1), FadeIn(eq2), FadeIn(eq3), FadeIn(note), run_time=0.50 / ANIM_SPEED)
        self.wait(0.5)

    # === 25. Digital register ==========================================
    def _slide_digital_register(self) -> None:
        self.begin_slide(section="QADC")

        heading = self._heading("QPE and arithmetic produce fidelity bits")
        prob = VGroup(
            fit_math(r"p_j", scale=0.22, max_width=0.90, color=TEXT_MUTED),
            Rectangle(
                width=1.00,
                height=0.44,
                stroke_color=COLOR_TRUE,
                stroke_width=1.5,
                fill_color=COLOR_TRUE,
                fill_opacity=0.25,
            ),
        ).arrange(DOWN, buff=0.16)
        prob[1].add(
            body_text("prob.", size=15, color=TEXT_PRIMARY).move_to(prob[1].get_center())
        )
        theta_reg = VGroup(
            fit_math(r"\widetilde\theta_j", scale=0.16, max_width=1.00, color=TEXT_MUTED),
            bit_register("011010"),
        ).arrange(DOWN, buff=0.16)
        p_reg = VGroup(
            fit_math(r"\widetilde p_j", scale=0.16, max_width=0.90, color=TEXT_MUTED),
            bit_register("110001"),
        ).arrange(DOWN, buff=0.16)
        f_reg = VGroup(
            fit_math(r"\widetilde F_j", scale=0.16, max_width=0.90, color=TEXT_MUTED),
            bit_register("101101"),
        ).arrange(DOWN, buff=0.16)
        stages = VGroup(prob, theta_reg, p_reg, f_reg).arrange(RIGHT, buff=0.72).move_to([0, 0.18, 0])
        arrows = VGroup(
            Arrow(stages[0].get_right() + 0.15 * RIGHT, stages[1].get_left() + 0.15 * LEFT, buff=0, stroke_color=TEXT_MUTED),
            Arrow(stages[1].get_right() + 0.15 * RIGHT, stages[2].get_left() + 0.15 * LEFT, buff=0, stroke_color=TEXT_MUTED),
            Arrow(stages[2].get_right() + 0.15 * RIGHT, stages[3].get_left() + 0.15 * LEFT, buff=0, stroke_color=TEXT_MUTED),
        )
        labels = VGroup(
            body_text("QPE", size=17, color=TEXT_ACCENT).next_to(arrows[0], UP, buff=0.14),
            body_text("rev. sin^2", size=17, color=TEXT_ACCENT).next_to(arrows[1], UP, buff=0.14),
            body_text("2p - 1", size=17, color=TEXT_ACCENT).next_to(arrows[2], UP, buff=0.14),
        )
        eq = fit_math(
            r"p_j=\sin^2(\pi\theta_j),\qquad \widetilde F_j = 2\widetilde p_j-1",
            scale=0.25,
            max_width=8.2,
            color=TEXT_ACCENT,
        ).move_to([0, -1.80, 0])

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(prob), run_time=0.35 / ANIM_SPEED)
        self.play(Create(arrows[0]), FadeIn(labels[0]), FadeIn(theta_reg), run_time=0.45 / VISUAL_SPEED)
        self.play(Create(arrows[1]), FadeIn(labels[1]), FadeIn(p_reg), run_time=0.45 / VISUAL_SPEED)
        self.play(Create(arrows[2]), FadeIn(labels[2]), FadeIn(f_reg), FadeIn(eq), run_time=0.45 / VISUAL_SPEED)
        self.wait(0.5)

    # === 26. Central oracle ============================================
    def _slide_central_oracle(self) -> None:
        self.begin_slide(section="QADC")

        heading = self._heading("Now comparison becomes arithmetic")
        eq = fit_math(
            r"O_F:\left|j\right\rangle\left|0\right\rangle"
            r"\mapsto \left|j\right\rangle\left|\widetilde F_j\right\rangle",
            scale=0.38,
            max_width=8.5,
            color=TEXT_ACCENT,
        ).move_to([0, 0.82, 0])
        caveat = body_text(
            "Precision, copies, and state-preparation costs are inside this oracle.",
            size=22,
            color=TEXT_MUTED,
        ).move_to([0, -0.60, 0])
        use = body_text(
            "Once we have it, comparison becomes ordinary reversible arithmetic.",
            size=24,
            color=TEXT_PRIMARY,
        ).move_to([0, -1.55, 0])

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(eq), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(caveat), FadeIn(use), run_time=0.45 / ANIM_SPEED)
        self.wait(0.5)

    # === 25. Comparisons ===============================================
    def _slide_comparisons(self) -> None:
        self.begin_slide(section="Comparator")

        heading = self._heading("To find top-k, compare two candidates")
        values = [v for _, _, v in TRAINING_DATA]
        chart, bars = bar_chart(
            values,
            labels=[idx for idx, _, _ in TRAINING_DATA],
            class_labels=[label for _, label, _ in TRAINING_DATA],
            selected={3, 5},
        )
        chart.move_to([0, -0.35, 0])
        question = fit_math(r"F_i>F_j\;?", scale=0.45, max_width=3.0, color=TEXT_ACCENT).move_to([0, 1.95, 0])
        b1 = SurroundingRectangle(bars[3], color=COLOR_HIGHLIGHT, buff=0.10)
        b2 = SurroundingRectangle(bars[5], color=COLOR_VAR4, buff=0.10)

        self.play(FadeIn(heading), FadeIn(question), run_time=0.40 / ANIM_SPEED)
        self.play(FadeIn(chart), run_time=0.45 / ANIM_SPEED)
        self.play(Create(b1), Create(b2), run_time=0.45 / VISUAL_SPEED)
        self.wait(0.5)

    # === 26. Comparator construction ===================================
    def _slide_comparator_construction(self) -> None:
        self.begin_slide(section="Comparator")

        heading = self._heading("Comparator oracle from fidelity registers")
        top_eq = fit_math(
            r"O_>:\left|i\right\rangle\left|j\right\rangle\left|0\right\rangle"
            r"\mapsto \left|i\right\rangle\left|j\right\rangle"
            r"\left|[\widetilde F_i>\widetilde F_j]\right\rangle",
            scale=0.30,
            max_width=8.9,
            color=TEXT_ACCENT,
        ).move_to([0, 1.78, 0])

        left = VGroup(small_register("i", "i", width=0.72), small_register("j", "j", width=0.72)).arrange(DOWN, buff=0.16).move_to([-4.25, 0.0, 0])
        of1 = oracle_box("O_F", width=1.05, height=0.70).move_to([-2.15, 0.42, 0])
        of2 = oracle_box("O_F", width=1.05, height=0.70).move_to([-2.15, -0.42, 0])
        regs = VGroup(bit_register("111010"), bit_register("110001")).arrange(DOWN, buff=0.26).move_to([0.0, 0.0, 0])
        comp = oracle_box(">", width=0.95, height=0.95).move_to([2.05, 0.0, 0])
        flag = small_register("flag", "1", width=0.72).move_to([3.75, 0.0, 0])
        arrows = VGroup(
            Arrow(left.get_right() + 0.1 * RIGHT, of1.get_left() + 0.1 * LEFT, buff=0, stroke_color=TEXT_MUTED),
            Arrow(left.get_right() + 0.1 * RIGHT, of2.get_left() + 0.1 * LEFT, buff=0, stroke_color=TEXT_MUTED),
            Arrow(of1.get_right() + 0.1 * RIGHT, regs[0].get_left() + 0.1 * LEFT, buff=0, stroke_color=TEXT_MUTED),
            Arrow(of2.get_right() + 0.1 * RIGHT, regs[1].get_left() + 0.1 * LEFT, buff=0, stroke_color=TEXT_MUTED),
            Arrow(regs.get_right() + 0.1 * RIGHT, comp.get_left() + 0.1 * LEFT, buff=0, stroke_color=TEXT_MUTED),
            Arrow(comp.get_right() + 0.1 * RIGHT, flag.get_left() + 0.1 * LEFT, buff=0, stroke_color=TEXT_MUTED),
        )
        uncompute = body_text("then uncompute the two fidelity registers", size=21, color=TEXT_MUTED).move_to([0, -2.25, 0])

        self.play(FadeIn(heading), FadeIn(top_eq), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(left), Create(arrows[0]), Create(arrows[1]), FadeIn(of1), FadeIn(of2), run_time=0.50 / VISUAL_SPEED)
        self.play(Create(arrows[2]), Create(arrows[3]), FadeIn(regs), run_time=0.50 / VISUAL_SPEED)
        self.play(Create(arrows[4]), FadeIn(comp), Create(arrows[5]), FadeIn(flag), run_time=0.55 / VISUAL_SPEED)
        self.play(FadeIn(uncompute), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

    # === 27. Top-k machinery ===========================================
    def _slide_topk_machinery(self) -> None:
        self.begin_slide(section="Top-k")

        heading = self._heading("Top-k search uses the comparator")
        comp = oracle_box("comparator", width=2.15, height=0.90).move_to([-3.05, 0.35, 0])
        selector = oracle_box("k-maxima", width=2.05, height=1.05).move_to([0, 0.35, 0])
        selected = VGroup(*[state_card(str(i), "cat", width=1.0, height=0.72) for i in [3, 5, 7]]).arrange(RIGHT, buff=0.18).scale(0.82).move_to([3.25, 0.35, 0])
        a1 = Arrow(comp.get_right() + 0.12 * RIGHT, selector.get_left() + 0.12 * LEFT, buff=0, stroke_color=TEXT_MUTED)
        a2 = Arrow(selector.get_right() + 0.12 * RIGHT, selected.get_left() + 0.12 * LEFT, buff=0, stroke_color=TEXT_MUTED)
        result = fit_math(r"O(\sqrt{kM})\ \text{comparison/fidelity-oracle calls}", scale=0.24, max_width=6.8, color=TEXT_ACCENT).move_to([0, -1.35, 0])
        cite = body_text("Basheer, Afham, Goyal: QkNN reduces to quantum k-maxima.", size=18, color=TEXT_MUTED).move_to([0, -2.25, 0])

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(comp), Create(a1), FadeIn(selector), Create(a2), FadeIn(selected), run_time=0.75 / VISUAL_SPEED)
        self.play(FadeIn(result), FadeIn(cite), run_time=0.45 / ANIM_SPEED)
        self.wait(0.5)

    # === 28. Majority vote =============================================
    def _slide_majority_vote(self) -> None:
        self.begin_slide(section="Top-k")

        heading = self._heading("The classifier still votes over labels")
        selected = VGroup(
            state_card("3", "cat", width=1.12, height=0.82),
            state_card("5", "cat", width=1.12, height=0.82),
            state_card("7", "cat", width=1.12, height=0.82),
            state_card("0", "dog", width=1.12, height=0.82),
            state_card("2", "dog", width=1.12, height=0.82),
        ).arrange(RIGHT, buff=0.18).move_to([0, 1.02, 0])
        panel = Rectangle(width=5.95, height=1.72, stroke_color=TEXT_MUTED, fill_color="#101010", fill_opacity=1).move_to([0, -0.64, 0])
        chips = VGroup(
            label_chip("cat", color=LABEL_COLORS["cat"], width=1.0),
            label_chip("cat", color=LABEL_COLORS["cat"], width=1.0),
            label_chip("cat", color=LABEL_COLORS["cat"], width=1.0),
            label_chip("dog", color=LABEL_COLORS["dog"], width=1.0),
            label_chip("dog", color=LABEL_COLORS["dog"], width=1.0),
        ).arrange(RIGHT, buff=0.12).move_to(panel.get_center() + 0.38 * UP)
        winner = VGroup(
            body_text("vote result", size=20, color=TEXT_MUTED),
            fit_math(
                r"\hat{\ell}=\mathrm{cat}",
                scale=0.25,
                max_width=3.0,
                color=LABEL_COLORS["cat"],
            ),
        ).arrange(DOWN, buff=0.08).move_to(panel.get_center() + 0.42 * DOWN)
        eq = fit_math(r"\hat{\ell}=\operatorname{majority}\{\ell_j:j\in S_k(\psi)\}", scale=0.22, max_width=6.0).move_to([0, -2.35, 0])

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(LaggedStart(*[FadeIn(c) for c in selected], lag_ratio=0.08), run_time=0.50 / ANIM_SPEED)
        self.play(FadeIn(panel), LaggedStart(*[FadeIn(c) for c in chips], lag_ratio=0.10), run_time=0.65 / VISUAL_SPEED)
        self.play(FadeIn(winner), FadeIn(eq), run_time=0.40 / ANIM_SPEED)
        self.wait(0.5)

    # === 29. Top-k enough ==============================================
    def _slide_topk_enough(self) -> None:
        self.begin_slide(section="Primitives")

        heading = self._heading("Core classifier is done; now look at primitives")
        core = pipeline_node("k-NN core\nTop-k + vote", color=TEXT_ACCENT, width=2.45).move_to([-3.35, 0.40, 0])
        done = body_text("classification pipeline", size=21, color=TEXT_MUTED).next_to(core, UP, buff=0.28)
        divider = Line([0.0, 1.35, 0], [0.0, -1.30, 0], stroke_color=TEXT_MUTED, stroke_width=1.4).set_opacity(0.45)
        primitive_title = body_text("separate primitive examples", size=24, color=TEXT_PRIMARY, weight="BOLD").move_to([2.75, 1.15, 0])
        sorting = pipeline_node("comparison\nsorting", color=COLOR_VAR4, width=2.35).move_to([2.75, 0.45, 0])
        collision = pipeline_node("element distinctness\ncollision finding", color=COLOR_HIGHLIGHT, width=2.70).move_to([2.75, -0.75, 0])
        notes = VGroup(
            body_text("These are not required for the k-NN classifier.", size=23, color=TEXT_PRIMARY),
            body_text("They show how comparator/oracle ideas reappear in quantum algorithms.", size=22, color=TEXT_ACCENT),
        ).arrange(DOWN, buff=0.25).move_to([0, -2.15, 0])

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(done), FadeIn(core), Create(divider), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(primitive_title), FadeIn(sorting), FadeIn(collision), run_time=0.65 / VISUAL_SPEED)
        self.play(FadeIn(notes), run_time=0.45 / ANIM_SPEED)
        self.wait(0.5)

    # === 30. Why ranking ===============================================
    def _slide_why_ranking(self) -> None:
        self.begin_slide(section="Ranking")

        heading = self._heading("Primitive: sort using only comparisons")

        def item_box(label: str) -> VGroup:
            rect = Rectangle(
                width=0.86,
                height=0.58,
                stroke_color=TEXT_ACCENT,
                stroke_width=1.5,
                fill_color=TEXT_ACCENT,
                fill_opacity=0.06,
            )
            txt = fit_math(label, scale=0.18, max_width=0.58, color=TEXT_PRIMARY)
            txt.move_to(rect.get_center())
            return VGroup(rect, txt)

        input_title = body_text("Given black-box items", size=22, color=TEXT_MUTED)
        unordered = VGroup(
            item_box(r"x_3"),
            item_box(r"x_1"),
            item_box(r"x_4"),
            item_box(r"x_0"),
            item_box(r"x_2"),
        ).arrange(RIGHT, buff=0.12)
        input_group = VGroup(input_title, unordered).arrange(DOWN, buff=0.26).move_to([-3.45, 0.35, 0])

        oracle = oracle_box("O_>", width=1.35, height=0.92).move_to([0, 0.35, 0])
        oracle_eq = fit_math(
            r"O_>:\left|i,j,0\right\rangle\mapsto"
            r"\left|i,j,[x_i>x_j]\right\rangle",
            scale=0.20,
            max_width=4.6,
            color=TEXT_ACCENT,
        ).move_to([0, -0.82, 0])

        output_title = body_text("Recover the full order", size=22, color=TEXT_MUTED)
        ordered = VGroup(
            item_box(r"x_0"),
            item_box(r"x_1"),
            item_box(r"x_2"),
            item_box(r"x_3"),
            item_box(r"x_4"),
        ).arrange(RIGHT, buff=0.12)
        order_relation = fit_math(r"x_0<x_1<x_2<x_3<x_4", scale=0.22, max_width=3.2, color=TEXT_ACCENT)
        output_group = VGroup(output_title, ordered, order_relation).arrange(DOWN, buff=0.22).move_to([3.45, 0.25, 0])

        left_arrow = Arrow(input_group.get_right() + 0.15 * RIGHT, oracle.get_left() + 0.10 * LEFT, buff=0, stroke_color=TEXT_MUTED)
        right_arrow = Arrow(oracle.get_right() + 0.10 * RIGHT, output_group.get_left() + 0.15 * LEFT, buff=0, stroke_color=TEXT_MUTED)
        message = body_text(
            "Sorting asks for the whole order, not just the largest or top-k.",
            size=23,
            color=COLOR_HIGHLIGHT,
        ).move_to([0, -2.35, 0])

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(input_group), run_time=0.45 / ANIM_SPEED)
        self.play(Create(left_arrow), FadeIn(oracle), FadeIn(oracle_eq), run_time=0.55 / VISUAL_SPEED)
        self.play(Create(right_arrow), FadeIn(output_group), run_time=0.55 / VISUAL_SPEED)
        self.play(FadeIn(message), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

    # === 31. All-pairs rank ============================================
    def _slide_all_pairs_rank(self) -> None:
        self.begin_slide(section="Ranking")

        heading = self._heading("Ranks come from pairwise comparisons")
        eq1 = fit_math(r"c_{ij}=[x_j>x_i]", scale=0.24, max_width=3.2, color=TEXT_ACCENT).move_to([-2.65, 1.65, 0])
        eq2 = fit_math(r"r_i=\sum_{j=0}^{M-1}c_{ij}", scale=0.28, max_width=3.5).move_to([2.65, 1.65, 0])
        cells = []
        size = 0.38
        matrix = VGroup()
        pattern = [
            [0, 1, 1, 0, 1],
            [0, 0, 1, 0, 1],
            [0, 0, 0, 0, 1],
            [1, 1, 1, 0, 1],
            [0, 0, 0, 0, 0],
        ]
        for r in range(5):
            row = []
            for c in range(5):
                val = pattern[r][c]
                color = TEXT_ACCENT if val else TEXT_MUTED
                rect = Rectangle(width=size, height=size, stroke_color=TEXT_MUTED, stroke_width=0.8, fill_color=color, fill_opacity=0.24 if val else 0.04)
                txt = body_text(str(val), size=13, color=TEXT_PRIMARY if val else TEXT_MUTED).move_to(rect.get_center())
                cell = VGroup(rect, txt)
                cell.move_to([(c - 2) * size * 1.15, (2 - r) * size * 1.15, 0])
                row.append(cell)
                matrix.add(cell)
            cells.append(row)
        matrix.move_to([-1.9, -0.32, 0])
        rank_boxes = VGroup()
        sums = [3, 2, 1, 4, 0]
        for r, s in enumerate(sums):
            box = small_register("rank", str(s), width=0.60)
            box.move_to([1.45, matrix.get_top()[1] - r * size * 1.15 - 0.20, 0])
            rank_boxes.add(box)
        row_arrows = VGroup(
            *[
                Arrow(
                    cells[r][-1].get_right() + 0.25 * RIGHT,
                    rank_boxes[r].get_left() + 0.10 * LEFT,
                    buff=0,
                    stroke_color=TEXT_MUTED,
                    max_tip_length_to_length_ratio=0.12,
                )
                for r in range(5)
            ]
        )
        note = fit_math(
            r"\text{Tie-breaking can be folded into }c_{ij}.",
            scale=0.20,
            max_width=6.0,
            color=TEXT_MUTED,
        ).move_to([0, -2.35, 0])

        self.play(FadeIn(heading), FadeIn(eq1), FadeIn(eq2), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(matrix), run_time=0.55 / ANIM_SPEED)
        self.play(LaggedStart(*[Create(a) for a in row_arrows], lag_ratio=0.08), LaggedStart(*[FadeIn(b) for b in rank_boxes], lag_ratio=0.08), run_time=0.70 / VISUAL_SPEED)
        self.play(FadeIn(note), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

    # === 32. Sorting caveat ============================================
    def _slide_sorting_caveat(self) -> None:
        self.begin_slide(section="Ranking")

        heading = self._heading("Comparison sorting still has a lower bound")
        layers = []
        xs = [-4.0, -2.6, -1.2, 0.2, 1.6, 3.0]
        ys = [1.0, 0.55, 0.10, -0.35, -0.80]
        for x in xs:
            col = VGroup(*[Dot([x, y, 0], radius=0.035, color=TEXT_MUTED) for y in ys])
            layers.append(col)
        wires = VGroup()
        for y in ys:
            wires.add(Line([xs[0], y, 0], [xs[-1], y, 0], stroke_color=TEXT_MUTED, stroke_width=0.8).set_opacity(0.6))
        comps = VGroup()
        for k, x in enumerate(xs[1:-1]):
            pairs = [(0, 1), (2, 3)] if k % 2 == 0 else [(1, 2), (3, 4)]
            for a, b in pairs:
                comps.add(Line([x, ys[a], 0], [x, ys[b], 0], stroke_color=TEXT_ACCENT, stroke_width=2.0))
        lb = fit_math(r"\Omega(M\log M)\ \text{comparisons}", scale=0.38, max_width=5.5, color=COLOR_HIGHLIGHT).move_to([0, -1.75, 0])
        cite = body_text("Shi: quantum comparison sorting lower bound.", size=18, color=TEXT_MUTED).move_to([0, -2.45, 0])

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(wires), LaggedStart(*[FadeIn(col) for col in layers], lag_ratio=0.05), run_time=0.45 / ANIM_SPEED)
        self.play(LaggedStart(*[Create(c) for c in comps], lag_ratio=0.05), run_time=0.75 / VISUAL_SPEED)
        self.play(FadeIn(lb), FadeIn(cite), run_time=0.45 / ANIM_SPEED)
        self.wait(0.5)

    # === 33. Warning detector ==========================================
    def _slide_warning_detector(self) -> None:
        self.begin_slide(section="Collision")

        heading = self._heading("Collision finding asks for a repeated value")
        values = ["7", "2", "5", "9", "5", "1", "8"]
        registers = VGroup(
            *[
                VGroup(
                    fit_math(rf"x_{{{i}}}", scale=0.10, max_width=0.45, color=TEXT_MUTED),
                    small_register("", value, width=0.72),
                ).arrange(DOWN, buff=0.09)
                for i, value in enumerate(values)
            ]
        ).arrange(RIGHT, buff=0.20).move_to([0, 0.45, 0])
        collision = SurroundingRectangle(
            VGroup(registers[2], registers[4]),
            color=COLOR_HIGHLIGHT,
            buff=0.13,
            stroke_width=2.3,
        )
        q = fit_math(r"\exists i\neq j:\ x_i=x_j\;?", scale=0.32, max_width=4.4, color=TEXT_ACCENT).move_to([0, -1.05, 0])
        result = fit_math(r"\text{Ambainis: }O(N^{2/3})\text{ input queries}", scale=0.23, max_width=5.6, color=COLOR_HIGHLIGHT).move_to([0, -2.00, 0])
        note = body_text("The hard part is not comparing two stored values; it is finding the right two indices.", size=21, color=TEXT_MUTED).move_to([0, -2.58, 0])

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(LaggedStart(*[FadeIn(r) for r in registers], lag_ratio=0.07), run_time=0.70 / VISUAL_SPEED)
        self.play(Create(collision), FadeIn(q), run_time=0.55 / VISUAL_SPEED)
        self.play(FadeIn(result), FadeIn(note), run_time=0.40 / ANIM_SPEED)
        self.wait(0.5)

    # === 34. Binning ====================================================
    def _slide_binning(self) -> None:
        self.begin_slide(section="Collision")

        heading = self._heading("Grover over pairs still costs O(N)")
        pair_boxes = VGroup(
            *[small_register("", pair, width=0.92) for pair in ["(1,2)", "(1,3)", "(1,4)", "(2,3)", "(2,4)", "(3,4)"]]
        ).arrange_in_grid(rows=2, cols=3, buff=(0.18, 0.20)).move_to([-3.20, 0.15, 0])
        pair_label = body_text("search over pairs", size=24, color=TEXT_PRIMARY, weight="BOLD").next_to(pair_boxes, UP, buff=0.42)
        pair_count = fit_math(r"\binom N2=\Theta(N^2)", scale=0.27, max_width=3.2, color=TEXT_ACCENT).move_to([2.10, 0.85, 0])
        grover = fit_math(r"\sqrt{\Theta(N^2)}=O(N)", scale=0.31, max_width=3.6, color=COLOR_FALSE).move_to([2.10, -0.10, 0])
        verdict = body_text("So the trick cannot be: just Grover over all pairs.", size=27, color=COLOR_HIGHLIGHT, weight="BOLD").move_to([0, -1.85, 0])
        note = body_text("Ambainis changes the search object: pair -> cached subset.", size=21, color=TEXT_MUTED).move_to([0, -2.50, 0])
        arrow = Arrow(pair_boxes.get_right() + 0.35 * RIGHT, pair_count.get_left() + 0.15 * LEFT, buff=0, stroke_color=TEXT_MUTED)

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(pair_label), FadeIn(pair_boxes), Create(arrow), FadeIn(pair_count), run_time=0.65 / VISUAL_SPEED)
        self.play(FadeIn(grover), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(verdict), FadeIn(note), run_time=0.45 / ANIM_SPEED)
        self.wait(0.5)

    # === 35. Labeled collision =========================================
    def _slide_labeled_collision(self) -> None:
        self.begin_slide(section="Collision")

        heading = self._heading("Key idea: walk with a cached subset")
        room = Rectangle(width=5.30, height=1.55, stroke_color=TEXT_ACCENT, stroke_width=1.9, fill_color=TEXT_ACCENT, fill_opacity=0.05).move_to([0, 0.55, 0])
        people = VGroup(*[small_register("", item, width=0.78) for item in ["2", "5", "9", "13", "...", "r"]]).arrange(RIGHT, buff=0.12).move_to(room.get_center() + 0.24 * UP)
        values = VGroup(
            *[
                math_register(item, width=0.78, scale=0.13)
                for item in [r"x_2", r"x_5", r"x_9", r"x_{13}", r"\cdots", r"x_r"]
            ]
        ).arrange(RIGHT, buff=0.12).move_to(room.get_center() + 0.38 * DOWN)
        room_label = body_text("one vertex = subset plus queried value table", size=22, color=TEXT_PRIMARY, weight="BOLD").next_to(room, UP, buff=0.35)
        cost = VGroup(
            body_text("setup: query r values once", size=24, color=TEXT_PRIMARY),
            body_text("walk step: replace one index", size=24, color=TEXT_PRIMARY),
            body_text("update: reuse r-1 values; query only the newcomer", size=24, color=COLOR_HIGHLIGHT, weight="BOLD"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.28).move_to([0, -1.75, 0])

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(room_label), FadeIn(room), FadeIn(people), FadeIn(values), run_time=0.65 / VISUAL_SPEED)
        self.play(LaggedStart(*[FadeIn(line) for line in cost], lag_ratio=0.15), run_time=0.80 / VISUAL_SPEED)
        self.wait(0.5)

    # === 36. Element distinctness ======================================
    def _slide_element_distinctness(self) -> None:
        self.begin_slide(section="Collision")

        heading = self._heading("Johnson graph: one step changes one element")
        left = VGroup(*[small_register("", item, width=0.72) for item in ["1", "2", "5", "7"]]).arrange(RIGHT, buff=0.10).move_to([-3.00, 0.62, 0])
        right = VGroup(*[small_register("", item, width=0.72) for item in ["1", "5", "7", "9"]]).arrange(RIGHT, buff=0.10).move_to([3.00, 0.62, 0])
        l_label = fit_math(r"S=\{1,2,5,7\}", scale=0.22, max_width=2.5, color=TEXT_PRIMARY).next_to(left, UP, buff=0.32)
        r_label = fit_math(r"T=S-\{2\}+\{9\}", scale=0.22, max_width=3.0, color=TEXT_PRIMARY).next_to(right, UP, buff=0.32)
        replace = Arrow(left.get_right() + 0.28 * RIGHT, right.get_left() + 0.28 * LEFT, buff=0, stroke_color=TEXT_MUTED)
        replace_label = body_text("edge in J(N,r)", size=22, color=TEXT_ACCENT, weight="BOLD").next_to(replace, DOWN, buff=0.22)
        rule = fit_math(r"\text{vertices: }S\subseteq[N], |S|=r\qquad \text{edges: }T=S-\{a\}+\{b\}", scale=0.22, max_width=9.4, color=TEXT_ACCENT).move_to([0, -0.85, 0])
        marked = fit_math(r"S\text{ is marked}\Longleftrightarrow \exists i\neq j\in S:\ x_i=x_j", scale=0.22, max_width=7.8, color=COLOR_HIGHLIGHT).move_to([0, -1.80, 0])
        note = body_text("We move locally so the stored value table can be updated cheaply.", size=21, color=TEXT_MUTED).move_to([0, -2.48, 0])

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(l_label), FadeIn(left), Create(replace), FadeIn(r_label), FadeIn(right), run_time=0.75 / VISUAL_SPEED)
        self.play(FadeIn(replace_label), FadeIn(rule), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(marked), FadeIn(note), run_time=0.45 / ANIM_SPEED)
        self.wait(0.5)

    # === 37. Collision oracle model ====================================
    def _slide_collision_oracle_model(self) -> None:
        self.begin_slide(section="Collision")

        heading = self._heading("Only the value oracle is primitive")
        formula = fit_math(
            r"O_x:\left|i\right\rangle\left|y\right\rangle\mapsto"
            r"\left|i\right\rangle\left|y\oplus x_i\right\rangle",
            scale=0.25,
            max_width=8.6,
            color=TEXT_ACCENT,
        ).move_to([0, 1.55, 0])

        left_inputs = VGroup(
            math_register(r"\left|i\right\rangle", width=1.30, scale=0.18),
            math_register(r"\left|y\right\rangle", width=1.30, scale=0.18),
        ).arrange(DOWN, buff=0.25).move_to([-4.35, 0.15, 0])
        oracle = oracle_box(r"O_x", width=1.55, height=1.15, math_label=True).move_to([-2.55, 0.15, 0])
        outputs = VGroup(
            math_register(r"\left|i\right\rangle", width=1.55, scale=0.18),
            math_register(r"\left|y\oplus x_i\right\rangle", width=1.90, scale=0.15),
        ).arrange(DOWN, buff=0.25).move_to([-0.55, 0.15, 0])
        arrows = VGroup(
            Arrow(left_inputs.get_right() + 0.10 * RIGHT, oracle.get_left() + 0.08 * LEFT, buff=0, stroke_color=TEXT_MUTED),
            Arrow(oracle.get_right() + 0.08 * RIGHT, outputs.get_left() + 0.10 * LEFT, buff=0, stroke_color=TEXT_MUTED),
        )

        not_given = oracle_box(r"R_{\rm coll}", width=1.95, height=1.15, math_label=True).move_to([3.05, 0.15, 0])
        x1 = Line(not_given.get_left() + 0.20 * UP, not_given.get_right() + 0.20 * DOWN, stroke_color=COLOR_FALSE, stroke_width=4)
        x2 = Line(not_given.get_left() + 0.20 * DOWN, not_given.get_right() + 0.20 * UP, stroke_color=COLOR_FALSE, stroke_width=4)
        not_label = body_text("not given as input", size=21, color=COLOR_FALSE, weight="BOLD").next_to(not_given, DOWN, buff=0.30)
        allowed = body_text("one call loads one indexed value", size=23, color=TEXT_PRIMARY).move_to([-2.45, -1.35, 0])
        note = body_text("A collision marker must be constructed after the subset values are cached.", size=23, color=COLOR_HIGHLIGHT, weight="BOLD").move_to([0, -2.25, 0])

        self.play(FadeIn(heading), FadeIn(formula), run_time=0.40 / ANIM_SPEED)
        self.play(FadeIn(left_inputs), FadeIn(oracle), Create(arrows), FadeIn(outputs), run_time=0.65 / VISUAL_SPEED)
        self.play(FadeIn(not_given), Create(x1), Create(x2), FadeIn(not_label), FadeIn(allowed), run_time=0.65 / VISUAL_SPEED)
        self.play(FadeIn(note), run_time=0.40 / ANIM_SPEED)
        self.wait(0.5)

    # === 38. Collision subset idea =====================================
    def _slide_collision_subset_idea(self) -> None:
        self.begin_slide(section="Collision")

        heading = self._heading("One walk vertex carries registers")
        rows = [
            ("subset indices", r"\left|i_1,\ldots,i_r\right\rangle", r"r\log N"),
            ("cached values", r"\left|x_{i_1},\ldots,x_{i_r}\right\rangle", r"rm"),
            ("coin move", r"\left|t,b\right\rangle", r"\log r+\log N"),
            ("work", r"\left|0\cdots0\right\rangle", r"\text{scratch}"),
        ]
        table = VGroup()
        for name, reg, cost in rows:
            left = body_text(name, size=21, color=TEXT_PRIMARY, weight="BOLD")
            mid = math_register(reg, width=4.30, scale=0.14)
            right = fit_math(cost, scale=0.15, max_width=1.7, color=TEXT_MUTED)
            table.add(VGroup(left, mid, right).arrange(RIGHT, buff=0.38))
        table.arrange(DOWN, aligned_edge=LEFT, buff=0.27).move_to([0, 0.08, 0])
        summary = fit_math(r"O(r(\log N+m))\text{ qubits plus workspace}", scale=0.23, max_width=6.4, color=COLOR_HIGHLIGHT).move_to([0, -2.10, 0])

        self.play(FadeIn(heading), run_time=0.40 / ANIM_SPEED)
        self.play(LaggedStart(*[FadeIn(row) for row in table], lag_ratio=0.10), run_time=0.90 / VISUAL_SPEED)
        self.play(FadeIn(summary), run_time=0.45 / ANIM_SPEED)
        self.wait(0.5)

    # === 39. Collision registers =======================================
    def _slide_collision_registers(self) -> None:
        self.begin_slide(section="Collision")

        heading = self._heading("Setup costs r queries; one move costs O(1) queries")
        start = VGroup(
            body_text("setup", size=22, color=TEXT_MUTED),
            math_register(r"\left|S\right\rangle\left|0\right\rangle", width=2.15, scale=0.14),
        ).arrange(DOWN, buff=0.14).move_to([-3.85, 1.10, 0])
        query_r = pipeline_node("query r\nvalues", color=TEXT_ACCENT, width=1.70).move_to([0, 1.10, 0])
        loaded = VGroup(
            body_text("cached vertex", size=22, color=TEXT_MUTED),
            math_register(r"\left|S\right\rangle\left|D_S\right\rangle", width=2.15, scale=0.14),
        ).arrange(DOWN, buff=0.14).move_to([3.85, 1.10, 0])
        top_arrows = VGroup(
            Arrow(start.get_right() + 0.15 * RIGHT, query_r.get_left() + 0.08 * LEFT, buff=0, stroke_color=TEXT_MUTED),
            Arrow(query_r.get_right() + 0.08 * RIGHT, loaded.get_left() + 0.15 * LEFT, buff=0, stroke_color=TEXT_MUTED),
        )

        before = VGroup(*[small_register("", item, width=0.66) for item in ["2", "5", "9"]]).arrange(RIGHT, buff=0.10).move_to([-3.35, -0.45, 0])
        before_vals = VGroup(*[math_register(item, width=0.76, scale=0.13) for item in [r"x_2", r"x_5", r"x_9"]]).arrange(RIGHT, buff=0.08).next_to(before, DOWN, buff=0.17)
        after = VGroup(*[small_register("", item, width=0.66) for item in ["2", "13", "9"]]).arrange(RIGHT, buff=0.10).move_to([3.35, -0.45, 0])
        after_vals = VGroup(*[math_register(item, width=0.76, scale=0.13) for item in [r"x_2", r"x_{13}", r"x_9"]]).arrange(RIGHT, buff=0.08).next_to(after, DOWN, buff=0.17)
        old_box = SurroundingRectangle(VGroup(before[1], before_vals[1]), color=COLOR_FALSE, buff=0.08, stroke_width=2.0)
        new_box = SurroundingRectangle(VGroup(after[1], after_vals[1]), color=COLOR_TRUE, buff=0.08, stroke_width=2.0)
        update = VGroup(
            pipeline_node("unquery\nold value", color=TEXT_MUTED, width=1.70),
            pipeline_node("swap\nindex", color=TEXT_ACCENT, width=1.45),
            pipeline_node("query\nnew value", color=COLOR_HIGHLIGHT, width=1.70),
        ).arrange(DOWN, buff=0.12).move_to([0, -0.55, 0])
        arrows = VGroup(
            Arrow(before.get_right() + 0.20 * RIGHT, update.get_left() + 0.08 * LEFT, buff=0, stroke_color=TEXT_MUTED),
            Arrow(update.get_right() + 0.08 * RIGHT, after.get_left() + 0.20 * LEFT, buff=0, stroke_color=TEXT_MUTED),
        )
        note = body_text("Clean reversible update uses 1 or 2 value-oracle calls, still O(1), not r.", size=22, color=COLOR_HIGHLIGHT, weight="BOLD").move_to([0, -2.55, 0])

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(start), FadeIn(query_r), Create(top_arrows), FadeIn(loaded), run_time=0.75 / VISUAL_SPEED)
        self.play(FadeIn(before), FadeIn(before_vals), Create(old_box), run_time=0.45 / VISUAL_SPEED)
        self.play(FadeIn(update), Create(arrows[0]), Create(arrows[1]), FadeIn(after), FadeIn(after_vals), Create(new_box), run_time=0.80 / VISUAL_SPEED)
        self.play(FadeIn(note), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

    # === 40. Collision setup ===========================================
    def _slide_collision_setup(self) -> None:
        self.begin_slide(section="Collision")

        heading = self._heading("Marking is not a magic oracle")
        table = VGroup(
            *[
                math_register(v, width=0.88, scale=0.12)
                for v in [r"x_2=4", r"x_5=1", r"x_9=4", r"x_{13}=7"]
            ]
        ).arrange(RIGHT, buff=0.14).move_to([0, 0.80, 0])
        highlight = VGroup(
            SurroundingRectangle(table[0], color=COLOR_HIGHLIGHT, buff=0.09, stroke_width=2.2),
            SurroundingRectangle(table[2], color=COLOR_HIGHLIGHT, buff=0.09, stroke_width=2.2),
        )
        data_label = fit_math(r"D_S\text{ is already cached}", scale=0.22, max_width=3.4, color=TEXT_ACCENT).next_to(table, UP, buff=0.35)
        compare = pipeline_node("compare\nstored values", color=TEXT_ACCENT, width=2.20).move_to([-2.60, -0.55, 0])
        flag = pipeline_node("collision\nflag", color=COLOR_HIGHLIGHT, width=1.85).move_to([0, -0.55, 0])
        phase = pipeline_node("phase\nflip", color=COLOR_HIGHLIGHT, width=1.55).move_to([2.55, -0.55, 0])
        flow = VGroup(
            Arrow(compare.get_right() + 0.10 * RIGHT, flag.get_left() + 0.08 * LEFT, buff=0, stroke_color=TEXT_MUTED),
            Arrow(flag.get_right() + 0.08 * RIGHT, phase.get_left() + 0.10 * LEFT, buff=0, stroke_color=TEXT_MUTED),
        )
        no_query = body_text("input queries: 0 during marking, because the values are already stored", size=22, color=COLOR_HIGHLIGHT, weight="BOLD").move_to([0, -1.75, 0])
        caveat = fit_math(r"\text{Gate caveat: naive pair checks cost }O(r^2m).", scale=0.17, max_width=6.4, color=TEXT_MUTED).move_to([0, -2.45, 0])

        self.play(FadeIn(heading), FadeIn(data_label), FadeIn(table), run_time=0.45 / ANIM_SPEED)
        self.play(Create(highlight), run_time=0.40 / VISUAL_SPEED)
        self.play(FadeIn(compare), Create(flow[0]), FadeIn(flag), Create(flow[1]), FadeIn(phase), run_time=0.75 / VISUAL_SPEED)
        self.play(FadeIn(no_query), FadeIn(caveat), run_time=0.45 / ANIM_SPEED)
        self.wait(0.5)

    # === 41. Collision marking =========================================
    def _slide_collision_marking(self) -> None:
        self.begin_slide(section="Collision")

        heading = self._heading("Local moves make spectral gap matter")
        complete = VGroup(
            body_text("Grover", size=25, color=TEXT_PRIMARY, weight="BOLD"),
            body_text("free mixing", size=21, color=TEXT_MUTED),
            fit_math(r"\delta=\Theta(1)", scale=0.22, max_width=2.1, color=TEXT_ACCENT),
        ).arrange(DOWN, buff=0.20).move_to([-3.50, 0.40, 0])
        local = VGroup(
            body_text("Quantum walk", size=25, color=TEXT_PRIMARY, weight="BOLD"),
            body_text("local graph moves", size=21, color=TEXT_MUTED),
            fit_math(r"\text{speed depends on }\delta", scale=0.20, max_width=3.0, color=COLOR_HIGHLIGHT),
        ).arrange(DOWN, buff=0.20).move_to([3.20, 0.40, 0])
        p_label = body_text("P is the one-step transition matrix", size=22, color=TEXT_PRIMARY, weight="BOLD").move_to([0, -0.80, 0])
        p_def = fit_math(r"P_{S,T}=\Pr[\text{one walk step sends }S\text{ to }T]", scale=0.18, max_width=7.4, color=TEXT_ACCENT).move_to([0, -1.20, 0])
        evolve = fit_math(r"\mu_{t+1}=\mu_t P,\qquad \delta=1-\lambda_1", scale=0.24, max_width=5.4, color=TEXT_PRIMARY).move_to([0, -1.78, 0])
        note = body_text("Spectral gap measures how fast the walk forgets its starting subset.", size=22, color=COLOR_HIGHLIGHT, weight="BOLD").move_to([0, -2.42, 0])
        arrow = Arrow(complete.get_right() + 0.25 * RIGHT, local.get_left() + 0.25 * LEFT, buff=0, stroke_color=TEXT_MUTED)

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(complete), Create(arrow), FadeIn(local), run_time=0.70 / VISUAL_SPEED)
        self.play(FadeIn(p_label), FadeIn(p_def), FadeIn(evolve), run_time=0.55 / ANIM_SPEED)
        self.play(FadeIn(note), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

    # === 42. Johnson graph walk update =================================
    def _slide_johnson_walk_update(self) -> None:
        self.begin_slide(section="Collision")

        heading = self._heading("Two numbers control the walk search")
        eps_title = body_text("marked fraction", size=25, color=TEXT_PRIMARY, weight="BOLD").move_to([-3.20, 1.05, 0])
        eps_formula = fit_math(r"\varepsilon=\Pr[a,b\in S]\approx \frac{r^2}{N^2}", scale=0.25, max_width=4.0, color=TEXT_ACCENT).move_to([-3.20, 0.25, 0])
        eps_note = body_text("collision pair must both be in the room", size=19, color=TEXT_MUTED).move_to([-3.20, -0.55, 0])
        delta_title = body_text("Johnson graph gap", size=25, color=TEXT_PRIMARY, weight="BOLD").move_to([3.20, 1.05, 0])
        delta_formula = fit_math(r"\delta=\Theta(1/r)", scale=0.30, max_width=3.2, color=COLOR_HIGHLIGHT).move_to([3.20, 0.25, 0])
        delta_note = body_text("one stored element survives about r steps", size=19, color=TEXT_MUTED).move_to([3.20, -0.55, 0])
        divider = Line([0, 1.40, 0], [0, -1.05, 0], stroke_color=TEXT_MUTED, stroke_width=1.2).set_opacity(0.55)
        intuition = body_text("More marked vertices help; faster mixing helps.", size=25, color=COLOR_HIGHLIGHT, weight="BOLD").move_to([0, -1.88, 0])

        self.play(FadeIn(heading), Create(divider), run_time=0.40 / ANIM_SPEED)
        self.play(FadeIn(eps_title), FadeIn(eps_formula), FadeIn(eps_note), run_time=0.55 / VISUAL_SPEED)
        self.play(FadeIn(delta_title), FadeIn(delta_formula), FadeIn(delta_note), run_time=0.55 / VISUAL_SPEED)
        self.play(FadeIn(intuition), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

    # === 43. Search operator ===========================================
    def _slide_walk_search_operator(self) -> None:
        self.begin_slide(section="Collision")

        heading = self._heading("Quantum walk search cost")
        theorem = fit_math(r"\text{steps}\approx O\!\left(\frac{1}{\sqrt{\varepsilon\delta}}\right)", scale=0.32, max_width=5.4, color=TEXT_ACCENT).move_to([0, 1.25, 0])
        sub = fit_math(
            r"\varepsilon\approx \frac{r^2}{N^2},\quad \delta\approx \frac{1}{r}",
            scale=0.28,
            max_width=5.4,
            color=TEXT_PRIMARY,
        ).move_to([0, 0.25, 0])
        result = fit_math(
            r"\frac{1}{\sqrt{\varepsilon\delta}}"
            r"\approx \frac{1}{\sqrt{(r^2/N^2)(1/r)}}"
            r"=\frac{N}{\sqrt r}",
            scale=0.31,
            max_width=8.8,
            color=COLOR_HIGHLIGHT,
        ).move_to([0, -0.70, 0])
        loop = VGroup(
            pipeline_node("phase flip\nmarked S", color=COLOR_HIGHLIGHT, width=2.35),
            pipeline_node("Johnson\nwalk step", color=TEXT_ACCENT, width=2.25),
        ).arrange(RIGHT, buff=0.45).move_to([0, -1.80, 0])
        arrows = VGroup(
            Arrow(loop[0].get_right() + 0.06 * RIGHT, loop[1].get_left() + 0.06 * LEFT, buff=0, stroke_color=TEXT_MUTED),
            Arrow(loop[1].get_bottom() + 0.06 * DOWN, loop[0].get_bottom() + 0.06 * DOWN, buff=0.12, stroke_color=TEXT_MUTED),
        )

        self.play(FadeIn(heading), FadeIn(theorem), run_time=0.40 / ANIM_SPEED)
        self.play(FadeIn(sub), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(result), run_time=0.55 / VISUAL_SPEED)
        self.play(FadeIn(loop), Create(arrows), run_time=0.55 / VISUAL_SPEED)
        self.wait(0.5)

    # === 44. Collision query complexity ================================
    def _slide_collision_query_complexity(self) -> None:
        self.begin_slide(section="Collision")

        heading = self._heading("Balance setup cost and walk cost")
        setup = VGroup(
            body_text("setup", size=24, color=TEXT_MUTED),
            fit_math(r"r", scale=0.42, max_width=1.3, color=TEXT_PRIMARY),
        ).arrange(DOWN, buff=0.16).move_to([-3.25, 0.95, 0])
        steps = VGroup(
            body_text("walk steps", size=24, color=TEXT_MUTED),
            fit_math(r"\Theta\!\left(\frac{N}{\sqrt r}\right)", scale=0.34, max_width=2.6, color=TEXT_PRIMARY),
        ).arrange(DOWN, buff=0.16).move_to([3.25, 0.95, 0])
        plus = body_text("+", size=36, color=TEXT_MUTED).move_to([0, 0.95, 0])
        total = fit_math(
            r"\text{queries}=O\!\left(r+\frac{N}{\sqrt r}\right)",
            scale=0.34,
            max_width=5.8,
            color=TEXT_ACCENT,
        ).move_to([0, 0.00, 0])
        balance = fit_math(r"r=\frac{N}{\sqrt r}\quad\Rightarrow\quad r=N^{2/3}", scale=0.32, max_width=6.0, color=COLOR_HIGHLIGHT).move_to([0, -0.85, 0])
        result_box = Rectangle(width=4.15, height=0.84, stroke_color=COLOR_HIGHLIGHT, stroke_width=2.2, fill_color=COLOR_HIGHLIGHT, fill_opacity=0.08).move_to([0, -1.45, 0])
        result = fit_math(r"O(N^{2/3})\text{ queries}", scale=0.32, max_width=3.5, color=COLOR_HIGHLIGHT).move_to(result_box.get_center())
        caveat = VGroup(
            fit_math(r"\text{Query complexity only.}", scale=0.15, max_width=3.2, color=TEXT_MUTED),
            fit_math(r"\text{Naive gates cost more; efficient versions maintain counters and data structures.}", scale=0.13, max_width=7.0, color=TEXT_MUTED),
        ).arrange(DOWN, buff=0.08).move_to([0, -2.42, 0])

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(setup), FadeIn(plus), FadeIn(steps), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(total), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(balance), run_time=0.45 / ANIM_SPEED)
        self.play(Create(result_box), FadeIn(result), FadeIn(caveat), run_time=0.50 / VISUAL_SPEED)
        self.wait(0.5)

    # === 45. Pipeline summary ==========================================
    def _slide_pipeline_summary(self) -> None:
        self.begin_slide(section="Closing")

        heading = self._heading("Core pipeline: similarity to decision")
        specs = [
            ("data", "test + labeled library", False),
            ("Swap Test", r"p_j=\frac{1+F_j}{2}", True),
            ("QADC", r"\left|j\right\rangle\left|\widetilde F_j\right\rangle", True),
            ("Comparator", r"[\widetilde F_i>\widetilde F_j]", True),
            ("k-NN vote", "top-k majority", False),
        ]
        xs = [-5.20, -2.60, 0.0, 2.60, 5.20]
        nodes = VGroup()
        for (label, content, is_math), x in zip(specs, xs):
            color = COLOR_HIGHLIGHT if label == "k-NN vote" else TEXT_ACCENT
            rect = Rectangle(
                width=2.00,
                height=1.34,
                stroke_color=color,
                stroke_width=1.8,
                fill_color=color,
                fill_opacity=0.07,
            ).move_to([x, 0.20, 0])
            chip = label_chip(label, color=color, width=1.70 if len(label) > 7 else 1.34, height=0.32, font_size=12)
            chip.move_to(rect.get_top() + 0.27 * DOWN)
            if is_math:
                formula = fit_math(content, scale=0.18, max_width=1.62, max_height=0.46, color=TEXT_PRIMARY)
            else:
                formula = body_text(content, size=20, color=TEXT_PRIMARY, weight="BOLD")
                if formula.width > 1.62:
                    formula.scale(1.62 / formula.width)
            formula.move_to(rect.get_center() + 0.23 * DOWN)
            nodes.add(VGroup(rect, chip, formula))
        arrows = VGroup(
            *[
                Arrow(
                    nodes[i].get_right() + 0.08 * RIGHT,
                    nodes[i + 1].get_left() + 0.08 * LEFT,
                    buff=0,
                    stroke_color=TEXT_MUTED,
                    max_tip_length_to_length_ratio=0.12,
                )
                for i in range(len(nodes) - 1)
            ]
        )
        primitive_note = body_text(
            "Sorting and element distinctness are separate primitive-algorithm examples after the core pipeline.",
            size=22,
            color=TEXT_MUTED,
        ).move_to([0, -1.65, 0])
        closing = body_text(
            "The classifier needs top-k and vote; the later primitives illustrate broader oracle-based design.",
            size=22,
            color=TEXT_ACCENT,
        ).move_to([0, -2.35, 0])

        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(nodes[0]), run_time=0.30 / ANIM_SPEED)
        for i, arrow in enumerate(arrows):
            self.play(Create(arrow), FadeIn(nodes[i + 1]), run_time=0.32 / ANIM_SPEED)
        self.play(FadeIn(primitive_note), FadeIn(closing), run_time=0.45 / ANIM_SPEED)
        self.wait(0.5)

    # === 38. Final sentence ============================================
    def _slide_final_sentence(self) -> None:
        self.begin_slide(section="Closing")

        lines = VGroup(
            body_text("Tomography asks: What is the whole state?", size=32, color=TEXT_MUTED),
            body_text("Quantum k-NN asks: Which labeled states is it closest to?", size=32, color=TEXT_ACCENT, weight="BOLD"),
            body_text("QADC and comparator oracles turn similarity into decisions.", size=30, color=TEXT_PRIMARY),
            body_text("Sorting and collision detection are separate primitive examples.", size=28, color=TEXT_MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.55).move_to([0, 0.30, 0])
        thanks = body_text("Thank you", size=28, color=TEXT_MUTED).move_to([0, -2.20, 0])

        self.play(LaggedStart(*[FadeIn(line) for line in lines], lag_ratio=0.30), run_time=0.90 / ANIM_SPEED)
        self.play(Indicate(lines[2], color=COLOR_HIGHLIGHT), run_time=0.80 / VISUAL_SPEED)
        self.play(FadeIn(thanks), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)


class Preview(Lecture5):
    """Render a single slide's final state as a static PNG for fast iteration."""

    def _save_slides(self, *args, **kwargs):  # type: ignore[override]
        return None

    def construct(self) -> None:
        target = int(os.environ.get("SLIDE", str(len(SLIDE_METHODS))))
        target = max(1, min(target, len(SLIDE_METHODS)))
        self.setup_lecture(author=AUTHOR, title=TITLE, total_pages=TOTAL_PAGES)
        if os.environ.get("FAST_PREVIEW", "").lower() in {"1", "true", "yes"}:
            self._current_page = target - 1
            getattr(self, SLIDE_METHODS[target - 1])()
            return
        for name in SLIDE_METHODS[:target]:
            getattr(self, name)()
