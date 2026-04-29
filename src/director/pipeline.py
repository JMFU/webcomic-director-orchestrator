from __future__ import annotations

INITIAL_ACTION = "Test-Reader"

NEXT_ACTION = {
    "Test-Reader": "Escritor/Guionista",
    "Escritor/Guionista": "Storyboarder/Maquetador Visual",
    "Storyboarder/Maquetador Visual": "Artista Concept & Prompter",
    "Artista Concept & Prompter": "Generación de Imágenes",
    "Generación de Imágenes": "Consistencia de Personajes",
    "Consistencia de Personajes": "QA Visual",
    "QA Visual": "Rotulista/Letterer",
    "Rotulista/Letterer": "Compositing y Compilador",
    "Compositing y Compilador": "QA final",
    "QA final": "Publicación y SEO",
    "Publicación y SEO": "Analítica Post-Publicación",
    "Analítica Post-Publicación": "Retroalimentación",
}

REVISION_ROUTING = {
    "Test-Reader": "Escritor/Guionista",
    "Escritor/Guionista": "Escritor/Guionista",
    "Storyboarder/Maquetador Visual": "Escritor/Guionista",
    "Artista Concept & Prompter": "Artista Concept & Prompter",
    "Generación de Imágenes": "Artista Concept & Prompter",
    "Consistencia de Personajes": "Generación de Imágenes",
    "QA Visual": "Generación de Imágenes",
    "Rotulista/Letterer": "Rotulista/Letterer",
    "Compositing y Compilador": "Compositing y Compilador",
    "QA final": "Compositing y Compilador",
    "Publicación y SEO": "Publicación y SEO",
    "Analítica Post-Publicación": "Escritor/Guionista",
}
