import asyncio
import csv
import os
from lightrag import LightRAG
from lightrag.base import QueryParam
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.llm.ollama import ollama_embed, ollama_model_complete
from lightrag.llm.openai import gpt_4o_mini_complete
from lightrag.utils import EmbeddingFunc
import uuid
from typing import List, Dict, Any

#########
# Uncomment the below two lines if running in a jupyter notebook to handle the async nature of rag.insert()
# import nest_asyncio
# nest_asyncio.apply()
#########


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


def is_folder_missing_or_empty(folder_path: str) -> bool:
    return not os.path.exists(folder_path) or not os.listdir(folder_path)


async def build_kg(flows: List[Dict[str, Any]], rag: LightRAG) -> None:
    """
    Build and insert a custom knowledge graph into LightRAG from flow records.

    :param flows: List of flow dictionaries.
    :param rag: LightRAG instance with `insert_custom_kg(custom_kg)` method.
    """
    entity_map = {}
    relationships = []
    chunks = []

    chunks.insert(
        0,
        {
            "content": (
                "This knowledge graph visualizes network traffic flows between IP addresses. "
                "Each entity represents an IP, and relationships indicate flows with protocol, ports, throughput, and timestamp."
            ),
            "source_id": "overview",
            "source_chunk_index": 0,
        },
    )

    for index, flow in enumerate(flows):
        flow_id = flow.get("Flow ID", str(uuid.uuid4()))
        src_ip = flow.get("Src IP")
        dst_ip = flow.get("Dst IP")
        src_port = str(flow.get("Src Port"))
        dst_port = str(flow.get("Dst Port"))
        protocol = str(flow.get("Protocol"))
        timestamp = flow.get("Timestamp", "Unknown Timestamp")
        flow_duration = flow.get("Flow Duration", "N/A")
        flow_bytes_per_second = flow.get("Flow Byts/s", "N/A")
        label = flow.get("Label", "Unknown")
        source_id = f"flow-{flow_id}"

        # Entities
        for ip, role in [(src_ip, "Source"), (dst_ip, "Destination")]:
            if ip and ip not in entity_map:
                entity_map[ip] = {
                    "entity_name": ip,
                    "entity_type": "IP",
                    "description": (
                        f"This is the {role.lower()} IP address involved in a {label} session. "
                        f"It plays a key role in the flow of data between devices."
                    ),
                    "source_id": source_id,
                }

        # Relationship
        if src_ip and dst_ip:
            relationships.append(
                {
                    "src_id": src_ip,
                    "tgt_id": dst_ip,
                    "description": (
                        f"This relationship represents a {label} flow from source IP {src_ip} to destination IP {dst_ip}.\n"
                        f"- Flow ID: {flow_id}\n"
                        f"- Ports: {src_port} → {dst_port}\n"
                        f"- Protocol: {'TCP' if protocol == '6' else 'UDP'}\n"
                        f"- Timestamp: {timestamp}\n"
                        f"- Duration: {flow_duration} µs\n"
                        f"- Throughput: {flow_bytes_per_second} Bps"
                    ),
                    "keywords": f"flow, traffic, port:{src_port}-{dst_port}, protocol:{protocol}, label:{label}",
                    "weight": 1.0,
                    "source_id": source_id,
                }
            )

        # Chunk
        chunks.append(
            {
                "content": (
                    f"A {label} session was recorded from {src_ip}:{src_port} to {dst_ip}:{dst_port} "
                    f"over protocol {protocol}. Duration: {flow_duration} µs, Throughput: {flow_bytes_per_second} Bps."
                ),
                "source_id": source_id,
                "source_chunk_index": index,
            }
        )

    # Combine into the correct format
    custom_kg = {
        "entities": list(entity_map.values()),
        "relationships": relationships,
        "chunks": chunks,
    }

    try:
        await rag.ainsert_custom_kg(custom_kg)
    except Exception as e:
        print(f"Error inserting custom KG: {e}")


WORKING_DIR = "./custom_kg"

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)

# rag = LightRAG(
#     working_dir=WORKING_DIR,
#     llm_model_func=,  # Use gpt_4o_mini_complete LLM model
#     # llm_model_func=gpt_4o_complete  # Optionally, use a stronger model
# )

custom_kg = {
    "entities": [
        {
            "entity_name": "CompanyA",
            "entity_type": "Organization",
            "description": "A major technology company",
            "source_id": "Source1",
        },
        {
            "entity_name": "ProductX",
            "entity_type": "Product",
            "description": "A popular product developed by CompanyA",
            "source_id": "Source1",
        },
        {
            "entity_name": "PersonA",
            "entity_type": "Person",
            "description": "A renowned researcher in AI",
            "source_id": "Source2",
        },
        {
            "entity_name": "UniversityB",
            "entity_type": "Organization",
            "description": "A leading university specializing in technology and sciences",
            "source_id": "Source2",
        },
        {
            "entity_name": "CityC",
            "entity_type": "Location",
            "description": "A large metropolitan city known for its culture and economy",
            "source_id": "Source3",
        },
        {
            "entity_name": "EventY",
            "entity_type": "Event",
            "description": "An annual technology conference held in CityC",
            "source_id": "Source3",
        },
    ],
    "relationships": [
        {
            "src_id": "CompanyA",
            "tgt_id": "ProductX",
            "description": "CompanyA develops ProductX",
            "keywords": "develop, produce",
            "weight": 1.0,
            "source_id": "Source1",
        },
        {
            "src_id": "PersonA",
            "tgt_id": "UniversityB",
            "description": "PersonA works at UniversityB",
            "keywords": "employment, affiliation",
            "weight": 0.9,
            "source_id": "Source2",
        },
        {
            "src_id": "CityC",
            "tgt_id": "EventY",
            "description": "EventY is hosted in CityC",
            "keywords": "host, location",
            "weight": 0.8,
            "source_id": "Source3",
        },
    ],
    "chunks": [
        {
            "content": "ProductX, developed by CompanyA, has revolutionized the market with its cutting-edge features.",
            "source_id": "Source1",
            "source_chunk_index": 0,
        },
        {
            "content": "One outstanding feature of ProductX is its advanced AI capabilities.",
            "source_id": "Source1",
            "chunk_order_index": 1,
        },
        {
            "content": "PersonA is a prominent researcher at UniversityB, focusing on artificial intelligence and machine learning.",
            "source_id": "Source2",
            "source_chunk_index": 0,
        },
        {
            "content": "EventY, held in CityC, attracts technology enthusiasts and companies from around the globe.",
            "source_id": "Source3",
            "source_chunk_index": 0,
        },
        {
            "content": "None",
            "source_id": "UNKNOWN",
            "source_chunk_index": 0,
        },
    ],
}


async def initialize_rag():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=ollama_model_complete,
        llm_model_name="llama3.2",
        llm_model_max_token_size=32768,
        llm_model_kwargs={
            "host": "http://localhost:11434",
            "options": {"num_ctx": 3200},  # "num_ctx": 32768
        },
        embedding_func=EmbeddingFunc(
            embedding_dim=1024,
            max_token_size=8192,
            func=lambda texts: ollama_embed(
                texts,
                embed_model="qllama/bge-large-en-v1.5",
                host="http://localhost:11434",
            ),
        ),
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag


def main():

    rag = asyncio.run(initialize_rag())

    if is_folder_missing_or_empty(WORKING_DIR):
        flows = asyncio.run(csv_to_json_list("Skype.csv"))
        asyncio.run(build_kg(flows, rag))

    # Initialize RAG instance
    print("Custom knowledge graph inserted successfully.")
    print("Entities, relationships, and chunks have been added to the knowledge graph.")

    # Example query
    query = "What does this kg graph represent ?"
    response = rag.query(query, param=QueryParam(mode="global"))
    print(f"Query: {query}")
    print(f"Response: {response}")


if __name__ == "__main__":
    main()
