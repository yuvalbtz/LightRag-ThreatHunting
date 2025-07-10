import os
import re
from fastapi import HTTPException
import requests
import asyncio
import logging
import json
import time
from functools import lru_cache, wraps
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dotenv import load_dotenv
from examples.utils import read_json_file

from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.lightrag import LightRAG
from lightrag.utils import EmbeddingFunc
from lightrag.llm.ollama import ollama_embed
from lightrag.llm.open_router import openrouter_model_complete
import pipmaster as pm

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 📦 Load environment
load_dotenv()

# === 🔧 Configuration ===
DEEPSEEK_API_KEY = os.getenv("OPENROUTER_API_KEY")
DEEPSEEK_MODEL = "deepseek/deepseek-r1:free"
DEEPSEEK_API_BASE = "https://openrouter.ai/api/v1/chat/completions"
WORKING_DIR = "./email2a_vpn_kg"
EMBED_MODEL = "nomic-embed-text"
OLLAMA_HOST = "http://ollama:11434"
OLLAMA_MODEL = "qwen2.5:1.5b"

# Cache configuration
CACHE_TTL = 3600  # 1 hour in seconds
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds


def retry_on_failure(max_retries: int = MAX_RETRIES, delay: int = RETRY_DELAY):
    """Decorator for retrying functions on failure."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}"
                    )
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (attempt + 1))
            raise last_exception

        return wrapper

    return decorator


@lru_cache(maxsize=128)
def get_rag_instance(
    model_type: str = "ollama",
    working_dir: str = "custom_kg",
) -> LightRAG:
    """Get or create a cached RAG instance."""
    if model_type == "ollama":
        print(f"get_rag_instance-ollama-working_dir: {working_dir}")
        return LightRAG(
            working_dir=f"./AppDbStore/{working_dir}",
            llm_model_func=ollama_model_complete,
            llm_model_name=OLLAMA_MODEL,
            llm_model_max_token_size=32768,
            llm_model_kwargs={
                "host": OLLAMA_HOST,
                "options": {
                    "num_ctx": 32768,
                    "temperature": 0,
                },
            },
            embedding_func=EmbeddingFunc(
                embedding_dim=768,
                max_token_size=8192,
                func=lambda texts: ollama_embed(
                    texts,
                    embed_model=EMBED_MODEL,
                    host=OLLAMA_HOST,
                ),
            ),
        )
    else:
        return LightRAG(
            working_dir=f"./AppDbStore/{working_dir}",
            llm_model_func=openrouter_model_complete,
            llm_model_name=DEEPSEEK_MODEL,
            llm_model_max_token_size=164000,
            llm_model_kwargs={
                "temperature": 0.0,
                "num_ctx": 164000,
            },
            embedding_func=EmbeddingFunc(
                embedding_dim=768,
                max_token_size=8192,
                func=lambda texts: ollama_embed(
                    texts, embed_model=EMBED_MODEL, host=OLLAMA_HOST
                ),
            ),
        )


async def initialize_rag_deepseek(working_dir: str = "custom_kg"):
    """Initialize RAG with DeepSeek model."""
    try:
        # Debug: Check the type and value of working_dir
        logger.info(
            f"Initializing RAG with DeepSeek - working_dir type: {type(working_dir)}, value: {working_dir}"
        )

        # Ensure working_dir is a string
        if not isinstance(working_dir, str):
            logger.error(
                f"working_dir must be a string, got {type(working_dir)}: {working_dir}"
            )
            raise ValueError(f"working_dir must be a string, got {type(working_dir)}")

        # Get conversation history
        history_messages = await get_conversation_history(dir_path=working_dir)
        logger.info(f"Loaded {len(history_messages)} conversation history messages")

        # Create RAG instance with conversation history in model kwargs
        rag = get_rag_instance(
            model_type="deepseek",
            working_dir=working_dir,
        )

        # Update the model kwargs to include conversation history
        rag.llm_model_kwargs["conversation_history"] = history_messages
        await rag.initialize_storages()
        await initialize_pipeline_status()
        logger.info("Successfully initialized RAG with DeepSeek model")
        return rag
    except Exception as e:
        logger.error(f"Failed to initialize RAG with DeepSeek: {str(e)}")
        raise


async def initialize_rag_ollama(working_dir: str = "./custom_kg"):
    """Initialize RAG with Ollama model."""
    try:
        # Get conversation history
        history_messages = await get_conversation_history(dir_path=working_dir)
        logger.info(f"Loaded {len(history_messages)} conversation history messages")

        # Create RAG instance with conversation history in model kwargs
        rag = get_rag_instance("ollama", working_dir=working_dir)

        # Update the model kwargs to include conversation history
        rag.llm_model_kwargs["conversation_history"] = history_messages
        await rag.initialize_storages()
        await initialize_pipeline_status()
        logger.info("Successfully initialized RAG with Ollama model")
        return rag
    except Exception as e:
        logger.error(f"Failed to initialize RAG with Ollama: {str(e)}")
        raise


@retry_on_failure()
async def ollama_model_complete(prompt: str, system_prompt: str = "", **kwargs) -> str:
    """Complete text using Ollama model with retry logic."""
    import aiohttp

    model = kwargs.get("model", OLLAMA_MODEL)
    host = kwargs.get("host", OLLAMA_HOST)

    payload = {
        "model": model,
        "messages": [],
        "stream": False,
        "temperature": 0.0,
        "num_ctx": 32768,
    }

    if system_prompt:
        payload["messages"].append({"role": "system", "content": system_prompt})
    payload["messages"].append({"role": "user", "content": prompt})

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{host}/api/chat", json=payload) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                logger.error(f"Ollama API error: {error_text}")
                raise Exception(f"Ollama API error: {error_text}")

            data = await resp.json()
            if "message" not in data:
                logger.error(f"Invalid Ollama response: {data}")
                raise Exception("Invalid Ollama response")

            return data["message"]["content"]


@retry_on_failure()
async def deepseek_model_complete(prompt: str, system_prompt: str = "", **kwargs):
    """Complete text using OpenRouter model with streaming support."""
    from lightrag.llm.open_router import openrouter_model_complete

    return await openrouter_model_complete(
        prompt=prompt, system_prompt=system_prompt, **kwargs
    )


# Set the current model completion function
current_model_complete = deepseek_model_complete

# Set the current RAG initialization function
current_initialize_rag_model = initialize_rag_ollama


async def get_graph_llm_conversations(
    dir_path: str = "custom_kg",
) -> List[Dict[str, Any]]:
    """Get graph LLM conversations for a given directory."""
    try:
        if not os.path.exists(
            f"./AppDbStore/{dir_path}/kv_store_llm_response_cache.json"
        ):
            return []

        conversations_data = await read_json_file(
            f"./AppDbStore/{dir_path}/kv_store_llm_response_cache.json"
        )
        return conversations_data
    except Exception as e:
        logger.error(f"Failed to get graph LLM conversations: {str(e)}")
        raise


async def generate_visual_graph(dir_path: str = "./custom_kg") -> Dict[str, Any]:
    """Generate graph data compatible with vis-network."""
    if not pm.is_installed("pyvis"):
        pm.install("pyvis")
    if not pm.is_installed("networkx"):
        pm.install("networkx")

    import networkx as nx
    from pyvis.network import Network
    import random

    # Load the GraphML file
    G = nx.read_graphml(f"./AppDbStore/{dir_path}/graph_chunk_entity_relation.graphml")
    G = nx.MultiDiGraph(G)
    # Create a Pyvis network
    net = Network(height="100vh", notebook=True)

    # Convert NetworkX graph to Pyvis network
    net.from_nx(G)

    # Prepare nodes for vis-network
    nodes = []
    for node in net.nodes:
        node_data = {
            "id": node["id"],
            "label": node.get("label", node["id"]),
            "color": "#{:06x}".format(random.randint(0, 0xFFFFFF)),
            "title": node.get("description", ""),
            "group": node.get("group", "default"),
        }
        nodes.append(node_data)

    # Prepare edges for vis-network
    edges = []
    for edge in net.edges:
        edge_data = {
            "from": edge["from"],
            "to": edge["to"],
            "label": edge.get("label", ""),
            "title": edge.get("description", ""),
            "arrows": "to",
            "smooth": {"type": "continuous"},
        }
        edges.append(edge_data)

    return {"nodes": nodes, "edges": edges}


@retry_on_failure()
async def fetch_sample_links(year: str = "2013", max_samples: int = 5) -> List[str]:
    """Fetch sample malware analysis blog links with retry logic."""
    base_url = f"https://www.malware-traffic-analysis.net/{year}/"
    index_url = urljoin(base_url, "index.html")
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }

    try:
        resp = requests.get(index_url, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch sample links: {str(e)}")
        raise

    soup = BeautifulSoup(resp.text, "html.parser")
    header_links = soup.find_all("a", class_="list_header", href=True)

    sample_links = [
        urljoin(base_url, a["href"])
        for a in header_links
        if re.fullmatch(r"\d{2}/\d{2}/index\d*\.html", a["href"])
    ]

    logger.info(f"Found {len(sample_links)} sample links for year {year}")
    return sample_links[:max_samples]


FLOW_FEATURES = [
    "Source IP",
    "Destination IP",
    "Source Port",
    "Destination Port",
    "Protocol",
    "Flow Duration",
    "Flow Bytes/s",
    "Flow Packets/s",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Fwd Packet Length Mean",
    "Bwd Packet Length Mean",
    "SYN Flag Count",
    "ACK Flag Count",
    "RST Flag Count",
    "Idle Mean",
    "Active Mean",
    "Down/Up Ratio",
]


async def fetch_playbook_content(url: str) -> Dict[str, Any]:
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch blog post {url}: {str(e)}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    content = soup.get_text(separator="\n", strip=True)

    system_prompt = f"""
You are a cybersecurity analyst assistant.

Given the raw text of a malware blog post and a list of flow-based features,
your task is to extract the following:

1. **malware_name**: Name(s) of malware families mentioned (e.g. Simda, Emotet, Dridex)
2. **hunt_goal**: A 1-sentence summary of the hunting objective (e.g. detect download and C2 behavior of Simda)
3. **generated_prompt**: A smart investigation prompt using only these flow features:

{", ".join(FLOW_FEATURES)}

This prompt should:
- Include 5–7 flow-based investigation questions
- Reference only flow metadata, no payloads, hashes, or domains
- Be usable as an input to another LLM or analyst
- Write in a way that is easy to understand and use

Return your output in the following **valid JSON format only** (no explanation):

{{
  "malware_name": "...",
  "hunt_goal": "...",
  "generated_prompt": "..."
}}
"""

    user_prompt = f"Blog content:\n{content[:4000]}\n\nExtract the required JSON."

    try:
        response = await current_model_complete(
            prompt=user_prompt, system_prompt=system_prompt
        )

        if not response or not response.strip():
            logger.error(f"Empty response from model for {url}")
            return None

        # Extract and clean JSON
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response[json_start:json_end]
            try:
                parsed = json.loads(json_str)
                return {
                    "sample_url": url,
                    "malware_name": parsed.get("malware_name", ""),
                    "hunt_goal": parsed.get("hunt_goal", ""),
                    "generated_prompt": parsed.get("generated_prompt", ""),
                }
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response for {url}: {str(e)}")
                return None

        logger.error(f"No JSON object found in model output for {url}")
        return None

    except Exception as e:
        logger.error(f"Error processing {url}: {str(e)}")
        return None


async def fetch_all_playbooks(
    year: str = "2013", max_samples: int = 2
) -> List[Dict[str, Any]]:
    """Fetch and process multiple playbooks in parallel."""
    # Get all sample links
    links = await fetch_sample_links(year, max_samples)

    # Process all links concurrently
    tasks = [fetch_playbook_content(link) for link in links]
    playbooks = await asyncio.gather(*tasks)

    # Filter out None results and return valid playbooks
    return [p for p in playbooks if p is not None]


@retry_on_failure()
async def playbook_to_graph_prompt(playbook: Dict[str, Any]) -> Dict[str, str]:
    """Convert playbook to graph prompt with retry logic."""
    if not playbook:
        logger.error("Empty playbook provided")
        raise ValueError("Empty playbook provided")

    system_prompt = """
You are an assistant that converts a malware playbook JSON object into
a prompt for a graph-based LLM to search for related anomalies, threats,
and context in a knowledge graph.

Return only a valid JSON object with a single field 'prompt' that contains
a clear, detailed prompt for the graph LLM.

Example output format:
{
  "prompt": "<your generated prompt text here>"
}
"""

    user_prompt = f"Convert this playbook into a graph search prompt:\n{json.dumps(playbook, indent=2)}"

    try:
        response = await current_model_complete(
            system_prompt=system_prompt, prompt=user_prompt
        )

        # Clean and parse response
        response_clean = response.replace("'", "'").replace(""", '"').replace(""", '"')
        prompt_obj = json.loads(response_clean)

        logger.info("Successfully converted playbook to graph prompt")
        return prompt_obj

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {str(e)}")
        logger.debug(f"Raw response: {response}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in playbook_to_graph_prompt: {str(e)}")
        raise


# Stores past conversation history to maintain context.
# Format: [{"role": "user/assistant", "content": "message"}]
# from kv_store_llm_response_cache.json
async def get_conversation_history(
    dir_path: str = "custom_kg",
) -> List[Dict[str, Any]]:
    try:
        raw_data = await get_graph_llm_conversations(dir_path=dir_path)
        if not raw_data:
            return []
        hybrid_data = raw_data.get("hybrid", {})

        history_messages: List[Dict[str, Any]] = []

        for _, entry in hybrid_data.items():
            if entry.get("cache_type") == "query":
                prompt = entry.get("original_prompt", "")
                response = entry.get("return", "")

                # Append user message
                if prompt:
                    history_messages.append(
                        {
                            "content": prompt,
                            "role": "user",
                        }
                    )

                # Append assistant message
                if response:
                    history_messages.append(
                        {
                            "content": response,
                            "role": "assistant",
                        }
                    )

        return history_messages

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def generate_enriched_playbooks(
    year: str = "2013", max_samples: int = 3
) -> List[Dict[str, Any]]:
    """Generate enriched playbooks with improved error handling and logging."""
    start_time = time.time()

    try:
        rag = await current_initialize_rag_model()
        playbooks = await fetch_all_playbooks(year, max_samples)

        enriched_playbooks = []
        for playbook in playbooks:
            try:
                playbook_prompt = await playbook_to_graph_prompt(playbook)

                # Add enrichment data
                playbook["enrichment"] = {
                    "processing_time": time.time() - start_time,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "graph_prompt": playbook_prompt,
                }

                enriched_playbooks.append(playbook)
                logger.info(f"Successfully processed {playbook['sample_url']}")

            except Exception as e:
                logger.error(
                    f"Failed to process {playbook.get('sample_url', 'unknown')}: {str(e)}"
                )
                continue

        logger.info(
            f"Generated {len(enriched_playbooks)} enriched playbooks in {time.time() - start_time:.2f} seconds"
        )
        return enriched_playbooks

    except Exception as e:
        logger.error(f"Failed to generate enriched playbooks: {str(e)}")
        raise


if __name__ == "__main__":
    # playbooks = asyncio.run(fetch_all_playbooks(year="2014", max_samples=1))
    # print("playbook", playbooks)
    # graph_prompt = asyncio.run(playbook_to_graph_prompt(playbooks[0]))
    # print("graph promt", graph_prompt)
    history_messages = asyncio.run(get_conversation_history(dir_path="Friday-PortScan"))
    print("history messages", history_messages)
