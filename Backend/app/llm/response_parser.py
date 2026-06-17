"""
OpenRouter LLM response parser.
Extracts JSON from LLM responses that may be wrapped in:
  - Markdown code fences: ```json ... ```
  - XML-style tags: <json>...</json>, <jsonoutput>...</jsonoutput>
  - Thinking tags: <think>...</think> (Qwen, DeepSeek, Gemini)
  - Plain JSON with surrounding prose
"""
import json
import re
from typing import Any


def _strip_thinking_tags(text: str) -> str:
    """Remove <think>...</think> and similar reasoning blocks that some models emit."""
    text = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<thinking>[\s\S]*?</thinking>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<reasoning>[\s\S]*?</reasoning>", "", text, flags=re.IGNORECASE)
    return text.strip()


def extract_json(text: str) -> Any:
    """
    Extract and parse the first JSON object or array from LLM output.

    Handles common LLM quirks:
      1. Thinking/reasoning tags: <think>...</think>
      2. JSON wrapped in ```json ... ``` code fences
      3. JSON wrapped in XML-like tags: <json>...</json>, <jsonoutput>...</jsonoutput>
      4. JSON with leading/trailing prose
      5. Trailing commas (cleaned before parsing)
    """
    if not text:
        return None

    # Step 1: Strip thinking/reasoning blocks first
    text = _strip_thinking_tags(text)

    if not text:
        return None

    # Step 2: Try direct parse (ideal case — clean JSON)
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Step 3: Extract from ```json ... ``` or ``` ... ``` code fence
    fence_match = re.search(
        r"```(?:json)?\s*(\{[\s\S]*?\}|\[[\s\S]*?\])\s*```",
        text,
        re.IGNORECASE,
    )
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass

    # Step 4: Extract from XML-style tags <json>...</json> or <jsonoutput>...</jsonoutput>
    xml_match = re.search(
        r"<(?:json|jsonoutput|result|output)>([\s\S]*?)</(?:json|jsonoutput|result|output)>",
        text,
        re.IGNORECASE,
    )
    if xml_match:
        candidate = xml_match.group(1).strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # Step 5: Greedy search — find the first complete { ... } or [ ... ] block
    for pattern in (r"\{[\s\S]*\}", r"\[[\s\S]*\]"):
        match = re.search(pattern, text)
        if match:
            candidate = match.group(0)
            # Fix trailing commas — common LLM mistake
            candidate = re.sub(r",\s*([}\]])", r"\1", candidate)
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue

    return None
