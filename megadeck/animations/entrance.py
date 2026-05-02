"""Entrance animations — fade-in / slide-in / scale-in for slide elements.

PowerPoint's animation system is keyframe-based; we generate the appropriate
`<p:timing>` block per slide and stagger entrances by a configurable delay.

The choreography (which-shape-when) is computed by `megadeck.animations.choreography`
which is itself a port of Motion's `stagger()` function. A spring or named easing
on the `--motion-spring` / `--motion-easing` CLI flag maps onto delay distribution
exactly like Motion's WAAPI orchestration examples.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Union

from lxml import etree

from megadeck.animations.choreography import StaggerOrigin, materialise_stagger
from megadeck.animations.easing import EasingFn
from megadeck.animations.spring import Spring
from megadeck.core.schemas import EntranceKind


P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"


# Mapping from EntranceKind → PowerPoint preset metadata.
# preset IDs come from the OOXML spec: Fade=10, FlyIn=2, ZoomIn=23.
_PRESETS = {
    EntranceKind.FADE_IN: {"presetID": "10", "presetClass": "entr", "presetSubtype": "0"},
    EntranceKind.SLIDE_FROM_LEFT:   {"presetID": "2", "presetClass": "entr", "presetSubtype": "4"},
    EntranceKind.SLIDE_FROM_RIGHT:  {"presetID": "2", "presetClass": "entr", "presetSubtype": "8"},
    EntranceKind.SLIDE_FROM_BOTTOM: {"presetID": "2", "presetClass": "entr", "presetSubtype": "2"},
    EntranceKind.SCALE_UP:          {"presetID": "23", "presetClass": "entr", "presetSubtype": "0"},
}


@dataclass
class EntrancePlan:
    """Describes how a single shape should animate in."""
    shape_id: str          # the cNvPr id of the shape
    kind: EntranceKind
    delay_ms: int = 0
    duration_ms: int = 350


def _shape_ids(slide_elem) -> List[str]:
    """Yield the cNvPr ids of every drawable shape on the slide."""
    sp_tree = slide_elem.find(f"{{{P_NS}}}cSld/{{{P_NS}}}spTree")
    if sp_tree is None:
        return []
    ids: List[str] = []
    for sp in sp_tree:
        tag = etree.QName(sp).localname
        if tag in ("sp", "pic", "graphicFrame", "cxnSp"):
            nv = sp.find(f".//{{{P_NS}}}cNvPr")
            if nv is not None and nv.get("id"):
                ids.append(nv.get("id"))
    return ids


def stagger_entrance(
    slide_elem,
    *,
    kind: EntranceKind = EntranceKind.FADE_IN,
    duration_ms: int = 350,
    stagger_ms: int = 80,
    skip_first_n: int = 0,
    origin: StaggerOrigin = "first",
    easing: Optional[Union[str, EasingFn]] = None,
    spring: Optional[Spring] = None,
) -> None:
    """Apply a staggered entrance animation to every shape on the slide.

    The delay distribution is computed via `materialise_stagger()` which is
    a port of Motion's stagger function — pass `origin="center"` for a
    rippling out-from-the-middle effect, or `easing="back-out"` to make the
    cascade itself eased.

    If `spring` is supplied, the per-shape `duration_ms` is overridden by
    the spring's calculated rest time (computed via Motion's spring solver).
    """
    if kind == EntranceKind.NONE:
        return
    shape_ids = _shape_ids(slide_elem)
    targets = shape_ids[skip_first_n:]
    if not targets:
        return

    delays_s = materialise_stagger(
        len(targets),
        duration_s=stagger_ms / 1000.0,
        origin=origin,
        easing=easing,
    )

    # If a spring is supplied, derive the per-shape duration from the spring's
    # natural settling time. We sample the spring until velocity falls under
    # restSpeed (matching Motion's spring.next() done condition).
    per_shape_ms = duration_ms
    if spring is not None:
        for t_step in range(50, 4001, 50):
            if abs(spring.velocity_per_s(t_step)) < 2.0 and abs(
                spring.target - spring.position(t_step)
            ) < 0.5:
                per_shape_ms = t_step
                break

    plans = [
        EntrancePlan(
            shape_id=sid,
            kind=kind,
            delay_ms=int(round(delays_s[i] * 1000)),
            duration_ms=int(per_shape_ms),
        )
        for i, sid in enumerate(targets)
    ]
    apply_entrances(slide_elem, plans)


def apply_entrances(slide_elem, plans: Iterable[EntrancePlan]) -> None:
    """Build a `<p:timing>` block for the given entrance plans and attach it."""
    plans = list(plans)
    if not plans:
        return

    # Remove an existing timing block if present (idempotency)
    existing = slide_elem.find(f"{{{P_NS}}}timing")
    if existing is not None:
        slide_elem.remove(existing)

    parts: List[str] = [
        f'<p:timing xmlns:p="{P_NS}" xmlns:a="{A_NS}">',
        "  <p:tnLst>",
        "    <p:par>",
        '      <p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">',
        "        <p:childTnLst>",
        '          <p:seq concurrent="1" nextAc="seek">',
        '            <p:cTn id="2" dur="indefinite" nodeType="mainSeq">',
        "              <p:childTnLst>",
    ]
    cTn_id = 3
    for plan in plans:
        preset = _PRESETS.get(plan.kind)
        if preset is None:
            continue
        parts.extend(_animation_par_xml(plan, preset, cTn_id))
        cTn_id += 5
    parts.extend([
        "              </p:childTnLst>",
        "            </p:cTn>",
        '            <p:prevCondLst><p:cond evt="onPrev" delay="0">'
        '<p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>',
        '            <p:nextCondLst><p:cond evt="onNext" delay="0">'
        '<p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>',
        "          </p:seq>",
        "        </p:childTnLst>",
        "      </p:cTn>",
        "    </p:par>",
        "  </p:tnLst>",
        "  <p:bldLst>",
    ])
    for plan in plans:
        parts.append(
            f'    <p:bldP spid="{plan.shape_id}" grpId="0" animBg="1"/>'
        )
    parts.append("  </p:bldLst>")
    parts.append("</p:timing>")

    timing = etree.fromstring("\n".join(parts))
    slide_elem.append(timing)


def _animation_par_xml(plan: EntrancePlan, preset: dict, cTn_id: int) -> list[str]:
    """Build the `<p:par>` XML fragment for one entrance animation."""
    return [
        "                <p:par>",
        f'                  <p:cTn id="{cTn_id}" fill="hold">',
        '                    <p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>',
        "                    <p:childTnLst>",
        "                      <p:par>",
        f'                        <p:cTn id="{cTn_id+1}" fill="hold">',
        '                          <p:stCondLst><p:cond delay="0"/></p:stCondLst>',
        "                          <p:childTnLst>",
        "                            <p:par>",
        f'                              <p:cTn id="{cTn_id+2}" '
        f'presetID="{preset["presetID"]}" '
        f'presetClass="{preset["presetClass"]}" '
        f'presetSubtype="{preset["presetSubtype"]}" '
        f'fill="hold" grpId="0" nodeType="afterEffect">',
        f'                                <p:stCondLst>'
        f'<p:cond delay="{plan.delay_ms}"/></p:stCondLst>',
        "                                <p:childTnLst>",
        "                                  <p:set>",
        "                                    <p:cBhvr>",
        f'                                      <p:cTn id="{cTn_id+3}" dur="1" fill="hold">'
        '<p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>',
        f'                                      <p:tgtEl>'
        f'<p:spTgt spid="{plan.shape_id}"/></p:tgtEl>',
        "                                      <p:attrNameLst>"
        "<p:attrName>style.visibility</p:attrName></p:attrNameLst>",
        "                                    </p:cBhvr>",
        "                                    <p:to><p:strVal val=\"visible\"/></p:to>",
        "                                  </p:set>",
        "                                  <p:anim calcmode=\"lin\" valueType=\"num\">",
        "                                    <p:cBhvr additive=\"base\">",
        f'                                      <p:cTn id="{cTn_id+4}" '
        f'dur="{plan.duration_ms}" fill="hold"/>',
        f'                                      <p:tgtEl>'
        f'<p:spTgt spid="{plan.shape_id}"/></p:tgtEl>',
        "                                      <p:attrNameLst>"
        "<p:attrName>style.opacity</p:attrName></p:attrNameLst>",
        "                                    </p:cBhvr>",
        "                                    <p:tavLst>",
        "                                      <p:tav tm=\"0\">"
        "<p:val><p:fltVal val=\"0\"/></p:val></p:tav>",
        "                                      <p:tav tm=\"100000\">"
        "<p:val><p:fltVal val=\"1\"/></p:val></p:tav>",
        "                                    </p:tavLst>",
        "                                  </p:anim>",
        "                                </p:childTnLst>",
        "                              </p:cTn>",
        "                            </p:par>",
        "                          </p:childTnLst>",
        "                        </p:cTn>",
        "                      </p:par>",
        "                    </p:childTnLst>",
        "                  </p:cTn>",
        "                </p:par>",
    ]
