from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .image_generator import (
    CAROUSEL_AGENT_INSTRUCTIONS,
    INSTAGRAM_DIR,
    OUTPUT_DIR,
    generate_batch,
    generate_image,
    generate_instagram_carousel,
)
from .pipeline import INITIAL_ACTION, NEXT_ACTION, REVISION_ROUTING


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


class DirectorOrchestrator:
    """
    Núcleo de orquestación para el pipeline modular de webcómics.
    """

    def __init__(self) -> None:
        self.version = 0
        self.history: list[dict[str, Any]] = []
        self.message_queue: list[dict[str, Any]] = []
        self.task_status: dict[str, str] = {}
        self.generated_images: list[dict[str, Any]] = []

    def start(self, brief: str) -> dict[str, Any]:
        """
        Comienza un nuevo flujo enviando el brief al Test-Reader.
        """
        return self._emit(
            action=INITIAL_ACTION,
            payload={
                "brief": brief,
                "metadata": {
                    "created_at": _utc_timestamp(),
                    "priority": "normal",
                },
            },
        )

    def handle_result(self, agent: str, result_payload: dict[str, Any]) -> dict[str, Any]:
        """
        Decide el siguiente paso a partir del resultado entregado por un agente.
        """
        if agent not in NEXT_ACTION:
            raise ValueError(f"Agente desconocido en flujo: {agent}")

        self.task_status[agent] = "done"
        requires_revision = bool(result_payload.get("requires_revision"))

        if requires_revision:
            target = REVISION_ROUTING.get(agent, agent)
            payload = {
                "motivo": "Corrección solicitada",
                "agente_origen": agent,
                "feedback": result_payload.get("feedback", ""),
                "insumo": result_payload,
                "metadata": {
                    "requested_at": _utc_timestamp(),
                    "severity": result_payload.get("severity", "normal"),
                },
            }
            return self._emit(target, payload)

        next_action = NEXT_ACTION[agent]
        payload = {
            "agente_origen": agent,
            "input": result_payload,
            "metadata": {
                "routed_at": _utc_timestamp(),
                "quality_gate": "passed",
            },
        }
        return self._emit(next_action, payload)

    def generate_images(
        self,
        prompts: list[dict[str, Any]],
        *,
        width: int = 1024,
        height: int = 1024,
        model: str = "flux",
    ) -> dict[str, Any]:
        """
        Ejecuta la generación de imágenes para un lote de prompts.
        """
        results = generate_batch(
            prompts,
            width=width,
            height=height,
            model=model,
        )
        for result in results:
            if result.get("ok"):
                self.generated_images.append(result)

        ok_count = sum(1 for r in results if r.get("ok"))
        fail_count = len(results) - ok_count

        self.version += 1
        self.history.append(
            {
                "version": self.version,
                "timestamp": _utc_timestamp(),
                "accion": "Generación de Imágenes",
                "payload": {
                    "total": len(results),
                    "ok": ok_count,
                    "failed": fail_count,
                    "images": results,
                },
            }
        )

        return {
            "accion": "Generación de Imágenes",
            "payload": {
                "total": len(results),
                "ok": ok_count,
                "failed": fail_count,
                "images": results,
            },
        }

    def generate_single_image(
        self,
        prompt: str,
        *,
        panel_id: int | str = 0,
        width: int = 1024,
        height: int = 1024,
        model: str = "flux",
        seed: int | None = None,
    ) -> dict[str, Any]:
        """
        Genera una imagen individual a partir de un prompt.
        """
        result = generate_image(
            prompt,
            panel_id=panel_id,
            width=width,
            height=height,
            model=model,
            seed=seed,
        )
        if result.get("ok"):
            self.generated_images.append(result)

        self.version += 1
        self.history.append(
            {
                "version": self.version,
                "timestamp": _utc_timestamp(),
                "accion": "Generación de Imágenes",
                "payload": result,
            }
        )

        return {
            "accion": "Generación de Imágenes",
            "payload": result,
        }

    def list_images(self) -> list[dict[str, Any]]:
        """
        Lista todas las imágenes generadas en la sesión actual.
        """
        return self.generated_images

    def list_image_files(self) -> list[dict[str, str]]:
        """
        Escanea el directorio de output y lista archivos PNG/JPG generados.
        """
        if not OUTPUT_DIR.exists():
            return []
        files = []
        for path in sorted(OUTPUT_DIR.glob("*")):
            if path.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
                files.append(
                    {
                        "filename": path.name,
                        "filepath": str(path),
                        "size_bytes": path.stat().st_size,
                        "modified_at": datetime.fromtimestamp(
                            path.stat().st_mtime, tz=timezone.utc
                        ).isoformat(),
                    }
                )
        return files

    def generate_instagram_carousel(
        self,
        prompts: list[dict[str, Any]],
        *,
        format: str = "portrait",
        model: str = "flux",
        title: str = "carousel",
    ) -> dict[str, Any]:
        """
        Genera un carrusel de Instagram a partir de prompts optimizados.
        """
        results = generate_instagram_carousel(
            prompts,
            format=format,
            model=model,
            title=title,
        )
        for result in results:
            if result.get("ok"):
                self.generated_images.append(result)

        ok_count = sum(1 for r in results if r.get("ok"))
        fail_count = len(results) - ok_count
        fmt_info = {"portrait": "1080x1350 (4:5)", "square": "1080x1080 (1:1)"}.get(format, format)

        self.version += 1
        self.history.append(
            {
                "version": self.version,
                "timestamp": _utc_timestamp(),
                "accion": "Carrusel Instagram",
                "payload": {
                    "title": title,
                    "format": fmt_info,
                    "total": len(results),
                    "ok": ok_count,
                    "failed": fail_count,
                    "slides": results,
                },
            }
        )

        return {
            "accion": "Carrusel Instagram",
            "payload": {
                "title": title,
                "format": fmt_info,
                "total": len(results),
                "ok": ok_count,
                "failed": fail_count,
                "slides": results,
            },
        }

    def list_instagram_carousels(self) -> list[dict[str, Any]]:
        """
        Escanea el directorio de Instagram y lista carruseles generados.
        """
        if not INSTAGRAM_DIR.exists():
            return []
        carousels = []
        for carousel_dir in sorted(INSTAGRAM_DIR.iterdir()):
            if carousel_dir.is_dir():
                slides = []
                total_bytes = 0
                for path in sorted(carousel_dir.glob("*.png")):
                    slides.append(
                        {
                            "filename": path.name,
                            "filepath": str(path),
                            "size_bytes": path.stat().st_size,
                            "modified_at": datetime.fromtimestamp(
                                path.stat().st_mtime, tz=timezone.utc
                            ).isoformat(),
                        }
                    )
                    total_bytes += path.stat().st_size
                carousels.append(
                    {
                        "name": carousel_dir.name,
                        "slide_count": len(slides),
                        "total_bytes": total_bytes,
                        "slides": slides,
                    }
                )
        return carousels

    def dashboard(self) -> dict[str, Any]:
        """
        Snapshot simple para observar estado, cola y versionado.
        """
        return {
            "version": self.version,
            "queue_length": len(self.message_queue),
            "queued_actions": [item["accion"] for item in self.message_queue],
            "task_status": self.task_status,
            "history_size": len(self.history),
            "images_generated": len(self.generated_images),
            "image_files": len(self.list_image_files()),
            "last_update_at": _utc_timestamp(),
        }

    def _emit(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.version += 1
        self.task_status[action] = "queued"
        response = {"accion": action, "payload": payload}
        self.message_queue.append(response)
        self.history.append(
            {
                "version": self.version,
                "timestamp": _utc_timestamp(),
                "accion": action,
                "payload": payload,
            }
        )
        return response
