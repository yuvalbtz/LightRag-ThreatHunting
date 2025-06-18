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
import re
from agent import initialize_rag_deepseek

#########
# Uncomment the below two lines if running in a jupyter notebook to handle the async nature of rag.insert()
# import nest_asyncio
# nest_asyncio.apply()
#########


async def csv_to_json_list(
    file_path: str, max_rows: int = None
) -> List[Dict[str, Any]]:
    """
    Asynchronously converts a CSV file to a list of cleaned dictionaries.

    :param file_path: Path to the CSV file.
    :return: A list of dictionaries with stripped and cleaned key-value pairs.
    """
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if max_rows:
            rows = list(reader)[:max_rows]
        else:
            rows = list(reader)

    def clean(s: str) -> str:
        return s.strip().replace('"', "").replace("'", "")

    json_data = [{clean(k): clean(v) for k, v in row.items()} for row in rows]

    return json_data


def is_folder_missing_or_empty(folder_path: str) -> bool:
    return not os.path.exists(folder_path) or not os.listdir(folder_path)


async def determine_entity_type(
    value: str, available_columns: List[str], flow: Dict[str, Any]
) -> str:
    """
    Automatically determine the entity type based on the value and available data.

    Args:
        value: The entity value to analyze
        available_columns: List of available columns in the data
        flow: The current flow record containing the entity

    Returns:
        str: The determined entity type
    """
    # Check if it's an IP address
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", value):
        return "IP Address"

    # Check if it's a port number
    if value.isdigit() and 0 <= int(value) <= 65535:
        return "Port"

    # Check if it's a protocol
    if "Protocol" in flow and value == flow["Protocol"]:
        return "Protocol"

    # Check if it's a service
    if "Service" in flow and value == flow["Service"]:
        return "Service"

    # Check if it's a hostname
    if re.match(r"^[a-zA-Z0-9][a-zA-Z0-9-]*(\.[a-zA-Z0-9][a-zA-Z0-9-]*)*$", value):
        return "Hostname"

    # Check if it's a traffic class
    if "class" in value.lower() or "type" in value.lower():
        return "Traffic Class"

    # Default to Network Entity if no specific type is determined
    return "Network Entity"


async def build_kg(
    flows: List[Dict[str, Any]],
    rag: LightRAG,
    source_column: str = "Source",
    target_column: str = "Destination",
    relationship_columns: List[str] = None,
) -> None:
    """
    Build and insert a custom knowledge graph into LightRAG from flow records.
    Automatically extracts entities and their types from the data.

    Args:
        flows: List of flow dictionaries parsed from CSV/PCAP
        rag: LightRAG instance
        source_column: Column name for source entity
        target_column: Column name for target entity
        relationship_columns: List of column names to include in relationships
    """
    entity_map = {}
    relationships = []
    chunks = []

    if not flows:
        raise ValueError("No data provided")

    # Get all available columns from the first record
    available_columns = list(flows[0].keys())

    # If relationship_columns not specified, use all columns except source and target
    if relationship_columns is None:
        relationship_columns = [
            col
            for col in available_columns
            if col not in [source_column, target_column]
        ]

    # Overview chunk
    chunks.append(
        {
            "content": (
                "This knowledge graph visualizes network traffic flow characteristics. "
                "Each entity represents a network endpoint or component, and relationships capture "
                "various attributes and metrics from the traffic data."
            ),
            "source_id": "overview",
            "source_chunk_index": 0,
        }
    )

    for index, flow in enumerate(flows):
        session_id = flow.get("Flow ID", "Unknown")
        source_id = session_id

        # Get source and target
        source = flow.get(source_column, "Unknown")
        target = flow.get(target_column, "Unknown")

        def generate_entity_id(ip: str, port: str, protocol: str) -> str:
            return f"{ip}:{port}/{protocol}".lower()

        source = generate_entity_id(
            flow[source_column],
            flow.get("Source Port", "Unknown"),
            flow.get("Protocol", "Unknown"),
        )
        target = generate_entity_id(
            flow[target_column],
            flow.get("Destination Port", "Unknown"),
            flow.get("Protocol", "Unknown"),
        )

        # Create entities if they don't exist
        for endpoint in (source, target):
            if endpoint not in entity_map:
                # Determine entity type automatically
                entity_type = await determine_entity_type(
                    endpoint, available_columns, flow
                )

                # Create entity description based on available data
                entity_desc_parts = [f"{entity_type} involved in network traffic"]
                for col in relationship_columns:
                    if flow.get(col) is not None:
                        entity_desc_parts.append(f"{col}: {flow[col]}")

                entity_attrs = {
                    "entity_name": endpoint,
                    "entity_type": entity_type,
                    "description": "\n".join(entity_desc_parts),
                    "source_id": source_id,
                }

                # Add all available attributes to the entity
                for col in available_columns:
                    if (
                        col not in [source_column, target_column]
                        and flow.get(col) is not None
                    ):
                        entity_attrs[col] = flow[col]

                entity_map[endpoint] = entity_attrs

        # Build relationship description from specified columns
        relationship_desc = []
        for col in relationship_columns:
            if flow.get(col) is not None:
                relationship_desc.append(f"{col}: {flow[col]}")

        # Create relationship
        relationship_attrs = {
            "src_id": source,
            "tgt_id": target,
            "description": "\n".join(relationship_desc),
            "keywords": ", ".join(
                [
                    str(flow.get(col, "")).lower()
                    for col in relationship_columns
                    if flow.get(col)
                ]
            ),
            "weight": 1.0,
            "source_id": source_id,
        }

        # Add all relationship columns as attributes
        for col in relationship_columns:
            if flow.get(col) is not None:
                relationship_attrs[col] = flow[col]

        relationships.append(relationship_attrs)

        # Create chunk with all available information
        chunk_content = []
        if source != "Unknown" and target != "Unknown":
            chunk_content.append(f"Traffic from {source} to {target}")

        for col in relationship_columns:
            if flow.get(col) is not None:
                chunk_content.append(f"{col}: {flow[col]}")

        chunks.append(
            {
                "content": "\n".join(chunk_content),
                "source_id": source_id,
                "source_chunk_index": index + 1,
            }
        )

        # Deduplicate chunks: ensure every entity has a chunk with its source_id
        existing_chunk_ids = {
            (chunk["source_id"], chunk["source_chunk_index"]) for chunk in chunks
        }

        for endpoint, entity in entity_map.items():
            chunk_key = (entity["source_id"], 0)
            if entity["source_id"] != "Unknown" and chunk_key not in existing_chunk_ids:
                chunks.append(
                    {
                        "content": f"{entity['entity_type']} Entity: {endpoint}\n{entity['description']}",
                        "source_id": entity["source_id"],
                        "source_chunk_index": 0,
                    }
                )

    # Create and insert the knowledge graph
    custom_kg = {
        "entities": list(entity_map.values()),
        "relationships": relationships,
        "chunks": chunks,
    }

    try:
        await rag.ainsert_custom_kg(custom_kg=custom_kg, file_path=rag.working_dir)
        print(
            f"Successfully inserted knowledge graph with {len(entity_map)} entities and {len(relationships)} relationships"
        )
        print(f"Used columns: {relationship_columns}")
        print(
            f"Entity types found: {set(entity['entity_type'] for entity in entity_map.values())}"
        )
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
    rag = asyncio.run(initialize_rag_deepseek())

    if is_folder_missing_or_empty(WORKING_DIR):
        flows = asyncio.run(csv_to_json_list("Skype.csv"))
        asyncio.run(
            build_kg(
                flows=flows,
                rag=rag,
                source_column="Src IP",
                target_column="Dst IP",
                relationship_columns=[
                    "Protocol",
                    "Length",
                    "Time",
                    "duration",
                    "total_fiat",
                    "total_biat",
                    "mean_fiat",
                    "mean_biat",
                    "flowPktsPerSecond",
                    "flowBytesPerSecond",
                    "std_idle",
                ],
            )
        )

    print("Custom knowledge graph inserted successfully.")
    print("Entities, relationships, and chunks have been added to the knowledge graph.")

    # Start interactive chat
    asyncio.run(interactive_chat(rag))


if __name__ == "__main__":
    main()
