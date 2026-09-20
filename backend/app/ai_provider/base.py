"""
Abstraction du fournisseur IA utilise pour :
- l'analyse vision des photos (materiaux, ouvertures, isolation apparente, equipements)
- la generation de questions adaptatives du questionnaire
- l'extraction structuree du texte OCR des factures materiaux

Deux implementations V1 : GeminiProvider (defaut, gratuit) et ClaudeProvider (optionnel).
Le choix actif est determine par la variable d'environnement AI_PROVIDER (voir app/ai_provider/factory.py).
"""
from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    @abstractmethod
    def analyze_image(self, image_bytes: bytes, mime_type: str, instruction: str) -> dict[str, Any]:
        """
        Envoie une image + une instruction au modele multimodal et retourne un objet JSON
        (le prompt demande explicitement une reponse JSON stricte).
        """

    @abstractmethod
    def generate_structured(self, prompt: str) -> dict[str, Any]:
        """
        Envoie un prompt texte et retourne un objet JSON
        (utilise pour le questionnaire adaptatif et l'extraction de factures OCR).
        """
