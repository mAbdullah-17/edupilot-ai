"""AI provider package — exports shared error types."""

from modules.ai.providers.gemini_provider import RateLimitError, ProviderUnavailableError

__all__ = ["RateLimitError", "ProviderUnavailableError"]
