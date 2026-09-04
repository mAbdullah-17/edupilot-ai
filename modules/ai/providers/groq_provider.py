"""Groq provider used only by the Interview Coach."""
from config import settings
from modules.ai.providers.gemini_provider import RateLimitError, ProviderUnavailableError

class GroqProvider:
    MODEL = "openai/gpt-oss-20b"
    _LIMITS = {"interview": 220}

    def _get_client(self):
        if not settings.GROQ_API_KEY:
            raise RuntimeError("Groq API key is not configured")
        try:
            from groq import Groq
        except ImportError as exc:
            raise RuntimeError("groq package not installed. Run: python -m pip install groq") from exc
        return Groq(api_key=settings.GROQ_API_KEY)

    def generate(self, prompt: str, **kwargs) -> str:
        feature = kwargs.pop("feature", "interview") or "interview"
        max_tokens = int(kwargs.pop("max_completion_tokens", self._LIMITS.get(feature, 220)))
        try:
            response = self._get_client().chat.completions.create(
                model=self.MODEL,
                messages=[
                    {"role":"system","content":"You are EduPilot AI's interview coach. Be concise, practical and encouraging."},
                    {"role":"user","content":prompt},
                ],
                max_completion_tokens=max_tokens,
            )
            text = response.choices[0].message.content
            if not text:
                raise ProviderUnavailableError("Groq returned an empty response")
            return text.strip()
        except (RuntimeError, RateLimitError, ProviderUnavailableError):
            raise
        except Exception as exc:
            err = str(exc).lower()
            if "429" in err or "rate limit" in err or "rate_limit" in err:
                raise RateLimitError("Groq rate limit reached. Please wait and try again.") from exc
            if "timeout" in err or "503" in err or "502" in err or "unavailable" in err:
                raise ProviderUnavailableError(f"Groq temporarily unavailable: {exc}") from exc
            if "authentication" in err or "401" in err or "api key" in err:
                raise RuntimeError("Groq API key was rejected. Check GROQ_API_KEY in .env.") from exc
            raise RuntimeError(f"Groq error: {exc}") from exc

    def analyze(self, content: bytes, task: str, **kwargs):
        # Interview Coach does not use document analysis.
        raise RuntimeError("Groq document analysis is not configured; use Gemini for documents.")
