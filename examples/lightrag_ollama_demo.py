import asyncio
import nest_asyncio
from utils import Colors, printTextColor
nest_asyncio.apply()
import os
import csv
import logging
from typing import List, Dict, Any
from lightrag import LightRAG, QueryParam
from lightrag.llm.ollama import ollama_model_complete, ollama_embed
from lightrag.utils import EmbeddingFunc
from lightrag.kg.shared_storage import initialize_pipeline_status


def is_folder_missing_or_empty(folder_path: str) -> bool:
    return not os.path.exists(folder_path) or not os.listdir(folder_path)

async def csv_to_json_list(file_path: str) -> List[Dict[str, Any]]:
    """
    Asynchronously converts a CSV file to a list of dictionaries.

    :param file_path: Path to the CSV file.
    :return: A list of dictionaries where each row is a dictionary with proper key-value pairs.
    """
    loop = asyncio.get_running_loop()

    # Read CSV asynchronously
    with open(file_path, mode='r', encoding='utf-8') as csv_file:
        reader = await loop.run_in_executor(None, lambda: list(csv.DictReader(csv_file)))

    # Convert all values to strings with double quotes
    json_data = [{str(k): str(v) for k, v in row.items()} for row in reader]

    return json_data  # List[Dict[str, Any]]



async def build_kg(flows: List[Dict[str, Any]], rag: LightRAG) -> None:
    # Sets to track unique entities and relationships by their identifiers (to prevent duplicates)
    existing_entities = set()
    existing_relationships = set()

    for flow in flows:
        flow_id = flow["Flow ID"]
        source_id = f"flow-{flow_id}"

        src_ip = flow["Src IP"]
        dst_ip = flow["Dst IP"]
        src_port = str(flow["Src Port"])
        dst_port = str(flow["Dst Port"])
        protocol = str(flow["Protocol"])
        flow_name = f"{src_ip} to {dst_ip}"

        # === ENTITIES ===
        entities = [
            (src_ip, {"entity_type": "Src IP", "description": "Source IP address", "source_id": source_id}),
            (dst_ip, {"entity_type": "Dst IP", "description": "Destination IP address", "source_id": source_id}),
            (src_port, {"entity_type": "Src Port", "description": "Source Port", "source_id": source_id}),
            (dst_port, {"entity_type": "Dst Port", "description": "Destination Port", "source_id": source_id}),
            (f"Protocol {protocol}", {"entity_type": "Protocol", "description": "TCP" if protocol == "6" else "UDP", "source_id": source_id}),
            (flow_name, {"entity_type": "Flow", "description": "Represents a communication flow", "source_id": source_id}),
        ]

        for entity, data in entities:
            try:
                # Skip if the entity already exists 
                if entity not in existing_entities:
                    await rag.acreate_entity(entity, data)  # Await the coroutine
                    printTextColor(Colors.SUCCESS, f"entity '{entity}' was created.")
                    existing_entities.add(entity)  # Add to the set to track it
            except Exception as e:
                printTextColor(Colors.WARNING, f"Failed to create entity '{entity}': {e}")

        # === RELATIONSHIPS ===
        relationships = [
            (src_ip, dst_ip, {"description": f"{src_ip} communicates with {dst_ip}", "keywords": "network, communication", "weight": 1.0, "source_id": source_id}),
            (src_ip, src_port, {"description": f"{src_ip} uses port {src_port}", "keywords": "source, port", "weight": 0.9, "source_id": source_id}),
            (dst_ip, dst_port, {"description": f"{dst_ip} uses port {dst_port}", "keywords": "destination, port", "weight": 0.9, "source_id": source_id}),
            (flow_name, f"Protocol {protocol}", {"description": f"Flow uses protocol {protocol}", "keywords": "protocol", "weight": 1.0, "source_id": source_id}),
        ]

        for src, tgt, data in relationships:
            try:
                # Skip if the relationship already exists
                if (src, tgt) not in existing_relationships:
                    await rag.acreate_relation(src, tgt, data)  # Await the coroutine
                    printTextColor(Colors.SUCCESS, f"relation '{src} -> {tgt}' was created.")
                    existing_relationships.add((src, tgt))  # Add to the set to track it
            except Exception as e:
                printTextColor(Colors.WARNING, f"Failed to create relation '{src} -> {tgt}': {e}")


WORKING_DIR = "./dickens_ollama"

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)


async def initialize_rag():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=ollama_model_complete,
        llm_model_name="qwen2.5:0.5b",
        llm_model_max_async=4,
        llm_model_max_token_size=32768,
        llm_model_kwargs={
            "host": "http://localhost:11434",
            "options": {"num_ctx": 3200}, # "num_ctx": 32768
        },
        embedding_func=EmbeddingFunc(
            embedding_dim=768,
            max_token_size=8192,
            func=lambda texts: ollama_embed(
                texts, embed_model="nomic-embed-text", host="http://localhost:11434"
            ),
        ),
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag


async def print_stream(stream):
    async for chunk in stream:
        print(chunk, end="", flush=True)

def main():
    # Initialize RAG instance
    rag = asyncio.run(initialize_rag())
    if is_folder_missing_or_empty(WORKING_DIR):
        flows = asyncio.run(csv_to_json_list('Skype.csv'))
        asyncio.run(build_kg(flows, rag))

    print("\nLocal Search:")
    print(
        rag.query(
            "what the graph represent ?", param=QueryParam(mode="local")
        )
    )
    # print(
    #     rag.query(
    #         "what ip address uses port 1968 ?", param=QueryParam(mode="local")
    #     )
    # )
    print(
        rag.query(
            "do you see any suspicius network activity in the graph ?", param=QueryParam(mode="local")
        )
    )


    # stream response
    # resp = rag.query(
    #     "What are the top themes in this story?",
    #     param=QueryParam(mode="hybrid", stream=True),
    # )

    # if inspect.isasyncgen(resp):
    #     asyncio.run(print_stream(resp))
    # else:
    #     print(resp)


if __name__ == "__main__":
    main()
