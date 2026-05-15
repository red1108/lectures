"""Reusable Manim primitives for quantum-circuit diagrams.

The helpers here keep circuit symbols consistent across Manim lecture decks.
They deliberately return plain Manim ``VGroup`` objects so a slide can still
position, animate, recolor, or compose them however it needs.
"""
from __future__ import annotations

from collections.abc import Iterable

from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Arc,
    Arrow,
    Dot,
    Line,
    Rectangle,
    Text,
    VGroup,
)

DEFAULT_FONT = "Apple SD Gothic Neo"
DEFAULT_TEXT = "#f0f0f0"
DEFAULT_MUTED = "#9aa0a6"
DEFAULT_ACCENT = "#79b8ff"
DEFAULT_FILL = "#111111"

PAULI_GATES = frozenset(("X", "Y", "Z"))
PHASE_GATES = frozenset(("S", "T"))
STANDARD_SINGLE_QUBIT_GATES = frozenset(("I", "X", "Y", "Z", "H", "S", "T"))


def _point(x: float, y: float) -> list[float]:
    return [x, y, 0]


def wire(
    x0: float,
    x1: float,
    y: float,
    *,
    color: str = DEFAULT_MUTED,
    stroke_width: float = 2.0,
) -> Line:
    """Horizontal quantum wire."""
    return Line(_point(x0, y), _point(x1, y), stroke_color=color, stroke_width=stroke_width)


def wire_bundle(
    x0: float,
    x1: float,
    ys: Iterable[float],
    *,
    color: str = DEFAULT_MUTED,
    stroke_width: float = 2.0,
) -> VGroup:
    """A group of parallel horizontal quantum wires."""
    return VGroup(
        *[wire(x0, x1, y, color=color, stroke_width=stroke_width) for y in ys]
    )


def single_qubit_gate(
    label: str,
    *,
    width: float = 0.46,
    height: float = 0.46,
    stroke_color: str = DEFAULT_TEXT,
    text_color: str = DEFAULT_TEXT,
    fill_color: str = DEFAULT_FILL,
    fill_opacity: float = 1.0,
    stroke_width: float = 2.2,
    font: str = DEFAULT_FONT,
    font_size: int = 18,
    weight: str = "BOLD",
) -> VGroup:
    """Boxed one-qubit gate with a text label."""
    rect = Rectangle(
        width=width,
        height=height,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
        fill_color=fill_color,
        fill_opacity=fill_opacity,
    )
    txt = Text(label, font=font, font_size=font_size, color=text_color, weight=weight)
    if txt.width > width * 0.72:
        txt.scale((width * 0.72) / txt.width)
    if txt.height > height * 0.62:
        txt.scale((height * 0.62) / txt.height)
    txt.move_to(rect.get_center())
    return VGroup(rect, txt)


def standard_gate(label: str, **kwargs: object) -> VGroup:
    """One of the standard single-qubit gates: I, X, Y, Z, H, S, T."""
    if label not in STANDARD_SINGLE_QUBIT_GATES:
        allowed = ", ".join(sorted(STANDARD_SINGLE_QUBIT_GATES))
        raise ValueError(f"unsupported gate {label!r}; expected one of {allowed}")
    return single_qubit_gate(label, **kwargs)


def h_gate(**kwargs: object) -> VGroup:
    return standard_gate("H", **kwargs)


def pauli_gate(axis: str, **kwargs: object) -> VGroup:
    axis = axis.upper()
    if axis not in PAULI_GATES:
        allowed = ", ".join(sorted(PAULI_GATES))
        raise ValueError(f"unsupported Pauli gate {axis!r}; expected one of {allowed}")
    return standard_gate(axis, **kwargs)


def x_gate(**kwargs: object) -> VGroup:
    return pauli_gate("X", **kwargs)


def y_gate(**kwargs: object) -> VGroup:
    return pauli_gate("Y", **kwargs)


def z_gate(**kwargs: object) -> VGroup:
    return pauli_gate("Z", **kwargs)


def s_gate(**kwargs: object) -> VGroup:
    return standard_gate("S", **kwargs)


def t_gate(**kwargs: object) -> VGroup:
    return standard_gate("T", **kwargs)


def phase_gate(label: str, **kwargs: object) -> VGroup:
    label = label.upper()
    if label not in PHASE_GATES:
        allowed = ", ".join(sorted(PHASE_GATES))
        raise ValueError(f"unsupported phase gate {label!r}; expected one of {allowed}")
    return standard_gate(label, **kwargs)


def measurement_gate(
    *,
    width: float = 0.72,
    height: float = 0.52,
    stroke_color: str = DEFAULT_ACCENT,
    symbol_color: str | None = None,
    fill_color: str | None = None,
    fill_opacity: float = 1.0,
    stroke_width: float = 2.2,
    symbol_stroke_width: float = 2.0,
) -> VGroup:
    """Measurement gate drawn as the standard meter symbol.

    The symbol is a boxed semicircular gauge plus a diagonal pointer, matching
    the visual convention used by many quantum-circuit diagrams.
    """
    if symbol_color is None:
        symbol_color = stroke_color
    if fill_color is None:
        fill_color = DEFAULT_FILL

    rect = Rectangle(
        width=width,
        height=height,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
        fill_color=fill_color,
        fill_opacity=fill_opacity,
    )
    arc = Arc(
        radius=width * 0.30,
        start_angle=0,
        angle=3.141592653589793,
        color=symbol_color,
        stroke_width=symbol_stroke_width,
    )
    arc.move_to(rect.get_center() + height * 0.06 * DOWN)
    pointer = Arrow(
        rect.get_center() + width * 0.13 * LEFT + height * 0.23 * DOWN,
        rect.get_center() + width * 0.27 * RIGHT + height * 0.27 * UP,
        buff=0,
        stroke_color=symbol_color,
        color=symbol_color,
        stroke_width=symbol_stroke_width,
        max_tip_length_to_length_ratio=0.32,
    )
    return VGroup(rect, arc, pointer)


def control_dot(
    x: float,
    y: float,
    *,
    radius: float = 0.06,
    color: str = DEFAULT_TEXT,
) -> Dot:
    return Dot(_point(x, y), radius=radius, color=color)


def vertical_connector(
    x: float,
    y0: float,
    y1: float,
    *,
    color: str = DEFAULT_TEXT,
    stroke_width: float = 2.0,
) -> Line:
    return Line(_point(x, y0), _point(x, y1), stroke_color=color, stroke_width=stroke_width)


def swap_cross(
    x: float,
    y: float,
    *,
    size: float = 0.18,
    color: str = DEFAULT_TEXT,
    stroke_width: float = 2.4,
) -> VGroup:
    """Cross marker used for the two target wires of a SWAP gate."""
    return VGroup(
        Line(
            _point(x - size / 2, y - size / 2),
            _point(x + size / 2, y + size / 2),
            stroke_color=color,
            stroke_width=stroke_width,
        ),
        Line(
            _point(x - size / 2, y + size / 2),
            _point(x + size / 2, y - size / 2),
            stroke_color=color,
            stroke_width=stroke_width,
        ),
    )


def swap_gate(
    x: float,
    y0: float,
    y1: float,
    *,
    color: str = DEFAULT_TEXT,
    stroke_width: float = 2.0,
    cross_size: float = 0.20,
) -> VGroup:
    """Two-wire SWAP gate."""
    return VGroup(
        vertical_connector(x, y0, y1, color=color, stroke_width=stroke_width),
        swap_cross(x, y0, size=cross_size, color=color, stroke_width=stroke_width + 0.4),
        swap_cross(x, y1, size=cross_size, color=color, stroke_width=stroke_width + 0.4),
    )


def controlled_swap_gate(
    x: float,
    control_y: float,
    target_y0: float,
    target_y1: float,
    *,
    color: str = DEFAULT_TEXT,
    stroke_width: float = 2.0,
    dot_radius: float = 0.06,
    cross_size: float = 0.20,
) -> VGroup:
    """Fredkin-style controlled-SWAP primitive."""
    return VGroup(
        vertical_connector(x, control_y, target_y1, color=color, stroke_width=stroke_width),
        control_dot(x, control_y, radius=dot_radius, color=color),
        swap_cross(x, target_y0, size=cross_size, color=color, stroke_width=stroke_width + 0.4),
        swap_cross(x, target_y1, size=cross_size, color=color, stroke_width=stroke_width + 0.4),
    )


def place(mobject: VGroup, x: float, y: float) -> VGroup:
    """Convenience wrapper for ``move_to([x, y, 0])`` in circuit code."""
    return mobject.move_to(_point(x, y))
