"""
LinkedIn Publisher Agent — Publicación de artículos via OAuth 2.0
Pendiente de implementación hasta que los agentes estén pulidos.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class LinkedInConfig:
    access_token: str = ""
    author_urn: str = ""
    publication_type: str = "ARTICLE"
    visibility: str = "PUBLIC"
    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = "http://localhost:8080/callback"


@dataclass
class PublicationResult:
    status: str
    post_url: str = ""
    post_id: str = ""
    timestamp: str = ""
    error_detail: str = ""


class LinkedInPublisherAgent:
    """
    Agente para publicar artículos en LinkedIn via LinkedIn API v2.

    Requiere configuración OAuth 2.0 (ver linkedin_config.env.example)
    """

    BASE_API_URL = "https://api.linkedin.com/v2"
    REQUIRED_SCOPES = ["w_member_social", "r_liteprofile"]

    def __init__(self, config: LinkedInConfig | None = None):
        self.config = config or LinkedInConfig()

    def verify_token(self) -> bool:
        """
        Verifica que el access_token sea válido.
        """
        raise NotImplementedError("Pendiente: implementar verificación de token")

    def get_author_info(self) -> dict[str, Any]:
        """
        Obtiene información del perfil del autor.
        """
        raise NotImplementedError("Pendiente: implementar获取 perfil")

    def publish_article(
        self,
        title: str,
        body: str,
        hashtags: list[str],
        github_url: str,
    ) -> PublicationResult:
        """
        Publica un artículo en LinkedIn.

        Args:
            title: Título del artículo
            body: Contenido en Markdown
            hashtags: Lista de hashtags
            github_url: URL del repositorio

        Returns:
            PublicationResult con status y URL del post
        """
        raise NotImplementedError("Pendiente: implementar publicación")

    def build_oauth_url(self) -> str:
        """
        Construye la URL de autorización OAuth 2.0.
        """
        if not self.config.client_id:
            raise ValueError("LINKEDIN_CLIENT_ID no configurado")
        scope = "%20".join(self.REQUIRED_SCOPES)
        return (
            f"https://www.linkedin.com/oauth/v2/authorization"
            f"?response_type=code"
            f"&client_id={self.config.client_id}"
            f"&redirect_uri={self.config.redirect_uri}"
            f"&scope={scope}"
        )

    def exchange_code_for_token(self, code: str) -> dict[str, Any]:
        """
        Intercambia código OAuth por access token.
        """
        raise NotImplementedError("Pendiente: implementar intercambio de token")