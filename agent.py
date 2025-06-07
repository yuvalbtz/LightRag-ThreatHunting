import os
import re
import requests
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dotenv import load_dotenv
import json
from smolagents import CodeAgent, tool
from smolagents.models import LiteLLMModel
from lightrag.base import QueryParam
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.lightrag import LightRAG
from lightrag.utils import EmbeddingFunc
from lightrag.llm.ollama import ollama_embed

# 📦 Load environment
load_dotenv()

# === 🔧 Configuration ===
DEEPSEEK_API_KEY = os.getenv("OPENROUTER_API_KEY")
DEEPSEEK_MODEL = "deepseek/deepseek-r1:free"
DEEPSEEK_API_BASE = "https://openrouter.ai/api/v1/chat/completions"
WORKING_DIR = "./email2a_vpn_kg"
EMBED_MODEL = "nomic-embed-text"
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5-coder:7b-instruct"  # Default Ollama model


async def initialize_rag_deepseek():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=deepseek_model_complete,
        llm_model_name=DEEPSEEK_MODEL,
        llm_model_max_token_size=32768,
        llm_model_kwargs={},
        embedding_func=EmbeddingFunc(
            embedding_dim=768,
            max_token_size=8192,
            func=lambda texts: ollama_embed(
                texts, embed_model=EMBED_MODEL, host=OLLAMA_HOST
            ),
        ),
    )
    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag


async def initialize_rag_ollama():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=ollama_model_complete,
        llm_model_name=OLLAMA_MODEL,
        llm_model_max_token_size=32768,
        llm_model_kwargs={
            "host": "http://localhost:11434",
            "options": {
                "num_ctx": 32768,
                "temperature": 0,
            },  # "num_ctx": 32768
        },
        embedding_func=EmbeddingFunc(
            embedding_dim=768,
            max_token_size=8192,
            func=lambda texts: ollama_embed(
                texts,
                embed_model="nomic-embed-text",
                host="http://localhost:11434",
            ),
        ),
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag


# === 🤖 LLM Integration for Ollama ===
async def ollama_model_complete(prompt: str, system_prompt: str = "", **kwargs) -> str:
    import aiohttp

    model = kwargs.get("model", OLLAMA_MODEL)  # Default to global or passed model
    host = kwargs.get("host", OLLAMA_HOST)  # Default to local Ollama host

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
            data = await resp.json()
            if "message" not in data:
                print("❌ Ollama API error:", data)
                return ""
            return data["message"]["content"]


# === 🤖 LLM Integration for DeepSeek ===
async def deepseek_model_complete(
    prompt: str, system_prompt: str = "", **kwargs
) -> str:
    import aiohttp

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    async with aiohttp.ClientSession() as session:
        async with session.post(
            DEEPSEEK_API_BASE,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": DEEPSEEK_MODEL,
                "messages": messages,
                "temperature": 0.0,
            },
        ) as resp:
            data = await resp.json()
            if "choices" not in data:
                print("❌ DeepSeek API error:", data)
                return ""
            return data["choices"][0]["message"]["content"]


# === 🛠️ Tools ===


@tool
async def fetch_sample_links(year: str = "2013", max_samples: int = 5) -> list[str]:
    """
    Fetch sample malware analysis blog links from a specific year.

    Args:
        year (str): The year to fetch blog links from.
        max_samples (int): The maximum number of sample links to return.

    Returns:
        list[str]: A list of sample blog URLs.
    """
    base_url = f"https://www.malware-traffic-analysis.net/{year}/"
    index_url = urljoin(base_url, "index.html")
    headers = {"User-Agent": "Mozilla/5.0"}

    resp = requests.get(index_url, headers=headers)
    if resp.status_code != 200:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    header_links = soup.find_all("a", class_="list_header", href=True)

    sample_links = [
        urljoin(base_url, a["href"])
        for a in header_links
        if re.fullmatch(r"\d{2}/\d{2}/index\d*\.html", a["href"])
    ]
    return sample_links[:max_samples]


@tool
async def extract_playbook(url: str) -> dict:
    """
    Extracts structured data from a malware blog post.

    Args:
        url (str): The URL of the malware blog post to extract information from.

    Returns:
        dict: A dictionary containing extracted playbook information.
    """

    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return {}

    soup = BeautifulSoup(resp.text, "html.parser")
    content = soup.get_text(separator="\n", strip=True)
    system_prompt = """
You are a cybersecurity analyst assistant. Given the raw text of a malware blog post, extract and return a structured JSON playbook with the following format:

{
  "sample_url": "<the blog URL>",
  "associated_files": ["list of file names (e.g., .zip, .exe, .doc)", ...],
  "snort_events": ["any Snort rules or alerts mentioned", ...],
  "infection_chain": ["step-by-step infection process", ...],
  "associated_domains": ["any suspicious domains or IPs mentioned", ...]
}

Only return the JSON object. Do not include any text before or after the JSON. Make sure the JSON is valid.
"""

    user_prompt = f"Blog content:\n{content}\n\nNow extract the playbook as described."

    try:
        response = await ollama_model_complete(
            prompt=user_prompt, system_prompt=system_prompt
        )

        # Optionally: clean invalid JSON chars
        response = response.replace("’", "'").replace("“", '"').replace("”", '"')

        parsed = json.loads(response)
        parsed["sample_url"] = url
        print(f"✅ Extracted playbook as json {parsed}")

        return parsed

    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON LLM response: {e}")
        print(f"🧾 Raw response:\n{response}")
        return {}
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return {}


@tool
async def playbook_to_graph_prompt(playbook: dict) -> dict:
    """
    Given a structured playbook dict, generate a JSON prompt object for
    the RAG graph LLM to perform anomaly detection or search.

    Args:
        playbook (dict): Structured malware playbook information.

    Returns:
        dict: JSON object containing the prompt for graph LLM.
    """
    if not playbook:
        return {"error": "Empty playbook provided."}

    # System prompt instructing the LLM how to convert playbook into a graph search prompt
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

    # Pass the playbook JSON as the user prompt (stringify it for LLM input)
    user_prompt = f"Convert this playbook into a graph search prompt:\n{json.dumps(playbook, indent=2)}"

    try:
        # Call your LLM model's async completion method (adjust function name if needed)
        response = await ollama_model_complete(
            system_prompt=system_prompt, prompt=user_prompt
        )

        # Clean and parse response as JSON
        response_clean = response.replace("’", "'").replace("“", '"').replace("”", '"')
        prompt_obj = json.loads(response_clean)

        return prompt_obj

    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error from LLM response: {e}")
        print(f"Raw LLM response:\n{response}")
        return {"error": "Failed to parse LLM JSON response"}

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return {"error": str(e)}


# @tool
# async def initialize_rag_and_search_graph(query: str) -> str:
#     """
#     Initialize LightRAG and perform a query over the graph.

#     Args:
#         query (str): The query string to search the knowledge graph.

#     Returns:
#         str: The result of the query.
#     """
#     rag = LightRAG(
#         working_dir=WORKING_DIR,
#         llm_model_func=deepseek_model_complete,
#         llm_model_name=DEEPSEEK_MODEL,
#         llm_model_max_token_size=32768,
#         llm_model_kwargs={},
#         embedding_func=EmbeddingFunc(
#             embedding_dim=768,
#             max_token_size=8192,
#             func=lambda texts: ollama_embed(
#                 texts, embed_model=EMBED_MODEL, host=OLLAMA_HOST
#             ),
#         ),
#     )

#     await rag.initialize_storages()
#     await initialize_pipeline_status()
#     return await rag.aquery(query, param=QueryParam(mode="global"))


@tool
async def generate_enriched_playbooks(
    year: str = "2013", max_samples: int = 3
) -> list[dict]:
    """
    Scrape blogs, extract playbooks, and enrich with RAG.

    Args:
        year (str): The year to fetch blog links from.
        max_samples (int): The maximum number of sample links to process.

    Returns:
        list[dict]: A list of enriched playbook dictionaries.
    """
    rag = await initialize_rag_ollama()

    links = await fetch_sample_links(year, max_samples)

    for link in links:
        print(f"📥 Extracting from: {link}")
        playbook = await extract_playbook(link)
        playbook_prompt_for_llm = await playbook_to_graph_prompt.forward(playbook)
        print(f"🔍 Generated prompt for LLM: {playbook_prompt_for_llm}")
        # prompt_str = playbook_prompt_for_llm.get("prompt", "")
        # insight = await rag.aquery(prompt_str)
        # print(f"🔍 Insight: {insight}")


def main():
    """
    Main function to run the agent.
    """
    agent = CodeAgent(
        model=LiteLLMModel(
            model_id="deepseek-chat",
            api_base=DEEPSEEK_API_BASE,
            api_key=DEEPSEEK_API_KEY,
        ),
        tools=[fetch_sample_links, extract_playbook, generate_enriched_playbooks],
    )
    return agent


async def run_agent():
    """
    Run the agent asynchronously.
    """
    agent = main()
    response = await agent.run("hello")
    return response


# === 🧪 Entry Point ===
if __name__ == "__main__":
    asyncio.run(generate_enriched_playbooks(year="2016", max_samples=1))
