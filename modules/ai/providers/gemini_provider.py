"""Google Gemini provider using the current Google GenAI SDK."""
from functools import lru_cache
from config import settings

class RateLimitError(Exception):
    pass
class ProviderUnavailableError(Exception):
    pass

class GeminiProvider:
    MODEL = "gemini-3.6-flash"
    _LIMITS = {"chat": 500, "career": 700, "resume": 900, "study": 900, "document": 900, "planner": 1000}

    @staticmethod
    @lru_cache(maxsize=1)
    def _get_client():
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("Gemini API key is not configured")
        try:
            from google import genai
        except ImportError as exc:
            raise RuntimeError("google-genai package not installed") from exc
        return genai.Client(api_key=settings.GEMINI_API_KEY)

    @classmethod
    def _default_config(cls, feature="chat", **kwargs):
        from google.genai import types
        # `feature` is removed before this method is called by generate/analyze,
        # but keeping it as a named parameter also prevents duplicate-argument errors.
        return types.GenerateContentConfig(
            max_output_tokens=int(kwargs.get("max_output_tokens", cls._LIMITS.get(feature, 500))),
            thinking_config=types.ThinkingConfig(thinking_level="low"),
        )

    def generate(self, prompt: str, **kwargs) -> str:
        feature = kwargs.pop("feature", "chat") or "chat"
        config = kwargs.pop("config", None) or self._default_config(feature, **kwargs)
        try:
            response = self._get_client().models.generate_content(
                model=self.MODEL, contents=prompt, config=config
            )
            text = getattr(response, "text", None)
            if not text:
                raise ProviderUnavailableError("Gemini returned an empty response")
            return text.strip()
        except (RuntimeError, RateLimitError, ProviderUnavailableError):
            raise
        except ImportError as exc:
            raise RuntimeError("google-genai package not installed") from exc
        except Exception as exc:
            self._raise_mapped(exc)

    def analyze(self, content: bytes, task: str, **kwargs) -> str:
        feature = kwargs.pop("feature", "document") or "document"
        mime = kwargs.pop("mime_type", "application/pdf")
        config = kwargs.pop("config", None) or self._default_config(feature, **kwargs)
        try:
            from google.genai import types
            part = types.Part.from_bytes(data=content, mime_type=mime)
            response = self._get_client().models.generate_content(
                model=self.MODEL, contents=[task, part], config=config
            )
            text = getattr(response, "text", None)
            if not text:
                raise ProviderUnavailableError("Gemini returned an empty response")
            return text.strip()
        except (RuntimeError, RateLimitError, ProviderUnavailableError):
            raise
        except ImportError as exc:
            raise RuntimeError("google-genai package not installed") from exc
        except Exception as exc:
            self._raise_mapped(exc)

    def generate_with_google_search_response(self, prompt: str, **kwargs):
        try:
            from google.genai import types
            config = types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                max_output_tokens=int(kwargs.get("max_output_tokens", 3000)),
                thinking_config=types.ThinkingConfig(thinking_level="low"),
            )
            return self._get_client().models.generate_content(
                model=self.MODEL, contents=prompt, config=config
            )
        except Exception as exc:
            self._raise_mapped(exc)

    @staticmethod
    def _raise_mapped(exc):
        message = str(exc)
        lower = message.lower()
        if any(x in lower for x in ("rate", "quota", "429", "resource_exhausted")):
            raise RateLimitError(f"Gemini rate limit: {message}") from exc
        if any(x in lower for x in ("timeout", "deadline", "unavailable", "503", "500", "502", "504")):
            raise ProviderUnavailableError(f"Gemini temporarily unavailable: {message}") from exc
        raise RuntimeError(f"Gemini error: {message}") from exc
