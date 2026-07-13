"""
Handler: User Created
SPDX-License-Identifier: LGPL-3.0-or-later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

import os
from pathlib import Path
from typing import Dict, Any

from handlers.base import EventHandler


class UserCreatedHandler(EventHandler):
    """Handles UserCreated events."""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        super().__init__()

    def get_event_type(self) -> str:
        return "UserCreated"

    def handle(self, event_data: Dict[str, Any]) -> None:
        """Create an HTML email based on user creation data."""

        user_id = event_data.get("id")
        name = event_data.get("name")
        email = event_data.get("email")
        creation_date = event_data.get("datetime")
        user_type_id = event_data.get("user_type_id")

        if user_type_id == 1:
            message = (
                "Merci d'avoir visité notre magasin. Si vous avez des questions "
                "ou des problèmes concernant votre achat, n'hésitez pas à nous contacter."
            )
        elif user_type_id == 2:
            message = (
                "Salut et bienvenue dans l'équipe ! Nous sommes heureux de vous "
                "compter parmi les employés du Magasin du Coin."
            )
        elif user_type_id == 3:
            message = (
                "Bienvenue dans l'équipe de direction ! Nous vous souhaitons beaucoup "
                "de succès dans vos nouvelles fonctions."
            )
        else:
            message = "Bienvenue au Magasin du Coin !"

        project_root = Path(__file__).parent.parent
        template_path = (
                project_root / "templates" / "welcome_client_template.html"
        )

        with open(template_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        html_content = html_content.replace("{{user_id}}", str(user_id))
        html_content = html_content.replace("{{name}}", str(name))
        html_content = html_content.replace("{{email}}", str(email))
        html_content = html_content.replace(
            "{{creation_date}}", str(creation_date)
        )
        html_content = html_content.replace("{{message}}", message)

        filename = Path(self.output_dir) / f"welcome_{user_id}.html"
        filename.write_text(html_content, encoding="utf-8")

        self.logger.debug(
            f"Courriel HTML généré à {name} "
            f"(ID: {user_id}, type: {user_type_id}), {filename}"
        )