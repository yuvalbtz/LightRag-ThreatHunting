import asyncio
import sys
from dotenv import load_dotenv
from fastapi import HTTPException, status

load_dotenv()

if sys.version_info < (3, 9):
    from typing import AsyncIterator
else:
    from collections.abc import AsyncIterator

import logging
import pipmaster as pm

# Install dependencies dynamically if missing
if not pm.is_installed("requests"):
    pm.install("requests")
if not pm.is_installed("tenacity"):
    pm.install("tenacity")

import requests
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

from typing import Union, Optional, List

logger = logging.getLogger(__name__)


async def _openrouter_model_if_cache(
    model: str,
    prompt: str,
    system_prompt: Optional[str] = None,
    history_messages: Optional[List[dict]] = None,
    **kwargs,
) -> Union[str, AsyncIterator[str]]:
    """OpenRouter model completion with optional streaming."""
    history_messages = history_messages or []

    # Get stream parameter and remove from kwargs
    stream = kwargs.pop("stream", False)

    print("===== Entering OpenRouter LLM function =====")
    print(f"Model: {model}")
    print(f"Stream: {stream}")
    print(f"Additional kwargs: {kwargs}")
    print(f"Num of history messages: {len(history_messages)}")
    try:
        response = await _make_openrouter_request(
            model, prompt, system_prompt, history_messages, stream=stream, **kwargs
        )

        # Handle streaming response like OpenAI does
        if hasattr(response, "__aiter__"):

            async def inner():
                try:
                    async for chunk in response:
                        if chunk:
                            yield chunk
                except Exception as e:
                    logger.error(f"Error in stream response: {str(e)}")
                    raise

            return inner()
        else:
            # Non-streaming response
            if not response or response.strip() == "":
                logger.error("Received empty content from OpenRouter API")
                raise Exception("Received empty content from OpenRouter API")

            logger.debug(f"Response content len: {len(response)}")
            return response

    except Exception as e:
        logger.error(f"OpenRouter API call failed: {e}")
        raise


async def _make_openrouter_request(
    model: str,
    prompt: str,
    system_prompt: Optional[str] = None,
    history_messages: Optional[List[dict]] = None,
    stream: bool = False,
    **kwargs,
) -> Union[str, AsyncIterator[str]]:
    """Make the actual OpenRouter API request."""
    history_messages = history_messages or []
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is required")

    api_base = "https://openrouter.ai/api/v1/chat/completions"

    # Prepare message format
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    # Prepare payload
    payload = {
        "model": model,
        "messages": messages,
        "temperature": kwargs.get("temperature", 0.0),
        "stream": stream,
    }
    for param in [
        "max_tokens",
        "top_p",
        "frequency_penalty",
        "presence_penalty",
        "response_format",
    ]:
        if param in kwargs:
            payload[param] = kwargs[param]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    print(f"Making request to: {api_base}")
    print(f"Headers: {headers}")
    print(f"Payload: {payload}")

    # Create session with custom DNS resolution
    session = requests.Session()
    session.mount("https://", requests.adapters.HTTPAdapter(max_retries=3))

    if stream:
        # Use requests for streaming like the official example
        print("Using OpenRouter streaming API with requests")

        async def stream_generator() -> AsyncIterator[str]:
            try:
                print("Starting real OpenRouter streaming")
                buffer = ""
                with session.post(
                    api_base,
                    headers=headers,
                    json=payload,
                    stream=True,
                    verify=True,
                    timeout=30,
                ) as r:
                    print(f"Response status: {r.status_code}")
                    print(f"Response headers: {dict(r.headers)}")

                    if r.status_code != 200:
                        error_text = r.text
                        logger.error(f"OpenRouter API error: {error_text}")
                        raise Exception(f"OpenRouter API error: {error_text}")

                    for chunk in r.iter_content(chunk_size=1024, decode_unicode=True):
                        buffer += chunk
                        print(f"Buffer length: {len(buffer)}")

                        while True:
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
                                    data_obj = json.loads(data)
                                    content = data_obj["choices"][0]["delta"].get(
                                        "content"
                                    )
                                    if content:
                                        yield content
                                except json.JSONDecodeError:
                                    pass

            except Exception as e:
                logger.error(f"Unexpected streaming error: {e}")
                raise

        return stream_generator()
    else:
        # Non-streaming request
        response = session.post(
            api_base, headers=headers, json=payload, verify=True, timeout=30
        )
        print(f"Response status: {response.status_code}")

        if response.status_code != 200:
            error_text = response.text
            logger.error(f"OpenRouter API error: {error_text}")
            raise Exception(f"OpenRouter API error: {error_text}")

        data = response.json()
        if "choices" not in data:
            raise ValueError("Invalid OpenRouter response")

        content = data["choices"][0]["message"]["content"]
        if not content or content.strip() == "":
            raise Exception("Received empty content from OpenRouter API")

        return content


async def openrouter_model_complete(
    prompt: str,
    system_prompt: Optional[str] = None,
    history_messages: Optional[List[dict]] = None,
    keyword_extraction: bool = False,
    **kwargs,
) -> Union[str, AsyncIterator[str]]:
    """Main LLM interface."""
    history_messages = history_messages or []

    # Handle keyword extraction like OpenAI does
    keyword_extraction = kwargs.pop("keyword_extraction", None)
    if keyword_extraction:
        kwargs["response_format"] = "json"

    model_name = kwargs["hashing_kv"].global_config["llm_model_name"]
    logger.info(f"Calling OpenRouter model: {model_name}")

    return await _openrouter_model_if_cache(
        model_name,
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        **kwargs,
    )
