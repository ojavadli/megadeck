"""Adapter: Radix Colors → megadeck themes.

Source data
-----------
Radix UI ships 30 colour scales (gray, mauve, red, … plus saturated
variants) each with 12 carefully-tuned steps designed for accessible
light/dark UI pairs. MIT-licensed, see https://www.radix-ui.com/colors.

We use steps 9 (solid colours) and 11 (high-contrast text) for accent /
accent_dk, and step 4 (UI element backgrounds) as accent_lt. Producing
30 scales × 2 modes × 4 visual styles = 240 themes.
"""
from __future__ import annotations

from typing import Dict, Iterator, List

from megadeck.design_system.themegen import Palette, VisualStyle, generate_theme


# Step 9 = solid base, Step 11 = hi-contrast text, Step 4 = UI bg, Step 1 = page bg
RADIX_LIGHT: Dict[str, Dict[int, str]] = {
    "gray":   {1: "#FCFCFC", 4: "#EEEEEE", 9: "#8D8D8D", 11: "#646464"},
    "mauve":  {1: "#FDFCFD", 4: "#EEEDEF", 9: "#8E8C99", 11: "#65636D"},
    "slate":  {1: "#FCFCFD", 4: "#EDEEF0", 9: "#8B8D98", 11: "#62636C"},
    "sage":   {1: "#FBFDFC", 4: "#EBEEEC", 9: "#868E8B", 11: "#5F6661"},
    "olive":  {1: "#FCFDFC", 4: "#ECEEEB", 9: "#898E87", 11: "#60655C"},
    "sand":   {1: "#FDFDFC", 4: "#EEEEEC", 9: "#8D8D86", 11: "#63635E"},
    "tomato": {1: "#FFFCFC", 4: "#FFE6E2", 9: "#E54D2E", 11: "#CA3214"},
    "red":    {1: "#FFFCFC", 4: "#FFE5E5", 9: "#E5484D", 11: "#CD2B31"},
    "ruby":   {1: "#FFFCFD", 4: "#FFE6E6", 9: "#E54666", 11: "#CA244D"},
    "crimson":{1: "#FFFCFD", 4: "#FCE5EE", 9: "#E93D82", 11: "#CB1D63"},
    "pink":   {1: "#FFFCFE", 4: "#FCE5F3", 9: "#D6409F", 11: "#B71F7E"},
    "plum":   {1: "#FEFCFF", 4: "#F8E4F8", 9: "#AB4ABA", 11: "#854093"},
    "purple": {1: "#FEFCFE", 4: "#F0DDFA", 9: "#8E4EC6", 11: "#793AAF"},
    "violet": {1: "#FDFCFE", 4: "#E5DDF6", 9: "#6E56CF", 11: "#5746AF"},
    "iris":   {1: "#FDFDFF", 4: "#DDE2FF", 9: "#5B5BD6", 11: "#3D3DB9"},
    "indigo": {1: "#FDFDFE", 4: "#D2DEFF", 9: "#3E63DD", 11: "#2D44AC"},
    "blue":   {1: "#FBFDFF", 4: "#CCE4F8", 9: "#0090FF", 11: "#006ADC"},
    "cyan":   {1: "#FAFDFE", 4: "#BCE6F1", 9: "#05A2C2", 11: "#0E7A93"},
    "teal":   {1: "#FAFEFD", 4: "#B7E5DD", 9: "#12A594", 11: "#067A6F"},
    "jade":   {1: "#FBFEFB", 4: "#BDE5CD", 9: "#29A383", 11: "#107D67"},
    "green":  {1: "#FBFEFB", 4: "#BBE9C5", 9: "#30A46C", 11: "#18794E"},
    "grass":  {1: "#FBFEFB", 4: "#C2E8C7", 9: "#46A758", 11: "#297C3B"},
    "bronze": {1: "#FDFCFB", 4: "#EEDED1", 9: "#A18072", 11: "#7D5E54"},
    "gold":   {1: "#FDFDFC", 4: "#ECE6CF", 9: "#978365", 11: "#71624B"},
    "brown":  {1: "#FEFDFC", 4: "#F0D9C2", 9: "#AD7F58", 11: "#815E46"},
    "orange": {1: "#FEFCFB", 4: "#FFCFA9", 9: "#F76808", 11: "#BD4B00"},
    "amber":  {1: "#FEFDFB", 4: "#FFE0B5", 9: "#FFB224", 11: "#AD5700"},
    "yellow": {1: "#FDFDF9", 4: "#FFEFA5", 9: "#FFD60A", 11: "#946800"},
    "lime":   {1: "#FCFDFA", 4: "#DDF0AB", 9: "#BDEE63", 11: "#5C7C2F"},
    "mint":   {1: "#F9FEFD", 4: "#A2EBDC", 9: "#86EAD4", 11: "#147D6F"},
    "sky":    {1: "#F9FEFF", 4: "#B7E0FA", 9: "#7CE2FE", 11: "#00749E"},
}

RADIX_DARK: Dict[str, Dict[int, str]] = {
    "gray":   {1: "#111111", 4: "#2A2A2A", 9: "#7B7B7B", 11: "#B4B4B4"},
    "mauve":  {1: "#121113", 4: "#28252D", 9: "#7E7989", 11: "#B5B2BC"},
    "slate":  {1: "#111113", 4: "#26282E", 9: "#797A86", 11: "#B0B4BA"},
    "tomato": {1: "#181111", 4: "#391714", 9: "#E54D2E", 11: "#FF977D"},
    "red":    {1: "#191111", 4: "#3B1219", 9: "#E5484D", 11: "#FF9592"},
    "ruby":   {1: "#191113", 4: "#3A141E", 9: "#E54666", 11: "#FF949D"},
    "crimson":{1: "#191114", 4: "#38122D", 9: "#E93D82", 11: "#FF92AD"},
    "pink":   {1: "#191117", 4: "#341240", 9: "#D6409F", 11: "#FF8DCC"},
    "plum":   {1: "#181118", 4: "#2F123E", 9: "#AB4ABA", 11: "#E796F3"},
    "purple": {1: "#18111B", 4: "#2B1747", 9: "#8E4EC6", 11: "#D19DFF"},
    "violet": {1: "#14121F", 4: "#241245", 9: "#6E56CF", 11: "#BAA7FF"},
    "iris":   {1: "#13131E", 4: "#202248", 9: "#5B5BD6", 11: "#B1A9FF"},
    "indigo": {1: "#11131F", 4: "#162454", 9: "#3E63DD", 11: "#9EB1FF"},
    "blue":   {1: "#0D1520", 4: "#003362", 9: "#0090FF", 11: "#70B8FF"},
    "cyan":   {1: "#0B161A", 4: "#003F5C", 9: "#00A2C7", 11: "#5AD2DD"},
    "teal":   {1: "#0D1514", 4: "#003F3D", 9: "#12A594", 11: "#0AC8B5"},
    "jade":   {1: "#0D1512", 4: "#0F3F2C", 9: "#29A383", 11: "#1FD8A4"},
    "green":  {1: "#0D1410", 4: "#113B29", 9: "#30A46C", 11: "#3DD68C"},
    "grass":  {1: "#0E1511", 4: "#1B361F", 9: "#46A758", 11: "#65BA75"},
    "orange": {1: "#17120E", 4: "#46220C", 9: "#F76808", 11: "#FFA57C"},
    "amber":  {1: "#16120C", 4: "#3A2200", 9: "#FFB224", 11: "#FFCB47"},
    "yellow": {1: "#14120B", 4: "#2D2200", 9: "#F0C000", 11: "#F5E147"},
    "sky":    {1: "#0D141F", 4: "#003363", 9: "#7CE2FE", 11: "#75D5FF"},
    "mint":   {1: "#0E1515", 4: "#093E3E", 9: "#86EAD4", 11: "#41D9C2"},
}


def palette_from_radix(name: str, mode: str = "light") -> Palette:
    table = RADIX_LIGHT if mode == "light" else RADIX_DARK
    if name not in table:
        raise ValueError(f"Unknown Radix scale (mode={mode!r}): {name!r}")
    p = table[name]
    return Palette(
        name=f"radix-{name}-{mode}",
        accent=p[9],
        accent_dk=p[11],
        accent_lt=p[4],
        bg_light=p[1] if mode == "light" else None,
        bg_dark=p[1] if mode == "dark" else None,
    )


def generate_radix_themes(
    visual_styles: List[VisualStyle] = None,
) -> Iterator[Dict]:
    if visual_styles is None:
        visual_styles = ["flat", "shadow", "glass", "orbs"]
    for mode_name, table in (("light", RADIX_LIGHT), ("dark", RADIX_DARK)):
        for scale in table:
            palette = palette_from_radix(scale, mode_name)
            for style in visual_styles:
                yield generate_theme(
                    palette,
                    visual_style=style,
                    mode=mode_name,
                    name=f"radix-{scale}-{mode_name}-{style}",
                    description=f"Radix {scale} ({mode_name}, {style}).",
                )


__all__ = [
    "RADIX_LIGHT", "RADIX_DARK",
    "palette_from_radix", "generate_radix_themes",
]
