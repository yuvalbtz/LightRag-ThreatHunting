import sys

if sys.version_info < (3, 9):
    from typing import AsyncIterator
else:
    from collections.abc import AsyncIterator

import pipmaster as pm  # Pipmaster for dynamic library install

# install specific modules
if not pm.is_installed("aiohttp"):
    pm.install("aiohttp")
if not pm.is_installed("tenacity"):
    pm.install("tenacity")

import aiohttp
import json
import os
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from lightrag.exceptions import (
    APIConnectionError,
    RateLimitError,
    APITimeoutError,
)
from lightrag.api import __api_version__

from typing import Union


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(
        (RateLimitError, APIConnectionError, APITimeoutError)
    ),
)
async def _openrouter_model_if_cache(
    model,
    prompt,
    system_prompt=None,
    history_messages=[],
    **kwargs,
) -> Union[str, AsyncIterator[str]]:
    """OpenRouter model completion with caching support."""

    # Get configuration
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is required")

    api_base = "https://openrouter.ai/api/v1/chat/completions"
    stream = kwargs.get("stream", True)

    # Build messages array
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    # Prepare request payload
    payload = {
        "model": model,
        "messages": messages,
        "temperature": kwargs.get("temperature", 0.0),
        "stream": stream,
    }

    # Add optional parameters
    if "max_tokens" in kwargs:
        payload["max_tokens"] = kwargs["max_tokens"]
    if "top_p" in kwargs:
        payload["top_p"] = kwargs["top_p"]
    if "frequency_penalty" in kwargs:
        payload["frequency_penalty"] = kwargs["frequency_penalty"]
    if "presence_penalty" in kwargs:
        payload["presence_penalty"] = kwargs["presence_penalty"]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream" if stream else "application/json",
        "User-Agent": f"LightRAG/{__api_version__}",
    }

    timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes timeout

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(api_base, headers=headers, json=payload) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise Exception(f"OpenRouter API error: {error_text}")

            if stream:

                async def stream_generator():
                    buffer = ""
                    try:
                        async for chunk in resp.content.iter_chunked(1024):
                            if not chunk:
                                continue
                            buffer += chunk.decode("utf-8")

                            while True:
                                try:
                                    # Find the next complete SSE line
                                    line_end = buffer.find("\n")
                                    if line_end == -1:
                                        break

                                    line = buffer[:line_end].strip()
                                    buffer = buffer[line_end + 1 :]

                                    if line.startswith("data: "):
                                        data = line[6:]
                                        if data == "[DONE]":
                                            return

                                        try:
                                            payload = json.loads(data)
                                            token = payload["choices"][0]["delta"].get(
                                                "content"
                                            )
                                            if token:
                                                yield token
                                        except json.JSONDecodeError:
                                            pass
                                except Exception:
                                    break
                    except Exception as e:
                        raise APIConnectionError(f"Streaming error: {str(e)}")

                return stream_generator()
            else:
                data = await resp.json()
                if "choices" not in data:
                    raise Exception("Invalid OpenRouter response")

                return data["choices"][0]["message"]["content"]


async def openrouter_model_complete(
    prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs
) -> Union[str, AsyncIterator[str]]:
    """Complete function for OpenRouter model generation."""

    # Force non-streaming for keyword extraction
    if keyword_extraction:
        kwargs["stream"] = False

    # Get model name from config
    model_name = kwargs["hashing_kv"].global_config["llm_model_name"]

    return await _openrouter_model_if_cache(
        model_name,
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        **kwargs,
    )
