import asyncio
import uuid
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
    with open(file_path, mode="r", encoding="utf-8") as csv_file:
        reader = await loop.run_in_executor(
            None, lambda: list(csv.DictReader(csv_file))
        )

    # Convert all values to strings with double quotes
    json_data = [{str(k): str(v) for k, v in row.items()} for row in reader]

    return json_data  # List[Dict[str, Any]]


async def build_kg(flows: List[Dict[str, Any]], rag: LightRAG) -> None:
    """
    Builds a knowledge graph from flow data for threat hunting, where only IPs are entities,
    and all flow attributes are included as metadata in the relationships.

    :param flows: List of dictionaries representing flow data.
    :param rag: LightRAG instance to insert entities and relationships into.
    """
    # Sets to track unique entities and relationships by their identifiers (to prevent duplicates)
    existing_entities = set()
    existing_relationships = set()

    for flow in flows:
        # Extract core attributes
        flow_id = flow.get("Flow ID", str(uuid.uuid4()))
        src_ip = flow.get("Src IP")
        dst_ip = flow.get("Dst IP")
        src_port = str(flow.get("Src Port"))
        dst_port = str(flow.get("Dst Port"))
        protocol = str(flow.get("Protocol"))
        timestamp = flow.get("Timestamp", "Unknown Timestamp")
        flow_duration = flow.get("Flow Duration", "N/A")
        flow_bytes_per_second = flow.get("Flow Byts/s", "N/A")

        # === ENTITIES ===
        # Create entities for Source IP and Destination IP
        for ip, role in [(src_ip, "Source"), (dst_ip, "Destination")]:
            if ip and ip not in existing_entities:
                entity_data = {
                    "entity_name": ip,
                    "entity_type": "IP",
                    "description": (
                        f"This is the {role.lower()} IP address involved in network communication. "
                        f"It plays a key role in the flow of data between devices."
                    ),
                    "source_id": f"flow-{flow_id}",
                }
                try:
                    await rag.acreate_entity(ip, entity_data)
                    printTextColor(
                        Colors.SUCCESS, f"Entity '{ip}' created successfully."
                    )
                    existing_entities.add(ip)
                except Exception as e:
                    printTextColor(
                        Colors.WARNING, f"Failed to create entity '{ip}': {e}"
                    )

        # === RELATIONSHIPS ===
        # Create a relationship between Source IP and Destination IP with all attributes as metadata
        if (src_ip, dst_ip) not in existing_relationships:
            relationship_data = {
                "description": (
                    f"This relationship represents a network flow from the source IP address {src_ip} "
                    f"to the destination IP address {dst_ip}. The flow includes the following details:\n"
                    f"- **Flow ID**: {flow_id}\n"
                    f"- **Source Port**: {src_port}\n"
                    f"- **Destination Port**: {dst_port}\n"
                    f"- **Protocol**: {'TCP' if protocol == '6' else 'UDP'}\n"
                    f"- **Timestamp**: {timestamp}\n"
                    f"- **Flow Duration**: {flow_duration} microseconds\n"
                    f"- **Flow Bytes per Second**: {flow_bytes_per_second} bytes/s"
                ),
                "keywords": f"network flow, {protocol}, src_port: {src_port}, dst_port: {dst_port}",
                "weight": 1.0,
                "source_id": f"flow-{flow_id}",
            }
            try:
                await rag.acreate_relation(src_ip, dst_ip, relationship_data)
                printTextColor(
                    Colors.SUCCESS,
                    f"Relationship '{src_ip} -> {dst_ip}' created successfully.",
                )
                existing_relationships.add((src_ip, dst_ip))
            except Exception as e:
                printTextColor(
                    Colors.WARNING,
                    f"Failed to create relationship '{src_ip} -> {dst_ip}': {e}",
                )


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
            "options": {"num_ctx": 3200},  # "num_ctx": 32768
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
        flows = asyncio.run(csv_to_json_list("Skype.csv"))
        asyncio.run(build_kg(flows, rag))

    print("\nLocal Search:")
    print(rag.query("What does the graph represent?", param=QueryParam(mode="global")))
    # print(
    #     rag.query(
    #         "what ip address uses port 1968 ?", param=QueryParam(mode="local")
    #     )
    # )
    print(
        rag.query(
            "do you see any suspicius network activity in the graph ?",
            param=QueryParam(mode="local"),
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
