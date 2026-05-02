"""Layout data model + registry of ingested human-designed layouts."""
from __future__ import annotations

import json
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class LayoutShape:
    """One shape extracted from a source slide."""
    role: str  # 'title' | 'subtitle' | 'body' | 'number' | 'eyebrow' | 'accent_bar' | 'image' | 'icon' | 'decoration' | 'unknown'
    left_in: float
    top_in: float
    width_in: float
    height_in: float
    text: Optional[str] = None
    font_size_pt: Optional[float] = None
    font_bold: bool = False
    font_italic: bool = False
    font_name: Optional[str] = None
    color: Optional[str] = None  # hex without #
    fill: Optional[str] = None
    alignment: str = "left"  # 'left' | 'center' | 'right'
    z: int = 0


@dataclass
class Layout:
    """A single human-designed slide layout."""
    name: str
    source: str          # 'unsplash:<id>', 'file:<filename>:<slide_idx>', etc.
    kind_hint: str       # rough match against megadeck slide kinds: 'numbered_list', 'hero_statement', etc.
    slide_w_in: float
    slide_h_in: float
    shapes: List[LayoutShape] = field(default_factory=list)
    palette: Tuple[str, ...] = field(default_factory=tuple)  # accent colours observed
    description: str = ""


def layout_to_dict(lay: Layout) -> Dict[str, Any]:
    return {
        "name": lay.name,
        "source": lay.source,
        "kind_hint": lay.kind_hint,
        "slide_w_in": lay.slide_w_in,
        "slide_h_in": lay.slide_h_in,
        "palette": list(lay.palette),
        "description": lay.description,
        "shapes": [
            {
                "role": s.role,
                "left_in": s.left_in,
                "top_in": s.top_in,
                "width_in": s.width_in,
                "height_in": s.height_in,
                "text": s.text,
                "font_size_pt": s.font_size_pt,
                "font_bold": s.font_bold,
                "font_italic": s.font_italic,
                "font_name": s.font_name,
                "color": s.color,
                "fill": s.fill,
                "alignment": s.alignment,
                "z": s.z,
            }
            for s in lay.shapes
        ],
    }


def layout_from_dict(d: Dict[str, Any]) -> Layout:
    return Layout(
        name=d["name"],
        source=d.get("source", ""),
        kind_hint=d.get("kind_hint", "unknown"),
        slide_w_in=float(d.get("slide_w_in", 13.333)),
        slide_h_in=float(d.get("slide_h_in", 7.5)),
        palette=tuple(d.get("palette", [])),
        description=d.get("description", ""),
        shapes=[
            LayoutShape(
                role=s.get("role", "unknown"),
                left_in=float(s["left_in"]),
                top_in=float(s["top_in"]),
                width_in=float(s["width_in"]),
                height_in=float(s["height_in"]),
                text=s.get("text"),
                font_size_pt=s.get("font_size_pt"),
                font_bold=bool(s.get("font_bold", False)),
                font_italic=bool(s.get("font_italic", False)),
                font_name=s.get("font_name"),
                color=s.get("color"),
                fill=s.get("fill"),
                alignment=s.get("alignment", "left"),
                z=int(s.get("z", 0)),
            )
            for s in d.get("shapes", [])
        ],
    )


# In-memory registry of ingested layouts: {layout_name: Layout}
_LAYOUTS: Dict[str, Layout] = {}


def register_layout_obj(lay: Layout) -> None:
    _LAYOUTS[lay.name] = lay


def get_layout(name: str) -> Optional[Layout]:
    return _LAYOUTS.get(name)


def all_layouts() -> List[Layout]:
    return list(_LAYOUTS.values())


def layouts_by_kind(kind: str) -> List[Layout]:
    return [l for l in _LAYOUTS.values() if l.kind_hint == kind]


def default_layout_lib_dir() -> Path:
    """Where ingested layout JSONs are stored on disk."""
    return Path(__file__).resolve().parent / "lib"


def load_layout_json(path: str | Path) -> Layout:
    p = Path(path)
    return layout_from_dict(json.loads(p.read_text(encoding="utf-8")))


def save_layout_json(lay: Layout, path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(layout_to_dict(lay), indent=2), encoding="utf-8")
    return p


def sync_default_layout_lib() -> List[Layout]:
    """Load every JSON in `lib/` into the registry. Called at package import."""
    out: List[Layout] = []
    base = default_layout_lib_dir()
    if not base.exists():
        return out
    for p in sorted(base.rglob("*.json")):
        try:
            lay = load_layout_json(p)
            register_layout_obj(lay)
            out.append(lay)
        except Exception as exc:  # noqa: BLE001
            warnings.warn(f"Skipping bad layout {p}: {exc}")
    return out


__all__ = [
    "Layout", "LayoutShape",
    "layout_to_dict", "layout_from_dict",
    "register_layout_obj", "get_layout", "all_layouts", "layouts_by_kind",
    "default_layout_lib_dir", "load_layout_json", "save_layout_json",
    "sync_default_layout_lib",
]
