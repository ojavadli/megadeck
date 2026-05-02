"""Slide-to-slide transitions implemented via raw pptx XML."""
from __future__ import annotations

from lxml import etree

from megadeck.core.schemas import TransitionKind


P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
P14_NS = "http://schemas.microsoft.com/office/powerpoint/2010/main"


def _make_transition_xml(kind: TransitionKind, duration_ms: int = 450) -> str | None:
    """Return the <p:transition> XML element string, or None for kind=NONE."""
    if kind == TransitionKind.NONE:
        return None
    if kind == TransitionKind.FADE:
        body = "<p:fade/>"
    elif kind == TransitionKind.PUSH:
        body = '<p:push dir="r"/>'
    elif kind == TransitionKind.MORPH:
        body = '<p:morph option="byObject"/>'
    else:
        return None
    return (
        f'<p:transition xmlns:p="{P_NS}" xmlns:p14="{P14_NS}" '
        f'spd="med" p14:dur="{duration_ms}">{body}</p:transition>'
    )


def apply_transition(slide_elem, kind: TransitionKind) -> None:
    """Idempotently apply (or remove) a transition on a slide's XML element.

    The transition element must sit *between* `cSld`/`clrMapOvr` and `timing`
    or PowerPoint will refuse to read the file, so we re-order children after
    insertion.
    """
    # Remove any existing transition
    for t in slide_elem.findall("{%s}transition" % P_NS):
        slide_elem.remove(t)
    xml = _make_transition_xml(kind)
    if xml is None:
        return
    transition = etree.fromstring(xml)
    # Capture existing children
    cSld = slide_elem.find("{%s}cSld" % P_NS)
    clrMapOvr = slide_elem.find("{%s}clrMapOvr" % P_NS)
    timing = slide_elem.find("{%s}timing" % P_NS)
    for child in list(slide_elem):
        slide_elem.remove(child)
    if cSld is not None:
        slide_elem.append(cSld)
    if clrMapOvr is not None:
        slide_elem.append(clrMapOvr)
    slide_elem.append(transition)
    if timing is not None:
        slide_elem.append(timing)
