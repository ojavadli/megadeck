"""Unsplash auto-sourcing for photo_card slides.

When a `PhotoCardSlide` has `photo` set to a string starting with
`unsplash:` (e.g. `unsplash:office,startup`), this module fetches a
matching photo from Unsplash's public source CDN and caches it on disk.

Two endpoints are used in order, with graceful fallback:

  1. https://source.unsplash.com/featured/?<keywords>
       — public, no API key needed; returns a random matching photo.
  2. (cached) ~/.megadeck/unsplash_cache/<hash>.jpg

If the network is unavailable or the request fails, we return None and
the photo_card template renders a tinted placeholder (the existing
behaviour). Megadeck never breaks if Unsplash is down.
"""
from __future__ import annotations

import hashlib
import os
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional


_CACHE_DIR = Path(os.path.expanduser("~/.megadeck/unsplash_cache"))


def _cache_dir() -> Path:
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return _CACHE_DIR


def _hash_key(query: str, size: tuple[int, int]) -> str:
    h = hashlib.sha1()
    h.update(query.encode("utf-8"))
    h.update(f"{size[0]}x{size[1]}".encode("utf-8"))
    return h.hexdigest()[:16]


def fetch_unsplash(
    query: str,
    *,
    width: int = 1600,
    height: int = 1200,
    timeout_s: float = 8.0,
) -> Optional[Path]:
    """Fetch a photo for `query` from Unsplash. Returns a local file path
    on success, None on failure. Cached on disk indefinitely."""
    cache_path = _cache_dir() / f"{_hash_key(query, (width, height))}.jpg"
    if cache_path.exists() and cache_path.stat().st_size > 1024:
        return cache_path
    encoded = urllib.parse.quote(query)
    url = f"https://source.unsplash.com/featured/{width}x{height}/?{encoded}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "megadeck/0.4"})
        with urllib.request.urlopen(req, timeout=timeout_s) as r:
            data = r.read()
        if len(data) < 1024:
            return None
        cache_path.write_bytes(data)
        return cache_path
    except Exception:
        return None


def resolve_photo(photo_spec: Optional[str]) -> Optional[str]:
    """Resolve a `photo` field on PhotoCardSlide:
       - None → None (caller draws placeholder)
       - 'unsplash:keywords' → fetched local path or None
       - HTTPS URL → return as-is (template downloads it itself)
       - Local path → return as-is
    """
    if not photo_spec:
        return None
    if photo_spec.startswith("unsplash:"):
        query = photo_spec.removeprefix("unsplash:").strip()
        if not query:
            return None
        path = fetch_unsplash(query)
        return str(path) if path else None
    return photo_spec


__all__ = ["fetch_unsplash", "resolve_photo"]
