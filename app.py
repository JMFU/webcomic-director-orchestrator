from __future__ import annotations

import argparse
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any

from src.director import DirectorOrchestrator

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
INSTAGRAM_DIR = PROJECT_ROOT / "data" / "instagram"
VIEWER_HTML = PROJECT_ROOT / "viewer.html"
CAROUSEL_VIEWER_HTML = PROJECT_ROOT / "viewer-carousel.html"


def _json(text: str) -> dict[str, Any]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as error:
        raise argparse.ArgumentTypeError(f"JSON inválido: {error}") from error
    if not isinstance(value, dict):
        raise argparse.ArgumentTypeError("El JSON debe ser un objeto.")
    return value


def _json_list(text: str) -> list[dict[str, Any]]:
    try:
        if text.startswith("@"):
            filepath = Path(text[1:])
            with open(filepath, encoding="utf-8") as f:
                value = json.load(f)
        else:
            value = json.loads(text)
    except json.JSONDecodeError as error:
        raise argparse.ArgumentTypeError(f"JSON inválido: {error}") from error
    except FileNotFoundError as error:
        raise argparse.ArgumentTypeError(f"Archivo no encontrado: {text[1:]}") from error
    if not isinstance(value, list):
        raise argparse.ArgumentTypeError("El JSON debe ser un array.")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CLI base para el Agente Director (Orquestador Principal)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_cmd = subparsers.add_parser("start", help="Inicia un flujo desde un brief.")
    start_cmd.add_argument("--brief", required=True, help="Brief de usuario.")

    next_cmd = subparsers.add_parser(
        "next",
        help="Calcula el siguiente agente según el resultado del agente actual.",
    )
    next_cmd.add_argument("--agent", required=True, help="Agente que reporta resultado.")
    next_cmd.add_argument(
        "--result-json",
        required=True,
        type=_json,
        help='Resultado del agente en JSON, p.ej. \'{"ok": true}\'.',
    )

    img_cmd = subparsers.add_parser("gen-img", help="Genera una imagen desde un prompt.")
    img_cmd.add_argument("--prompt", required=True, help="Prompt de imagen.")
    img_cmd.add_argument("--panel-id", type=int, default=0, help="ID del panel.")
    img_cmd.add_argument("--width", type=int, default=1024, help="Ancho en px.")
    img_cmd.add_argument("--height", type=int, default=1024, help="Alto en px.")
    img_cmd.add_argument("--model", default="flux", help="Modelo (flux, turbo, etc).")
    img_cmd.add_argument("--seed", type=int, default=None, help="Seed para reproducibilidad.")

    batch_cmd = subparsers.add_parser("gen-batch", help="Genera imágenes desde un lote de prompts.")
    batch_cmd.add_argument(
        "--prompts-json",
        required=True,
        type=_json_list,
        help='Array de objetos con campos "prompt" y opcional "panel_id" y "seed".',
    )
    batch_cmd.add_argument("--width", type=int, default=1024, help="Ancho en px.")
    batch_cmd.add_argument("--height", type=int, default=1024, help="Alto en px.")
    batch_cmd.add_argument("--model", default="flux", help="Modelo.")

    carousel_cmd = subparsers.add_parser("gen-carousel", help="Genera carrusel de Instagram (max 10 slides).")
    carousel_cmd.add_argument(
        "--prompts-json",
        required=True,
        type=_json_list,
        help='Array de objetos con campos "prompt", "slide_id" y opcional "seed".',
    )
    carousel_cmd.add_argument("--title", required=True, help="Nombre del carrusel (carpeta).")
    carousel_cmd.add_argument("--format", default="portrait", choices=["portrait", "square"], help="Formato: portrait (4:5) o square (1:1).")
    carousel_cmd.add_argument("--model", default="flux", help="Modelo.")

    subparsers.add_parser("list-images", help="Lista imágenes generadas en disco.")
    subparsers.add_parser("list-carousels", help="Lista carruseles de Instagram generados.")
    subparsers.add_parser("dashboard", help="Muestra el dashboard en memoria.")

    serve_cmd = subparsers.add_parser("serve", help="Sirve el visor del webcomic en un servidor HTTP.")
    serve_cmd.add_argument("--port", type=int, default=8080, help="Puerto del servidor.")
    serve_cmd.add_argument("--host", default="127.0.0.1", help="Host del servidor.")

    return parser


class ComicHandler(SimpleHTTPRequestHandler):
    """Handler que sirve el viewer, las imágenes y una API de listado."""

    def do_GET(self):
        if self.path == "/":
            self._serve_file(VIEWER_HTML, "text/html; charset=utf-8")
        elif self.path == "/carousel":
            self._serve_file(CAROUSEL_VIEWER_HTML, "text/html; charset=utf-8")
        elif self.path.startswith("/images/"):
            filename = self.path.removeprefix("/images/")
            filepath = OUTPUT_DIR / filename
            if filepath.exists() and filepath.is_file():
                ext = filepath.suffix.lower()
                mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}.get(ext, "application/octet-stream")
                self._serve_file(filepath, mime)
            else:
                self.send_error(404, "Imagen no encontrada")
        elif self.path.startswith("/carousel/"):
            parts = self.path.removeprefix("/carousel/").split("/", 1)
            if len(parts) == 1:
                self.send_error(404, "Ruta de carrusel invalida. Usa /carousel/<nombre>/<archivo>")
                return
            carousel_name, filename = parts
            filepath = INSTAGRAM_DIR / carousel_name / filename
            if filepath.exists() and filepath.is_file():
                ext = filepath.suffix.lower()
                mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}.get(ext, "application/octet-stream")
                self._serve_file(filepath, mime)
            else:
                self.send_error(404, "Slide de carrusel no encontrada")
        elif self.path == "/api/images":
            director = DirectorOrchestrator()
            images = director.list_image_files()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"images": images}, ensure_ascii=False).encode("utf-8"))
        elif self.path == "/api/carousels":
            director = DirectorOrchestrator()
            carousels = director.list_instagram_carousels()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"carousels": carousels}, ensure_ascii=False).encode("utf-8"))
        else:
            super().do_GET()

    def _serve_file(self, filepath: Path, mime: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(filepath.stat().st_size))
        self.end_headers()
        self.wfile.write(filepath.read_bytes())

    def log_message(self, format: str, *args) -> None:
        print(f"  [{self.address_string()}] {format % args}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    director = DirectorOrchestrator()

    if args.command == "start":
        output = director.start(args.brief)
    elif args.command == "next":
        output = director.handle_result(args.agent, args.result_json)
    elif args.command == "gen-img":
        output = director.generate_single_image(
            args.prompt,
            panel_id=args.panel_id,
            width=args.width,
            height=args.height,
            model=args.model,
            seed=args.seed,
        )
    elif args.command == "gen-batch":
        output = director.generate_images(
            args.prompts_json,
            width=args.width,
            height=args.height,
            model=args.model,
        )
    elif args.command == "list-images":
        output = {"images": director.list_image_files()}
    elif args.command == "list-carousels":
        output = {"carousels": director.list_instagram_carousels()}
    elif args.command == "gen-carousel":
        output = director.generate_instagram_carousel(
            args.prompts_json,
            format=args.format,
            model=args.model,
            title=args.title,
        )
    elif args.command == "serve":
        if not OUTPUT_DIR.exists():
            print("No hay imágenes generadas. Genera paneles primero con 'gen-img' o 'gen-batch'.")
            return
        server = HTTPServer((args.host, args.port), ComicHandler)
        print(f"[SERVER] Visor del webcomic disponible en http://{args.host}:{args.port}")
        print(f"   Presiona Ctrl+C para detener.\n")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido.")
            return
    else:
        output = director.dashboard()

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
