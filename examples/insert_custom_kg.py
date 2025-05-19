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

    :param flows: List of flow dictionaries parsed from CSV.
    :param rag: LightRAG instance with `ainsert_custom_kg(custom_kg)` method.
    """
    entity_map = {}
    relationships = []
    chunks = []

    # Overview chunk
    chunks.append(
        {
            "content": (
                "This knowledge graph visualizes network traffic flow characteristics extracted from packet captures. "
                "Each entity represents a session label (e.g., VPN or Non-VPN), and relationships capture statistics "
                "such as duration, throughput, and timing metrics."
            ),
            "source_id": "overview",
            "source_chunk_index": 0,
        }
    )

    for index, flow in enumerate(flows):
        session_id = str(uuid.uuid4())
        label = flow.get("class1", "Unknown")
        source_id = f"session-{session_id}"

        # Create one entity per traffic class label
        if label not in entity_map:
            entity_map[label] = {
                "entity_name": label,
                "entity_type": "Traffic Class",
                "description": f"{label} traffic sessions with flow-level statistical features.",
                "source_id": f"entity-{label}",
            }

        # Build relationship details
        relationship_desc = (
            f"This is a {label} session with the following characteristics:\n"
            f"- Duration: {flow.get('duration', 'N/A')} µs\n"
            f"- Total Forward Bytes (fiat): {flow.get('total_fiat', 'N/A')}\n"
            f"- Total Backward Bytes (biat): {flow.get('total_biat', 'N/A')}\n"
            f"- Mean Forward IAT: {flow.get('mean_fiat', 'N/A')}\n"
            f"- Mean Backward IAT: {flow.get('mean_biat', 'N/A')}\n"
            f"- Flow Packets/sec: {flow.get('flowPktsPerSecond', 'N/A')}\n"
            f"- Flow Bytes/sec: {flow.get('flowBytesPerSecond', 'N/A')}\n"
            f"- Std Dev of Idle Time: {flow.get('std_idle', 'N/A')}"
        )

        relationships.append(
            {
                "src_id": label,
                "tgt_id": session_id,
                "description": relationship_desc,
                "keywords": f"flow, {label}, statistics, traffic, performance",
                "weight": 1.0,
                "source_id": source_id,
            }
        )

        # Chunk for retrieval
        chunks.append(
            {
                "content": (
                    f"A network flow labeled as {label} was observed. "
                    f"Duration: {flow.get('duration', 'N/A')} µs, "
                    f"total fiat: {flow.get('total_fiat', 'N/A')}, "
                    f"biat: {flow.get('total_biat', 'N/A')}, "
                    f"throughput: {flow.get('flowBytesPerSecond', 'N/A')} Bps."
                ),
                "source_id": source_id,
                "source_chunk_index": index + 1,
            }
        )

    # Final KG
    custom_kg = {
        "entities": list(entity_map.values()),
        "relationships": relationships,
        "chunks": chunks,
    }

    try:
        await rag.ainsert_custom_kg(custom_kg)
    except Exception as e:
        print(f"Error inserting custom KG: {e}")


async def build_kg_email2a(flows: List[Dict[str, Any]], rag: LightRAG) -> None:
    """
    Build and insert a custom knowledge graph into LightRAG from packet-level flow records.

    :param flows: List of packet dictionaries parsed from CSV.
    :param rag: LightRAG instance with `ainsert_custom_kg(custom_kg)` method.
    """
    entity_map = {}
    relationships = []
    chunks = []

    # Overview chunk
    chunks.append(
        {
            "content": (
                "This knowledge graph visualizes individual network packet flows. "
                "Each entity represents an IP address participating in the network, and edges show communication "
                "between source and destination IPs with associated protocol, timing, and packet metadata."
            ),
            "source_id": "overview",
            "source_chunk_index": 0,
        }
    )

    for index, packet in enumerate(flows):
        source_ip = packet["Source"]
        dest_ip = packet["Destination"]
        protocol = packet["Protocol"]
        info = packet["Info"]
        time = packet["Time"]
        length = packet["Length"]
        session_id = str(uuid.uuid4())
        source_id = f"packet-{session_id}"

        # Add source and destination entities if not already added
        for ip in (source_ip, dest_ip):
            if ip not in entity_map:
                entity_map[ip] = {
                    "entity_name": ip,
                    "entity_type": "IP Address",
                    "description": f"IP address involved in network traffic.",
                    "source_id": f"entity-{ip}",
                }

        # Add relationship (source → destination)
        relationships.append(
            {
                "src_id": source_ip,
                "tgt_id": dest_ip,
                "description": (
                    f"Packet sent from {source_ip} to {dest_ip} using {protocol} protocol at time {time}s. "
                    f"Packet length: {length} bytes. Info: {info}"
                ),
                "keywords": f"{protocol}, packet, traffic, {source_ip}, {dest_ip}",
                "weight": 1.0,
                "source_id": source_id,
            }
        )

        # Add chunk for this packet
        chunks.append(
            {
                "content": (
                    f"Packet from {source_ip} to {dest_ip} at time {time}s using protocol {protocol}. "
                    f"Length: {length} bytes. Details: {info}."
                ),
                "source_id": source_id,
                "source_chunk_index": index + 1,
            }
        )

    # Final KG
    custom_kg = {
        "entities": list(entity_map.values()),
        "relationships": relationships,
        "chunks": chunks,
    }

    try:
        await rag.ainsert_custom_kg(custom_kg)
    except Exception as e:
        print(f"Error inserting custom KG: {e}")


WORKING_DIR = "./email2a_vpn_kg"

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
        llm_model_name="qwen2.5:1.5b",
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


async def interactive_chat(rag: LightRAG):
    print("\n🔁 Enter 'exit' or 'quit' to end the chat.")
    while True:
        query = input("🧠 You: ")
        if query.lower() in {"exit", "quit"}:
            print("👋 Chat ended.")
            break
        try:
            response = await rag.aquery(query, param=QueryParam(mode="global"))
            print(f"🤖 LLM: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")


def main():

    rag = asyncio.run(initialize_rag())

    if is_folder_missing_or_empty(WORKING_DIR):
        flows = asyncio.run(csv_to_json_list("email2a_vpn.csv"))
        asyncio.run(build_kg_email2a(flows, rag))

    # Initialize RAG instance
    print("Custom knowledge graph inserted successfully.")
    print("Entities, relationships, and chunks have been added to the knowledge graph.")

    # Example query
    # query = "What does this kg graph represent ?"
    # response = rag.query(query, param=QueryParam(mode="global"))
    # print(f"Query: {query}")
    # print(f"Response: {response}")

    # Start interactive chat
    asyncio.run(interactive_chat(rag))


if __name__ == "__main__":
    main()
