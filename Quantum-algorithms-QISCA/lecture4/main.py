"""Lecture 4 — random walks, satisfiability, and quantum walks.

Render and convert (run from this directory):

    python build.py

For per-slide preview during dev:

    SLIDE=8 ../../.venv/bin/manim -s -ql main.py Preview
"""
from __future__ import annotations

import os
from math import atan2, comb, cos, exp, pi, sin

from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    AddTextLetterByLetter,
    Arc,
    Arrow,
    Circle,
    Create,
    Dot,
    Ellipse,
    FadeIn,
    FadeOut,
    Indicate,
    LaggedStart,
    Line,
    Rectangle,
    SurroundingRectangle,
    Transform,
    VGroup,
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
    math,
)

AUTHOR = "Mingyu Lee"
TITLE = "Lecture 4"

SLIDE_METHODS = (
    "_slide_title",
    "_slide_welcome_back",
    "_slide_manim_experiment",
    "_slide_today",
    "_slide_random_walk",
    "_slide_so_what",
    "_slide_random_walk_math",
    "_slide_two_sat",
    "_slide_two_sat_assignment",
    "_slide_classical_solver",
    "_slide_schoning",
    "_slide_schoning_trace",
    "_slide_hamming_walk",
    "_slide_proof",
    "_slide_three_sat_transition",
    "_slide_three_sat_drift",
    "_slide_three_sat_trace",
    "_slide_three_sat_runtime",
    "_slide_quantum_bridge",
    "_slide_ctqw_equation",
    "_slide_ctqw_properties",
    "_slide_quantum_1d_setup",
    "_slide_ballistic_vs_diffusive",
    "_slide_plane_wave_shift",
    "_slide_group_velocity",
    "_slide_glued_trees_bridge",
    "_slide_glued_trees_graph",
    "_slide_glued_trees_cycle",
    "_slide_black_box_access",
    "_slide_classical_glued_trees_failure",
    "_slide_hidden_columns",
    "_slide_column_states",
    "_slide_column_invariance",
    "_slide_reduced_1d_walk",
    "_slide_quantum_vs_classical_columns",
    "_slide_exponential_separation",
    "_slide_quantum_walk_closing",
)
# Extra proof slides that live inside existing methods but should be counted as
# real footer pages. These are not animation-only beats; they carry new proof
# content.
EXTRA_PROOF_PAGES = 26
TOTAL_PAGES = len(SLIDE_METHODS) + EXTRA_PROOF_PAGES

MAJOR_SECTION_BY_SECTION = {
    "": "Intro",
    "Welcome": "Intro",
    "Today": "Intro",
    "Motivation": "Random Walk",
    "2-SAT": "Random Walk",
    "3-SAT": "Random Walk",
    "Bridge": "Quantum Walk",
    "CTQW": "Quantum Walk",
    "Ballistic": "Quantum Walk",
    "Glued Trees": "Quantum Walk",
    "Column Subspace": "Quantum Walk",
    "Closing": "Quantum Walk",
    "Quantum Walk": "Quantum Walk",
}


class Lecture4(LectureScene):
    def begin_slide(
        self,
        *,
        section: str | None = None,
        major_section: str | None = None,
        clear: bool = True,
        advance_page: bool | None = None,
    ) -> None:
        if major_section is None and section is not None:
            major_section = MAJOR_SECTION_BY_SECTION.get(
                section,
                section or "Intro",
            )
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

    # === Slide 1: Title =================================================
    def _slide_title(self) -> None:
        self.begin_slide(section="")

        title = body_text("Lecture 4", size=72, weight="BOLD")
        subtitle = body_text(
            "Random walks, satisfiability, and quantum walks",
            size=28,
            color=TEXT_MUTED,
        )
        subtitle.next_to(title, DOWN, buff=0.4)
        title_group = VGroup(title, subtitle).move_to([0, 1.0, 0])

        author = body_text("Mingyu Lee", size=28)
        affiliation = body_text(
            "Seoul National University", size=22, color=TEXT_MUTED
        )
        date = body_text("2026 Apr 30", size=20, color=TEXT_MUTED)
        author_block = (
            VGroup(author, affiliation, date)
            .arrange(DOWN, buff=0.2)
            .move_to([0, -1.4, 0])
        )

        self.play(FadeIn(title_group), run_time=0.4 / ANIM_SPEED)
        self.play(FadeIn(author_block), run_time=0.3 / ANIM_SPEED)
        self.wait(0.3 / ANIM_SPEED)

    # === Slide 2: Welcome back ==========================================
    def _slide_welcome_back(self) -> None:
        self.begin_slide(section="Welcome")

        heading = body_text("Welcome back", size=52, weight="BOLD").to_edge(
            UP, buff=0.9
        )

        bullet1 = body_text(
            "Lectures 1–3:  Grover, query complexity, min/max finding."
        )
        bullet2 = body_text(
            "Today:  random walks for SAT, then quantum walks."
        )
        bullets = (
            VGroup(bullet1, bullet2)
            .arrange(DOWN, aligned_edge=LEFT, buff=0.5)
            .move_to([0, 0.4, 0])
        )

        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)
        # FadeIn stagger instead of typewriter: the audience does not need to
        # read along character-by-character on a TOC-style intro slide. The
        # typewriter felt slow even at ANIM_SPEED=3.0.
        self.play(
            LaggedStart(
                *[FadeIn(b) for b in bullets],
                lag_ratio=0.4,
                run_time=0.6 / ANIM_SPEED,
            )
        )
        # 0.5s real-time so the build_static.py last-frame seek (-sseof -0.2)
        # lands after the FadeIn completes — otherwise the static PNG can
        # capture mid-animation.
        self.wait(0.5)

    # === Slide 3: An experiment with manim (conversational) =============
    def _slide_manim_experiment(self) -> None:
        self.begin_slide(section="Welcome")

        heading = body_text(
            "A small note before we start",
            size=44,
            weight="BOLD",
        ).to_edge(UP, buff=0.9)

        line1 = body_text(
            "You'll notice today's deck looks a little different.",
            size=26,
        )
        line2 = body_text(
            "Lectures 1 through 3 were Beamer; this one is manim-slides — first try.",
            size=26,
        )
        line3 = body_text(
            "Reason: a lot of what's coming up is motion — walks, distributions.",
            size=26,
        )
        line4 = body_text(
            "If something looks rough, please tell me. That's the experiment.",
            size=26,
            color=TEXT_ACCENT,
        )

        body = (
            VGroup(line1, line2, line3, line4)
            .arrange(DOWN, aligned_edge=LEFT, buff=0.5)
            .move_to([0, 0, 0])
        )

        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)
        self.play(
            LaggedStart(
                *[FadeIn(b) for b in body],
                lag_ratio=0.35,
                run_time=0.8 / ANIM_SPEED,
            )
        )
        self.wait(0.5)

    # === Slide 4: Today's outline =======================================
    def _slide_today(self) -> None:
        self.begin_slide(section="Today")

        heading = body_text("Today", size=52, weight="BOLD").to_edge(UP, buff=0.9)
        self.play(FadeIn(heading), run_time=0.5 / ANIM_SPEED)

        items = [
            ("First — ",       "classical random walks: diffusion and scale."),
            ("Then — ",        "2-SAT: a local walk becomes polynomial."),
            ("Next — ",        "3-SAT: the same idea needs exponential restarts."),
            ("Then — ",        "quantum walk: replace diffusion by wave propagation."),
            ("Finally — ",     "glued trees: an algorithmic speedup."),
        ]
        rows = []
        for prefix, body in items:
            p = body_text(prefix, size=26, color=TEXT_MUTED)
            b = body_text(body, size=26, color=TEXT_PRIMARY)
            rows.append(VGroup(p, b).arrange(RIGHT, buff=0.15))
        body_block = (
            VGroup(*rows)
            .arrange(DOWN, aligned_edge=LEFT, buff=0.42)
            .move_to([0, -0.05, 0])
        )

        for row in rows:
            self.play(FadeIn(row), run_time=0.3 / ANIM_SPEED)
        self.wait(0.5 / ANIM_SPEED)

    # === Slide 5: A coin-flip walk (Pascal lattice) =====================
    def _slide_random_walk(self) -> None:
        self.begin_slide(section="Motivation")

        heading = body_text(
            "A coin-flip walk", size=44, weight="BOLD"
        ).to_edge(UP, buff=0.7)
        rules = body_text(
            "Each step:  +1 with prob ½,  −1 with prob ½.",
            size=22,
            color=TEXT_MUTED,
        ).next_to(heading, DOWN, buff=0.3)

        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)
        self.play(FadeIn(rules), run_time=0.3 / ANIM_SPEED)

        h_spacing = 0.95
        v_spacing = 0.7
        y_top = 1.3
        steps = 4

        nodes: dict[tuple[int, int], tuple[Dot, object]] = {}
        for t in range(steps + 1):
            for x in range(-t, t + 1, 2):
                pos = [x * h_spacing, y_top - t * v_spacing, 0]
                dot = Dot(pos, color=TEXT_PRIMARY, radius=0.07)
                k = (t + x) // 2
                num = comb(t, k)
                den = 2 ** t
                lbl = body_text(f"{num}/{den}", size=14, color=TEXT_MUTED)
                lbl.next_to(dot, DOWN, buff=0.05)
                nodes[(t, x)] = (dot, lbl)

        edges_per_step: dict[int, list[Line]] = {}
        for t in range(1, steps + 1):
            edges: list[Line] = []
            for x in range(-t, t + 1, 2):
                child_pos = nodes[(t, x)][0].get_center()
                for parent_x in (x - 1, x + 1):
                    if (t - 1, parent_x) in nodes:
                        parent_pos = nodes[(t - 1, parent_x)][0].get_center()
                        edges.append(
                            Line(
                                parent_pos,
                                child_pos,
                                stroke_color=TEXT_MUTED,
                                stroke_width=1.0,
                            )
                        )
            edges_per_step[t] = edges

        dot0, label0 = nodes[(0, 0)]
        self.play(FadeIn(dot0), FadeIn(label0), run_time=0.5 / VISUAL_SPEED)

        for t in range(1, steps + 1):
            self.play(
                *[Create(e) for e in edges_per_step[t]],
                run_time=0.4 / VISUAL_SPEED,
            )
            anims = []
            for x in range(-t, t + 1, 2):
                d, lbl = nodes[(t, x)]
                anims.extend([FadeIn(d), FadeIn(lbl)])
            self.play(*anims, run_time=0.4 / VISUAL_SPEED)
        self.wait(0.6 / ANIM_SPEED)

    # === Slide 5b: Random walk scale ====================================
    def _slide_random_walk_math(self) -> None:
        """Quantitative anchor: a classical random walk spreads like sqrt(t)."""
        def fit_math(latex: str, *, scale: float, max_width: float, color=TEXT_PRIMARY):
            obj = math(latex, scale=scale, color=color)
            if obj.width > max_width:
                obj.scale(max_width / obj.width)
            return obj

        def step_chip(label: str, color: str) -> VGroup:
            box = Rectangle(
                width=0.64,
                height=0.42,
                stroke_color=color,
                stroke_width=2.0,
                fill_color=color,
                fill_opacity=0.08,
            )
            text = body_text(label, size=17, color=color)
            text.move_to(box.get_center())
            return VGroup(box, text)

        self.begin_slide(section="Motivation")

        heading = body_text(
            "How fast does it spread?",
            size=42,
            weight="BOLD",
        ).to_edge(UP, buff=0.7)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        setup = body_text(
            "A walk is a sum of small steps.",
            size=23,
            color=TEXT_MUTED,
        ).move_to([0, 1.95, 0])
        self.play(FadeIn(setup), run_time=0.35 / ANIM_SPEED)

        sum_eq = fit_math(
            r"X_t=\xi_1+\xi_2+\cdots+\xi_t",
            scale=0.26,
            max_width=4.0,
        ).move_to([-2.95, 0.85, 0])
        mean_eq = fit_math(
            r"\mathbb{E}[\xi_i]=0 \Rightarrow \mathbb{E}[X_t]=0",
            scale=0.20,
            max_width=4.0,
            color=TEXT_MUTED,
        ).move_to([-2.95, 0.15, 0])

        chips = VGroup(
            step_chip("+1", COLOR_VAR1),
            step_chip("-1", COLOR_VAR2),
            step_chip("+1", COLOR_VAR1),
            step_chip("+1", COLOR_VAR3),
            step_chip("-1", COLOR_VAR2),
            step_chip("+1", COLOR_VAR1),
        ).arrange(RIGHT, buff=0.16)
        chips.move_to([2.75, 0.55, 0])
        chip_label = body_text("one sample path", size=18, color=TEXT_MUTED)
        chip_label.next_to(chips, UP, buff=0.25)

        question = body_text(
            "Mean is zero.  Spread is the question.",
            size=23,
            color=TEXT_ACCENT,
        ).move_to([0, -1.45, 0])
        self.play(FadeIn(sum_eq), run_time=0.5 / ANIM_SPEED)
        self.play(FadeIn(mean_eq), run_time=0.4 / ANIM_SPEED)
        self.play(FadeIn(chip_label), FadeIn(chips), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(question), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

        # ---- Beat 2: variance adds -------------------------------------
        self.next_slide()
        self.begin_slide(section="Motivation", clear=False)

        var_one = fit_math(
            r"\mathrm{Var}(\xi_i)=1",
            scale=0.22,
            max_width=2.6,
        ).move_to([-2.95, -0.75, 0])
        var_reason = body_text(
            "independent steps: variances add",
            size=21,
            color=TEXT_MUTED,
        ).move_to([2.75, -0.75, 0])
        var_sum = fit_math(
            r"\mathrm{Var}(X_t)=1+\cdots+1=t",
            scale=0.24,
            max_width=4.8,
            color=TEXT_ACCENT,
        ).move_to([0, -1.95, 0])
        self.play(
            FadeOut(question),
            FadeIn(var_one),
            FadeIn(var_reason),
            run_time=0.45 / ANIM_SPEED,
        )
        self.play(FadeIn(var_sum), run_time=0.5 / ANIM_SPEED)
        self.wait(0.6)

        # ---- Beat 3: sqrt(t) spread ------------------------------------
        self.next_slide()
        self.begin_slide(section="Motivation", advance_page=False)

        heading = body_text(
            "Diffusive scaling",
            size=42,
            weight="BOLD",
        ).to_edge(UP, buff=0.7)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        std_eq = fit_math(
            r"\sigma(t)=\sqrt{t}",
            scale=0.28,
            max_width=3.2,
            color=TEXT_ACCENT,
        ).move_to([0, 1.55, 0])
        self.play(FadeIn(std_eq), run_time=0.5 / ANIM_SPEED)

        row_specs = [
            ("time  t", 0.82, COLOR_VAR1, "spread 1"),
            ("time  4t", 1.64, COLOR_VAR2, "spread 2"),
            ("time 16t", 3.28, COLOR_VAR3, "spread 4"),
        ]
        row_ys = [0.70, -0.05, -0.80]
        rows = []
        for (time_label, half_width, color, spread_label), y in zip(row_specs, row_ys):
            baseline = Line(
                [-3.55, y, 0],
                [3.55, y, 0],
                stroke_color=TEXT_MUTED,
                stroke_width=1.2,
            )
            origin_tick = Line(
                [0, y - 0.09, 0],
                [0, y + 0.09, 0],
                stroke_color=TEXT_MUTED,
                stroke_width=1.3,
            )
            spread = Line(
                [-half_width, y, 0],
                [half_width, y, 0],
                stroke_color=color,
                stroke_width=9.0,
            )
            left_tick = Line(
                [-half_width, y - 0.10, 0],
                [-half_width, y + 0.10, 0],
                stroke_color=color,
                stroke_width=2.0,
            )
            right_tick = Line(
                [half_width, y - 0.10, 0],
                [half_width, y + 0.10, 0],
                stroke_color=color,
                stroke_width=2.0,
            )
            time_text = body_text(time_label, size=20, color=color).move_to([-4.65, y, 0])
            spread_text = body_text(spread_label, size=20, color=color).move_to([4.55, y, 0])
            rows.append(
                VGroup(
                    baseline,
                    origin_tick,
                    spread,
                    left_tick,
                    right_tick,
                    time_text,
                    spread_text,
                )
            )

        zero = body_text("0", size=16, color=TEXT_MUTED).move_to([0, -1.12, 0])
        time_jump_1 = body_text("×4 time", size=16, color=TEXT_MUTED).move_to([-4.65, 0.33, 0])
        time_jump_2 = body_text("×4 time", size=16, color=TEXT_MUTED).move_to([-4.65, -0.43, 0])
        dist_jump_1 = body_text("×2 distance", size=16, color=TEXT_ACCENT).move_to([4.55, 0.33, 0])
        dist_jump_2 = body_text("×2 distance", size=16, color=TEXT_ACCENT).move_to([4.55, -0.43, 0])

        for row in rows:
            self.play(FadeIn(row), run_time=0.50 / VISUAL_SPEED)
        self.play(
            FadeIn(zero),
            FadeIn(time_jump_1),
            FadeIn(time_jump_2),
            FadeIn(dist_jump_1),
            FadeIn(dist_jump_2),
            run_time=0.45 / ANIM_SPEED,
        )

        takeaway = body_text(
            "To go twice as far, pay four times as many steps.",
            size=22,
            color=TEXT_PRIMARY,
        ).move_to([0, -2.35, 0])
        self.play(FadeIn(takeaway), run_time=0.45 / ANIM_SPEED)
        self.wait(0.6)

        # ---- Beat 4: invert the scale ----------------------------------
        self.next_slide()
        self.begin_slide(section="Motivation", advance_page=False)

        heading = body_text(
            "Invert the scale",
            size=42,
            weight="BOLD",
        ).to_edge(UP, buff=0.75)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        prompt = body_text(
            "To reach distance n:",
            size=23,
            color=TEXT_MUTED,
        ).move_to([0, 1.55, 0])

        line = Line(
            [-3.2, 0.45, 0],
            [3.2, 0.45, 0],
            stroke_color=TEXT_MUTED,
            stroke_width=2.0,
        )
        origin = Dot([-3.2, 0.45, 0], radius=0.055, color=TEXT_PRIMARY)
        target = Dot([3.2, 0.45, 0], radius=0.065, color=TEXT_ACCENT)
        origin_label = body_text("0", size=17, color=TEXT_MUTED).next_to(
            origin, DOWN, buff=0.16
        )
        target_label = body_text("n", size=20, color=TEXT_ACCENT).next_to(
            target, DOWN, buff=0.14
        )
        distance_arrow = Arrow(
            [-3.0, 0.88, 0],
            [3.0, 0.88, 0],
            buff=0,
            stroke_color=TEXT_ACCENT,
            stroke_width=3.0,
        )
        distance_label = body_text("distance n", size=19, color=TEXT_ACCENT)
        distance_label.next_to(distance_arrow, UP, buff=0.12)
        distance_picture = VGroup(
            line,
            origin,
            target,
            origin_label,
            target_label,
            distance_arrow,
            distance_label,
        )

        invert = fit_math(
            r"\sqrt{t}\sim n \quad\Rightarrow\quad t\sim n^2",
            scale=0.24,
            max_width=5.0,
        ).move_to([0, -0.85, 0])
        result = fit_math(
            r"\text{time to reach }n=\Theta(n^2)",
            scale=0.27,
            max_width=5.2,
            color=TEXT_ACCENT,
        ).move_to([0, -1.55, 0])
        bridge = body_text(
            "Now use this walk in practice:  2-SAT.",
            size=21,
            color=TEXT_PRIMARY,
        ).move_to([0, -2.15, 0])
        cliffhanger = body_text(
            "n² steps for distance n — friend or limit?  (We will return to this.)",
            size=20,
            color=TEXT_ACCENT,
        ).move_to([0, -2.67, 0])
        self.play(FadeIn(prompt), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(distance_picture), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(invert), run_time=0.5 / ANIM_SPEED)
        self.play(FadeIn(result), run_time=0.5 / ANIM_SPEED)
        self.play(FadeIn(bridge), run_time=0.45 / ANIM_SPEED)
        self.wait(0.4)
        self.play(FadeIn(cliffhanger), run_time=0.4 / ANIM_SPEED)
        self.wait(0.7)

    # === Slide 6: Why we care ===========================================
    def _slide_so_what(self) -> None:
        self.begin_slide(section="Motivation")

        heading = body_text("Why we care", size=48, weight="BOLD").to_edge(
            UP, buff=0.9
        )
        self.play(FadeIn(heading), run_time=0.5 / ANIM_SPEED)

        line1 = body_text(
            "Random walks model diffusion, mixing, exploration.",
            size=26,
        )
        line2 = body_text(
            "But here's the surprise — they also drive satisfiability search.",
            size=26,
        )
        line3 = body_text(
            "Warm-up:  a 2-SAT solver that just keeps flipping bits.",
            size=26,
            color=TEXT_ACCENT,
        )

        body = (
            VGroup(line1, line2, line3)
            .arrange(DOWN, aligned_edge=LEFT, buff=0.55)
            .move_to([0, 0, 0])
        )

        for row in body:
            self.play(AddTextLetterByLetter(row, time_per_char=0.02 / ANIM_SPEED))
        self.wait(0.5)

    # === Slide 7: 2-SAT problem =========================================
    def _slide_two_sat(self) -> None:
        self.begin_slide(section="2-SAT")

        heading = body_text("2-SAT", size=52, weight="BOLD").to_edge(UP, buff=0.9)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        intro = body_text(
            "n variables. m clauses. Each clause OR's two literals.",
            size=24,
        ).move_to([0, 1.7, 0])

        formula = math(
            r"(x_1 \lor x_2) \,\land\, (\lnot x_1 \lor x_3) \,\land\, (x_2 \lor \lnot x_3)",
            scale=0.35,
        ).move_to([0, 0.5, 0])

        detail = body_text(
            "n = 3, m = 3.",
            size=22,
            color=TEXT_MUTED,
        ).move_to([0, -0.5, 0])

        question = body_text(
            "Question:  is there an assignment satisfying every clause?",
            size=24,
            color=TEXT_ACCENT,
        ).move_to([0, -1.7, 0])

        self.play(FadeIn(intro), run_time=0.4 / ANIM_SPEED)
        self.play(FadeIn(formula), run_time=0.5 / ANIM_SPEED)
        self.play(FadeIn(detail), run_time=0.3 / ANIM_SPEED)
        self.play(FadeIn(question), run_time=0.5 / ANIM_SPEED)
        self.wait(0.6 / ANIM_SPEED)

    # === Slide 8: 2-SAT animated assignment (3 arrow-advanced sub-slides)
    def _slide_two_sat_assignment(self) -> None:
        # ---- Sub-slide 1 (page 8): color-code each variable ----
        self.begin_slide(section="2-SAT")

        heading = body_text(
            "Trying an assignment",
            size=44,
            weight="BOLD",
        ).to_edge(UP, buff=0.7)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        # Each variable gets a unique color so the audience can trace its
        # occurrences across the formula and link them to the boxes below.
        # Operators / parens stay in the base text color.
        clause_a = math(
            r"({\color[HTML]{06B6D4}x_1} \lor {\color[HTML]{A78BFA}x_2})",
            color=None,
            scale=0.32,
        )
        clause_b = math(
            r"(\lnot{\color[HTML]{06B6D4}x_1} \lor {\color[HTML]{FB923C}x_3})",
            color=None,
            scale=0.32,
        )
        clause_c = math(
            r"({\color[HTML]{A78BFA}x_2} \lor \lnot{\color[HTML]{FB923C}x_3})",
            color=None,
            scale=0.32,
        )
        sep1 = math(r"\land", scale=0.32, color=TEXT_MUTED)
        sep2 = math(r"\land", scale=0.32, color=TEXT_MUTED)
        formula_row = (
            VGroup(clause_a, sep1, clause_b, sep2, clause_c)
            .arrange(RIGHT, buff=0.3)
            .move_to([0, 1.6, 0])
        )
        self.play(FadeIn(formula_row), run_time=0.5 / ANIM_SPEED)

        def make_var_box(name: str, value: int, accent: str) -> VGroup:
            rect = Rectangle(
                width=1.2,
                height=1.2,
                stroke_color=accent,
                stroke_width=2.5,
            )
            value_text = body_text(
                str(value),
                size=44,
                color=TEXT_PRIMARY,
                weight="BOLD",
            ).move_to(rect.get_center())
            name_text = body_text(name, size=22, color=accent).next_to(
                rect, UP, buff=0.15
            )
            return VGroup(rect, name_text, value_text)

        box1 = make_var_box("x₁", 0, COLOR_VAR1)
        box2 = make_var_box("x₂", 0, COLOR_VAR2)
        box3 = make_var_box("x₃", 0, COLOR_VAR3)
        var_row = (
            VGroup(box1, box2, box3)
            .arrange(RIGHT, buff=0.7)
            .move_to([0, -0.6, 0])
        )
        self.play(FadeIn(var_row), run_time=0.4 / ANIM_SPEED)
        self.wait(0.6 / ANIM_SPEED)

        # ---- Sub-slide 2 (page 9): evaluate clauses for (0,0,0) ----
        self.next_slide()
        self.begin_slide(section="2-SAT", clear=False)

        # (0,0,0):  clause_a = 0∨0 = F,  clause_b = 1∨0 = T,  clause_c = 0∨1 = T
        mark_a = body_text("✗", size=36, color=COLOR_FALSE).next_to(
            clause_a, DOWN, buff=0.3
        )
        mark_b = body_text("✓", size=36, color=COLOR_TRUE).next_to(
            clause_b, DOWN, buff=0.3
        )
        mark_c = body_text("✓", size=36, color=COLOR_TRUE).next_to(
            clause_c, DOWN, buff=0.3
        )
        status = body_text(
            "(0, 0, 0) — one clause fails",
            size=22,
            color=COLOR_FALSE,
        ).move_to([0, -2.4, 0])

        self.play(
            FadeIn(mark_a),
            FadeIn(mark_b),
            FadeIn(mark_c),
            run_time=0.5 / ANIM_SPEED,
        )
        self.play(FadeIn(status), run_time=0.4 / ANIM_SPEED)
        self.wait(0.6 / ANIM_SPEED)

        # ---- Sub-slide 3 (page 10): flip x₂, all clauses satisfied ----
        self.next_slide()
        self.begin_slide(section="2-SAT", clear=False)

        rect2 = box2[0]
        val2 = box2[2]
        new_val2 = body_text(
            "1",
            size=44,
            color=TEXT_PRIMARY,
            weight="BOLD",
        ).move_to(val2.get_center())

        self.play(
            rect2.animate.set_stroke(color=COLOR_HIGHLIGHT, width=4.0),
            run_time=0.35 / VISUAL_SPEED,
        )
        self.play(
            FadeOut(val2),
            FadeIn(new_val2),
            run_time=0.45 / VISUAL_SPEED,
        )

        new_mark_a = body_text("✓", size=36, color=COLOR_TRUE).move_to(
            mark_a.get_center()
        )
        new_status = body_text(
            "(0, 1, 0) — all clauses satisfied",
            size=22,
            color=COLOR_TRUE,
        ).move_to(status.get_center())

        self.play(
            FadeOut(mark_a),
            FadeIn(new_mark_a),
            rect2.animate.set_stroke(color=COLOR_VAR2, width=2.5),
            FadeOut(status),
            FadeIn(new_status),
            run_time=0.55 / VISUAL_SPEED,
        )
        self.wait(0.7 / ANIM_SPEED)

    # === Slide 9: Classical solver (4 arrow-advanced sub-slides) ========
    def _slide_classical_solver(self) -> None:
        """Walk through the implication-graph + SCC algorithm step by step.

        Uses a fresh, smaller example —  (x_1 ∨ x_2) ∧ (¬x_1 ∨ ¬x_2) ∧
        (x_1 ∨ ¬x_2) — chosen because it produces non-trivial 2-element
        SCCs (so the SCC step has visual content) and a clean SAT verdict
        with assignment x_1=1, x_2=0 by reverse-topological selection.

        Layout: 4 literal nodes in two horizontal rows. Top row becomes
        SCC A = {x_1, ¬x_2}; bottom row becomes SCC B = {¬x_1, x_2};
        cross-row diagonals encode the inter-SCC edges (B → A in DAG order).
        """
        # ---- Sub-slide 1: formula → first clause becomes 2 edges ----
        self.begin_slide(section="2-SAT")

        heading = body_text(
            "Classically, this is solved",
            size=36,
            weight="BOLD",
        ).to_edge(UP, buff=0.4)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        # Color-coded formula. x_1 cyan, x_2 purple — same palette as slide 8
        # so the per-symbol identity carries across the deck.
        clause1 = math(
            r"({\color[HTML]{06B6D4}x_1} \lor {\color[HTML]{A78BFA}x_2})",
            color=None,
            scale=0.28,
        )
        clause2 = math(
            r"(\lnot{\color[HTML]{06B6D4}x_1} \lor \lnot{\color[HTML]{A78BFA}x_2})",
            color=None,
            scale=0.28,
        )
        clause3 = math(
            r"({\color[HTML]{06B6D4}x_1} \lor \lnot{\color[HTML]{A78BFA}x_2})",
            color=None,
            scale=0.28,
        )
        sep1 = math(r"\land", scale=0.28, color=TEXT_MUTED)
        sep2 = math(r"\land", scale=0.28, color=TEXT_MUTED)
        formula_row = (
            VGroup(clause1, sep1, clause2, sep2, clause3)
            .arrange(RIGHT, buff=0.3)
            .move_to([0, 2.15, 0])
        )
        self.play(FadeIn(formula_row), run_time=0.4 / ANIM_SPEED)

        caption = body_text(
            "Each clause becomes two implications.",
            size=22,
            color=TEXT_MUTED,
        ).move_to([0, 1.55, 0])
        self.play(FadeIn(caption), run_time=0.35 / ANIM_SPEED)

        # The rewrite rule itself, color-matched so a/b align with x_1/x_2.
        rule = math(
            r"({\color[HTML]{06B6D4}a} \lor {\color[HTML]{A78BFA}b}) \;\equiv\; "
            r"(\lnot{\color[HTML]{06B6D4}a} \to {\color[HTML]{A78BFA}b}) \,\land\, "
            r"(\lnot{\color[HTML]{A78BFA}b} \to {\color[HTML]{06B6D4}a})",
            color=None,
            scale=0.30,
        ).move_to([0, 0.9, 0])
        self.play(FadeIn(rule), run_time=0.5 / ANIM_SPEED)

        # 4 literal nodes — circle + label. Top row is SCC A, bottom SCC B.
        node_radius = 0.42

        def make_node(label: str, x: float, y: float, color: str) -> VGroup:
            circ = Circle(
                radius=node_radius,
                color=color,
                stroke_width=2.5,
            ).move_to([x, y, 0])
            lbl = body_text(label, size=24, color=color, weight="BOLD").move_to(
                circ.get_center()
            )
            return VGroup(circ, lbl)

        top_y, bot_y = -0.25, -1.95
        col_x = 1.7
        n_x1 = make_node("x₁", -col_x, top_y, COLOR_VAR1)
        n_nx2 = make_node("¬x₂", col_x, top_y, COLOR_VAR2)
        n_nx1 = make_node("¬x₁", -col_x, bot_y, COLOR_VAR1)
        n_x2 = make_node("x₂", col_x, bot_y, COLOR_VAR2)

        self.play(
            FadeIn(n_x1),
            FadeIn(n_nx2),
            FadeIn(n_nx1),
            FadeIn(n_x2),
            run_time=0.55 / VISUAL_SPEED,
        )

        # Highlight clause 1 — the box also serves as the "active clause"
        # marker that we'll Transform across sub-slides 1-2.
        active_box = SurroundingRectangle(
            clause1,
            color=COLOR_HIGHLIGHT,
            buff=0.08,
            stroke_width=2.5,
        )
        self.play(Create(active_box), run_time=0.4 / VISUAL_SPEED)

        # Edge helpers. Within-row pairs are bidirectional, so offset each
        # arrow ±0.1 perpendicular to the row to keep them readable.
        def row_arrow(
            start_node: VGroup,
            end_node: VGroup,
            offset: float,
        ) -> Arrow:
            s = start_node[0].get_center() + offset * UP
            e = end_node[0].get_center() + offset * UP
            return Arrow(
                s,
                e,
                buff=node_radius + 0.05,
                color=TEXT_PRIMARY,
                stroke_width=2.4,
                max_tip_length_to_length_ratio=0.07,
            )

        def cross_arrow(start_node: VGroup, end_node: VGroup) -> Arrow:
            return Arrow(
                start_node[0].get_center(),
                end_node[0].get_center(),
                buff=node_radius + 0.05,
                color=TEXT_PRIMARY,
                stroke_width=2.4,
                max_tip_length_to_length_ratio=0.05,
            )

        # Clause 1 (x_1 ∨ x_2) — implications: ¬x_1 → x_2  and  ¬x_2 → x_1.
        # ¬x_1 (BL) → x_2 (BR): bottom-row arrow, offset up.
        # ¬x_2 (TR) → x_1 (TL): top-row arrow, offset down.
        e_c1_a = row_arrow(n_nx1, n_x2, +0.12)
        e_c1_b = row_arrow(n_nx2, n_x1, -0.12)
        self.play(Create(e_c1_a), Create(e_c1_b), run_time=0.7 / VISUAL_SPEED)
        self.wait(0.5)

        # ---- Sub-slide 2: clauses 2 & 3 → all 6 edges, rule fades ----
        self.next_slide()
        self.begin_slide(section="2-SAT", clear=False)

        # Move the active-clause highlight to clause 2.
        box_c2 = SurroundingRectangle(
            clause2,
            color=COLOR_HIGHLIGHT,
            buff=0.08,
            stroke_width=2.5,
        )
        self.play(Transform(active_box, box_c2), run_time=0.4 / VISUAL_SPEED)

        # Clause 2 (¬x_1 ∨ ¬x_2) — implications: x_1 → ¬x_2  and  x_2 → ¬x_1.
        # x_1 (TL) → ¬x_2 (TR): top-row arrow, offset up.
        # x_2 (BR) → ¬x_1 (BL): bottom-row arrow, offset down.
        e_c2_a = row_arrow(n_x1, n_nx2, +0.12)
        e_c2_b = row_arrow(n_x2, n_nx1, -0.12)
        self.play(Create(e_c2_a), Create(e_c2_b), run_time=0.7 / VISUAL_SPEED)

        # Move highlight to clause 3.
        box_c3 = SurroundingRectangle(
            clause3,
            color=COLOR_HIGHLIGHT,
            buff=0.08,
            stroke_width=2.5,
        )
        self.play(Transform(active_box, box_c3), run_time=0.4 / VISUAL_SPEED)

        # Clause 3 (x_1 ∨ ¬x_2) — implications: ¬x_1 → ¬x_2  and  x_2 → x_1.
        # Both are cross-row diagonals that go bottom → top.
        e_c3_a = cross_arrow(n_nx1, n_nx2)
        e_c3_b = cross_arrow(n_x2, n_x1)
        self.play(Create(e_c3_a), Create(e_c3_b), run_time=0.7 / VISUAL_SPEED)

        # Drop the active-clause highlight and the rewrite rule.
        new_caption = body_text(
            "Three clauses, six edges. The implication graph.",
            size=22,
            color=TEXT_MUTED,
        ).move_to(caption.get_center())
        self.play(
            FadeOut(active_box),
            FadeOut(rule),
            Transform(caption, new_caption),
            run_time=0.5 / ANIM_SPEED,
        )
        self.wait(0.5)

        # ---- Sub-slide 3: SCC identification (pulse cycles, draw blobs) ----
        self.next_slide()
        self.begin_slide(section="2-SAT", clear=False)

        scc_caption = body_text(
            "Strongly connected components — literals that imply each other.",
            size=22,
            color=TEXT_MUTED,
        ).move_to(caption.get_center())
        self.play(Transform(caption, scc_caption), run_time=0.4 / ANIM_SPEED)

        # Pulse the top-row cycle: x_1 → ¬x_2 → x_1.
        self.play(
            Indicate(e_c2_a, color=COLOR_TRUE, scale_factor=1.0),
            run_time=0.45 / VISUAL_SPEED,
        )
        self.play(
            Indicate(e_c1_b, color=COLOR_TRUE, scale_factor=1.0),
            run_time=0.45 / VISUAL_SPEED,
        )

        # Pulse the bottom-row cycle: ¬x_1 → x_2 → ¬x_1.
        self.play(
            Indicate(e_c1_a, color=COLOR_TRUE, scale_factor=1.0),
            run_time=0.45 / VISUAL_SPEED,
        )
        self.play(
            Indicate(e_c2_b, color=COLOR_TRUE, scale_factor=1.0),
            run_time=0.45 / VISUAL_SPEED,
        )

        # Enclose each SCC with a translucent ellipse.
        scc_top = Ellipse(
            width=2 * col_x + 1.6,
            height=1.3,
            color=TEXT_ACCENT,
            stroke_width=2.0,
            fill_color=TEXT_ACCENT,
            fill_opacity=0.10,
        ).move_to([0, top_y, 0])
        scc_bot = Ellipse(
            width=2 * col_x + 1.6,
            height=1.3,
            color=TEXT_ACCENT,
            stroke_width=2.0,
            fill_color=TEXT_ACCENT,
            fill_opacity=0.10,
        ).move_to([0, bot_y, 0])

        scc_top_lbl = body_text(
            "SCC A", size=20, color=TEXT_ACCENT
        ).next_to(scc_top, RIGHT, buff=0.25)
        scc_bot_lbl = body_text(
            "SCC B", size=20, color=TEXT_ACCENT
        ).next_to(scc_bot, RIGHT, buff=0.25)

        self.play(
            Create(scc_top),
            Create(scc_bot),
            run_time=0.7 / VISUAL_SPEED,
        )
        self.play(
            FadeIn(scc_top_lbl),
            FadeIn(scc_bot_lbl),
            run_time=0.4 / ANIM_SPEED,
        )
        self.wait(0.5)

        # ---- Sub-slide 4: verdict + assignment ----
        self.next_slide()
        self.begin_slide(section="2-SAT", clear=False)

        verdict_caption = body_text(
            "Any x and ¬x in the same SCC?   No.   →   SAT.",
            size=22,
            color=COLOR_TRUE,
        ).move_to(caption.get_center())
        self.play(Transform(caption, verdict_caption), run_time=0.5 / ANIM_SPEED)

        # SCC A is "later" in reverse topological order (bottom → top in our
        # DAG, so top is the sink → reverse-topo first). Aspvall-Plass-Tarjan:
        # set every literal in the chosen SCC to TRUE.
        self.play(
            scc_top.animate.set_stroke(color=COLOR_TRUE, width=3.5).set_fill(
                color=COLOR_TRUE, opacity=0.18
            ),
            run_time=0.5 / VISUAL_SPEED,
        )

        # Assignment readout: SCC A contains x_1 and ¬x_2 → x_1=1, x_2=0.
        truth_x1 = body_text(
            "x₁ = 1",
            size=24,
            color=COLOR_TRUE,
            weight="BOLD",
        )
        truth_x2 = body_text(
            "x₂ = 0",
            size=24,
            color=COLOR_TRUE,
            weight="BOLD",
        )
        truths = (
            VGroup(truth_x1, truth_x2)
            .arrange(RIGHT, buff=0.8)
            .move_to([0, -3.05, 0])
        )
        self.play(FadeIn(truths), run_time=0.5 / ANIM_SPEED)
        self.wait(0.5)

    # === Slide 10: 2-SAT random-walk solver =============================
    def _slide_schoning(self) -> None:
        self.begin_slide(section="2-SAT")

        heading = body_text(
            "The random-walk solver",
            size=44,
            weight="BOLD",
        ).to_edge(UP, buff=0.9)
        self.play(FadeIn(heading), run_time=0.5 / ANIM_SPEED)

        step1 = body_text("Start with a random assignment.", size=28)
        step2 = body_text("Find an unsatisfied clause.", size=28)
        step3 = body_text("Flip one of its variables, at random.", size=28)
        step4 = body_text("Repeat until everything is satisfied.", size=28)
        steps = (
            VGroup(step1, step2, step3, step4)
            .arrange(DOWN, aligned_edge=LEFT, buff=0.5)
            .move_to([0, 0.3, 0])
        )

        runtime = body_text(
            "Expected runtime:  O(n²)",
            size=32,
            color=TEXT_ACCENT,
        ).move_to([0, -2.6, 0])

        self.play(
            LaggedStart(
                *[FadeIn(s) for s in steps],
                lag_ratio=0.35,
                run_time=0.9 / ANIM_SPEED,
            )
        )
        self.play(FadeIn(runtime), run_time=0.5 / ANIM_SPEED)
        self.wait(0.5)

    # === Slide 10b: 2-SAT walk trace (4 arrow-advanced sub-slides) =======
    def _slide_schoning_trace(self) -> None:
        """Walk the audience through the 2-SAT random-walk solver step by step.

        Same starting state (0,0,0) as slide 8 so the audience can compare:
        slide 8 deliberately picked x_2 and won in one flip; here the
        random walk picks x_1 first, undoes it next step (cycle!), then
        finally picks x_2 and lands on a satisfying assignment.
        """
        # ---- Sub-slide 1 (page 13): setup, initial state (0,0,0) ----
        self.begin_slide(section="2-SAT")

        heading = body_text(
            "A 2-SAT random walk", size=44, weight="BOLD"
        ).to_edge(UP, buff=0.6)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        clause_a = math(
            r"({\color[HTML]{06B6D4}x_1} \lor {\color[HTML]{A78BFA}x_2})",
            color=None, scale=0.32,
        )
        clause_b = math(
            r"(\lnot{\color[HTML]{06B6D4}x_1} \lor {\color[HTML]{FB923C}x_3})",
            color=None, scale=0.32,
        )
        clause_c = math(
            r"({\color[HTML]{A78BFA}x_2} \lor \lnot{\color[HTML]{FB923C}x_3})",
            color=None, scale=0.32,
        )
        sep1 = math(r"\land", scale=0.32, color=TEXT_MUTED)
        sep2 = math(r"\land", scale=0.32, color=TEXT_MUTED)
        formula_row = (
            VGroup(clause_a, sep1, clause_b, sep2, clause_c)
            .arrange(RIGHT, buff=0.3)
            .move_to([0, 1.5, 0])
        )
        clauses = [clause_a, clause_b, clause_c]
        self.play(FadeIn(formula_row), run_time=0.5 / ANIM_SPEED)

        def make_box(name: str, value: int, accent: str) -> VGroup:
            rect = Rectangle(
                width=1.0, height=1.0,
                stroke_color=accent, stroke_width=2.5,
            )
            v_text = body_text(
                str(value), size=36, color=TEXT_PRIMARY, weight="BOLD",
            ).move_to(rect.get_center())
            n_text = body_text(name, size=20, color=accent).next_to(
                rect, UP, buff=0.12
            )
            return VGroup(rect, n_text, v_text)

        box1 = make_box("x₁", 0, COLOR_VAR1)
        box2 = make_box("x₂", 0, COLOR_VAR2)
        box3 = make_box("x₃", 0, COLOR_VAR3)
        boxes = [box1, box2, box3]
        box_colors = [COLOR_VAR1, COLOR_VAR2, COLOR_VAR3]
        var_row = (
            VGroup(box1, box2, box3)
            .arrange(RIGHT, buff=0.55)
            .move_to([0, -0.5, 0])
        )
        self.play(FadeIn(var_row), run_time=0.4 / ANIM_SPEED)

        # Mutable trackers shared with the inner ``iterate`` closure.
        state = [0, 0, 0]
        val_texts = [box1[2], box2[2], box3[2]]

        def evaluate(s: list[int]) -> list[bool]:
            return [
                bool(s[0] or s[1]),                # clause_a
                bool((not s[0]) or s[2]),          # clause_b
                bool(s[1] or (not s[2])),          # clause_c
            ]

        def make_marks(s: list[int]) -> list:
            evs = evaluate(s)
            out = []
            for cl, ok in zip(clauses, evs):
                sym = "✓" if ok else "✗"
                color = COLOR_TRUE if ok else COLOR_FALSE
                m = body_text(sym, size=32, color=color).next_to(
                    cl, DOWN, buff=0.25
                )
                out.append(m)
            return out

        def status_line(prefix: str, s: list[int], extra: str = "") -> str:
            evs = evaluate(s)
            n_fail = sum(1 for v in evs if not v)
            if n_fail == 0:
                tail = "all clauses satisfied!"
            elif n_fail == 1:
                tail = "1 clause fails"
            else:
                tail = f"{n_fail} clauses fail"
            if extra:
                tail = extra + "  —  " + tail
            a, b, c = s
            return f"{prefix}  ({a}, {b}, {c})  —  {tail}"

        marks_list = make_marks(state)
        self.play(*[FadeIn(m) for m in marks_list], run_time=0.4 / ANIM_SPEED)

        status = body_text(
            status_line("Initial:", state),
            size=20,
            color=COLOR_FALSE,
        ).move_to([0, -2.4, 0])
        self.play(FadeIn(status), run_time=0.3 / ANIM_SPEED)
        status_holder = [status]
        # Buffer past build_static.py's -sseof -0.2 capture point so the
        # static PNG sees the status text fully faded in.
        self.wait(0.5)

        def iterate(step_n: int, picked_clause_idx: int, picked_var_idx: int,
                    extra: str = "") -> None:
            new_state = state.copy()
            new_state[picked_var_idx] = 1 - state[picked_var_idx]

            # 1. Highlight chosen clause with a yellow box (the random pick).
            chosen_clause = clauses[picked_clause_idx]
            hl_box = Rectangle(
                width=chosen_clause.width + 0.25,
                height=chosen_clause.height + 0.35,
                stroke_color=COLOR_HIGHLIGHT,
                stroke_width=2.5,
                fill_opacity=0,
            ).move_to(chosen_clause.get_center())
            self.play(FadeIn(hl_box), run_time=0.3 / VISUAL_SPEED)
            self.wait(0.2 / VISUAL_SPEED)

            # 2. Pulse the chosen variable's box border (the random variable).
            chosen_box = boxes[picked_var_idx]
            chosen_rect = chosen_box[0]
            accent = box_colors[picked_var_idx]
            self.play(
                chosen_rect.animate.set_stroke(color=COLOR_HIGHLIGHT, width=4.0),
                run_time=0.3 / VISUAL_SPEED,
            )
            self.wait(0.15 / VISUAL_SPEED)

            # 3. Flip the value.
            old_val = val_texts[picked_var_idx]
            new_val = body_text(
                str(new_state[picked_var_idx]),
                size=36,
                color=TEXT_PRIMARY,
                weight="BOLD",
            ).move_to(old_val.get_center())
            self.play(
                FadeOut(old_val),
                FadeIn(new_val),
                run_time=0.45 / VISUAL_SPEED,
            )
            val_texts[picked_var_idx] = new_val

            # 4. Re-evaluate everything: markers swap, status updates,
            #    highlights revert. All in one play so it reads as a single
            #    "consequence" beat.
            new_marks = make_marks(new_state)
            new_status_color = (
                COLOR_TRUE if all(evaluate(new_state)) else COLOR_FALSE
            )
            new_status = body_text(
                status_line(f"Step {step_n}:", new_state, extra=extra),
                size=20,
                color=new_status_color,
            ).move_to([0, -2.4, 0])

            anims = [
                FadeOut(hl_box),
                chosen_rect.animate.set_stroke(color=accent, width=2.5),
                FadeOut(status_holder[0]),
                FadeIn(new_status),
            ]
            for old_m, new_m in zip(marks_list, new_marks):
                anims.append(FadeOut(old_m))
                anims.append(FadeIn(new_m))
            self.play(*anims, run_time=0.55 / VISUAL_SPEED)

            for i in range(3):
                marks_list[i] = new_marks[i]
                state[i] = new_state[i]
            status_holder[0] = new_status
            # 0.5s real-time dwell so the build_static.py last-frame capture
            # (which seeks ``-sseof -0.2`` from MP4 end) lands well past the
            # FadeOut(hl_box) completion — otherwise the highlight box
            # leaves a faint residual outline in the static PNG.
            self.wait(0.5)

        # ---- Sub-slide 2 (page 14): iter 1 — pick clause_a, x₁ → (1,0,0) ----
        self.next_slide()
        self.begin_slide(section="2-SAT", clear=False)
        iterate(1, 0, 0)

        # ---- Sub-slide 3 (page 15): iter 2 — pick clause_b, x₁ → (0,0,0) [CYCLE]
        self.next_slide()
        self.begin_slide(section="2-SAT", clear=False)
        iterate(2, 1, 0, extra="back where we started")

        # ---- Sub-slide 4 (page 16): iter 3 — pick clause_a, x₂ → (0,1,0) [SAT] ----
        self.next_slide()
        self.begin_slide(section="2-SAT", clear=False)
        iterate(3, 0, 1)
        self.wait(0.4 / ANIM_SPEED)

    # === Slide 11: Hamming-distance walk ================================
    def _slide_hamming_walk(self) -> None:
        self.begin_slide(section="2-SAT")

        heading = body_text(
            "Why does it work?", size=44, weight="BOLD"
        ).to_edge(UP, buff=0.7)
        self.play(FadeIn(heading), run_time=0.5 / ANIM_SPEED)

        line1 = body_text(
            "Fix any satisfying assignment x*.",
            size=24,
        ).move_to([0, 2.2, 0])
        line2 = body_text(
            "d = Hamming distance from current assignment to x*.",
            size=24,
        ).move_to([0, 1.6, 0])
        self.play(FadeIn(line1), run_time=0.4 / ANIM_SPEED)
        self.play(FadeIn(line2), run_time=0.4 / ANIM_SPEED)

        n = 8
        line_y = -0.2
        line_left = -5.0
        line_right = 5.0
        line_width = line_right - line_left

        number_line = Line(
            [line_left, line_y, 0],
            [line_right, line_y, 0],
            stroke_color=TEXT_MUTED,
            stroke_width=2.0,
        )

        ticks: list[Line] = []
        labels_to_show = []
        for d in range(n + 1):
            tx = line_left + (d / n) * line_width
            tick = Line(
                [tx, line_y - 0.1, 0],
                [tx, line_y + 0.1, 0],
                stroke_color=TEXT_MUTED,
                stroke_width=1.5,
            )
            ticks.append(tick)
            if d == 0:
                lbl = body_text("0", size=18, color=COLOR_TRUE)
            elif d == n:
                lbl = body_text("n", size=18, color=TEXT_MUTED)
            elif d % 2 == 0:
                lbl = body_text(str(d), size=18, color=TEXT_MUTED)
            else:
                lbl = None
            if lbl is not None:
                lbl.next_to(tick, DOWN, buff=0.18)
                labels_to_show.append(lbl)

        target_label = body_text("x*", size=22, color=COLOR_TRUE).next_to(
            ticks[0], UP, buff=0.4
        )

        self.play(
            FadeIn(number_line),
            *[FadeIn(t) for t in ticks],
            *[FadeIn(l) for l in labels_to_show],
            FadeIn(target_label),
            run_time=0.6 / ANIM_SPEED,
        )

        walker_d = 5
        walker_x = line_left + (walker_d / n) * line_width
        walker = Dot([walker_x, line_y, 0], color=COLOR_HIGHLIGHT, radius=0.15)

        # Label = "d = N" with N animating each step. Built as two pieces so we
        # can swap the digit with a slot-machine drop while the prefix glides
        # alongside the walker.
        prefix = body_text("d = ", size=22, color=COLOR_HIGHLIGHT)
        value = body_text(
            str(walker_d), size=22, color=COLOR_HIGHLIGHT, weight="BOLD"
        )
        label_group = VGroup(prefix, value).arrange(RIGHT, buff=0.05)
        label_group.next_to(walker, UP, buff=0.18)

        # Capture the prefix/value offsets relative to the walker; reused each
        # step so the label stays glued above the dot at the new x.
        prefix_dx = prefix.get_center()[0] - walker.get_center()[0]
        prefix_dy = prefix.get_center()[1] - walker.get_center()[1]
        value_dx = value.get_center()[0] - walker.get_center()[0]
        value_dy = value.get_center()[1] - walker.get_center()[1]

        self.play(
            FadeIn(walker),
            FadeIn(prefix),
            FadeIn(value),
            run_time=0.4 / ANIM_SPEED,
        )

        # 5 → 4 → 3 → 4 → 3 → 2 → 1 → 0 — biased toward 0 with one bounce away
        # so the audience sees both directions, ending in absorption at d=0.
        moves = [-1, -1, +1, -1, -1, -1, -1]
        for delta in moves:
            new_d = max(0, min(n, walker_d + delta))
            new_x = line_left + (new_d / n) * line_width

            # New digit starts at the OLD value's position (invisible) and ends
            # at the new value's position (visible) — same trajectory as the old
            # digit so both ride together with the walker. The cross-fade then
            # happens with no x-position drift between the two digits.
            new_value = body_text(
                str(new_d),
                size=22,
                color=COLOR_HIGHLIGHT,
                weight="BOLD",
            ).move_to(value.get_center())
            new_value.set_opacity(0)
            self.add(new_value)

            self.play(
                walker.animate.move_to([new_x, line_y, 0]),
                prefix.animate.move_to(
                    [new_x + prefix_dx, line_y + prefix_dy, 0]
                ),
                value.animate.move_to(
                    [new_x + value_dx, line_y + value_dy, 0]
                ).set_opacity(0),
                new_value.animate.move_to(
                    [new_x + value_dx, line_y + value_dy, 0]
                ).set_opacity(1),
                run_time=0.5 / VISUAL_SPEED,
            )
            walker_d = new_d
            value = new_value
            if walker_d == 0:
                # Absorbed at x* — turn dot green and drop the "d = 0" label so
                # it doesn't sit on top of "x*" anchored at the same x position.
                self.play(
                    walker.animate.set_color(COLOR_TRUE),
                    FadeOut(prefix),
                    FadeOut(value),
                    run_time=0.4 / VISUAL_SPEED,
                )
                break

        conclusion = body_text(
            "Each step:  ≥ ½ chance to move toward 0.",
            size=24,
            color=TEXT_ACCENT,
        ).move_to([0, -2.5, 0])
        self.play(FadeIn(conclusion), run_time=0.5 / ANIM_SPEED)
        self.wait(0.7 / ANIM_SPEED)

    # === Slide 12: The proof ============================================
    def _slide_proof(self) -> None:
        self.begin_slide(section="2-SAT")

        heading = body_text(
            "Expected hitting time",
            size=42,
            weight="BOLD",
        ).to_edge(UP, buff=0.7)
        self.play(FadeIn(heading), run_time=0.5 / ANIM_SPEED)

        setup = body_text(
            "h(d) = expected steps from distance d to reach 0.",
            size=24,
        ).move_to([0, 2.2, 0])
        self.play(FadeIn(setup), run_time=0.4 / ANIM_SPEED)

        eq1 = math(r"h(0) = 0", scale=0.4).move_to([0, 1.3, 0])
        self.play(FadeIn(eq1), run_time=0.4 / ANIM_SPEED)

        eq2 = math(
            r"h(d) \;\le\; 1 + \tfrac{1}{2}\, h(d-1) + \tfrac{1}{2}\, h(d+1)",
            scale=0.4,
        ).move_to([0, 0.4, 0])
        self.play(FadeIn(eq2), run_time=0.5 / ANIM_SPEED)

        bridge = body_text(
            "Now solve it exactly.",
            size=26,
            color=TEXT_ACCENT,
        ).move_to([0, -1.45, 0])
        self.play(FadeIn(bridge), run_time=0.4 / ANIM_SPEED)
        self.wait(0.5 / ANIM_SPEED)

        def gap_boxes(
            *,
            y: float = -1.25,
            labels: list[str] | None = None,
            values: list[str] | None = None,
            label_scale: float = 0.24,
            value_scale: float = 0.20,
            box_width: float = 1.05,
            box_height: float = 0.72,
            buff: float = 0.25,
        ) -> tuple[VGroup, list[VGroup]]:
            box_labels = labels or [
                r"a_1",
                r"a_2",
                r"a_3",
                r"\cdots",
                r"a_{n-1}",
                r"a_n",
            ]
            boxes = []

            def box_math(
                latex: str,
                *,
                color: str,
                scale: float,
                max_width: float = 0.84,
            ):
                obj = math(latex, scale=scale, color=color)
                if obj.width > max_width:
                    obj.scale(max_width / obj.width)
                return obj

            for i, label in enumerate(box_labels):
                rect = Rectangle(
                    width=box_width,
                    height=box_height,
                    stroke_color=COLOR_HIGHLIGHT,
                    stroke_width=2.0,
                    fill_color=COLOR_HIGHLIGHT,
                    fill_opacity=0.06,
                )
                label_text = box_math(
                    label,
                    color=COLOR_HIGHLIGHT,
                    scale=label_scale,
                    max_width=box_width * 0.80,
                )
                if values is None:
                    label_text.move_to(rect.get_center())
                    boxes.append(VGroup(rect, label_text))
                else:
                    value_text = box_math(
                        values[i],
                        color=TEXT_ACCENT if i == len(box_labels) - 1 else TEXT_PRIMARY,
                        scale=value_scale,
                        max_width=box_width * 0.82,
                    )
                    value_text.move_to(rect.get_center())
                    label_text.next_to(rect, UP, buff=0.08)
                    boxes.append(VGroup(rect, label_text, value_text))
            group = VGroup(*boxes).arrange(RIGHT, buff=buff).move_to([0, y, 0])
            return group, boxes

        # ---- Recurrence proof A: setup ---------------------------------
        self.next_slide()
        self.begin_slide(section="2-SAT")

        heading = body_text("Solving the recurrence", size=42, weight="BOLD")
        heading.to_edge(UP, buff=0.7)
        rec = math(
            r"h(d)=1+\frac12h(d-1)+\frac12h(d+1)",
            scale=0.44,
            color=TEXT_PRIMARY,
        ).move_to([0, 1.15, 0])
        gap_text = body_text(
            "Look at the gaps — define",
            size=24,
            color=TEXT_MUTED,
        )
        gap_def = math(
            r"a_d:=h(d)-h(d-1)",
            scale=0.28,
            color=TEXT_ACCENT,
        )
        gap_line = VGroup(gap_text, gap_def).arrange(RIGHT, buff=0.25)
        gap_line.move_to([0, 0.10, 0])
        boxes_group, boxes = gap_boxes(y=-1.55)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)
        self.play(FadeIn(rec), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(gap_line), run_time=0.4 / ANIM_SPEED)
        self.play(
            LaggedStart(
                *[FadeIn(box) for box in boxes],
                lag_ratio=0.15,
                run_time=0.8 / ANIM_SPEED,
            )
        )
        self.wait(0.4)

        # ---- Recurrence proof B: gap recurrence -------------------------
        self.next_slide()
        self.begin_slide(section="2-SAT")

        heading = body_text("The gaps decrease by 2", size=42, weight="BOLD")
        heading.to_edge(UP, buff=0.7)
        step1 = math(
            r"\frac12(a_d-a_{d+1})=1",
            scale=0.46,
            color=TEXT_PRIMARY,
        ).move_to([0, 1.35, 0])
        step2 = math(
            r"a_{d+1}=a_d-2",
            scale=0.52,
            color=TEXT_ACCENT,
        ).move_to([0, 0.45, 0])
        boxes_group, boxes = gap_boxes(
            y=-1.35,
            label_scale=0.22,
            box_width=0.98,
            box_height=0.68,
            buff=0.52,
        )
        arrows = []
        arrow_labels = []
        for left_box, right_box in zip(boxes[:-1], boxes[1:]):
            arrow_y = left_box[0].get_top()[1] + 0.22
            start = [left_box[0].get_right()[0] + 0.05, arrow_y, 0]
            end = [right_box[0].get_left()[0] - 0.05, arrow_y, 0]
            arrow = Arrow(
                start,
                end,
                buff=0,
                color=TEXT_MUTED,
                stroke_width=2.2,
                max_tip_length_to_length_ratio=0.12,
            )
            label = math(r"-2", scale=0.15, color=TEXT_ACCENT).next_to(
                arrow, UP, buff=0.08
            )
            arrows.append(arrow)
            arrow_labels.append(label)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)
        self.play(FadeIn(step1), run_time=0.4 / ANIM_SPEED)
        self.play(FadeIn(step2), run_time=0.4 / ANIM_SPEED)
        self.play(FadeIn(boxes_group), run_time=0.35 / ANIM_SPEED)
        self.play(
            LaggedStart(
                *[Create(a) for a in arrows],
                *[FadeIn(l) for l in arrow_labels],
                lag_ratio=0.12,
                run_time=0.9 / VISUAL_SPEED,
            )
        )
        self.wait(0.45)

        # ---- Recurrence proof C: boundary and propagation ---------------
        self.next_slide()
        self.begin_slide(section="2-SAT")

        heading = body_text("Anchor at the boundary", size=42, weight="BOLD")
        heading.to_edge(UP, buff=0.7)
        boundary = self._fit_math(
            r"h(n)=1+h(n-1)\quad\Longrightarrow\quad a_n=1",
            scale=0.36,
            max_width=11.5,
            color=TEXT_PRIMARY,
        ).move_to([0, 1.35, 0])
        labels = [r"a_1", r"a_2", r"a_3", r"\cdots", r"a_{n-1}", r"a_n"]
        values = [r"2n-1", r"2n-3", r"2n-5", r"\cdots", r"3", r"1"]
        boxes_group, boxes = gap_boxes(
            y=-0.75,
            labels=labels,
            values=values,
            label_scale=0.22,
            value_scale=0.18,
        )
        for box in boxes:
            box[2].set_opacity(0)
        form = math(
            r"a_d=2(n-d)+1",
            scale=0.48,
            color=TEXT_ACCENT,
        ).move_to([0, -2.25, 0])
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)
        self.play(FadeIn(boundary), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(boxes_group), run_time=0.35 / ANIM_SPEED)
        self.play(
            boxes[-1][2].animate.set_opacity(1).shift(0.05 * DOWN),
            run_time=0.35 / VISUAL_SPEED,
        )
        self.play(
            LaggedStart(
                *[
                    boxes[i][2].animate.set_opacity(1)
                    for i in range(len(boxes) - 2, -1, -1)
                ],
                lag_ratio=0.18,
                run_time=1.1 / VISUAL_SPEED,
            )
        )
        self.play(FadeIn(form), run_time=0.4 / ANIM_SPEED)
        self.wait(0.45)

        # ---- Recurrence proof D: sum the gaps ---------------------------
        self.next_slide()
        self.begin_slide(section="2-SAT")

        heading = body_text("Sum the gaps", size=42, weight="BOLD")
        heading.to_edge(UP, buff=0.7)
        boxes_group, boxes = gap_boxes(
            y=1.25,
            labels=[r"a_1", r"a_2", r"a_3", r"\cdots", r"a_d", r"\cdots"],
            values=[
                r"2n-1",
                r"2n-3",
                r"2n-5",
                r"\cdots",
                r"2(n-d)+1",
                r"\cdots",
            ],
            label_scale=0.20,
            value_scale=0.15,
            box_width=0.95,
            box_height=0.58,
            buff=0.18,
        )
        first_d = SurroundingRectangle(
            VGroup(*boxes[:5]),
            color=TEXT_ACCENT,
            buff=0.10,
            stroke_width=2.5,
        )
        sum_def = math(
            r"h(d)=\sum_{k=1}^{d}a_k",
            scale=0.34,
            color=TEXT_PRIMARY,
        ).move_to([0, 0.10, 0])
        sum_calc = self._fit_math(
            r"\sum_{k=1}^{d}\bigl(2(n-k)+1\bigr)=d(2n-d)",
            scale=0.28,
            max_width=8.2,
            color=TEXT_PRIMARY,
        ).move_to([0, -0.65, 0])
        boxed = math(
            r"\boxed{h(d)=d(2n-d)}",
            scale=0.40,
            color=TEXT_ACCENT,
        ).move_to([0, -1.35, 0])
        max_line = math(
            r"d=n\quad\Longrightarrow\quad h(n)=n^2",
            scale=0.34,
            color=TEXT_ACCENT,
        ).move_to([0, -2.10, 0])
        note = body_text(
            "Maximum at d = n — exactly the diameter.",
            size=18,
            color=TEXT_MUTED,
        ).move_to([0, -2.58, 0])
        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(boxes_group), run_time=0.35 / ANIM_SPEED)
        self.play(Create(first_d), run_time=0.45 / VISUAL_SPEED)
        self.play(FadeIn(sum_def), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(sum_calc), run_time=0.4 / ANIM_SPEED)
        self.play(FadeIn(boxed), run_time=0.45 / VISUAL_SPEED)
        self.play(FadeIn(max_line), FadeIn(note), run_time=0.45 / ANIM_SPEED)
        self.play(Indicate(max_line, color=TEXT_ACCENT), run_time=0.6 / VISUAL_SPEED)
        self.wait(0.5)

    # === Slide 13: Transition to 3-SAT ==================================
    def _slide_three_sat_transition(self) -> None:
        self.begin_slide(section="3-SAT")

        heading = body_text("What changes for 3-SAT?", size=44, weight="BOLD")
        heading.to_edge(UP, buff=0.8)

        line1 = body_text(
            "Use the same local move: find a false clause, flip one variable.",
            size=26,
        )
        line2 = body_text(
            "But a false clause now has three variables, not two.",
            size=26,
        )
        line3 = body_text(
            "So the walk can drift away from a satisfying assignment.",
            size=28,
            color=TEXT_ACCENT,
        )
        body = (
            VGroup(line1, line2, line3)
            .arrange(DOWN, aligned_edge=LEFT, buff=0.55)
            .move_to([0, 0.35, 0])
        )

        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)
        self.play(
            LaggedStart(
                *[FadeIn(row) for row in body],
                lag_ratio=0.35,
                run_time=0.9 / ANIM_SPEED,
            )
        )
        self.wait(0.5)

    def _sat_distance_line(
        self,
        *,
        y: float = 0.0,
        r: int = 4,
        max_h: int = 6,
        left_x: float = -4.8,
        right_x: float = 4.8,
        label_zero: bool = True,
    ) -> tuple[VGroup, list[Line], list, Dot, callable]:
        def h_x(h: int) -> float:
            return left_x + (h / max_h) * (right_x - left_x)

        number_line = Line(
            [left_x, y, 0],
            [right_x, y, 0],
            stroke_color=TEXT_MUTED,
            stroke_width=2.0,
        )
        ticks = []
        labels = []
        for h in range(max_h + 1):
            x = h_x(h)
            tick = Line(
                [x, y - 0.10, 0],
                [x, y + 0.10, 0],
                stroke_color=TEXT_MUTED,
                stroke_width=1.5,
            )
            label = body_text(str(h), size=18, color=TEXT_MUTED)
            if h == 0 and label_zero:
                label.set_color(COLOR_TRUE)
            label.next_to(tick, DOWN, buff=0.14)
            ticks.append(tick)
            labels.append(label)
        walker = Dot([h_x(r), y, 0], color=COLOR_HIGHLIGHT, radius=0.13)
        group = VGroup(number_line, *ticks, *labels)
        return group, ticks, labels, walker, h_x

    # === Slide 14: 2-SAT vs 3-SAT drift =================================
    def _slide_three_sat_drift(self) -> None:
        self.begin_slide(section="3-SAT")

        heading = body_text("Drift changes everything", size=42, weight="BOLD")
        heading.to_edge(UP, buff=0.65)
        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)

        def make_panel(
            *,
            x: float,
            title: str,
            left_label: str,
            right_label: str,
            left_width: float,
            right_width: float,
            first_line: str,
            second_line: str,
            title_color: str,
        ) -> tuple[VGroup, VGroup]:
            title_obj = body_text(title, size=28, color=title_color, weight="BOLD")
            title_obj.move_to([x, 1.92, 0])

            line_y = 0.95
            left = x - 1.75
            right = x + 1.75
            center = x + 0.10
            axis = Line(
                [left, line_y, 0],
                [right, line_y, 0],
                stroke_color=TEXT_MUTED,
                stroke_width=1.8,
            )
            zero_dot = Dot([left, line_y, 0], radius=0.06, color=COLOR_TRUE)
            far_dot = Dot([right, line_y, 0], radius=0.045, color=TEXT_MUTED)
            walker = Dot([center, line_y, 0], radius=0.12, color=COLOR_HIGHLIGHT)
            zero_label = body_text("0", size=16, color=COLOR_TRUE).next_to(
                zero_dot, DOWN, buff=0.14
            )
            h_label = math(r"h", scale=0.14, color=COLOR_HIGHLIGHT).next_to(
                walker, DOWN, buff=0.14
            )

            left_arrow = Arrow(
                [center - 0.05, line_y + 0.45, 0],
                [center - 0.92, line_y + 0.45, 0],
                buff=0,
                color=COLOR_TRUE,
                stroke_width=left_width,
                max_tip_length_to_length_ratio=0.10,
            )
            right_arrow = Arrow(
                [center + 0.05, line_y + 0.45, 0],
                [center + 0.92, line_y + 0.45, 0],
                buff=0,
                color=COLOR_FALSE,
                stroke_width=right_width,
                max_tip_length_to_length_ratio=0.10,
            )
            left_prob = math(left_label, scale=0.16, color=COLOR_TRUE).next_to(
                left_arrow, UP, buff=0.08
            )
            right_prob = math(right_label, scale=0.16, color=COLOR_FALSE).next_to(
                right_arrow, UP, buff=0.08
            )

            text1 = body_text(first_line, size=20, color=TEXT_PRIMARY)
            text2 = body_text(second_line, size=20, color=TEXT_ACCENT)
            text_block = VGroup(text1, text2).arrange(DOWN, buff=0.24)
            text_block.move_to([x, -0.75, 0])

            static = VGroup(title_obj, axis, zero_dot, far_dot, walker, zero_label, h_label)
            arrows = VGroup(left_arrow, right_arrow, left_prob, right_prob, text_block)
            return static, arrows

        left_static, left_arrows = make_panel(
            x=-3.05,
            title="2-SAT",
            left_label=r"\geq\frac12",
            right_label=r"\leq\frac12",
            left_width=4.2,
            right_width=3.0,
            first_line="Walker reaches 0 eventually.",
            second_line="Question: how fast?",
            title_color=COLOR_VAR1,
        )
        right_static, right_arrows = make_panel(
            x=3.05,
            title="3-SAT",
            left_label=r"\frac13",
            right_label=r"\frac23",
            left_width=2.4,
            right_width=5.0,
            first_line="Walker may never reach 0.",
            second_line="Question: how often?",
            title_color=COLOR_VAR3,
        )

        divider = Line(
            [0, 2.15, 0],
            [0, -1.55, 0],
            stroke_color=TEXT_MUTED,
            stroke_width=1.0,
        )
        self.play(
            FadeIn(left_static),
            FadeIn(right_static),
            FadeIn(divider),
            run_time=0.6 / ANIM_SPEED,
        )
        self.play(FadeIn(left_arrows), FadeIn(right_arrows), run_time=0.9 / VISUAL_SPEED)

        bottom = body_text(
            "Different question, different math.",
            size=30,
            color=TEXT_ACCENT,
            weight="BOLD",
        ).move_to([0, -2.35, 0])
        self.play(FadeIn(bottom), run_time=0.4 / ANIM_SPEED)
        self.wait(0.45)

    # === Slide 14: 3-SAT trace (6 arrow-advanced sub-slides) ============
    def _slide_three_sat_trace(self) -> None:
        """Schöning-style random walk on a small 3-SAT instance.

        The horizontal meter tracks d = the number of currently unsatisfied
        clauses, not Hamming distance. The trace includes a no-progress move
        and a move that increases d before reaching a satisfying assignment.
        """
        # ---- Sub-slide 1 (page 23): setup, initial state (0,0,0,0) ----
        self.begin_slide(section="3-SAT")

        heading = body_text(
            "A 3-SAT random walk", size=42, weight="BOLD"
        ).to_edge(UP, buff=0.45)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        clause_1 = math(
            r"(\lnot{\color[HTML]{06B6D4}x_1} \lor "
            r"{\color[HTML]{FB923C}x_3} \lor "
            r"{\color[HTML]{EC4899}x_4})",
            color=None,
            scale=0.25,
        )
        clause_2 = math(
            r"({\color[HTML]{06B6D4}x_1} \lor "
            r"{\color[HTML]{FB923C}x_3} \lor "
            r"{\color[HTML]{EC4899}x_4})",
            color=None,
            scale=0.25,
        )
        clause_3 = math(
            r"({\color[HTML]{06B6D4}x_1} \lor "
            r"\lnot{\color[HTML]{A78BFA}x_2} \lor "
            r"{\color[HTML]{EC4899}x_4})",
            color=None,
            scale=0.25,
        )
        clause_4 = math(
            r"({\color[HTML]{A78BFA}x_2} \lor "
            r"{\color[HTML]{FB923C}x_3} \lor "
            r"{\color[HTML]{EC4899}x_4})",
            color=None,
            scale=0.25,
        )
        sep_1 = math(r"\land", scale=0.25, color=TEXT_MUTED)
        sep_2 = math(r"\land", scale=0.25, color=TEXT_MUTED)
        row_1 = VGroup(clause_1, sep_1, clause_2).arrange(RIGHT, buff=0.25)
        row_2 = VGroup(clause_3, sep_2, clause_4).arrange(RIGHT, buff=0.25)
        row_1.move_to([0, 2.15, 0])
        row_2.move_to([0, 1.45, 0])
        clauses = [clause_1, clause_2, clause_3, clause_4]

        formula_group = VGroup(row_1, row_2)
        self.play(FadeIn(formula_group), run_time=0.5 / ANIM_SPEED)

        def make_box(name: str, value: int, accent: str) -> VGroup:
            rect = Rectangle(
                width=0.88,
                height=0.88,
                stroke_color=accent,
                stroke_width=2.5,
            )
            value_text = body_text(
                str(value),
                size=32,
                color=TEXT_PRIMARY,
                weight="BOLD",
            ).move_to(rect.get_center())
            name_text = body_text(name, size=18, color=accent).next_to(
                rect, UP, buff=0.10
            )
            return VGroup(rect, name_text, value_text)

        box1 = make_box("x₁", 0, COLOR_VAR1)
        box2 = make_box("x₂", 0, COLOR_VAR2)
        box3 = make_box("x₃", 0, COLOR_VAR3)
        box4 = make_box("x₄", 0, COLOR_VAR4)
        boxes = [box1, box2, box3, box4]
        box_colors = [COLOR_VAR1, COLOR_VAR2, COLOR_VAR3, COLOR_VAR4]
        box_names = ["x₁", "x₂", "x₃", "x₄"]
        var_row = (
            VGroup(box1, box2, box3, box4)
            .arrange(RIGHT, buff=0.45)
            .move_to([0, 0.10, 0])
        )
        self.play(FadeIn(var_row), run_time=0.4 / ANIM_SPEED)

        state = [0, 0, 0, 0]
        val_texts = [box1[2], box2[2], box3[2], box4[2]]

        def evaluate(s: list[int]) -> list[bool]:
            return [
                bool((not s[0]) or s[2] or s[3]),
                bool(s[0] or s[2] or s[3]),
                bool(s[0] or (not s[1]) or s[3]),
                bool(s[1] or s[2] or s[3]),
            ]

        def unsat_count(s: list[int]) -> int:
            return sum(1 for ok in evaluate(s) if not ok)

        def make_marks(s: list[int]) -> list:
            marks = []
            for i, (clause, ok) in enumerate(zip(clauses, evaluate(s))):
                sym = "✓" if ok else "✗"
                color = COLOR_TRUE if ok else COLOR_FALSE
                direction = UP if i < 2 else DOWN
                marks.append(
                    body_text(sym, size=26, color=color).next_to(
                        clause, direction, buff=0.13
                    )
                )
            return marks

        marks_list = make_marks(state)
        self.play(*[FadeIn(m) for m in marks_list], run_time=0.35 / ANIM_SPEED)

        line_y = -1.35
        line_left = -3.25
        line_right = 3.25
        d_max = 4
        line_width = line_right - line_left

        def x_for_d(d: int) -> float:
            return line_left + (d / d_max) * line_width

        meter = Line(
            [line_left, line_y, 0],
            [line_right, line_y, 0],
            stroke_color=TEXT_MUTED,
            stroke_width=2.0,
        )
        ticks = []
        tick_labels = []
        for d in range(d_max + 1):
            tx = x_for_d(d)
            tick = Line(
                [tx, line_y - 0.08, 0],
                [tx, line_y + 0.08, 0],
                stroke_color=TEXT_MUTED,
                stroke_width=1.4,
            )
            color = COLOR_TRUE if d == 0 else TEXT_MUTED
            label = body_text(str(d), size=16, color=color).next_to(
                tick, DOWN, buff=0.12
            )
            ticks.append(tick)
            tick_labels.append(label)

        meter_caption = body_text(
            "d = number of unsatisfied clauses",
            size=18,
            color=TEXT_MUTED,
        ).move_to([0, -2.05, 0])

        d0 = unsat_count(state)
        d_dot = Dot([x_for_d(d0), line_y, 0], color=COLOR_HIGHLIGHT, radius=0.12)
        d_label = body_text(
            f"d = {d0}",
            size=20,
            color=COLOR_HIGHLIGHT,
            weight="BOLD",
        ).move_to([x_for_d(d0), line_y + 0.35, 0])
        d_label_holder = [d_label]

        self.play(
            FadeIn(meter),
            *[FadeIn(t) for t in ticks],
            *[FadeIn(l) for l in tick_labels],
            FadeIn(meter_caption),
            FadeIn(d_dot),
            FadeIn(d_label),
            run_time=0.55 / ANIM_SPEED,
        )

        def state_text(s: list[int]) -> str:
            return "(" + ", ".join(str(v) for v in s) + ")"

        status = body_text(
            f"Initial  {state_text(state)}  —  d = {d0}",
            size=18,
            color=COLOR_FALSE,
        ).move_to([0, -2.75, 0])
        self.play(FadeIn(status), run_time=0.3 / ANIM_SPEED)
        status_holder = [status]
        self.wait(0.5)

        def iterate(
            step_n: int,
            picked_clause_idx: int,
            picked_var_idx: int,
            note: str,
        ) -> None:
            new_state = state.copy()
            new_state[picked_var_idx] = 1 - state[picked_var_idx]

            chosen_clause = clauses[picked_clause_idx]
            hl_box = SurroundingRectangle(
                chosen_clause,
                color=COLOR_HIGHLIGHT,
                buff=0.08,
                stroke_width=2.5,
            )
            self.play(Create(hl_box), run_time=0.3 / VISUAL_SPEED)

            chosen_box = boxes[picked_var_idx]
            chosen_rect = chosen_box[0]
            accent = box_colors[picked_var_idx]
            self.play(
                chosen_rect.animate.set_stroke(color=COLOR_HIGHLIGHT, width=4.0),
                run_time=0.3 / VISUAL_SPEED,
            )

            old_val = val_texts[picked_var_idx]
            new_val = body_text(
                str(new_state[picked_var_idx]),
                size=32,
                color=TEXT_PRIMARY,
                weight="BOLD",
            ).move_to(old_val.get_center())
            self.play(
                FadeOut(old_val),
                FadeIn(new_val),
                run_time=0.4 / VISUAL_SPEED,
            )
            val_texts[picked_var_idx] = new_val

            new_marks = make_marks(new_state)
            new_d = unsat_count(new_state)
            done = new_d == 0
            d_color = COLOR_TRUE if done else COLOR_HIGHLIGHT
            new_d_label = body_text(
                f"d = {new_d}",
                size=20,
                color=d_color,
                weight="BOLD",
            ).move_to([x_for_d(new_d), line_y + 0.35, 0])
            new_status = body_text(
                f"Step {step_n}  —  flip {box_names[picked_var_idx]}  —  {note}  —  "
                f"{state_text(new_state)}, d = {new_d}",
                size=18,
                color=COLOR_TRUE if done else COLOR_FALSE,
            ).move_to(status_holder[0].get_center())

            anims = [
                FadeOut(hl_box),
                chosen_rect.animate.set_stroke(color=accent, width=2.5),
                d_dot.animate.move_to([x_for_d(new_d), line_y, 0]).set_color(
                    d_color
                ),
                FadeOut(d_label_holder[0]),
                FadeIn(new_d_label),
                FadeOut(status_holder[0]),
                FadeIn(new_status),
            ]
            for old_m, new_m in zip(marks_list, new_marks):
                anims.append(FadeOut(old_m))
                anims.append(FadeIn(new_m))
            self.play(*anims, run_time=0.55 / VISUAL_SPEED)

            for i in range(4):
                marks_list[i] = new_marks[i]
                state[i] = new_state[i]
            d_label_holder[0] = new_d_label
            status_holder[0] = new_status
            self.wait(0.5)

        # ---- Sub-slide 2: flip x₁ from C₂; d stays 2 --------------------
        self.next_slide()
        self.begin_slide(section="3-SAT", clear=False)
        iterate(1, 1, 0, "no progress")

        # ---- Sub-slide 3: flip x₂ from C₄; d drops to 1 -----------------
        self.next_slide()
        self.begin_slide(section="3-SAT", clear=False)
        iterate(2, 3, 1, "one fewer false clause")

        # ---- Sub-slide 4: flip x₁ from C₁; d increases back to 2 --------
        self.next_slide()
        self.begin_slide(section="3-SAT", clear=False)
        iterate(3, 0, 0, "a bad random choice")

        # ---- Sub-slide 5: flip x₃ from C₂; d drops to 1 -----------------
        self.next_slide()
        self.begin_slide(section="3-SAT", clear=False)
        iterate(4, 1, 2, "recover")

        # ---- Sub-slide 6: flip x₄ from C₃; all clauses satisfied --------
        self.next_slide()
        self.begin_slide(section="3-SAT", clear=False)
        iterate(5, 2, 3, "SAT")

    # === Slide 16: 3-SAT runtime proof ==================================
    def _slide_three_sat_runtime(self) -> None:
        # ---- 17a-0: bridge from the trace variable to the proof variable -
        self.begin_slide(section="3-SAT")

        heading = body_text("Two distances", size=42, weight="BOLD")
        heading.to_edge(UP, buff=0.7)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        def make_card(
            *,
            x: float,
            symbol: str,
            symbol_color: str,
            title: str,
            detail,
        ) -> VGroup:
            rect = Rectangle(
                width=4.35,
                height=2.10,
                stroke_color=symbol_color,
                stroke_width=1.8,
                fill_color=symbol_color,
                fill_opacity=0.06,
            )
            rect.move_to([x, 0.35, 0])
            sym = math(symbol, scale=0.44, color=symbol_color).move_to(
                [x, 0.88, 0]
            )
            title_obj = body_text(title, size=21, color=TEXT_PRIMARY).move_to(
                [x, 0.28, 0]
            )
            detail.move_to([x, -0.35, 0])
            return VGroup(rect, sym, title_obj, detail)

        d_card = make_card(
            x=-2.65,
            symbol=r"d",
            symbol_color=COLOR_HIGHLIGHT,
            title="what the trace shows",
            detail=body_text("# unsatisfied clauses", size=21, color=TEXT_MUTED),
        )
        h_card = make_card(
            x=2.65,
            symbol=r"h",
            symbol_color=TEXT_ACCENT,
            title="what the proof tracks",
            detail=math(
                r"h=\operatorname{dist}(x,x^*)",
                scale=0.22,
                color=TEXT_MUTED,
            ),
        )
        self.play(
            LaggedStart(FadeIn(d_card), FadeIn(h_card), lag_ratio=0.25),
            run_time=0.75 / ANIM_SPEED,
        )

        analysis_note = body_text(
            "The algorithm never sees the satisfying assignment.  The proof fixes one.",
            size=22,
            color=TEXT_MUTED,
        ).move_to([0, -1.45, 0])
        key = body_text(
            "In a false 3-clause, at least one variable points toward x*.",
            size=24,
            color=TEXT_ACCENT,
        ).move_to([0, -2.20, 0])
        self.play(FadeIn(analysis_note), run_time=0.4 / ANIM_SPEED)
        self.play(FadeIn(key), run_time=0.4 / ANIM_SPEED)
        self.wait(0.45)

        # ---- 17a-A: biased walk setup -----------------------------------
        self.next_slide()
        self.begin_slide(section="3-SAT")

        heading = body_text(
            "Hitting probability from h",
            size=42,
            weight="BOLD",
        ).to_edge(UP, buff=0.7)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        line, ticks, labels, walker, h_x = self._sat_distance_line(y=0.70, r=4)
        h_label = math(r"h=r", scale=0.14, color=COLOR_HIGHLIGHT)
        h_label.move_to([h_x(4), 0.98, 0])
        hit_label = body_text("hit 0", size=20, color=COLOR_TRUE).next_to(
            ticks[0], UP, buff=0.30
        )
        local_note = body_text(
            "A false 3-clause gives left probability at least 1/3.",
            size=22,
            color=TEXT_MUTED,
        ).move_to([0, 1.85, 0])

        self.play(
            FadeIn(local_note),
            FadeIn(line),
            FadeIn(walker),
            FadeIn(h_label),
            FadeIn(hit_label),
            run_time=0.65 / ANIM_SPEED,
        )

        left_arrow = Arrow(
            [h_x(4) - 0.05, 1.15, 0],
            [h_x(3) + 0.05, 1.15, 0],
            buff=0,
            color=COLOR_TRUE,
            stroke_width=2.6,
            max_tip_length_to_length_ratio=0.08,
        )
        right_arrow = Arrow(
            [h_x(4) + 0.05, 1.15, 0],
            [h_x(5) - 0.05, 1.15, 0],
            buff=0,
            color=COLOR_FALSE,
            stroke_width=2.6,
            max_tip_length_to_length_ratio=0.08,
        )
        left_prob = body_text("1/3", size=20, color=COLOR_TRUE).next_to(
            left_arrow, UP, buff=0.10
        )
        right_prob = body_text("2/3", size=20, color=COLOR_FALSE).next_to(
            right_arrow, UP, buff=0.10
        )

        self.play(Create(left_arrow), FadeIn(left_prob), run_time=0.4 / VISUAL_SPEED)
        self.play(Create(right_arrow), FadeIn(right_prob), run_time=0.4 / VISUAL_SPEED)

        want = self._fit_math(
            r"a_r:=\Pr[\text{hit }0\mid H_0=r]",
            scale=0.30,
            max_width=7.8,
            color=TEXT_ACCENT,
        ).move_to([0, -1.20, 0])
        self.play(FadeIn(want), run_time=0.45 / ANIM_SPEED)
        self.wait(0.45)

        # ---- 17a-B: intuition by direct path ----------------------------
        self.next_slide()
        self.begin_slide(section="3-SAT")

        heading = body_text("First, an intuition", size=42, weight="BOLD")
        heading.to_edge(UP, buff=0.7)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        line, ticks, labels, walker, h_x = self._sat_distance_line(y=0.65, r=4)
        self.play(FadeIn(line), FadeIn(walker), run_time=0.5 / ANIM_SPEED)

        path_arrows = []
        for h in range(4, 0, -1):
            path_arrows.append(
                Arrow(
                    [h_x(h) - 0.06, 1.08, 0],
                    [h_x(h - 1) + 0.06, 1.08, 0],
                    buff=0,
                    color=COLOR_TRUE,
                    stroke_width=2.4,
                    max_tip_length_to_length_ratio=0.10,
                )
            )
        probs = [
            body_text("1/3", size=17, color=COLOR_TRUE).next_to(a, UP, buff=0.08)
            for a in path_arrows
        ]
        self.play(
            LaggedStart(
                *[Create(a) for a in path_arrows],
                *[FadeIn(p) for p in probs],
                lag_ratio=0.12,
                run_time=1.0 / VISUAL_SPEED,
            )
        )
        direct = math(
            r"\Pr[\text{this path}]=\left(\frac13\right)^r",
            scale=0.30,
        ).move_to([0, -1.05, 0])
        caption = body_text(
            "Just one path — this is a lower bound.",
            size=22,
            color=TEXT_MUTED,
        ).move_to([0, -1.80, 0])
        hook = body_text(
            "But the recurrence gives the tight answer — let's solve it.",
            size=24,
            color=TEXT_ACCENT,
        ).move_to([0, -2.55, 0])
        self.play(FadeIn(direct), run_time=0.4 / ANIM_SPEED)
        self.play(FadeIn(caption), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(hook), run_time=0.45 / ANIM_SPEED)
        self.wait(0.45)

        # ---- 17a-C1: recurrence setup ----------------------------------
        self.next_slide()
        self.begin_slide(section="3-SAT")

        heading = body_text("Solve the recurrence", size=42, weight="BOLD")
        heading.to_edge(UP, buff=0.7)
        rec = self._fit_math(
            r"a_r=\frac13 a_{r-1}+\frac23 a_{r+1}",
            scale=0.36,
            max_width=7.8,
            color=TEXT_PRIMARY,
        ).move_to([0, 1.05, 0])
        b0 = VGroup(
            math(r"a_0=1", scale=0.30, color=COLOR_TRUE),
            body_text("already at 0", size=18, color=TEXT_MUTED),
        ).arrange(DOWN, buff=0.18)
        b_inf = VGroup(
            math(r"a_\infty=0", scale=0.30, color=COLOR_FALSE),
            body_text("too far to come back", size=18, color=TEXT_MUTED),
        ).arrange(DOWN, buff=0.18)
        boundaries = VGroup(b0, b_inf).arrange(RIGHT, buff=1.25).move_to([0, -0.25, 0])
        try_line = body_text(
            "Linear recurrence — try",
            size=24,
            color=TEXT_ACCENT,
        )
        try_math = math(r"a_r=\lambda^r", scale=0.24, color=TEXT_ACCENT)
        try_group = VGroup(try_line, try_math).arrange(RIGHT, buff=0.18)
        try_group.move_to([0, -1.65, 0])
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)
        self.play(FadeIn(rec), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(boundaries), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(try_group), run_time=0.40 / ANIM_SPEED)
        self.wait(0.45)

        # ---- 17a-C2: characteristic equation ---------------------------
        self.next_slide()
        self.begin_slide(section="3-SAT")

        heading = body_text("Characteristic equation", size=42, weight="BOLD")
        heading.to_edge(UP, buff=0.7)
        eq1 = self._fit_math(
            r"\lambda^r=\frac13\lambda^{r-1}+\frac23\lambda^{r+1}",
            scale=0.25,
            max_width=8.4,
            color=TEXT_PRIMARY,
        ).move_to([0, 1.35, 0])
        eq2 = math(
            r"\lambda=\frac13+\frac23\lambda^2",
            scale=0.29,
            color=TEXT_PRIMARY,
        ).move_to([0, 0.55, 0])
        eq3 = math(
            r"2\lambda^2-3\lambda+1=0",
            scale=0.30,
            color=TEXT_PRIMARY,
        ).move_to([0, -0.15, 0])
        roots = math(
            r"(2\lambda-1)(\lambda-1)=0"
            r"\quad\Rightarrow\quad \lambda=1,\;\frac12",
            scale=0.30,
            color=TEXT_ACCENT,
        ).move_to([0, -1.05, 0])
        general = math(
            r"a_r=A+B\cdot2^{-r}",
            scale=0.34,
            color=TEXT_PRIMARY,
        ).move_to([0, -2.05, 0])
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)
        self.play(FadeIn(eq1), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(eq2), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(eq3), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(roots), run_time=0.45 / VISUAL_SPEED)
        self.play(Indicate(roots, color=TEXT_ACCENT), run_time=0.45 / VISUAL_SPEED)
        self.play(FadeIn(general), run_time=0.35 / ANIM_SPEED)
        self.wait(0.45)

        # ---- 17a-C3: apply boundaries ----------------------------------
        self.next_slide()
        self.begin_slide(section="3-SAT")

        heading = body_text("Apply the boundaries", size=42, weight="BOLD")
        heading.to_edge(UP, buff=0.7)
        general = math(
            r"a_r=A+B\cdot2^{-r}",
            scale=0.34,
            color=TEXT_PRIMARY,
        ).move_to([0, 1.35, 0])
        inf = VGroup(
            math(r"a_\infty=0", scale=0.25, color=TEXT_MUTED),
            math(r"\Rightarrow A=0", scale=0.30, color=TEXT_ACCENT),
        ).arrange(RIGHT, buff=0.35)
        zero = VGroup(
            math(r"a_0=1", scale=0.25, color=TEXT_MUTED),
            math(r"\Rightarrow A+B=1", scale=0.25, color=TEXT_PRIMARY),
            math(r"\Rightarrow B=1", scale=0.30, color=TEXT_ACCENT),
        ).arrange(RIGHT, buff=0.30)
        boundary_steps = VGroup(inf, zero).arrange(DOWN, buff=0.45)
        boundary_steps.move_to([0, 0.15, 0])
        conclusion = math(
            r"\boxed{a_r=2^{-r}}",
            scale=0.42,
            color=TEXT_ACCENT,
        ).move_to([0, -1.55, 0])
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)
        self.play(FadeIn(general), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(inf), run_time=0.40 / ANIM_SPEED)
        self.play(FadeIn(zero), run_time=0.40 / ANIM_SPEED)
        self.play(FadeIn(conclusion), run_time=0.55 / VISUAL_SPEED)
        self.play(Indicate(conclusion, color=TEXT_ACCENT), run_time=0.55 / VISUAL_SPEED)
        self.wait(0.45)

        # ---- 17a-C4: why the root is one half --------------------------
        self.next_slide()
        self.begin_slide(section="3-SAT")

        heading = body_text("Why 1/2?", size=42, weight="BOLD").to_edge(UP, buff=0.7)
        line = body_text(
            "The non-trivial root is the drift ratio.",
            size=25,
            color=TEXT_PRIMARY,
        ).move_to([0, 1.45, 0])
        ratio = math(
            r"\frac{p_{\leftarrow}}{p_{\rightarrow}}"
            r"=\frac{1/3}{2/3}=\frac12",
            scale=0.36,
            color=TEXT_ACCENT,
        ).move_to([0, 0.45, 0])
        intuition_1 = body_text(
            "Each step is twice as likely to push you away.",
            size=23,
            color=TEXT_PRIMARY,
        ).move_to([0, -0.65, 0])
        intuition_2 = body_text(
            "To overcome distance r, you need consistent luck.",
            size=23,
            color=TEXT_PRIMARY,
        ).move_to([0, -1.20, 0])
        general_text = body_text(
            "Biased-walk fact:",
            size=20,
            color=TEXT_MUTED,
        )
        general_formula = math(
            r"\Pr[\text{hit }0\mid r]=\left(\frac{p_\leftarrow}{p_\rightarrow}\right)^r",
            scale=0.16,
            color=TEXT_MUTED,
        )
        general_fact = VGroup(general_text, general_formula).arrange(RIGHT, buff=0.18)
        general_fact.move_to([0, -2.15, 0])
        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(line), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(ratio), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(intuition_1), FadeIn(intuition_2), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(general_fact), run_time=0.35 / ANIM_SPEED)
        self.wait(0.45)

        # ---- 17b-A: what remains after fixed-start analysis -------------
        self.next_slide()
        self.begin_slide(section="3-SAT")

        heading = body_text("What we need", size=42, weight="BOLD")
        heading.to_edge(UP, buff=0.75)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        def make_chain_card(latex: str, label: str, x: float, color: str) -> VGroup:
            rect = Rectangle(
                width=3.0,
                height=1.35,
                stroke_color=color,
                stroke_width=1.8,
                fill_color=color,
                fill_opacity=0.06,
            ).move_to([x, 0.65, 0])
            expr = self._fit_math(latex, scale=0.26, max_width=2.55, color=color)
            expr.move_to(rect.get_center())
            cap = body_text(label, size=18, color=TEXT_MUTED).next_to(
                rect, DOWN, buff=0.18
            )
            return VGroup(rect, expr, cap)

        fixed = make_chain_card(r"a_r=2^{-r}", "fixed start", -3.6, TEXT_ACCENT)
        one_trial = make_chain_card(
            r"p_{\mathrm{success}}=?",
            "one trial",
            0.0,
            TEXT_PRIMARY,
        )
        total = make_chain_card(
            r"T=\left(\frac43\right)^n\cdot\mathrm{poly}(n)",
            "total time",
            3.6,
            TEXT_ACCENT,
        )
        arr1 = Arrow(
            [-2.05, 0.68, 0],
            [-1.50, 0.68, 0],
            buff=0,
            color=TEXT_MUTED,
            stroke_width=1.8,
            max_tip_length_to_length_ratio=0.20,
        )
        arr2 = Arrow(
            [1.50, 0.68, 0],
            [2.05, 0.68, 0],
            buff=0,
            color=TEXT_MUTED,
            stroke_width=1.8,
            max_tip_length_to_length_ratio=0.20,
        )
        arr1_label = VGroup(
            body_text("average over", size=13, color=TEXT_MUTED),
            math(r"H", scale=0.10, color=COLOR_HIGHLIGHT),
        ).arrange(RIGHT, buff=0.06)
        arr1_label.move_to([-1.78, 1.48, 0])
        arr2_label = math(r"1/p", scale=0.13, color=TEXT_MUTED).next_to(
            arr2, UP, buff=0.18
        )
        arr2_label.move_to([1.78, 1.48, 0])
        line1 = body_text(
            "This is for a fixed starting distance.",
            size=22,
            color=TEXT_MUTED,
        ).move_to([0, -1.25, 0])
        line2 = body_text(
            "But the algorithm starts from a random assignment — we need to average.",
            size=23,
            color=TEXT_ACCENT,
        ).move_to([0, -2.05, 0])
        self.play(
            LaggedStart(FadeIn(fixed), FadeIn(one_trial), FadeIn(total), lag_ratio=0.20),
            run_time=0.75 / ANIM_SPEED,
        )
        self.play(
            FadeIn(arr1),
            FadeIn(arr2),
            FadeIn(arr1_label),
            FadeIn(arr2_label),
            run_time=0.35 / ANIM_SPEED,
        )
        self.play(FadeIn(line1), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(line2), run_time=0.40 / ANIM_SPEED)
        self.wait(0.45)

        # ---- 17b-B: random initial distance -----------------------------
        self.next_slide()
        self.begin_slide(section="3-SAT")

        heading = body_text("Random initial distance", size=42, weight="BOLD")
        heading.to_edge(UP, buff=0.75)
        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)

        bit_boxes = []
        for label, wrong in [("x₁", 1), ("x₂", 0), ("x₃", 1), ("x₄", 0)]:
            color = COLOR_HIGHLIGHT if wrong else TEXT_MUTED
            rect = Rectangle(
                width=0.85,
                height=0.85,
                stroke_color=color,
                stroke_width=2.0,
            )
            mark = body_text("wrong" if wrong else "ok", size=14, color=color)
            name = body_text(label, size=17, color=color).next_to(rect, UP, buff=0.08)
            mark.move_to(rect.get_center())
            bit_boxes.append(VGroup(rect, mark, name))
        bits = VGroup(*bit_boxes).arrange(RIGHT, buff=0.35).move_to([-3.0, 0.55, 0])
        right_text = body_text(
            "Each bit matches x* with probability 1/2.",
            size=21,
            color=TEXT_PRIMARY,
        ).move_to([2.65, 1.05, 0])
        h_random = math(
            r"H\sim\mathrm{Bin}(n,\tfrac12)",
            scale=0.32,
            color=COLOR_HIGHLIGHT,
        ).move_to([2.65, 0.25, 0])
        bottom = math(
            r"\boxed{p_{\mathrm{success}}\ge\mathbb{E}[2^{-H}]}",
            scale=0.34,
            color=TEXT_ACCENT,
        ).move_to([0, -1.35, 0])
        hook = body_text(
            "Now compute the expectation.",
            size=22,
            color=TEXT_MUTED,
        ).move_to([0, -2.25, 0])
        self.play(
            LaggedStart(
                *[FadeIn(bit) for bit in bit_boxes],
                lag_ratio=0.25,
                run_time=0.8 / VISUAL_SPEED,
            )
        )
        self.play(FadeIn(right_text), FadeIn(h_random), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(bottom), run_time=0.45 / VISUAL_SPEED)
        self.play(FadeIn(hook), run_time=0.35 / ANIM_SPEED)
        self.wait(0.45)

        # ---- 17b-C1: expand the binomial sum ----------------------------
        self.next_slide()
        self.begin_slide(section="3-SAT")

        heading = body_text("Expand the sum explicitly", size=40, weight="BOLD")
        heading.to_edge(UP, buff=0.7)
        start = self._fit_math(
            r"=2^{-n}\sum_{k=0}^{n}\binom{n}{k}\left(\frac12\right)^k",
            scale=0.30,
            max_width=8.6,
            color=TEXT_PRIMARY,
        ).move_to([0, 1.35, 0])
        prefix = math(r"\mathbb{E}[2^{-H}]", scale=0.26, color=TEXT_PRIMARY)
        prefix.next_to(start, LEFT, buff=0.08)
        terms = [
            math(r"2^{-n}[", scale=0.20, color=TEXT_MUTED),
            math(r"\binom{n}{0}", scale=0.20, color=TEXT_PRIMARY),
            math(r"+", scale=0.18, color=TEXT_MUTED),
            math(r"\binom{n}{1}\frac12", scale=0.20, color=TEXT_PRIMARY),
            math(r"+", scale=0.18, color=TEXT_MUTED),
            math(r"\binom{n}{2}\frac14", scale=0.20, color=TEXT_PRIMARY),
            math(r"+", scale=0.18, color=TEXT_MUTED),
            math(r"\binom{n}{3}\frac18", scale=0.20, color=TEXT_PRIMARY),
            math(r"+\cdots]", scale=0.20, color=TEXT_MUTED),
        ]
        expanded = VGroup(*terms).arrange(RIGHT, buff=0.14).move_to([0, 0.15, 0])
        note = body_text(
            "The coefficients are exactly the binomial coefficients.",
            size=22,
            color=TEXT_MUTED,
        ).move_to([0, -1.35, 0])
        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(prefix), FadeIn(start), run_time=0.40 / ANIM_SPEED)
        self.play(
            LaggedStart(*[FadeIn(t) for t in terms], lag_ratio=0.12),
            run_time=1.0 / VISUAL_SPEED,
        )
        self.play(FadeIn(note), run_time=0.35 / ANIM_SPEED)
        self.wait(0.45)

        # ---- 17b-C2: fold using the binomial theorem --------------------
        self.next_slide()
        self.begin_slide(section="3-SAT")

        heading = body_text("Fold the binomial sum", size=40, weight="BOLD")
        heading.to_edge(UP, buff=0.7)
        sum_expr = self._fit_math(
            r"\sum_{k=0}^{n}\binom{n}{k}\left(\frac12\right)^k",
            scale=0.27,
            max_width=7.4,
            color=TEXT_ACCENT,
        ).move_to([0, 1.05, 0])
        identity_box = Rectangle(
            width=4.7,
            height=1.25,
            stroke_color=TEXT_MUTED,
            stroke_width=1.2,
            fill_color=TEXT_MUTED,
            fill_opacity=0.04,
        ).move_to([-3.05, -0.25, 0])
        identity = math(
            r"(1+x)^n=\sum_{k=0}^{n}\binom{n}{k}x^k",
            scale=0.21,
            color=TEXT_MUTED,
        ).move_to(identity_box.get_center())
        x_sub = math(
            r"x=\frac12",
            scale=0.25,
            color=TEXT_ACCENT,
        ).move_to([2.25, -0.25, 0])
        arrow = Arrow(
            [1.10, -0.25, 0],
            [1.72, -0.25, 0],
            buff=0,
            color=TEXT_MUTED,
            stroke_width=1.8,
        )
        folded = math(
            r"\left(1+\frac12\right)^n=\left(\frac32\right)^n",
            scale=0.31,
            color=TEXT_ACCENT,
        ).move_to([0, -1.55, 0])
        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(sum_expr), run_time=0.40 / ANIM_SPEED)
        self.play(FadeIn(identity_box), FadeIn(identity), run_time=0.40 / ANIM_SPEED)
        self.play(FadeIn(arrow), FadeIn(x_sub), run_time=0.35 / ANIM_SPEED)
        folded_from_sum = sum_expr.copy()
        self.play(Transform(folded_from_sum, folded), run_time=0.75 / VISUAL_SPEED)
        self.wait(0.45)

        # ---- 17b-C3: final success probability --------------------------
        self.next_slide()
        self.begin_slide(section="3-SAT")

        heading = body_text("One restart succeeds with probability", size=38, weight="BOLD")
        heading.to_edge(UP, buff=0.7)
        chain = self._fit_math(
            r"\mathbb{E}[2^{-H}]"
            r"=2^{-n}\cdot\left(\frac32\right)^n"
            r"=\left(\frac34\right)^n",
            scale=0.31,
            max_width=8.5,
            color=TEXT_PRIMARY,
        ).move_to([0, 0.85, 0])
        result = math(
            r"\boxed{p_{\mathrm{success}}\ge\left(\frac34\right)^n}",
            scale=0.37,
            color=TEXT_ACCENT,
        ).move_to([0, -0.45, 0])
        hook = VGroup(
            body_text("Inverse:", size=22, color=TEXT_MUTED),
            math(r"\left(\frac43\right)^n", scale=0.16, color=TEXT_MUTED),
            body_text("restarts on average.", size=22, color=TEXT_MUTED),
        ).arrange(RIGHT, buff=0.16)
        hook.move_to([0, -1.75, 0])
        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(chain), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(result), run_time=0.55 / VISUAL_SPEED)
        self.play(Indicate(result, color=TEXT_ACCENT), run_time=0.55 / VISUAL_SPEED)
        self.play(FadeIn(hook), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

        # ---- 17b-H1: restart count -------------------------------------
        self.next_slide()
        self.begin_slide(section="3-SAT")

        heading = body_text("Restarts", size=42, weight="BOLD").to_edge(UP, buff=0.8)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        success_prob = math(
            r"p_{\mathrm{success}} \gtrsim \left(\frac{3}{4}\right)^n",
            scale=0.34,
            color=TEXT_PRIMARY,
        ).move_to([0, 1.10, 0])
        arrow = Arrow(
            [0, 0.62, 0],
            [0, 0.02, 0],
            buff=0,
            color=TEXT_MUTED,
            stroke_width=2.0,
        )
        repeats = math(
            r"\#\mathrm{restarts}=O\!\left(\left(\frac{4}{3}\right)^n\right)",
            scale=0.34,
            color=TEXT_ACCENT,
        ).move_to([0, -0.55, 0])
        note = body_text(
            "Repeat independent trials until one succeeds.",
            size=22,
            color=TEXT_MUTED,
        ).move_to([0, -1.75, 0])
        self.play(FadeIn(success_prob), run_time=0.4 / ANIM_SPEED)
        self.play(Create(arrow), run_time=0.35 / VISUAL_SPEED)
        self.play(FadeIn(repeats), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(note), run_time=0.35 / ANIM_SPEED)
        self.wait(0.45)

        # ---- 17b-H2: runtime and optimality scale -----------------------
        self.next_slide()
        self.begin_slide(section="3-SAT")

        heading = body_text("Runtime", size=42, weight="BOLD").to_edge(UP, buff=0.8)
        runtime = math(
            r"T(n,m)=O^*\!\left(\left(\frac{4}{3}\right)^n\right)",
            scale=0.36,
            color=TEXT_ACCENT,
        ).move_to([0, 0.80, 0])
        compare = VGroup(
            math(r"2^n", scale=0.30, color=TEXT_MUTED),
            body_text("brute force", size=21, color=TEXT_MUTED),
            body_text("vs.", size=21, color=TEXT_PRIMARY),
            math(r"\left(\frac43\right)^n\approx 1.33^n", scale=0.30, color=TEXT_PRIMARY),
            body_text("random walk", size=21, color=TEXT_PRIMARY),
        ).arrange(RIGHT, buff=0.35)
        compare.move_to([0, -0.55, 0])
        near_opt = body_text(
            "Still exponential; ETH (Exponential Time Hypothesis) rules out subexponential 3-SAT.",
            size=19,
            color=TEXT_MUTED,
        ).move_to([0, -1.75, 0])
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)
        self.play(FadeIn(runtime), run_time=0.5 / ANIM_SPEED)
        self.play(FadeIn(compare), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(near_opt), run_time=0.40 / ANIM_SPEED)
        self.wait(0.5)

    # === Quantum walk helper visuals ===================================
    def _fit_math(
        self,
        latex: str,
        *,
        scale: float,
        max_width: float,
        color: str | None = TEXT_PRIMARY,
    ):
        obj = math(latex, scale=scale, color=color)
        if obj.width > max_width:
            obj.scale(max_width / obj.width)
        return obj

    def _path_graph(
        self,
        count: int,
        *,
        x_left: float,
        x_right: float,
        y: float,
        color: str = TEXT_MUTED,
        dot_color: str = TEXT_PRIMARY,
        radius: float = 0.065,
    ) -> tuple[VGroup, list[Dot]]:
        dots = [
            Dot(
                [
                    x_left + i * (x_right - x_left) / (count - 1),
                    y,
                    0,
                ],
                radius=radius,
                color=dot_color,
            )
            for i in range(count)
        ]
        edges = [
            Line(
                dots[i].get_center(),
                dots[i + 1].get_center(),
                stroke_color=color,
                stroke_width=2.0,
            )
            for i in range(count - 1)
        ]
        return VGroup(*edges, *dots), dots

    def _bar_distribution(
        self,
        probs: list[float],
        *,
        x_center: float,
        y_base: float,
        width: float,
        height: float,
        color: str,
    ) -> VGroup:
        bars = []
        n = len(probs)
        max_prob = max(max(probs), 1e-6)
        step = width / n
        bar_w = step * 0.70
        for i, p in enumerate(probs):
            h = height * p / max_prob
            h = max(h, 0.015)
            x = x_center - width / 2 + step * (i + 0.5)
            rect = Rectangle(
                width=bar_w,
                height=h,
                stroke_width=0,
                fill_color=color,
                fill_opacity=0.75 if p > 1e-5 else 0.08,
            ).move_to([x, y_base + h / 2, 0])
            bars.append(rect)
        return VGroup(*bars)

    def _classical_walk_probs(self, t: int, positions: list[int]) -> list[float]:
        out = []
        for x in positions:
            if abs(x) <= t and (t + x) % 2 == 0:
                k = (t + x) // 2
                out.append(comb(t, k) / (2**t))
            else:
                out.append(0.0)
        return out

    def _quantum_walk_shape(self, t: int, positions: list[int]) -> list[float]:
        if t <= 0:
            return [1.0 if x == 0 else 0.0 for x in positions]
        edge = 0.92 * t
        sigma = 0.95
        center_sigma = max(1.2, t / 4)
        vals = []
        for x in positions:
            left_peak = exp(-((x + edge) ** 2) / (2 * sigma**2))
            right_peak = exp(-((x - edge) ** 2) / (2 * sigma**2))
            middle = 0.13 * exp(-(x**2) / (2 * center_sigma**2))
            ripple = 1.0 + 0.18 * cos(1.55 * x + 0.35 * t)
            vals.append(max(0.0, (left_peak + right_peak + middle) * ripple))
        total = sum(vals) or 1.0
        return [v / total for v in vals]

    def _phasor(
        self,
        center: list[float],
        theta: float,
        *,
        radius: float = 0.18,
        color: str = TEXT_PRIMARY,
        circle_color: str = TEXT_MUTED,
        circle_opacity: float = 0.42,
        stroke_width: float = 2.1,
    ) -> VGroup:
        circle = Circle(radius=radius, color=circle_color, stroke_width=1.0)
        circle.set_stroke(opacity=circle_opacity)
        circle.move_to(center)
        visual_theta = pi / 2 + theta
        end = [
            center[0] + radius * 0.74 * cos(visual_theta),
            center[1] + radius * 0.74 * sin(visual_theta),
            0,
        ]
        arrow = Arrow(
            center,
            end,
            buff=0,
            color=color,
            stroke_width=stroke_width,
            max_tip_length_to_length_ratio=0.34,
        )
        return VGroup(circle, arrow)

    def _phasor_strip(
        self,
        *,
        p: float,
        js: list[int],
        x_left: float,
        x_right: float,
        y: float,
        radius: float,
        color: str,
    ) -> tuple[VGroup, dict[int, float]]:
        if len(js) == 1:
            xs = {js[0]: (x_left + x_right) / 2}
        else:
            xs = {
                j: x_left + i * (x_right - x_left) / (len(js) - 1)
                for i, j in enumerate(js)
            }
        line = Line([x_left, y, 0], [x_right, y, 0], stroke_color=TEXT_MUTED, stroke_width=1.3)
        ticks = []
        labels = []
        phasors = []
        for j in js:
            tick = Line(
                [xs[j], y - 0.07, 0],
                [xs[j], y + 0.07, 0],
                stroke_color=TEXT_MUTED,
                stroke_width=1.1,
            )
            label = body_text(str(j), size=13, color=TEXT_MUTED)
            label.next_to(tick, DOWN, buff=0.08)
            ticks.append(tick)
            labels.append(label)
            phasors.append(
                self._phasor(
                    [xs[j], y + 0.48, 0],
                    p * j,
                    radius=radius,
                    color=color,
                    circle_opacity=0.32,
                    stroke_width=1.8,
                )
            )
        return VGroup(line, *ticks, *labels, *phasors), xs

    def _glued_tree_visual(self, n: int = 3) -> dict[str, object]:
        y_span = 3.0
        left_x0, right_x0 = -5.25, 5.25
        dx = 1.12
        radius = 0.055

        def ys(count: int) -> list[float]:
            if count == 1:
                return [0.0]
            return [
                (i - (count - 1) / 2) * (y_span / (count - 1))
                for i in range(count)
            ]

        left_pos: dict[tuple[int, int], list[float]] = {}
        right_pos: dict[tuple[int, int], list[float]] = {}
        left_nodes: list[VGroup] = []
        right_nodes: list[VGroup] = []
        for level in range(n + 1):
            count = 2**level
            lx = left_x0 + level * dx
            rx = right_x0 - level * dx
            left_level = []
            right_level = []
            for i, y in enumerate(ys(count)):
                lp = [lx, y, 0]
                rp = [rx, y, 0]
                left_pos[(level, i)] = lp
                right_pos[(level, i)] = rp
                left_level.append(Dot(lp, radius=radius, color=TEXT_PRIMARY))
                right_level.append(Dot(rp, radius=radius, color=TEXT_PRIMARY))
            left_nodes.append(VGroup(*left_level))
            right_nodes.append(VGroup(*right_level))

        left_build = [left_nodes[0]]
        right_build = [right_nodes[0]]
        tree_edges = []
        for level in range(1, n + 1):
            left_edges = []
            right_edges = []
            for parent in range(2 ** (level - 1)):
                for child in (2 * parent, 2 * parent + 1):
                    left_edges.append(
                        Line(
                            left_pos[(level - 1, parent)],
                            left_pos[(level, child)],
                            stroke_color=TEXT_MUTED,
                            stroke_width=1.4,
                        )
                    )
                    right_edges.append(
                        Line(
                            right_pos[(level - 1, parent)],
                            right_pos[(level, child)],
                            stroke_color=TEXT_MUTED,
                            stroke_width=1.4,
                        )
                    )
            tree_edges.extend(left_edges)
            tree_edges.extend(right_edges)
            left_build.append(VGroup(*left_edges, left_nodes[level]))
            right_build.append(VGroup(*right_edges, right_nodes[level]))

        # Alternating cycle on the 2^(n+1) middle leaves:
        # L_0, R_perm[0], L_1, R_perm[1], ..., L_{2^n-1}, R_perm[-1].
        # Therefore each middle leaf has exactly two glue-cycle neighbors.
        perm = [0, 3, 6, 1, 4, 7, 2, 5]
        cycle_order: list[tuple[str, int]] = []
        for i, j in enumerate(perm):
            cycle_order.append(("L", i))
            cycle_order.append(("R", j))

        def leaf_point(item: tuple[str, int]) -> list[float]:
            side, idx = item
            return left_pos[(n, idx)] if side == "L" else right_pos[(n, idx)]

        glue_edges = []
        for k, item in enumerate(cycle_order):
            nxt = cycle_order[(k + 1) % len(cycle_order)]
            glue_edges.append(
                Line(
                    leaf_point(item),
                    leaf_point(nxt),
                    stroke_color=COLOR_VAR2 if k % 2 else COLOR_VAR3,
                    stroke_width=1.4,
                )
            )
        glue = VGroup(*glue_edges)
        entrance = body_text("ENTRANCE", size=18, color=COLOR_VAR1).next_to(
            left_nodes[0], LEFT, buff=0.25
        )
        exit_label = body_text("EXIT", size=18, color=COLOR_VAR3).next_to(
            right_nodes[0], RIGHT, buff=0.25
        )
        caption = body_text(
            "Each middle leaf has two glue-cycle edges.",
            size=20,
            color=TEXT_MUTED,
        ).move_to([0, -2.28, 0])
        stats = VGroup(
            self._fit_math(
                r"|V|=2^{n+2}-2\;(=30)",
                scale=0.13,
                max_width=2.7,
                color=TEXT_MUTED,
            ),
            self._fit_math(
                r"\text{glue edges}=2^{n+1}\;(=16)",
                scale=0.13,
                max_width=3.1,
                color=TEXT_ACCENT,
            ),
            self._fit_math(
                r"|E|=3\cdot2^{n+1}-4\;(=44)",
                scale=0.13,
                max_width=3.0,
                color=TEXT_MUTED,
            ),
        ).arrange(RIGHT, buff=0.45)
        stats.move_to([0, 2.16, 0])
        all_nodes = VGroup(*left_nodes, *right_nodes)
        all_tree_edges = VGroup(*tree_edges)
        return {
            "left_build": left_build,
            "right_build": right_build,
            "tree_edges": all_tree_edges,
            "glue": glue,
            "nodes": all_nodes,
            "labels": VGroup(entrance, exit_label),
            "caption": caption,
            "stats": stats,
            "shape": VGroup(all_tree_edges, glue, all_nodes, entrance, exit_label),
            "all": VGroup(
                all_tree_edges,
                glue,
                all_nodes,
                entrance,
                exit_label,
                caption,
                stats,
            ),
        }

    def _glued_tree_cycle_visual(self, n: int = 3) -> dict[str, object]:
        leaf_count = 2**n
        center = [0.0, -0.20, 0.0]
        leaf_radius = 0.88
        level_gap = 0.32
        dot_radius = 0.055
        perm = [0, 3, 6, 1, 4, 7, 2, 5]

        angles = [pi / 2 - k * 2 * pi / (2 * leaf_count) for k in range(2 * leaf_count)]
        left_leaf_slot = {i: 2 * i for i in range(leaf_count)}
        right_leaf_slot = {j: 2 * i + 1 for i, j in enumerate(perm)}

        def polar(radius: float, angle: float) -> list[float]:
            return [
                center[0] + radius * cos(angle),
                center[1] + radius * sin(angle),
                0,
            ]

        def angle_of(point: list[float]) -> float:
            return atan2(point[1] - center[1], point[0] - center[0])

        def radius_of(point: list[float]) -> float:
            dx = point[0] - center[0]
            dy = point[1] - center[1]
            return (dx * dx + dy * dy) ** 0.5

        def mean_angle(slots: list[int]) -> float:
            x = sum(cos(angles[s]) for s in slots)
            y = sum(sin(angles[s]) for s in slots)
            if abs(x) + abs(y) < 1e-6:
                return 0.0
            return atan2(y, x)

        def descendant_slots(side: str, level: int, index: int) -> list[int]:
            span = 2 ** (n - level)
            leaves = range(index * span, (index + 1) * span)
            if side == "L":
                return [left_leaf_slot[i] for i in leaves]
            return [right_leaf_slot[i] for i in leaves]

        def outer_edge(
            start: list[float],
            end: list[float],
            color: str,
            width: float = 0.95,
        ) -> VGroup:
            a0 = angle_of(start)
            a1 = angle_of(end)
            delta = (a1 - a0 + pi) % (2 * pi) - pi
            steps = max(2, int(abs(delta) / (pi / 8)) + 1)
            outer_radius = max(radius_of(start), radius_of(end)) + 0.07

            points = [start, polar(outer_radius, a0)]
            for s in range(1, steps):
                points.append(polar(outer_radius, a0 + delta * s / steps))
            points.extend([polar(outer_radius, a1), end])
            return VGroup(
                *[
                    Line(
                        points[i],
                        points[i + 1],
                        stroke_color=color,
                        stroke_width=width,
                    )
                    for i in range(len(points) - 1)
                ]
            )

        left_pos: dict[tuple[int, int], list[float]] = {}
        right_pos: dict[tuple[int, int], list[float]] = {}
        left_nodes: list[VGroup] = []
        right_nodes: list[VGroup] = []

        for level in range(n + 1):
            left_level = []
            right_level = []
            for i in range(2**level):
                if level == n:
                    lp = polar(leaf_radius, angles[left_leaf_slot[i]])
                    rp = polar(leaf_radius, angles[right_leaf_slot[i]])
                elif level == 0:
                    lp = polar(leaf_radius + n * level_gap + 0.25, pi)
                    rp = polar(leaf_radius + n * level_gap + 0.25, 0)
                else:
                    radius = leaf_radius + (n - level) * level_gap + 0.06
                    lp = polar(radius, mean_angle(descendant_slots("L", level, i)))
                    rp = polar(radius, mean_angle(descendant_slots("R", level, i)))
                left_pos[(level, i)] = lp
                right_pos[(level, i)] = rp
                left_level.append(Dot(lp, radius=dot_radius, color=COLOR_VAR1))
                right_level.append(Dot(rp, radius=dot_radius, color=COLOR_VAR3))
            left_nodes.append(VGroup(*left_level))
            right_nodes.append(VGroup(*right_level))

        tree_edges = []
        for level in range(1, n + 1):
            left_edges = []
            right_edges = []
            for parent in range(2 ** (level - 1)):
                for child in (2 * parent, 2 * parent + 1):
                    left_edges.append(
                        outer_edge(
                            left_pos[(level - 1, parent)],
                            left_pos[(level, child)],
                            COLOR_VAR1,
                        )
                    )
                    right_edges.append(
                        outer_edge(
                            right_pos[(level - 1, parent)],
                            right_pos[(level, child)],
                            COLOR_VAR3,
                        )
                    )
            tree_edges.extend(left_edges)
            tree_edges.extend(right_edges)

        cycle_order: list[tuple[str, int]] = []
        for i, j in enumerate(perm):
            cycle_order.append(("L", i))
            cycle_order.append(("R", j))

        def leaf_point(item: tuple[str, int]) -> list[float]:
            side, idx = item
            return left_pos[(n, idx)] if side == "L" else right_pos[(n, idx)]

        glue_edges = [
            Line(
                leaf_point(item),
                leaf_point(cycle_order[(k + 1) % len(cycle_order)]),
                stroke_color=COLOR_VAR2 if k % 2 else COLOR_VAR3,
                stroke_width=2.4,
            )
            for k, item in enumerate(cycle_order)
        ]
        cycle_guide = Circle(
            radius=leaf_radius,
            stroke_color=TEXT_MUTED,
            stroke_width=1.0,
        ).move_to(center)
        cycle_guide.set_fill(opacity=0).set_stroke(opacity=0.25)

        left_label = body_text("ENTRANCE side", size=17, color=COLOR_VAR1).next_to(
            left_nodes[0], LEFT, buff=0.20
        )
        right_label = body_text("EXIT side", size=17, color=COLOR_VAR3).next_to(
            right_nodes[0], RIGHT, buff=0.20
        )
        leaf_note = body_text(
            "The middle leaves are one alternating cycle.",
            size=24,
            color=TEXT_ACCENT,
        ).move_to([0, -2.42, 0])
        degree_note = body_text(
            "Every leaf has exactly two cycle neighbors.",
            size=20,
            color=TEXT_MUTED,
        ).move_to([0, -2.78, 0])

        all_tree_edges = VGroup(*tree_edges)
        glue = VGroup(*glue_edges)
        all_nodes = VGroup(*left_nodes, *right_nodes)
        labels = VGroup(left_label, right_label)
        return {
            "tree_edges": all_tree_edges,
            "glue": glue,
            "nodes": all_nodes,
            "labels": labels,
            "shape": VGroup(cycle_guide, all_tree_edges, glue, all_nodes, labels),
            "notes": VGroup(leaf_note, degree_note),
            "all": VGroup(
                cycle_guide,
                all_tree_edges,
                glue,
                all_nodes,
                labels,
                leaf_note,
                degree_note,
            ),
        }

    def _column_visual(self, n: int = 3) -> dict[str, object]:
        sizes = [2**i for i in range(n + 1)] + [
            2**i for i in range(n, -1, -1)
        ]
        x_left, x_right = -5.2, 5.2
        y_span = 3.0
        xs = [
            x_left + i * (x_right - x_left) / (len(sizes) - 1)
            for i in range(len(sizes))
        ]

        bands = []
        nodes_by_col: list[VGroup] = []
        counts = []
        labels = []
        for j, (x, count) in enumerate(zip(xs, sizes)):
            band_color = COLOR_VAR1 if j < len(sizes) / 2 else COLOR_VAR3
            band = Rectangle(
                width=0.95,
                height=3.45,
                stroke_width=0,
                fill_color=band_color,
                fill_opacity=0.08,
            ).move_to([x, 0.05, 0])
            bands.append(band)
            if count == 1:
                ys = [0.05]
            else:
                ys = [
                    0.05 + (i - (count - 1) / 2) * (y_span / (count - 1))
                    for i in range(count)
                ]
            dots = VGroup(
                *[
                    Dot([x, y, 0], radius=0.04, color=TEXT_PRIMARY)
                    for y in ys
                ]
            )
            nodes_by_col.append(dots)
            counts.append(
                body_text(str(count), size=17, color=TEXT_MUTED).move_to(
                    [x, 2.05, 0]
                )
            )
            labels.append(
                body_text(str(j), size=15, color=TEXT_MUTED).move_to(
                    [x, -1.95, 0]
                )
            )

        tree_edges = []
        glue_edges = []
        for j in range(len(sizes) - 1):
            left = nodes_by_col[j]
            right = nodes_by_col[j + 1]
            if j == n:
                leaf_count = 2**n
                perm = (
                    [0, 3, 6, 1, 4, 7, 2, 5]
                    if leaf_count == 8
                    else list(range(leaf_count))
                )
                cycle_order: list[tuple[str, int]] = []
                for i, p in enumerate(perm):
                    cycle_order.append(("L", i))
                    cycle_order.append(("R", p))

                def cycle_point(item: tuple[str, int]):
                    side, idx = item
                    return left[idx].get_center() if side == "L" else right[idx].get_center()

                for k, item in enumerate(cycle_order):
                    nxt = cycle_order[(k + 1) % len(cycle_order)]
                    glue_edges.append(
                        Line(
                            cycle_point(item),
                            cycle_point(nxt),
                            stroke_color=COLOR_VAR2 if k % 2 else COLOR_VAR3,
                            stroke_width=1.0,
                        )
                    )
                continue
            if sizes[j + 1] >= sizes[j]:
                for i, dot in enumerate(left):
                    for child in (2 * i, 2 * i + 1):
                        if child < len(right):
                            tree_edges.append(
                                Line(
                                    dot.get_center(),
                                    right[child].get_center(),
                                    stroke_color=TEXT_MUTED,
                                    stroke_width=0.8,
                                )
                            )
            else:
                for i, dot in enumerate(right):
                    for child in (2 * i, 2 * i + 1):
                        if child < len(left):
                            tree_edges.append(
                                Line(
                                    left[child].get_center(),
                                    dot.get_center(),
                                    stroke_color=TEXT_MUTED,
                                    stroke_width=0.8,
                                )
                            )

        entrance = body_text("ENTRANCE", size=15, color=COLOR_VAR1).next_to(
            nodes_by_col[0], LEFT, buff=0.18
        )
        exit_label = body_text("EXIT", size=15, color=COLOR_VAR3).next_to(
            nodes_by_col[-1], RIGHT, buff=0.18
        )
        return {
            "sizes": sizes,
            "xs": xs,
            "bands": VGroup(*bands),
            "nodes": VGroup(*nodes_by_col),
            "nodes_by_col": nodes_by_col,
            "edges": VGroup(*tree_edges, *glue_edges),
            "tree_edges": VGroup(*tree_edges),
            "glue_edges": VGroup(*glue_edges),
            "counts": VGroup(*counts),
            "labels": VGroup(*labels),
            "end_labels": VGroup(entrance, exit_label),
            "all": VGroup(
                *bands,
                *tree_edges,
                *glue_edges,
                *nodes_by_col,
                *counts,
                *labels,
                entrance,
                exit_label,
            ),
        }

    # === Quantum A1: bridge ============================================
    def _slide_quantum_bridge(self) -> None:
        self.begin_slide(section="Bridge")

        heading = body_text(
            "From random walk to quantum walk",
            size=42,
            weight="BOLD",
        ).to_edge(UP, buff=0.85)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        lines = VGroup(
            body_text(
                "Random walk already did algorithmic work for us.",
                size=25,
                color=TEXT_PRIMARY,
            ),
            body_text(
                "But classical motion is diffusive, not ballistic.",
                size=25,
                color=TEXT_PRIMARY,
            ),
            body_text(
                "Can the walk itself propagate faster?",
                size=27,
                color=TEXT_ACCENT,
            ),
        ).arrange(DOWN, buff=0.42).move_to([0, 0.30, 0])
        self.play(
            LaggedStart(
                *[FadeIn(line, shift=0.2 * UP) for line in lines],
                lag_ratio=0.4,
            ),
            run_time=1.0 / ANIM_SPEED,
        )

        hook = body_text(
            "Do we have a quantum analog?",
            size=26,
            color=TEXT_ACCENT,
        ).move_to([0, -2.05, 0])
        self.wait(0.5)
        self.play(FadeIn(hook), run_time=0.4 / ANIM_SPEED)
        self.wait(0.5)

    # === Quantum B1: CTQW equation =====================================
    def _slide_ctqw_equation(self) -> None:
        self.begin_slide(section="CTQW")

        heading = body_text(
            "Continuous-time quantum walk",
            size=42,
            weight="BOLD",
        ).to_edge(UP, buff=0.75)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        classical_label = body_text("classical flow", size=21, color=TEXT_MUTED)
        classical_eq = self._fit_math(
            r"\frac{d p}{d t}=L p",
            scale=0.40,
            max_width=4.8,
            color=TEXT_MUTED,
        )
        classical = VGroup(classical_label, classical_eq).arrange(DOWN, buff=0.22)
        classical.move_to([0, 0.95, 0])
        self.play(FadeIn(classical), run_time=0.5 / ANIM_SPEED)
        self.wait(0.5)

        self.next_slide()
        self.begin_slide(section="CTQW", clear=False)

        quantum_label = body_text("quantum flow", size=21, color=TEXT_PRIMARY)
        quantum_eq = self._fit_math(
            r"{\color[HTML]{79B8FF} i}\frac{d|\psi\rangle}{dt}"
            r"=L|\psi\rangle",
            scale=0.40,
            max_width=5.6,
            color=None,
        )
        quantum = VGroup(quantum_label, quantum_eq).arrange(DOWN, buff=0.22)
        quantum.move_to([0, -0.75, 0])
        self.play(FadeIn(quantum), run_time=0.5 / ANIM_SPEED)
        self.wait(0.5)

        self.next_slide()
        self.begin_slide(section="CTQW", clear=False)

        i_chip = VGroup(
            Rectangle(
                width=0.62,
                height=0.55,
                stroke_color=TEXT_ACCENT,
                stroke_width=2.2,
                fill_color=TEXT_ACCENT,
                fill_opacity=0.08,
            ),
            body_text("i", size=28, color=TEXT_ACCENT, weight="BOLD"),
        )
        i_chip[1].move_to(i_chip[0].get_center())
        i_chip.move_to([-2.25, -0.77, 0])
        note = body_text(
            "only an  i  apart",
            size=23,
            color=TEXT_ACCENT,
        ).move_to([0, -2.30, 0])
        self.play(FadeIn(i_chip), Indicate(i_chip), run_time=0.7 / VISUAL_SPEED)
        self.play(FadeIn(note), run_time=0.4 / ANIM_SPEED)
        self.wait(0.5)

    # === Quantum B2: CTQW properties ===================================
    def _slide_ctqw_properties(self) -> None:
        self.begin_slide(section="CTQW")

        heading = body_text("What this gives us", size=44, weight="BOLD")
        heading.to_edge(UP, buff=0.8)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        solution = self._fit_math(
            r"|\psi(t)\rangle=e^{-iLt}|\psi(0)\rangle",
            scale=0.40,
            max_width=6.2,
            color=TEXT_ACCENT,
        ).move_to([0, 1.25, 0])
        self.play(FadeIn(solution), run_time=0.5 / ANIM_SPEED)

        bullets = VGroup(
            body_text("L Hermitian  →  evolution is unitary", size=24),
            body_text("Normalization is preserved", size=24),
            body_text("Use H = L, or H = A on regular graphs", size=24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.42).move_to([0, -0.25, 0])
        self.play(
            LaggedStart(*[FadeIn(b) for b in bullets], lag_ratio=0.25),
            run_time=0.8 / ANIM_SPEED,
        )

        hook = body_text(
            "Does this actually move differently?",
            size=24,
            color=TEXT_ACCENT,
        ).move_to([0, -2.35, 0])
        self.play(FadeIn(hook), run_time=0.4 / ANIM_SPEED)
        self.wait(0.5)

    # === Quantum C1: 1D setup ==========================================
    def _slide_quantum_1d_setup(self) -> None:
        self.begin_slide(section="Ballistic")

        heading = body_text("1D quantum walk on Z", size=42, weight="BOLD")
        heading.to_edge(UP, buff=0.8)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        graph, dots = self._path_graph(
            11,
            x_left=-4.8,
            x_right=4.8,
            y=0.95,
            dot_color=TEXT_PRIMARY,
        )
        dots[5].set_color(TEXT_ACCENT)
        start_label = body_text("|0>", size=20, color=TEXT_ACCENT).next_to(
            dots[5], UP, buff=0.22
        )
        self.play(FadeIn(graph), FadeIn(start_label), run_time=0.6 / ANIM_SPEED)

        eqs = VGroup(
            self._fit_math(r"H=L", scale=0.30, max_width=2.0),
            self._fit_math(
                r"|\psi(0)\rangle=|0\rangle",
                scale=0.26,
                max_width=3.5,
                color=TEXT_MUTED,
            ),
            self._fit_math(
                r"\Pr[j\text{ at time }t]=|\langle j|\psi(t)\rangle|^2",
                scale=0.24,
                max_width=6.3,
                color=TEXT_ACCENT,
            ),
        ).arrange(DOWN, buff=0.35).move_to([0, -0.75, 0])
        self.play(
            LaggedStart(*[FadeIn(e) for e in eqs], lag_ratio=0.25),
            run_time=0.8 / ANIM_SPEED,
        )
        self.wait(0.5)

    # === Quantum C2: ballistic vs diffusive =============================
    def _slide_ballistic_vs_diffusive(self) -> None:
        self.begin_slide(section="Ballistic")

        heading = body_text("Same setup, two universes", size=42, weight="BOLD")
        heading.to_edge(UP, buff=0.65)
        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)

        panel_w, panel_h = 5.25, 3.35
        left_rect = Rectangle(
            width=panel_w,
            height=panel_h,
            stroke_color=TEXT_MUTED,
            stroke_width=1.2,
        ).move_to([-3.0, -0.05, 0])
        right_rect = Rectangle(
            width=panel_w,
            height=panel_h,
            stroke_color=TEXT_MUTED,
            stroke_width=1.2,
        ).move_to([3.0, -0.05, 0])
        left_title = body_text("CLASSICAL", size=20, color=TEXT_MUTED).next_to(
            left_rect, UP, buff=0.18
        )
        right_title = body_text("QUANTUM", size=20, color=TEXT_ACCENT).next_to(
            right_rect, UP, buff=0.18
        )
        self.play(
            FadeIn(left_rect),
            FadeIn(right_rect),
            FadeIn(left_title),
            FadeIn(right_title),
            run_time=0.4 / ANIM_SPEED,
        )

        positions = list(range(-10, 11))
        time_values = [1, 3, 5, 7, 9]
        base_y = -1.35
        width = 4.65
        height = 1.65

        classical_bars = self._bar_distribution(
            self._classical_walk_probs(time_values[0], positions),
            x_center=-3.0,
            y_base=base_y,
            width=width,
            height=height,
            color=TEXT_MUTED,
        )
        quantum_bars = self._bar_distribution(
            self._quantum_walk_shape(time_values[0], positions),
            x_center=3.0,
            y_base=base_y,
            width=width,
            height=height,
            color=TEXT_ACCENT,
        )
        axis_left = Line([-5.25, base_y, 0], [-0.75, base_y, 0], stroke_color=TEXT_MUTED)
        axis_right = Line([0.75, base_y, 0], [5.25, base_y, 0], stroke_color=TEXT_MUTED)
        t_label = body_text("t = 1", size=24, color=COLOR_HIGHLIGHT).move_to(
            [0, -2.45, 0]
        )
        self.play(
            FadeIn(axis_left),
            FadeIn(axis_right),
            FadeIn(classical_bars),
            FadeIn(quantum_bars),
            FadeIn(t_label),
            run_time=0.6 / VISUAL_SPEED,
        )

        for t in time_values[1:]:
            new_classical = self._bar_distribution(
                self._classical_walk_probs(t, positions),
                x_center=-3.0,
                y_base=base_y,
                width=width,
                height=height,
                color=TEXT_MUTED,
            )
            new_quantum = self._bar_distribution(
                self._quantum_walk_shape(t, positions),
                x_center=3.0,
                y_base=base_y,
                width=width,
                height=height,
                color=TEXT_ACCENT,
            )
            new_label = body_text(
                f"t = {t}", size=24, color=COLOR_HIGHLIGHT
            ).move_to(t_label.get_center())
            self.play(
                Transform(classical_bars, new_classical),
                Transform(quantum_bars, new_quantum),
                FadeOut(t_label),
                FadeIn(new_label),
                run_time=0.85 / VISUAL_SPEED,
            )
            t_label = new_label

        classical_width = body_text("width ~ sqrt(t)", size=21, color=TEXT_MUTED)
        classical_width.move_to([-3.0, 1.00, 0])
        quantum_width = body_text("front ~ t", size=23, color=TEXT_ACCENT)
        quantum_width.move_to([3.0, 1.00, 0])
        self.play(
            FadeIn(classical_width),
            FadeIn(quantum_width),
            run_time=0.4 / ANIM_SPEED,
        )
        self.wait(0.5)

    # === Quantum C2b: plane waves and shift eigenvalues =================
    def _slide_plane_wave_shift(self) -> None:
        def make_heading(left: str, latex: str, right: str) -> VGroup:
            pieces = [
                body_text(left, size=42, weight="BOLD"),
                math(latex, scale=0.25, color=TEXT_PRIMARY),
                body_text(right, size=42, weight="BOLD"),
            ]
            return VGroup(*pieces).arrange(RIGHT, buff=0.18).to_edge(UP, buff=0.7)

        self.begin_slide(section="Ballistic")

        heading = make_heading("What if", r"\psi", "is a plane wave?")
        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)

        p = pi / 4
        lattice_js = list(range(-5, 6))
        wave_js = list(range(-4, 5))
        shifted_js = list(range(-3, 6))
        x_left, x_right = -5.15, 5.15
        y_line = 0.05
        spacing = (x_right - x_left) / (len(lattice_js) - 1)

        def x_of(j: int) -> float:
            return x_left + (j - lattice_js[0]) * spacing

        axis = Line([x_left, y_line, 0], [x_right, y_line, 0], stroke_color=TEXT_MUTED)
        ticks = []
        labels = []
        for j in lattice_js:
            tick = Line(
                [x_of(j), y_line - 0.09, 0],
                [x_of(j), y_line + 0.09, 0],
                stroke_color=TEXT_MUTED,
                stroke_width=1.3,
            )
            label = body_text(str(j), size=15, color=TEXT_MUTED)
            if j == 0:
                label.set_color(TEXT_ACCENT)
            label.next_to(tick, DOWN, buff=0.13)
            ticks.append(tick)
            labels.append(label)
        anchor = Dot([x_of(0), y_line, 0], radius=0.055, color=TEXT_ACCENT)
        lattice = VGroup(axis, *ticks, *labels, anchor)

        phasors = VGroup(
            *[
                self._phasor(
                    [x_of(j), y_line + 0.86, 0],
                    p * j,
                    radius=0.17,
                    color=TEXT_PRIMARY,
                )
                for j in wave_js
            ]
        )
        psi_eq = math(r"\psi_j=e^{ipj}", scale=0.26, color=TEXT_ACCENT).move_to([0, -1.25, 0])
        adjacent = VGroup(
            body_text("Adjacent vertices: phase differs by", size=20, color=TEXT_MUTED),
            math(r"p", scale=0.15, color=COLOR_HIGHLIGHT),
        ).arrange(RIGHT, buff=0.12)
        adjacent.move_to([0, -1.90, 0])

        self.play(FadeIn(lattice), run_time=0.45 / ANIM_SPEED)
        self.play(
            LaggedStart(*[FadeIn(ph) for ph in phasors], lag_ratio=0.08),
            run_time=1.05 / VISUAL_SPEED,
        )
        self.play(FadeIn(psi_eq), FadeIn(adjacent), run_time=0.45 / ANIM_SPEED)
        self.wait(0.45)

        # ---- Beat 2: apply the shift operator --------------------------
        self.next_slide()
        self.begin_slide(section="Ballistic", clear=False, advance_page=True)

        shift_heading = make_heading("Apply", r"T", ": shift by one")
        self.play(Transform(heading, shift_heading), run_time=0.35 / ANIM_SPEED)
        question = math(r"T|\psi\rangle=?", scale=0.28, color=TEXT_PRIMARY).move_to([0, 1.90, 0])
        self.play(FadeIn(question), run_time=0.30 / ANIM_SPEED)
        self.play(phasors.animate.shift(RIGHT * spacing), run_time=1.35 / VISUAL_SPEED)
        shift_eq = math(
            r"(T\psi)_j=\psi_{j-1}",
            scale=0.26,
            color=TEXT_ACCENT,
        ).move_to([0, -1.25, 0])
        self.play(Transform(psi_eq, shift_eq), FadeOut(adjacent), run_time=0.45 / ANIM_SPEED)
        self.wait(0.45)

        # ---- Beat 3: compare with the original wave --------------------
        self.next_slide()
        self.begin_slide(section="Ballistic", clear=False, advance_page=True)

        ghost_heading = make_heading("Compare with", r"\psi", "again")
        self.play(Transform(heading, ghost_heading), run_time=0.35 / ANIM_SPEED)
        ghosts = VGroup(
            *[
                self._phasor(
                    [x_of(j), y_line + 0.86, 0],
                    p * j,
                    radius=0.17,
                    color=TEXT_MUTED,
                    circle_color=TEXT_MUTED,
                    circle_opacity=0.18,
                    stroke_width=1.6,
                ).set_opacity(0.42)
                for j in shifted_js
            ]
        )
        arcs = VGroup(
            *[
                Arc(
                    radius=0.25,
                    start_angle=pi / 2 + p * j,
                    angle=-p,
                    arc_center=[x_of(j), y_line + 0.86, 0],
                    color=COLOR_HIGHLIGHT,
                    stroke_width=2.0,
                )
                for j in shifted_js
            ]
        )
        same_shape = VGroup(
            body_text("Same shape — every phasor rotated by", size=24, color=TEXT_ACCENT),
            math(r"-p", scale=0.18, color=TEXT_ACCENT),
        ).arrange(RIGHT, buff=0.14)
        same_shape.move_to([0, -1.85, 0])
        self.play(FadeIn(ghosts), run_time=0.55 / VISUAL_SPEED)
        self.play(FadeIn(arcs), run_time=0.55 / VISUAL_SPEED)
        self.play(FadeIn(same_shape), run_time=0.40 / ANIM_SPEED)
        self.wait(0.55)

        # ---- Beat 4: translate the visual fact into an eigenvalue -------
        self.next_slide()
        self.begin_slide(section="Ballistic", clear=False, advance_page=True)

        eigen_heading = make_heading("So", r"\psi", "is an eigenstate")
        self.play(
            Transform(heading, eigen_heading),
            FadeOut(question),
            FadeOut(psi_eq),
            FadeOut(same_shape),
            run_time=0.35 / ANIM_SPEED,
        )
        eigen_eq = math(
            r"T|\psi\rangle=e^{-ip}|\psi\rangle",
            scale=0.34,
            color=TEXT_ACCENT,
        ).move_to([0, -1.18, 0])
        eigen_box = SurroundingRectangle(eigen_eq, color=TEXT_ACCENT, buff=0.18, stroke_width=1.4)
        eigen_caption = VGroup(
            body_text("Eigenvalue", size=22, color=TEXT_MUTED),
            math(r"\lambda=e^{-ip}", scale=0.20, color=TEXT_ACCENT),
        ).arrange(RIGHT, buff=0.15)
        eigen_caption.move_to([0, -2.15, 0])
        self.play(FadeIn(eigen_eq), Create(eigen_box), run_time=0.55 / VISUAL_SPEED)
        self.play(FadeIn(eigen_caption), run_time=0.35 / ANIM_SPEED)
        self.wait(0.55)

        # ---- Beat 5: different momenta, different eigenvalues ----------
        self.next_slide()
        self.begin_slide(section="Ballistic")

        heading = body_text("One eigenstate per momentum", size=42, weight="BOLD")
        heading.to_edge(UP, buff=0.7)
        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)

        rows = []
        cases = [
            (r"p=0", 0.0, r"\lambda=1", COLOR_VAR1),
            (r"p=\frac{\pi}{2}", pi / 2, r"\lambda=e^{-i\pi/2}=-i", COLOR_VAR2),
            (r"p=\pi", pi, r"\lambda=e^{-i\pi}=-1", COLOR_VAR3),
        ]
        row_y = [1.20, 0.18, -0.84]
        for (p_label, p_value, eig_label, color), y in zip(cases, row_y):
            label = math(p_label, scale=0.17, color=color).move_to([-4.75, y + 0.10, 0])
            strip, _ = self._phasor_strip(
                p=p_value,
                js=list(range(-2, 3)),
                x_left=-3.35,
                x_right=1.25,
                y=y - 0.18,
                radius=0.13,
                color=color,
            )
            eig = math(eig_label, scale=0.17, color=color).move_to([4.05, y + 0.15, 0])
            rows.append(VGroup(label, strip, eig))

        caption1 = VGroup(
            body_text("Each", size=21, color=TEXT_MUTED),
            math(r"p\in[-\pi,\pi]", scale=0.15, color=TEXT_MUTED),
            body_text("gives one eigenstate of", size=21, color=TEXT_MUTED),
            math(r"T", scale=0.15, color=TEXT_MUTED),
        ).arrange(RIGHT, buff=0.10)
        caption1.move_to([0, -2.05, 0])
        caption2 = body_text(
            "These same states diagonalize L — next, we read off the velocity.",
            size=21,
            color=TEXT_ACCENT,
        ).move_to([0, -2.55, 0])
        self.play(
            LaggedStart(*[FadeIn(row) for row in rows], lag_ratio=0.25),
            run_time=1.0 / ANIM_SPEED,
        )
        self.play(FadeIn(caption1), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(caption2), run_time=0.40 / ANIM_SPEED)
        self.wait(0.55)

    # === Quantum C3: why ballistic =====================================
    def _slide_group_velocity(self) -> None:
        self.begin_slide(section="Ballistic")

        heading = body_text("Why ballistic?", size=44, weight="BOLD")
        heading.to_edge(UP, buff=0.8)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        eig = self._fit_math(
            r"L|\hat p\rangle=2(\cos p-1)|\hat p\rangle",
            scale=0.34,
            max_width=7.0,
        ).move_to([0, 1.05, 0])
        vel = self._fit_math(
            r"v(p)=\frac{d\lambda}{dp}=-2\sin p,\qquad |v|\le 2",
            scale=0.32,
            max_width=7.0,
            color=TEXT_ACCENT,
        ).move_to([0, 0.05, 0])
        self.play(FadeIn(eig), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(vel), run_time=0.45 / ANIM_SPEED)

        compare = VGroup(
            body_text("Classical: diffusion equation", size=24, color=TEXT_MUTED),
            body_text("Quantum: wave equation", size=26, color=TEXT_ACCENT),
        ).arrange(DOWN, buff=0.35).move_to([0, -1.55, 0])
        self.play(
            LaggedStart(*[FadeIn(row) for row in compare], lag_ratio=0.3),
            run_time=0.7 / ANIM_SPEED,
        )
        self.wait(0.5)

    # === Quantum D1: algorithm bridge ==================================
    def _slide_glued_trees_bridge(self) -> None:
        self.begin_slide(section="Glued Trees")

        heading = body_text("From contrast to algorithm", size=42, weight="BOLD")
        heading.to_edge(UP, buff=0.85)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        line2 = VGroup(
            body_text(
                "What kind of graph would actually",
                size=25,
                color=TEXT_PRIMARY,
            ),
            body_text(
                "exploit ballistic transport?",
                size=25,
                color=TEXT_ACCENT,
            ),
        ).arrange(RIGHT, buff=0.16)
        lines = VGroup(
            body_text("1D ballistic is interesting — but it's a toy.", size=26),
            line2,
            body_text(
                "Hard for classical, traversable by ballistic propagation.",
                size=25,
                color=TEXT_PRIMARY,
            ),
        ).arrange(DOWN, buff=0.48).move_to([0, 0.35, 0])
        self.play(
            LaggedStart(
                *[FadeIn(line, shift=0.2 * UP) for line in lines],
                lag_ratio=0.35,
            ),
            run_time=0.9 / ANIM_SPEED,
        )
        closing = body_text("Glued trees.", size=30, color=TEXT_ACCENT)
        closing.move_to([0, -1.75, 0])
        self.wait(0.5)
        self.play(FadeIn(closing), run_time=0.4 / ANIM_SPEED)
        self.wait(0.5)

    # === Quantum D2: glued trees graph =================================
    def _slide_glued_trees_graph(self) -> None:
        self.begin_slide(section="Glued Trees")

        heading = body_text("Glued trees", size=46, weight="BOLD")
        heading.to_edge(UP, buff=0.65)
        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)

        visual = self._glued_tree_visual(n=3)
        left_build = visual["left_build"]  # type: ignore[index]
        right_build = visual["right_build"]  # type: ignore[index]
        self.play(
            FadeIn(left_build[0]),
            FadeIn(right_build[0]),
            run_time=0.4 / VISUAL_SPEED,
        )
        for l_group, r_group in zip(left_build[1:], right_build[1:]):
            self.play(
                FadeIn(l_group),
                FadeIn(r_group),
                run_time=0.45 / VISUAL_SPEED,
            )
        self.play(FadeIn(visual["glue"]), run_time=0.7 / VISUAL_SPEED)
        self.play(
            FadeIn(visual["labels"]),
            FadeIn(visual["stats"]),
            FadeIn(visual["caption"]),
            run_time=0.45 / ANIM_SPEED,
        )

        question = body_text("How do we find EXIT?", size=24, color=TEXT_ACCENT)
        question.move_to([0, -2.85, 0])
        self.play(FadeIn(question), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

    # === Quantum D3: middle cycle ======================================
    def _slide_glued_trees_cycle(self) -> None:
        self.begin_slide(section="Glued Trees")

        heading = body_text("Unfold the glued leaves", size=44, weight="BOLD")
        heading.to_edge(UP, buff=0.72)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        flat = self._glued_tree_visual(n=3)
        flat_shape = flat["shape"]  # type: ignore[index]
        flat_shape.scale(0.92).move_to([0, -0.05, 0])
        self.play(FadeIn(flat_shape), run_time=0.5 / ANIM_SPEED)

        cycle = self._glued_tree_cycle_visual(n=3)
        cycle_shape = cycle["shape"]  # type: ignore[index]
        cycle_shape.move_to([0, -0.10, 0])
        self.play(
            Transform(flat_shape, cycle_shape),
            run_time=1.8 / VISUAL_SPEED,
        )
        self.play(FadeIn(cycle["notes"]), run_time=0.45 / ANIM_SPEED)
        self.wait(0.5)

    # === Quantum D4: black-box access ==================================
    def _slide_black_box_access(self) -> None:
        self.begin_slide(section="Glued Trees")

        heading = body_text("What you can ask", size=44, weight="BOLD")
        heading.to_edge(UP, buff=0.8)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        oracle_box = Rectangle(
            width=4.8,
            height=1.25,
            stroke_color=TEXT_ACCENT,
            stroke_width=2.0,
            fill_color=TEXT_ACCENT,
            fill_opacity=0.06,
        ).move_to([0, 1.0, 0])
        oracle = self._fit_math(
            r"v_c(a)=\text{the }c\text{-th neighbor of }a",
            scale=0.25,
            max_width=4.2,
            color=TEXT_ACCENT,
        ).move_to(oracle_box.get_center())
        self.play(FadeIn(oracle_box), FadeIn(oracle), run_time=0.5 / ANIM_SPEED)

        bullets = VGroup(
            body_text("Vertices have random names.", size=24),
            body_text("ENTRANCE is the only name initially known.", size=24),
            body_text("Random strings usually return “no vertex”.", size=24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.42).move_to([0, -0.55, 0])
        self.play(
            LaggedStart(*[FadeIn(b) for b in bullets], lag_ratio=0.25),
            run_time=0.8 / ANIM_SPEED,
        )

        block = body_text(
            "So BFS cannot jump to the far side.",
            size=24,
            color=TEXT_ACCENT,
        ).move_to([0, -2.35, 0])
        self.play(FadeIn(block), run_time=0.4 / ANIM_SPEED)
        self.wait(0.5)

    # === Quantum D4: classical failure =================================
    def _slide_classical_glued_trees_failure(self) -> None:
        self.begin_slide(section="Glued Trees")

        heading = body_text("The classical problem", size=44, weight="BOLD")
        heading.to_edge(UP, buff=0.8)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        line1 = body_text("A local random walk has tiny mass at EXIT.", size=24)
        pi = self._fit_math(
            r"\pi(v)\propto \deg(v),\qquad \pi(\mathrm{EXIT})=O(2^{-n})",
            scale=0.32,
            max_width=7.2,
            color=TEXT_ACCENT,
        )
        lower = self._fit_math(
            r"\text{classical queries}=2^{\Omega(n)}",
            scale=0.38,
            max_width=5.8,
            color=COLOR_FALSE,
        )
        stronger = body_text(
            "Stronger theorem: even arbitrary classical query algorithms need exponential queries.",
            size=20,
            color=TEXT_MUTED,
        )
        group = VGroup(line1, pi, lower, stronger).arrange(DOWN, buff=0.40)
        group.move_to([0, 0.0, 0])
        self.play(FadeIn(line1), run_time=0.4 / ANIM_SPEED)
        self.play(FadeIn(pi), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(lower), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(stronger), run_time=0.4 / ANIM_SPEED)

        hook = body_text("So why does quantum walk escape?", size=24, color=TEXT_ACCENT)
        hook.move_to([0, -2.45, 0])
        self.play(FadeIn(hook), run_time=0.4 / ANIM_SPEED)
        self.wait(0.5)

    # === Quantum E1: hidden columns ====================================
    def _slide_hidden_columns(self) -> None:
        self.begin_slide(section="Column Subspace")

        heading = body_text(
            "Group vertices by distance from ENTRANCE",
            size=38,
            weight="BOLD",
        ).to_edge(UP, buff=0.65)
        self.play(FadeIn(heading), run_time=0.35 / ANIM_SPEED)

        motivation = body_text(
            "The graph has hidden symmetry — let's exploit it.",
            size=22,
            color=TEXT_ACCENT,
        ).next_to(heading, DOWN, buff=0.22)
        self.play(FadeIn(motivation), run_time=0.35 / ANIM_SPEED)

        visual = self._column_visual(n=3)
        self.play(
            FadeIn(visual["edges"]),
            FadeIn(visual["nodes"]),
            FadeIn(visual["end_labels"]),
            run_time=0.6 / ANIM_SPEED,
        )
        bands = visual["bands"]  # type: ignore[index]
        counts = visual["counts"]  # type: ignore[index]
        labels = visual["labels"]  # type: ignore[index]
        for band, count, label in zip(bands, counts, labels):
            self.play(
                FadeIn(band),
                FadeIn(count),
                FadeIn(label),
                run_time=0.18 / VISUAL_SPEED,
            )

        caption = body_text(
            "Column sizes double, then shrink.",
            size=22,
            color=TEXT_ACCENT,
        ).move_to([0, -2.45, 0])
        self.play(FadeIn(caption), run_time=0.4 / ANIM_SPEED)
        self.wait(0.5)

    # === Quantum E2: column states =====================================
    def _slide_column_states(self) -> None:
        self.begin_slide(section="Column Subspace")

        heading = body_text("Column states", size=44, weight="BOLD")
        heading.to_edge(UP, buff=0.7)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        visual = self._column_visual(n=3)
        all_visual = visual["all"]  # type: ignore[index]
        all_visual.scale(0.88).move_to([0, 0.15, 0])
        self.play(FadeIn(all_visual), run_time=0.5 / ANIM_SPEED)
        self.wait(0.5)

        self.next_slide()
        self.begin_slide(section="Column Subspace", clear=False)

        nodes_by_col = visual["nodes_by_col"]  # type: ignore[index]
        chosen = nodes_by_col[2]
        highlight = SurroundingRectangle(
            chosen,
            color=TEXT_ACCENT,
            buff=0.22,
            stroke_width=2.5,
        )
        self.play(Create(highlight), run_time=0.4 / VISUAL_SPEED)
        self.wait(0.5)

        self.next_slide()
        self.begin_slide(section="Column Subspace", clear=False)

        amp_bars = []
        for dot in chosen:
            x, y, _ = dot.get_center()
            amp_bars.append(
                Line(
                    [x + 0.12, y - 0.18, 0],
                    [x + 0.12, y + 0.18, 0],
                    stroke_color=TEXT_ACCENT,
                    stroke_width=3.0,
                )
            )
        formula = self._fit_math(
            r"|\mathrm{col}_j\rangle="
            r"\frac{1}{\sqrt{N_j}}\sum_{v\in \mathrm{col}_j}|v\rangle",
            scale=0.30,
            max_width=7.6,
            color=TEXT_ACCENT,
        ).move_to([0, -2.35, 0])
        self.play(
            *[Create(bar) for bar in amp_bars],
            FadeIn(formula),
            run_time=0.6 / VISUAL_SPEED,
        )
        self.wait(0.5)

    # === Quantum E3: invariance ========================================
    def _slide_column_invariance(self) -> None:
        self.begin_slide(section="Column Subspace")

        heading = body_text("H preserves the column subspace", size=38, weight="BOLD")
        heading.to_edge(UP, buff=0.7)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        setup = VGroup(
            body_text("Here take", size=20, color=TEXT_MUTED),
            math(r"H=A", scale=0.14, color=TEXT_MUTED),
            body_text("for this graph.  First: one ordinary tree column.", size=20, color=TEXT_MUTED),
        ).arrange(RIGHT, buff=0.12).move_to([0, 2.10, 0])
        self.play(FadeIn(setup), run_time=0.35 / ANIM_SPEED)

        xs = [-4.6, -2.65, -0.55]
        col_labels = ["j-1", "j", "j+1"]
        col_counts = [2, 2, 4]
        cols = []
        for x, label, count in zip(xs, col_labels, col_counts):
            dots = VGroup(
                *[
                    Dot(
                        [x, (i - (count - 1) / 2) * 0.58, 0],
                        radius=0.075,
                        color=TEXT_PRIMARY,
                    )
                    for i in range(count)
                ]
            )
            title = body_text(f"col {label}", size=18, color=TEXT_MUTED).next_to(
                dots, UP, buff=0.28
            )
            cols.append(VGroup(dots, title))
        graph = VGroup(*cols).move_to([-2.55, 0.20, 0])
        self.play(FadeIn(graph), run_time=0.5 / ANIM_SPEED)

        mid_dot = cols[1][0][0]
        focus = SurroundingRectangle(mid_dot, color=COLOR_HIGHLIGHT, buff=0.08)
        prompt = body_text(
            "What does A do to one vertex?",
            size=24,
            color=TEXT_ACCENT,
        ).move_to([3.15, 0.75, 0])
        self.play(
            Create(focus),
            FadeIn(prompt),
            run_time=0.35 / VISUAL_SPEED,
        )
        self.wait(0.5)

        self.next_slide()
        self.begin_slide(section="Column Subspace", clear=False)

        self.play(FadeOut(prompt), run_time=0.25 / ANIM_SPEED)
        one_edges = VGroup(
            Arrow(
                mid_dot.get_center(),
                cols[0][0][0].get_center(),
                buff=0.10,
                color=COLOR_TRUE,
                stroke_width=2.5,
            ),
            Arrow(
                mid_dot.get_center(),
                cols[2][0][0].get_center(),
                buff=0.10,
                color=TEXT_ACCENT,
                stroke_width=2.5,
            ),
            Arrow(
                mid_dot.get_center(),
                cols[2][0][1].get_center(),
                buff=0.10,
                color=TEXT_ACCENT,
                stroke_width=2.5,
            ),
        )
        parent_note = body_text("1 parent", size=28, color=COLOR_TRUE).move_to(
            [2.45, 0.85, 0]
        )
        child_note = body_text("2 children", size=28, color=TEXT_ACCENT).move_to(
            [2.55, 0.10, 0]
        )
        local_note = body_text(
            "local rule only",
            size=18,
            color=TEXT_MUTED,
        ).move_to([2.50, -0.62, 0])
        local_group = VGroup(parent_note, child_note, local_note)
        self.play(
            *[Create(e) for e in one_edges],
            FadeIn(local_group),
            run_time=0.55 / VISUAL_SPEED,
        )
        self.wait(0.5)

        self.next_slide()
        self.begin_slide(section="Column Subspace", clear=False)

        all_edges = []
        for i, dot in enumerate(cols[1][0]):
            all_edges.append(
                Line(
                    dot.get_center(),
                    cols[0][0][i].get_center(),
                    stroke_color=COLOR_TRUE,
                    stroke_width=1.5,
                )
            )
            all_edges.append(
                Line(
                    dot.get_center(),
                    cols[2][0][2 * i].get_center(),
                    stroke_color=TEXT_ACCENT,
                    stroke_width=1.5,
                )
            )
            all_edges.append(
                Line(
                    dot.get_center(),
                    cols[2][0][2 * i + 1].get_center(),
                    stroke_color=TEXT_ACCENT,
                    stroke_width=1.5,
                )
            )
        gather = body_text(
            "Uniform in  →  uniform out",
            size=30,
            color=TEXT_ACCENT,
        ).move_to([2.55, 0.45, 0])
        gather_detail = body_text(
            "No individual vertex is special.",
            size=18,
            color=TEXT_MUTED,
        ).move_to([2.55, -0.22, 0])
        self.play(
            FadeOut(focus),
            FadeOut(one_edges),
            FadeOut(local_group),
            *[Create(e) for e in all_edges],
            FadeIn(gather),
            FadeIn(gather_detail),
            run_time=0.65 / VISUAL_SPEED,
        )
        self.wait(0.5)

        self.next_slide()
        self.begin_slide(section="Column Subspace", clear=False)

        self.play(
            FadeOut(graph),
            *[FadeOut(edge) for edge in all_edges],
            FadeOut(gather),
            FadeOut(gather_detail),
            run_time=0.35 / ANIM_SPEED,
        )

        right_title = body_text("to col j+1", size=24, color=TEXT_ACCENT)
        right_eq = self._fit_math(
            r"\frac{1}{\sqrt{N_j}}"
            r"=\frac{\sqrt{2}}{\sqrt{N_{j+1}}}",
            scale=0.32,
            max_width=3.7,
            color=TEXT_PRIMARY,
        )
        right_reason = body_text(
            "next column is twice as large",
            size=17,
            color=TEXT_MUTED,
        )
        right_card = VGroup(right_title, right_eq, right_reason).arrange(
            DOWN, buff=0.25
        )
        right_card.move_to([-2.85, 0.05, 0])

        left_title = body_text("to col j-1", size=24, color=COLOR_TRUE)
        left_eq = self._fit_math(
            r"\frac{2}{\sqrt{N_j}}"
            r"=\frac{\sqrt{2}}{\sqrt{N_{j-1}}}",
            scale=0.32,
            max_width=3.7,
            color=TEXT_PRIMARY,
        )
        left_reason = body_text(
            "two children feed one parent",
            size=17,
            color=TEXT_MUTED,
        )
        left_card = VGroup(left_title, left_eq, left_reason).arrange(
            DOWN, buff=0.25
        )
        left_card.move_to([2.85, 0.05, 0])
        coeff_group = VGroup(right_card, left_card)
        self.play(FadeIn(right_card), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(left_card), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

        self.next_slide()
        self.begin_slide(section="Column Subspace", clear=False)

        formula = self._fit_math(
            r"A|\mathrm{col}_j\rangle="
            r"\sqrt{2}|\mathrm{col}_{j-1}\rangle"
            r"+\sqrt{2}|\mathrm{col}_{j+1}\rangle",
            scale=0.30,
            max_width=8.6,
            color=TEXT_ACCENT,
        ).move_to([0, 0.20, 0])
        formula_label = body_text(
            "ordinary tree columns",
            size=24,
            color=TEXT_MUTED,
        ).move_to([0, 1.30, 0])
        middle_note = body_text(
            "Glued middle: center coupling is 2, but the column subspace is still closed.",
            size=18,
            color=TEXT_MUTED,
        ).move_to([0, -1.10, 0])
        meaning = body_text(
            "Exponentially many vertices, but only O(n) relevant dimensions.",
            size=21,
            color=TEXT_ACCENT,
        ).move_to([0, -1.75, 0])
        self.play(
            FadeOut(coeff_group),
            FadeIn(formula_label),
            FadeIn(formula),
            run_time=0.55 / ANIM_SPEED,
        )
        self.play(FadeIn(middle_note), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(meaning), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

        # ---- Coefficient proof A1: tree-region edge count ----------------
        self.next_slide()
        self.begin_slide(section="Column Subspace")

        heading = body_text(
            r"Where does √2 come from?",
            size=40,
            weight="BOLD",
        ).to_edge(UP, buff=0.7)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        x_cols = [-4.20, -2.60, -0.85]
        counts = [1, 2, 4]
        labels = ["col j-1", "col j", "col j+1"]
        tree_cols = []
        for x, count, label in zip(x_cols, counts, labels):
            dots = VGroup(
                *[
                    Dot(
                        [x, (i - (count - 1) / 2) * 0.52, 0],
                        radius=0.075,
                        color=COLOR_HIGHLIGHT if label == "col j" else TEXT_PRIMARY,
                    )
                    for i in range(count)
                ]
            )
            title = body_text(label, size=16, color=TEXT_MUTED).next_to(
                dots, UP, buff=0.24
            )
            tree_cols.append(VGroup(dots, title))
        local_graph = VGroup(*tree_cols).move_to([-2.35, -0.05, 0])
        left_dots = tree_cols[0][0]
        mid_dots = tree_cols[1][0]
        right_dots = tree_cols[2][0]
        self.play(FadeIn(local_graph), run_time=0.45 / ANIM_SPEED)

        parent_arrows = VGroup(
            *[
                Arrow(
                    dot.get_center(),
                    left_dots[0].get_center(),
                    buff=0.09,
                    color=COLOR_TRUE,
                    stroke_width=2.0,
                    max_tip_length_to_length_ratio=0.10,
                )
                for dot in mid_dots
            ]
        )
        child_arrows = VGroup()
        for i, dot in enumerate(mid_dots):
            child_arrows.add(
                Arrow(
                    dot.get_center(),
                    right_dots[2 * i].get_center(),
                    buff=0.09,
                    color=TEXT_ACCENT,
                    stroke_width=2.0,
                    max_tip_length_to_length_ratio=0.10,
                )
            )
            child_arrows.add(
                Arrow(
                    dot.get_center(),
                    right_dots[2 * i + 1].get_center(),
                    buff=0.09,
                    color=TEXT_ACCENT,
                    stroke_width=2.0,
                    max_tip_length_to_length_ratio=0.10,
                )
            )
        mult_parent = body_text("parent multiplicity 2", size=24, color=COLOR_TRUE)
        mult_child = body_text("child multiplicity 1", size=24, color=TEXT_ACCENT)
        mult_group = VGroup(mult_parent, mult_child).arrange(DOWN, buff=0.20)
        mult_group.move_to([2.65, 0.80, 0])
        graph_note = body_text(
            "Count edges first. Normalize later.",
            size=20,
            color=TEXT_MUTED,
        ).move_to([2.65, -0.70, 0])
        self.play(
            Create(parent_arrows),
            Create(child_arrows),
            FadeIn(mult_group),
            run_time=0.75 / VISUAL_SPEED,
        )
        self.play(FadeIn(graph_note), run_time=0.35 / ANIM_SPEED)
        self.wait(0.45)

        # ---- Coefficient proof A2: normalization ------------------------
        self.next_slide()
        self.begin_slide(section="Column Subspace")

        heading = body_text("Normalize the two directions", size=40, weight="BOLD")
        heading.to_edge(UP, buff=0.7)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        left_title = body_text("to col j-1", size=26, color=COLOR_TRUE)
        left_eq = math(
            r"\frac{2}{\sqrt{N_j}}=\frac{\sqrt2}{\sqrt{N_{j-1}}}",
            scale=0.36,
            color=TEXT_PRIMARY,
        )
        left_note = body_text(
            "two children feed one parent",
            size=20,
            color=TEXT_MUTED,
        )
        left_card = VGroup(left_title, left_eq, left_note).arrange(DOWN, buff=0.38)
        left_card.move_to([-3.15, 0.05, 0])

        right_title = body_text("to col j+1", size=26, color=TEXT_ACCENT)
        right_eq = math(
            r"\frac{1}{\sqrt{N_j}}=\frac{\sqrt2}{\sqrt{N_{j+1}}}",
            scale=0.36,
            color=TEXT_PRIMARY,
        )
        right_note = body_text(
            "next column is twice as large",
            size=20,
            color=TEXT_MUTED,
        )
        right_card = VGroup(right_title, right_eq, right_note).arrange(DOWN, buff=0.38)
        right_card.move_to([3.15, 0.05, 0])

        self.play(FadeIn(left_card), run_time=0.50 / ANIM_SPEED)
        self.play(FadeIn(right_card), run_time=0.50 / ANIM_SPEED)
        self.wait(0.45)

        # ---- Coefficient proof A3: tree-region rule ---------------------
        self.next_slide()
        self.begin_slide(section="Column Subspace")

        heading = body_text("Ordinary tree columns", size=40, weight="BOLD")
        heading.to_edge(UP, buff=0.7)
        formula = self._fit_math(
            r"A|\mathrm{col}_j\rangle="
            r"\sqrt2|\mathrm{col}_{j-1}\rangle"
            r"+\sqrt2|\mathrm{col}_{j+1}\rangle",
            scale=0.32,
            max_width=8.2,
            color=TEXT_ACCENT,
        ).move_to([0, 0.35, 0])
        same = body_text(
            "Same hopping strength in both directions.",
            size=22,
            color=TEXT_MUTED,
        ).move_to([0, -1.15, 0])
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)
        self.play(FadeIn(formula), run_time=0.55 / VISUAL_SPEED)
        self.play(FadeIn(same), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

        # ---- Coefficient proof B1: center cycle visual ------------------
        self.next_slide()
        self.begin_slide(section="Column Subspace")

        heading = body_text("The cycle middle is different", size=40, weight="BOLD")
        heading.to_edge(UP, buff=0.7)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        x_cols = [-4.8, -3.35, -1.75, -0.30]
        counts = [2, 4, 4, 2]
        labels = ["n-1", "n", "n+1", "n+2"]
        cycle_cols = []
        for x, count, label in zip(x_cols, counts, labels):
            dots = VGroup(
                *[
                    Dot(
                        [x, (i - (count - 1) / 2) * 0.48, 0],
                        radius=0.068,
                        color=TEXT_ACCENT if label in {"n", "n+1"} else TEXT_PRIMARY,
                    )
                    for i in range(count)
                ]
            )
            title = body_text(f"col {label}", size=15, color=TEXT_MUTED).next_to(
                dots, UP, buff=0.22
            )
            cycle_cols.append(VGroup(dots, title))
        cycle_graph = VGroup(*cycle_cols).move_to([-1.90, -0.05, 0])
        left_leaf = cycle_cols[1][0]
        right_leaf = cycle_cols[2][0]
        self.play(FadeIn(cycle_graph), run_time=0.45 / ANIM_SPEED)

        cycle_edges = VGroup()
        pattern = [(0, 0), (0, 1), (1, 1), (1, 2), (2, 2), (2, 3), (3, 3), (3, 0)]
        for i, j in pattern:
            cycle_edges.add(
                Line(
                    left_leaf[i].get_center(),
                    right_leaf[j].get_center(),
                    stroke_color=COLOR_HIGHLIGHT,
                    stroke_width=2.1,
                )
            )
        cycle_caption = body_text(
            "Alternating cycle gives multiplicity 2.",
            size=24,
            color=COLOR_HIGHLIGHT,
        ).move_to([2.85, 0.70, 0])
        cycle_note = body_text(
            "This is the only non-uniform coupling.",
            size=20,
            color=TEXT_MUTED,
        ).move_to([2.85, -0.45, 0])
        self.play(
            Create(cycle_edges),
            FadeIn(cycle_caption),
            run_time=0.80 / VISUAL_SPEED,
        )
        self.play(FadeIn(cycle_note), run_time=0.35 / ANIM_SPEED)
        self.wait(0.45)

        # ---- Coefficient proof B2: center cycle rule --------------------
        self.next_slide()
        self.begin_slide(section="Column Subspace")

        heading = body_text("Middle coupling", size=40, weight="BOLD")
        heading.to_edge(UP, buff=0.7)
        formula_mid = self._fit_math(
            r"A|\mathrm{col}_n\rangle="
            r"\sqrt2|\mathrm{col}_{n-1}\rangle"
            r"+2|\mathrm{col}_{n+1}\rangle",
            scale=0.32,
            max_width=8.2,
            color=TEXT_ACCENT,
        ).move_to([0, 0.70, 0])
        conclusion_1 = body_text(
            "Center hopping rate: 2 instead of √2.",
            size=23,
            color=TEXT_PRIMARY,
        ).move_to([0, -0.45, 0])
        conclusion_2 = body_text(
            "The reduced 1D walk is almost uniform.",
            size=21,
            color=TEXT_MUTED,
        ).move_to([0, -1.15, 0])
        conclusion_3 = body_text(
            "Still O(n) ballistic transport.",
            size=23,
            color=TEXT_ACCENT,
        ).move_to([0, -1.85, 0])
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)
        self.play(FadeIn(formula_mid), run_time=0.45 / ANIM_SPEED)
        self.play(FadeIn(conclusion_1), run_time=0.35 / ANIM_SPEED)
        self.play(FadeIn(conclusion_2), run_time=0.30 / ANIM_SPEED)
        self.play(FadeIn(conclusion_3), run_time=0.35 / ANIM_SPEED)
        self.wait(0.5)

    # === Quantum E4: reduced 1D walk ===================================
    def _slide_reduced_1d_walk(self) -> None:
        self.begin_slide(section="Column Subspace")

        heading = body_text("Now it's just a 1D walk", size=42, weight="BOLD")
        heading.to_edge(UP, buff=0.7)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        visual = self._column_visual(n=3)
        xs = visual["xs"]  # type: ignore[index]
        col_markers = VGroup(
            *[
                Circle(
                    radius=0.13 + 0.025 * min(size, 8),
                    stroke_color=TEXT_ACCENT,
                    stroke_width=2.0,
                    fill_color=TEXT_ACCENT,
                    fill_opacity=0.08,
                ).move_to([x * 0.72, 1.15, 0])
                for x, size in zip(xs, visual["sizes"])  # type: ignore[index]
            ]
        )
        col_labels = VGroup(
            *[
                body_text(str(j), size=13, color=TEXT_MUTED).move_to(
                    [x * 0.72, 0.73, 0]
                )
                for j, x in enumerate(xs)
            ]
        )
        top = VGroup(col_markers, col_labels)
        self.play(FadeIn(top), run_time=0.5 / ANIM_SPEED)

        graph, dots = self._path_graph(
            8,
            x_left=-4.3,
            x_right=4.3,
            y=-0.45,
            color=TEXT_MUTED,
            dot_color=TEXT_PRIMARY,
            radius=0.075,
        )
        path_labels = VGroup(
            body_text("ENTRANCE", size=16, color=COLOR_VAR1).next_to(
                dots[0], DOWN, buff=0.22
            ),
            body_text("EXIT", size=16, color=COLOR_VAR3).next_to(
                dots[-1], DOWN, buff=0.22
            ),
        )
        arrow = Arrow(
            [0, 0.62, 0],
            [0, -0.05, 0],
            buff=0,
            color=TEXT_ACCENT,
            stroke_width=2.5,
        )
        self.play(FadeIn(arrow), run_time=0.3 / ANIM_SPEED)
        self.play(FadeIn(graph), FadeIn(path_labels), run_time=0.5 / ANIM_SPEED)

        center_edge = Line(
            dots[3].get_center(),
            dots[4].get_center(),
            stroke_color=COLOR_HIGHLIGHT,
            stroke_width=3.0,
        )
        sqrt_labels = VGroup()
        for i in range(len(dots) - 1):
            if i == 3:
                continue
            midpoint = (dots[i].get_center() + dots[i + 1].get_center()) / 2
            label = math(r"\sqrt{2}", scale=0.11, color=TEXT_MUTED)
            label.move_to([midpoint[0], midpoint[1] + 0.26, 0])
            sqrt_labels.add(label)
        edge_note = VGroup(
            body_text("edge weights:", size=18, color=TEXT_MUTED),
            math(r"\sqrt{2}", scale=0.12, color=TEXT_MUTED),
            body_text("except center", size=18, color=TEXT_MUTED),
            math(r"2", scale=0.12, color=COLOR_HIGHLIGHT),
        ).arrange(RIGHT, buff=0.14)
        edge_note.move_to([0, -1.15, 0])
        center_label = math(r"2", scale=0.13, color=COLOR_HIGHLIGHT).next_to(
            center_edge, UP, buff=0.12
        )
        self.play(
            FadeIn(sqrt_labels),
            Create(center_edge),
            FadeIn(center_label),
            FadeIn(edge_note),
            run_time=0.45 / ANIM_SPEED,
        )

        amp = Dot(dots[0].get_center(), radius=0.13, color=TEXT_ACCENT)
        self.play(FadeIn(amp), run_time=0.25 / ANIM_SPEED)
        for dot in dots[1:]:
            self.play(amp.animate.move_to(dot.get_center()), run_time=0.18 / VISUAL_SPEED)

        conclusion = body_text(
            "Ballistic transport reaches EXIT in O(n) time.",
            size=23,
            color=TEXT_ACCENT,
        ).move_to([0, -2.35, 0])
        self.play(FadeIn(conclusion), run_time=0.4 / ANIM_SPEED)
        self.wait(0.5)

    # === Quantum E4b: why quantum can exploit columns ===================
    def _slide_quantum_vs_classical_columns(self) -> None:
        self.begin_slide(section="Column Subspace")

        heading = body_text(
            "Why can't classical do this?",
            size=42,
            weight="BOLD",
        ).to_edge(UP, buff=0.65)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        divider = Line(
            [0, 2.05, 0],
            [0, -2.20, 0],
            stroke_color=TEXT_MUTED,
            stroke_width=1.0,
        )

        left_title = body_text("Classical", size=28, color=COLOR_FALSE, weight="BOLD")
        right_title = body_text("Quantum", size=28, color=TEXT_ACCENT, weight="BOLD")
        left_title.move_to([-3.2, 1.58, 0])
        right_title.move_to([3.2, 1.58, 0])

        left_line_top = VGroup(
            body_text("To act on column", size=18, color=TEXT_PRIMARY),
            math(r"j", scale=0.11, color=TEXT_PRIMARY),
            body_text(":", size=18, color=TEXT_PRIMARY),
        ).arrange(RIGHT, buff=0.06)
        left_line_bottom = VGroup(
            body_text("enumerate", size=18, color=TEXT_PRIMARY),
            math(r"2^j", scale=0.12, color=COLOR_FALSE),
            body_text("vertices.", size=18, color=TEXT_PRIMARY),
        ).arrange(RIGHT, buff=0.08)
        left_line = VGroup(left_line_top, left_line_bottom).arrange(DOWN, buff=0.12)
        left_line.move_to([-3.2, 0.98, 0])

        right_line = VGroup(
            body_text(
                "Unitary evolution distributes amplitude",
                size=18,
                color=TEXT_PRIMARY,
            ),
            body_text(
                "across the entire column at once.",
                size=18,
                color=TEXT_PRIMARY,
            ),
        ).arrange(DOWN, buff=0.12)
        right_line.move_to([3.2, 0.98, 0])

        def column_band(x: float, *, color: str, fill_opacity: float) -> tuple[VGroup, list[Dot]]:
            band = Rectangle(
                width=1.05,
                height=1.72,
                stroke_color=color,
                stroke_width=1.8,
                fill_color=color,
                fill_opacity=fill_opacity,
            ).move_to([x, -0.28, 0])
            dots = [
                Dot(
                    [x, -0.28 + (i - 3.5) * 0.21, 0],
                    radius=0.055,
                    color=TEXT_PRIMARY,
                )
                for i in range(8)
            ]
            label = math(r"\mathrm{col}_j", scale=0.14, color=TEXT_MUTED)
            label.next_to(band, DOWN, buff=0.16)
            return VGroup(band, label, *dots), dots

        classical_column, classical_dots = column_band(
            -3.2,
            color=TEXT_MUTED,
            fill_opacity=0.04,
        )
        quantum_column, quantum_dots = column_band(
            3.2,
            color=TEXT_ACCENT,
            fill_opacity=0.04,
        )
        quantum_glow = Rectangle(
            width=1.17,
            height=1.84,
            stroke_color=TEXT_ACCENT,
            stroke_width=3.0,
            fill_color=TEXT_ACCENT,
            fill_opacity=0.16,
        ).move_to([3.2, -0.28, 0])
        quantum_amp = VGroup(
            *[
                Circle(
                    radius=0.10,
                    stroke_color=TEXT_ACCENT,
                    stroke_width=2.0,
                    fill_color=TEXT_ACCENT,
                    fill_opacity=0.20,
                ).move_to(dot.get_center())
                for dot in quantum_dots
            ]
        )

        classical_cost = VGroup(
            body_text("Cost per column:", size=20, color=TEXT_MUTED),
            math(r"2^j", scale=0.16, color=COLOR_FALSE),
        ).arrange(RIGHT, buff=0.14)
        classical_cost.move_to([-3.2, -1.78, 0])
        quantum_cost = VGroup(
            body_text("Cost per column:", size=20, color=TEXT_MUTED),
            math(r"O(1)", scale=0.16, color=TEXT_ACCENT),
        ).arrange(RIGHT, buff=0.14)
        quantum_cost.move_to([3.2, -1.78, 0])

        self.play(
            FadeIn(divider),
            FadeIn(left_title),
            FadeIn(right_title),
            FadeIn(left_line),
            FadeIn(right_line),
            run_time=0.55 / ANIM_SPEED,
        )
        self.play(
            FadeIn(classical_column),
            FadeIn(quantum_column),
            run_time=0.45 / ANIM_SPEED,
        )

        walker = Dot(classical_dots[0].get_center(), radius=0.095, color=COLOR_HIGHLIGHT)
        ellipsis = body_text("...", size=26, color=COLOR_FALSE).move_to([-3.2, -1.42, 0])
        self.play(FadeIn(walker), run_time=0.20 / ANIM_SPEED)
        for dot in classical_dots[1:5]:
            self.play(
                walker.animate.move_to(dot.get_center()),
                run_time=0.35 / VISUAL_SPEED,
            )
        self.play(FadeIn(ellipsis), FadeIn(classical_cost), run_time=0.35 / ANIM_SPEED)

        self.play(
            FadeIn(quantum_glow),
            FadeIn(quantum_amp),
            FadeIn(quantum_cost),
            run_time=0.75 / VISUAL_SPEED,
        )

        bottom = body_text(
            "Same column structure. Different access cost.",
            size=29,
            color=TEXT_ACCENT,
            weight="BOLD",
        ).move_to([0, -2.45, 0])
        self.play(FadeIn(bottom), run_time=0.45 / ANIM_SPEED)
        self.wait(0.55)

    # === Quantum E5: verdict ===========================================
    def _slide_exponential_separation(self) -> None:
        self.begin_slide(section="Column Subspace")

        heading = body_text("Exponential separation", size=44, weight="BOLD")
        heading.to_edge(UP, buff=0.8)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        classical_box = Rectangle(
            width=4.7,
            height=2.0,
            stroke_color=COLOR_FALSE,
            stroke_width=2.0,
            fill_color=COLOR_FALSE,
            fill_opacity=0.06,
        ).move_to([-2.7, 0.25, 0])
        quantum_box = Rectangle(
            width=4.7,
            height=2.0,
            stroke_color=TEXT_ACCENT,
            stroke_width=2.0,
            fill_color=TEXT_ACCENT,
            fill_opacity=0.06,
        ).move_to([2.7, 0.25, 0])
        classical_title = body_text("Classical", size=25, color=COLOR_FALSE)
        quantum_title = body_text("Quantum walk", size=25, color=TEXT_ACCENT)
        classical_runtime = self._fit_math(
            r"2^{\Omega(n)}\ \text{queries}",
            scale=0.32,
            max_width=3.6,
            color=COLOR_FALSE,
        )
        quantum_runtime = self._fit_math(
            r"\mathrm{poly}(n)\ \text{queries}",
            scale=0.32,
            max_width=3.6,
            color=TEXT_ACCENT,
        )
        VGroup(classical_title, classical_runtime).arrange(DOWN, buff=0.35).move_to(
            classical_box.get_center()
        )
        VGroup(quantum_title, quantum_runtime).arrange(DOWN, buff=0.35).move_to(
            quantum_box.get_center()
        )
        self.play(
            FadeIn(classical_box),
            FadeIn(quantum_box),
            FadeIn(classical_title),
            FadeIn(quantum_title),
            run_time=0.5 / ANIM_SPEED,
        )
        self.play(
            FadeIn(classical_runtime),
            FadeIn(quantum_runtime),
            run_time=0.5 / ANIM_SPEED,
        )

        line = body_text(
            "Column symmetry turns a huge graph into 1D ballistic transport.",
            size=23,
            color=TEXT_PRIMARY,
        ).move_to([0, -1.75, 0])
        punch = body_text(
            "This is a genuine query-complexity exponential speedup.",
            size=23,
            color=TEXT_ACCENT,
        ).move_to([0, -2.35, 0])
        self.play(FadeIn(line), run_time=0.4 / ANIM_SPEED)
        self.play(FadeIn(punch), run_time=0.4 / ANIM_SPEED)
        self.wait(0.5)

    # === Quantum F1: closing ===========================================
    def _slide_quantum_walk_closing(self) -> None:
        self.begin_slide(section="Closing")

        heading = body_text("Where this leaves us", size=44, weight="BOLD")
        heading.to_edge(UP, buff=0.8)
        self.play(FadeIn(heading), run_time=0.4 / ANIM_SPEED)

        bullets = VGroup(
            body_text("Quantum walk = quantum time evolution on a graph.", size=24),
            body_text("1D: ballistic, not diffusive.", size=24),
            body_text("Glued trees: exponential classical-vs-quantum separation.", size=24),
            body_text(
                "Next: discrete-time walks and search frameworks.",
                size=24,
                color=TEXT_ACCENT,
            ),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.42).move_to([0, 0.05, 0])
        self.play(
            LaggedStart(*[FadeIn(b) for b in bullets], lag_ratio=0.25),
            run_time=0.9 / ANIM_SPEED,
        )
        self.wait(0.5)


class Preview(Lecture4):
    """Render a single slide's final state as a static PNG for fast dev iteration.

    Uses manim's ``-s`` flag to skip animations and save only the last frame.
    Pick which slide to preview via the ``SLIDE`` env var (1-indexed).

        SLIDE=8 ../../.venv/bin/manim -s -ql main.py Preview

    Output: ``builds/images/main/Preview_ManimCE_v0.19.1.png``
    """

    def _save_slides(self, *args, **kwargs):  # type: ignore[override]
        # In ``-s`` mode manim records no per-animation video files, so the
        # Slide base class crashes when it tries to bundle them at the end.
        # Preview only needs the rendered PNG — skip slide bookkeeping.
        return None

    def construct(self) -> None:
        target = int(os.environ.get("SLIDE", str(len(SLIDE_METHODS))))
        target = max(1, min(target, len(SLIDE_METHODS)))
        self.setup_lecture(author=AUTHOR, title=TITLE, total_pages=TOTAL_PAGES)
        for name in SLIDE_METHODS[:target]:
            getattr(self, name)()
