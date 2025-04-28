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
import pandas as pd
import json

def is_folder_missing_or_empty(folder_path: str) -> bool:
    return not os.path.exists(folder_path) or not os.listdir(folder_path)

async def csv_to_json_list(file_path: str) -> List[Dict[str, Any]]:
    loop = asyncio.get_running_loop()
    with open(file_path, mode='r', encoding='utf-8') as csv_file:
        reader = await loop.run_in_executor(None, lambda: list(csv.DictReader(csv_file)))
    json_data = [{str(k): str(v) for k, v in row.items()} for row in reader]
    return json_data

async def convert_to_custom_kg(flows: List[Dict[str, Any]], rag: LightRAG) -> Dict[str, Any]:
    custom_kg = {"entities": [], "relationships": []}
    existing_entities = set()
    existing_relationships = set()

    for i, flow in enumerate(flows):
        entity_id = f"Flow-{i}"

        if entity_id not in existing_entities:
            rag.create_entity(entity_id, {
                "entity_type": "Flow Entity",
                "description": f"Network flow number {i}",
                "source_id": entity_id
            })
            custom_kg["entities"].append({
                "entity_name": entity_id,
                "entity_type": "Flow Entity",
                "description": f"Network flow number {i}",
                "source_id": entity_id
            })
            existing_entities.add(entity_id)

        for key, value in flow.items():
            relation_target = f"{key}: {value}"
            relation_id = (entity_id, relation_target)

            description = f"{key} = {value}"
            tags = []

            # Semantic Enrichment
            try:
                numeric_value = float(value)
            except:
                numeric_value = None

            if key == "Fwd Pkt Len Mean" and numeric_value == 0:
                description = "Zero-length forward packets (possible scan or error)"
                tags = ["anomaly", "zero_packet"]
            elif key == "Pkt Len Std" and numeric_value is not None and numeric_value > 300:
                description = "High packet length standard deviation (possible tunneling)"
                tags = ["anomaly", "tunneling"]
            elif key == "Flow Duration" and numeric_value is not None and numeric_value > 1000000:
                description = "Long flow duration (possible beaconing behavior)"
                tags = ["anomaly", "long_duration"]
            elif key == "Protocol" and value == "17":
                description = "UDP protocol flow (could indicate special tunneling)"
                tags = ["udp", "protocol_check"]

            if relation_target not in existing_entities:
                rag.create_entity(relation_target, {
                    "entity_type": "FeatureValue",
                    "description": description,
                    "tags": tags,
                    "source_id": entity_id
                })
                custom_kg["entities"].append({
                    "entity_name": relation_target,
                    "entity_type": "FeatureValue",
                    "description": description,
                    "tags": tags,
                    "source_id": entity_id
                })
                existing_entities.add(relation_target)

            if relation_id not in existing_relationships:
                rag.create_relation(entity_id, relation_target, {
                    "description": description,
                    "keywords": ", ".join(tags) if tags else "flow, feature",
                    "weight": 1.0,
                    "source_id": entity_id
                })
                custom_kg["relationships"].append({
                    "src_id": entity_id,
                    "tgt_id": relation_target,
                    "description": description,
                    "keywords": ", ".join(tags) if tags else "flow, feature",
                    "weight": 1.0,
                    "source_id": entity_id
                })
                existing_relationships.add(relation_id)

    return custom_kg

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
            "options": {"num_ctx": 3200},
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
    rag = asyncio.run(initialize_rag())

    if is_folder_missing_or_empty(WORKING_DIR):
        flows = asyncio.run(csv_to_json_list('VPN_First10.csv'))
        asyncio.run(convert_to_custom_kg(flows, rag))
        printTextColor(Colors.SUCCESS, "✅ Custom KG created successfully.")

    print("\n📊 Global Graph Search Results:\n")

    # Run 2-3 smart queries
    print(rag.query(
        "List all flows connected to feature Fwd Pkt Len Mean: 0",
        param=QueryParam(mode="global")
    ))

    print(rag.query(
        "List all flows where Flow Duration is greater than 1,000,000 microseconds",
        param=QueryParam(mode="global")
    ))

    print(rag.query(
        "Find flows with Pkt Len Std greater than 300",
        param=QueryParam(mode="global")
    ))

if __name__ == "__main__":
    main()
