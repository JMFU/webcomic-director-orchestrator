# Webcomic Director Orchestrator
Proyecto base para el **Agente Director (Orquestador Principal)** de un pipeline modular de creación de webcómics.

## Objetivo
Coordinar tareas entre agentes especializados en tres etapas:
- Pre-producción
- Producción visual
- Post-producción y publicación

El orquestador emite siempre respuestas JSON con la forma:
```json
{
  "accion": "Nombre del agente destino",
  "payload": {}
}
```

## Estructura inicial
- `data/director_system_prompt.txt`: prompt del sistema del Agente Director (incluye instrucciones de doble formato: web + Instagram).
- `data/ortandria_prompts.json`: prompts de ejemplo para 16 paneles (formato web scroll).
- `data/ortandria_carousel_prompts.json`: prompts de ejemplo para carrusel Instagram (10 slides).
- `data/output/`: imágenes generadas para la web (scroll vertical).
- `data/instagram/`: carruseles de Instagram generados (portrait 4:5 o square 1:1).
- `src/director/pipeline.py`: definición de agentes, flujo principal y rutas de corrección.
- `src/director/orchestrator.py`: lógica de orquestación, historial/versionado y dashboard básico.
- `src/director/image_generator.py`: wrapper para Pollinations.ai con soporte web + Instagram carousel.
- `viewer.html`: visor web del webcomic en formato scroll vertical.
- `viewer-carousel.html`: visor de carruseles de Instagram con navegación slide a slide.
- `app.py`: CLI para iniciar un brief, generar imágenes, carruseles y servir los visores.

## Uso rápido

### Pipeline de agentes
```powershell
# Iniciar flujo desde un brief
python .\app.py start --brief "Quiero un cómic de 4 paneles sobre un robot que aprende salsa."

# Avanzar al siguiente agente tras resultado
python .\app.py next --agent "Test-Reader" --result-json '{"ok": true, "notas": "Concepto claro"}'
```

### Generación de imágenes (Pollinations.ai — gratis, sin API key)
```powershell
# Generar una imagen individual
python .\app.py gen-img --prompt "Hero with dark sunglasses in a cosmic shop" --panel-id 1

# Generar lote de paneles
python .\app.py gen-batch --prompts-json @prompts.json --width 768 --height 1024
```

### Carrusel de Instagram (max 10 slides)
```powershell
# Generar carrusel en formato portrait 4:5 (1080x1350) — recomendado
python .\app.py gen-carousel --prompts-json @carousel_prompts.json --title "ortandria-ep1" --format portrait

# Generar carrusel en formato square 1:1 (1080x1080)
python .\app.py gen-carousel --prompts-json @carousel_prompts.json --title "ortandria-ep1" --format square

# Listar carruseles generados
python .\app.py list-carousels
```

El agente **Artista Concept & Prompter** genera automáticamente prompts en DOS formatos:
1. **Web scroll vertical** — formato panoramico para la web
2. **Carrusel Instagram** — maximo 10 slides, portada con hook visual, ultima slide con CTA ("Sigue para mas"), composicion centrada con zona segura del 70%

### Visores
```powershell
# Servir visores en http://127.0.0.1:8080
python .\app.py serve
#   /            → Visor webcomic scroll vertical
#   /carousel    → Visor carrusel Instagram (navegacion slide a slide)
#   /api/images  → API de imagenes web
#   /api/carousels → API de carruseles Instagram

# Listar imágenes generadas
python .\app.py list-images
```

### Dashboard
```powershell
python .\app.py dashboard
```

## Próximos pasos sugeridos
1. Integrar un message broker real (Redis/RabbitMQ).
2. Añadir SLA por etapa y alertas de retraso.
3. Publicar dashboard en tiempo real (FastAPI + WebSocket).
4. Añadir agente de colorización automática.
5. Exportar carrusel como ZIP listo para subir a Instagram.
6. Generar caption automático para Instagram con hashtags.
