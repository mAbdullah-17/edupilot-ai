"""Central AI routing for EduPilot AI.

Gemini handles frequent/lightweight student features. Groq handles the
Interview Coach. Live opportunity discovery remains isolated in
modules/opportunity_discovery.py and uses Groq browser search.
"""
import json
import logging
from modules.ai.providers.gemini_provider import GeminiProvider
from modules.ai.providers.groq_provider import GroqProvider

logger = logging.getLogger(__name__)

class AIService:
    GEMINI_FEATURES = {"chat", "resume", "study", "career", "document"}
    GROQ_FEATURES = {"interview"}

    def __init__(self):
        self._gemini = GeminiProvider()
        self._groq = GroqProvider()

    @staticmethod
    def _clean_kwargs(kwargs):
        clean = dict(kwargs)
        clean.pop("feature", None)
        return clean

    def _provider_for(self, feature: str):
        return self._groq if (feature or "chat").lower() in self.GROQ_FEATURES else self._gemini

    def generate_text(self, prompt: str, feature: str = "chat", **kwargs) -> str:
        feature = (feature or "chat").lower()
        provider = self._provider_for(feature)
        try:
            return provider.generate(prompt, feature=feature, **self._clean_kwargs(kwargs))
        except Exception as exc:
            name = type(exc).__name__
            if name == "RateLimitError":
                raise RuntimeError(
                    "AI usage limit has been reached temporarily. Please try again shortly."
                ) from exc
            if name == "ProviderUnavailableError":
                raise RuntimeError(
                    "The AI provider is temporarily unavailable. Please try again shortly."
                ) from exc
            raise

    def analyze_document(self, file_bytes: bytes, task: str, feature: str = "document", **kwargs) -> str:
        feature = (feature or "document").lower()
        provider = self._provider_for(feature)
        try:
            return provider.analyze(file_bytes, task, feature=feature, **self._clean_kwargs(kwargs))
        except Exception as exc:
            name = type(exc).__name__
            if name == "RateLimitError":
                raise RuntimeError(
                    "AI usage limit has been reached temporarily. Please try again shortly."
                ) from exc
            if name == "ProviderUnavailableError":
                raise RuntimeError(
                    "The AI provider is temporarily unavailable. Please try again shortly."
                ) from exc
            raise

    def generate_structured_response(self, prompt: str, schema=None, feature: str = "chat", **kwargs):
        text = self.generate_text(prompt, feature=feature, **kwargs)
        cleaned = (text or "").strip()
        cleaned = cleaned.replace("```json", "").replace("```JSON", "").replace("```", "").strip()
        decoder = json.JSONDecoder()
        for i, ch in enumerate(cleaned):
            if ch not in "[{":
                continue
            try:
                parsed, _ = decoder.raw_decode(cleaned[i:])
                if isinstance(parsed, (dict, list)):
                    return parsed
            except json.JSONDecodeError:
                continue
        return {"raw": text}
