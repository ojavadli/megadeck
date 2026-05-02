"""Preview pipeline: .pptx → PDF → per-slide PNG.

Used both by the CLI (`megadeck preview`) and the critic loop (which feeds
PNGs into a vision LLM to detect overflow / alignment issues).
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import List


class PreviewError(RuntimeError):
    """Raised when the preview pipeline fails."""


def _find_libreoffice() -> str:
    """Locate `soffice` (LibreOffice headless binary)."""
    for candidate in ("soffice", "libreoffice"):
        path = shutil.which(candidate)
        if path:
            return path
    # Common macOS location
    macos_path = "/opt/homebrew/bin/soffice"
    if shutil.which(macos_path):
        return macos_path
    if Path(macos_path).exists():
        return macos_path
    raise PreviewError(
        "LibreOffice not found. Install it (brew install libreoffice on macOS, "
        "apt-get install libreoffice on Linux). LibreOffice is required for "
        "the preview pipeline."
    )


def pptx_to_pdf(pptx_path: str | Path, output_dir: str | Path) -> Path:
    """Convert a .pptx file to PDF via headless LibreOffice."""
    pptx_path = Path(pptx_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    soffice = _find_libreoffice()
    result = subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf",
         str(pptx_path), "--outdir", str(output_dir)],
        capture_output=True,
        text=True,
        timeout=180,
    )
    if result.returncode != 0:
        raise PreviewError(
            f"LibreOffice failed (code {result.returncode}): {result.stderr}"
        )
    pdf_path = output_dir / (pptx_path.stem + ".pdf")
    if not pdf_path.exists():
        raise PreviewError(f"Expected PDF at {pdf_path}, but it was not produced.")
    return pdf_path


def pdf_to_pngs(
    pdf_path: str | Path,
    output_dir: str | Path,
    *,
    dpi: int = 100,
) -> List[Path]:
    """Render every page of the PDF to PNG. Returns a sorted list of PNG paths."""
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    pdftoppm = shutil.which("pdftoppm")
    if pdftoppm is None:
        raise PreviewError(
            "pdftoppm not found. Install poppler (brew install poppler on macOS, "
            "apt-get install poppler-utils on Linux)."
        )
    prefix = output_dir / pdf_path.stem
    result = subprocess.run(
        [pdftoppm, "-r", str(dpi), "-png", str(pdf_path), str(prefix)],
        capture_output=True, text=True, timeout=180,
    )
    if result.returncode != 0:
        raise PreviewError(f"pdftoppm failed: {result.stderr}")
    pngs = sorted(output_dir.glob(f"{pdf_path.stem}-*.png"))
    if not pngs:
        raise PreviewError("No PNG output found after running pdftoppm.")
    return pngs


def render_pptx_to_pngs(
    pptx_path: str | Path,
    *,
    output_dir: str | Path | None = None,
    dpi: int = 100,
) -> List[Path]:
    """End-to-end: pptx -> pdf -> per-slide PNGs.

    If `output_dir` is None, drops them in `<pptx_dir>/.megadeck-preview/`.
    """
    pptx_path = Path(pptx_path)
    if output_dir is None:
        output_dir = pptx_path.parent / ".megadeck-preview"
    pdf = pptx_to_pdf(pptx_path, output_dir)
    return pdf_to_pngs(pdf, output_dir, dpi=dpi)
