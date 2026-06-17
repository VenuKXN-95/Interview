"""
OpenRouter async LLM client.
Features:
  - Exponential backoff retry (tenacity) on 429 / 5xx
  - Configurable timeout per call
  - Primary + fallback model support
  - Structured JSON output extraction
  - Full request/response logging (sanitized)
"""
import logging
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings
from app.core.exceptions import LLMResponseParseException, LLMServiceException
from app.llm.response_parser import extract_json

logger = logging.getLogger(__name__)


def _is_retryable(exc: BaseException) -> bool:
    """Retry on rate-limit or server errors, not on 4xx client errors."""
    if isinstance(exc, LLMServiceException):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in (429, 500, 502, 503, 504)
    return isinstance(exc, (httpx.TimeoutException, httpx.NetworkError))


class OpenRouterClient:
    """Reusable async OpenRouter API client."""

    def __init__(self) -> None:
        self._base_url = settings.openrouter_base_url
        self._api_key = settings.openrouter_api_key
        self._model = settings.openrouter_model
        self._fallback_model = settings.openrouter_fallback_model
        self._timeout = settings.openrouter_timeout
        self._max_retries = settings.openrouter_max_retries

    def _build_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://mock-interview-backend",
            "X-Title": "Mock Interview Platform",
        }

    @retry(
        retry=retry_if_exception(_is_retryable),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True,
    )
    async def _call(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        """Make a single API call and return the raw response text."""
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        logger.info(
            "LLM call initiated",
            extra={"model": model, "message_count": len(messages)},
        )

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    json=payload,
                    headers=self._build_headers(),
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            logger.error("LLM HTTP error: %s", status, extra={"model": model})
            raise LLMServiceException(
                message=f"OpenRouter returned HTTP {status}.",
                details={"model": model, "status_code": status},
            )
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            logger.error("LLM network/timeout error: %s", exc, extra={"model": model})
            raise LLMServiceException(
                message="OpenRouter request timed out or network error occurred.",
                details={"model": model},
            )

        data = response.json()
        if "error" in data:
            err_msg = data["error"].get("message", "Unknown error")
            logger.error("OpenRouter API returned error: %s", err_msg, extra={"error_data": data["error"]})
            raise LLMServiceException(
                message=f"OpenRouter API error: {err_msg}",
                details={"model": model, "error": data["error"]},
            )

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            logger.error("LLM response missing choices: %s", data, extra={"model": model})
            raise LLMServiceException(
                message="OpenRouter response is missing expected choices structure.",
                details={"model": model, "response": data},
            )

        logger.info(
            "LLM call completed",
            extra={"model": model, "tokens_used": data.get("usage", {})},
        )
        return content

    async def complete(
        self,
        user_prompt: str,
        system_prompt: str = "You are a helpful assistant.",
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        """
        Send a prompt and return the raw text response.
        Tries primary model first, falls back to fallback model on failure.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            return await self._call(messages, self._model, temperature, max_tokens)
        except LLMServiceException:
            logger.warning(
                "Primary model %s failed, trying fallback %s",
                self._model,
                self._fallback_model,
            )
            return await self._call(
                messages, self._fallback_model, temperature, max_tokens
            )

    async def complete_json(
        self,
        user_prompt: str,
        system_prompt: str = "You are a helpful assistant. Return only valid JSON.",
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> Any:
        """
        Send a prompt expecting a JSON response.
        Parses and returns the JSON object. Raises LLMResponseParseException if
        the response cannot be parsed as JSON.
        """
        raw = await self.complete(user_prompt, system_prompt, temperature, max_tokens)
        result = extract_json(raw)
        if result is None:
            logger.error(
                "LLM JSON parse failed",
                extra={"raw_response_preview": raw[:300]},
            )
            raise LLMResponseParseException(
                message="The AI response could not be parsed as JSON.",
                details={"raw_preview": raw[:200]},
            )
        return result
