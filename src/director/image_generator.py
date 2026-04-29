from __future__ import annotations

import hashlib
import re
import shutil
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

POLLINATIONS_BASE = "https://image.pollinations.ai/prompt"
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "data" / "output"
INSTAGRAM_DIR = Path(__file__).resolve().parents[2] / "data" / "instagram"

INSTAGRAM_FORMATS = {
    "portrait": {"width": 1080, "height": 1350, "ratio": "4:5"},
    "square": {"width": 1080, "height": 1080, "ratio": "1:1"},
}
MAX_INSTAGRAM_SLIDES = 10


CAROUSEL_AGENT_INSTRUCTIONS = """
## Instruccion para Agente Artista Concept & Prompter — Formato Instagram Carousel

Cuando se solicite carrusel para Instagram, el agente DEBE generar prompts optimizados para
formato vertical 4:5 (1080x1350px) o cuadrado 1:1 (1080x1080px). Maximo 10 slides.

Reglas para prompts de carrusel Instagram:
1. Cada slide debe ser autocontenida — el usuario puede ver cualquier slide individual
2. El primer slide (portada) debe tener hook visual fuerte y titulo del comic
3. Slides intermedias deben mantener composicion centrada para evitar recorte de texto/burbujas
4. El ultimo slide debe incluir CTA (call-to-action): "Sigue para mas", "Like y comenta"
5. Mantener zona segura central de ~70% del frame para texto y bocadillos
6. Usar alto contraste: fondos oscuros con texto claro o viceversa
7. Evitar elementos criticos en los bordes (se recortan en la vista previa del feed)
8. Numerar slides visiblemente: "1/10", "2/10", etc.
9. El estilo visual debe ser coherente entre todas las slides del carrusel
10. Si el comic original tiene 16+ paneles, condensar a maximo 10 slides priorizando momentos clave

Formato de salida esperado del agente:
[
  {"slide_id": 1, "prompt": "...", "seed": 1, "type": "cover"},
  {"slide_id": 2, "prompt": "...", "seed": 2, "type": "content"},
  ...
  {"slide_id": 10, "prompt": "...", "seed": 10, "type": "cta"}
]
"""


def _slugify(text: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", text).strip()[:80]
    slug = re.sub(r"[\s_]+", "-", slug).lower()
    return slug or "panel"


def _hash_prompt(prompt: str) -> str:
    return hashlib.md5(prompt.encode()).hexdigest()[:8]


def _build_url(prompt: str, *, width: int = 1024, height: int = 1024, model: str = "flux", seed: int | None = None) -> str:
    safe_prompt = urllib.parse.quote(prompt.strip())
    url = f"{POLLINATIONS_BASE}/{safe_prompt}?width={width}&height={height}&model={model}&nologo=true"
    if seed is not None:
        url += f"&seed={seed}"
    return url


def generate_image(
    prompt: str,
    *,
    panel_id: int | str = 0,
    width: int = 1024,
    height: int = 1024,
    model: str = "flux",
    seed: int | None = None,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    target_dir = output_dir or OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    url = _build_url(prompt, width=width, height=height, model=model, seed=seed)
    slug = _slugify(prompt)
    prompt_hash = _hash_prompt(prompt)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"panel_{panel_id}_{slug}_{prompt_hash}_{timestamp}.png"
    filepath = target_dir / filename

    try:
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "WebcomicDirector/1.0")
        with urllib.request.urlopen(req, timeout=120) as response:
            with open(filepath, "wb") as out_file:
                shutil.copyfileobj(response, out_file)
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
            "prompt": prompt,
            "panel_id": panel_id,
            "url": url,
        }

    return {
        "ok": True,
        "panel_id": panel_id,
        "filepath": str(filepath),
        "filename": filename,
        "url": url,
        "width": width,
        "height": height,
        "model": model,
        "seed": seed,
    }


def generate_batch(
    prompts: list[dict[str, Any]],
    *,
    output_dir: Path | None = None,
    width: int = 1024,
    height: int = 1024,
    model: str = "flux",
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for item in prompts:
        prompt_text = item.get("prompt", "")
        panel_id = item.get("panel_id", len(results))
        seed = item.get("seed")
        result = generate_image(
            prompt_text,
            panel_id=panel_id,
            width=width,
            height=height,
            model=model,
            seed=seed,
            output_dir=output_dir,
        )
        results.append(result)
    return results


def generate_instagram_carousel(
    prompts: list[dict[str, Any]],
    *,
    format: str = "portrait",
    model: str = "flux",
    title: str = "carousel",
) -> list[dict[str, Any]]:
    """
    Genera un carrusel de Instagram (max 10 slides) en formato portrait 4:5 o square 1:1.
    """
    if format not in INSTAGRAM_FORMATS:
        raise ValueError(f"Formato Instagram invalido: {format}. Usa {list(INSTAGRAM_FORMATS.keys())}")

    fmt = INSTAGRAM_FORMATS[format]
    slides = prompts[:MAX_INSTAGRAM_SLIDES]
    target_dir = INSTAGRAM_DIR / title
    target_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    for item in slides:
        prompt_text = item.get("prompt", "")
        slide_num = item.get("slide_id", item.get("panel_id", len(results) + 1))
        seed = item.get("seed")

        safe_prompt = urllib.parse.quote(prompt_text.strip())
        url = f"{POLLINATIONS_BASE}/{safe_prompt}?width={fmt['width']}&height={fmt['height']}&model={model}&nologo=true"
        if seed is not None:
            url += f"&seed={seed}"

        slug = _slugify(prompt_text)
        prompt_hash = _hash_prompt(prompt_text)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        filename = f"slide_{slide_num:02d}_{slug}_{prompt_hash}_{timestamp}.png"
        filepath = target_dir / filename

        try:
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "WebcomicDirector/1.0")
            with urllib.request.urlopen(req, timeout=120) as response:
                with open(filepath, "wb") as out_file:
                    shutil.copyfileobj(response, out_file)
        except Exception as exc:
            results.append(
                {
                    "ok": False,
                    "error": str(exc),
                    "slide_id": slide_num,
                    "prompt": prompt_text,
                    "url": url,
                }
            )
            continue

        results.append(
            {
                "ok": True,
                "slide_id": slide_num,
                "filepath": str(filepath),
                "filename": filename,
                "url": url,
                "width": fmt["width"],
                "height": fmt["height"],
                "format": format,
                "ratio": fmt["ratio"],
                "model": model,
                "seed": seed,
            }
        )

    return results
