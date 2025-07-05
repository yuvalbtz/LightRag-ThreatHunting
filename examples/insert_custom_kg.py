import asyncio
import csv
import os
from examples.build_kg_helpers import (
    SCAPY_AVAILABLE,
    _parse_csv_file,
    _parse_pcap_file,
    analyze_flow_behavior,
    generate_entity_id,
    get_entity_description,
    get_entity_type,
    get_threat_level,
)
from lightrag import LightRAG
from lightrag.base import QueryParam
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.llm.ollama import ollama_embed, ollama_model_complete
from lightrag.utils import EmbeddingFunc
import uuid
from typing import List, Dict, Any
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


async def pcap_to_json_list(
    file_path: str, max_rows: int = None
) -> List[Dict[str, Any]]:
    """
    Asynchronously converts a PCAP file (binary .pcap or CSV format) to a list of cleaned dictionaries.

    Supports:
    - Binary .pcap files (using scapy)
    - CSV files exported from Wireshark/tshark

    Expected CSV format:
    "No.","Time","Source","Destination","Protocol","Length","Info"

    :param file_path: Path to the PCAP file (.pcap or .csv).
    :param max_rows: Maximum number of rows to process (optional).
    :return: A list of dictionaries with cleaned PCAP packet data.
    """
    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext == ".pcap" or file_ext == ".pcapng":
        if not SCAPY_AVAILABLE:
            raise Exception(
                "scapy is required to read .pcap files. Install with: pip install scapy"
            )
        return await _parse_pcap_file(file_path, max_rows)
    elif file_ext == ".csv":
        return await _parse_csv_file(file_path, max_rows)
    else:
        raise ValueError(
            f"Unsupported file format: {file_ext}. Use .pcap, .pcapng, or .csv files"
        )


def is_folder_missing_or_empty(folder_path: str) -> bool:
    return not os.path.exists(folder_path) or not os.listdir(folder_path)


async def build_kg(
    flows: List[Dict[str, Any]],
    rag,  # LightRAG instance
    source_column: str = "Source IP",
    target_column: str = "Destination IP",
    relationship_columns: List[str] = None,
) -> None:
    """
    Build and insert a knowledge graph into LightRAG based on comprehensive network flow data.
    Enhanced for better LLM retrieval with detailed flow characteristics and threat analysis.
    """
    if not flows:
        raise ValueError("No flow data provided")

    entity_map = {}  # Maps unique endpoint IDs to entity dicts
    relationships = []  # List of relationship entries
    chunks = []  # List of narrative chunks

    # Define the expected columns based on the provided schema
    expected_columns = [
        "Flow ID",
        "Source IP",
        "Source Port",
        "Destination IP",
        "Destination Port",
        "Protocol",
        "Timestamp",
        "Flow Duration",
        "Total Fwd Packets",
        "Total Backward Packets",
        "Total Length of Fwd Packets",
        "Total Length of Bwd Packets",
        "Fwd Packet Length Max",
        "Fwd Packet Length Min",
        "Fwd Packet Length Mean",
        "Fwd Packet Length Std",
        "Bwd Packet Length Max",
        "Bwd Packet Length Min",
        "Bwd Packet Length Mean",
        "Bwd Packet Length Std",
        "Flow Bytes/s",
        "Flow Packets/s",
        "Flow IAT Mean",
        "Flow IAT Std",
        "Flow IAT Max",
        "Flow IAT Min",
        "Fwd IAT Total",
        "Fwd IAT Mean",
        "Fwd IAT Std",
        "Fwd IAT Max",
        "Fwd IAT Min",
        "Bwd IAT Total",
        "Bwd IAT Mean",
        "Bwd IAT Std",
        "Bwd IAT Max",
        "Bwd IAT Min",
        "Fwd PSH Flags",
        "Bwd PSH Flags",
        "Fwd URG Flags",
        "Bwd URG Flags",
        "Fwd Header Length",
        "Bwd Header Length",
        "Fwd Packets/s",
        "Bwd Packets/s",
        "Min Packet Length",
        "Max Packet Length",
        "Packet Length Mean",
        "Packet Length Std",
        "Packet Length Variance",
        "FIN Flag Count",
        "SYN Flag Count",
        "RST Flag Count",
        "PSH Flag Count",
        "ACK Flag Count",
        "URG Flag Count",
        "CWE Flag Count",
        "ECE Flag Count",
        "Down/Up Ratio",
        "Average Packet Size",
        "Avg Fwd Segment Size",
        "Avg Bwd Segment Size",
        "Fwd Avg Bytes/Bulk",
        "Fwd Avg Packets/Bulk",
        "Fwd Avg Bulk Rate",
        "Bwd Avg Bytes/Bulk",
        "Bwd Avg Packets/Bulk",
        "Bwd Avg Bulk Rate",
        "Subflow Fwd Packets",
        "Subflow Fwd Bytes",
        "Subflow Bwd Packets",
        "Subflow Bwd Bytes",
        "Init_Win_bytes_forward",
        "Init_Win_bytes_backward",
        "act_data_pkt_fwd",
        "min_seg_size_forward",
        "Active Mean",
        "Active Std",
        "Active Max",
        "Active Min",
        "Idle Mean",
        "Idle Std",
        "Idle Max",
        "Idle Min",
        "Label",
    ]

    # Auto-detect relationship columns (all columns except basic flow info)
    if relationship_columns is None:
        relationship_columns = [
            col
            for col in expected_columns
            if col
            not in [
                source_column,
                target_column,
                "Source Port",
                "Destination Port",
                "Protocol",
                "Flow ID",
                "Timestamp",
            ]
        ]

    # Enhanced overview chunk with comprehensive flow analysis
    chunks.append(
        {
            "content": (
                "COMPREHENSIVE NETWORK FLOW ANALYSIS KNOWLEDGE GRAPH\n\n"
                "This knowledge graph contains detailed network flow characteristics for advanced threat analysis:\n"
                "- ENTITIES: Network endpoints (IP:Port/Protocol) with behavioral classifications\n"
                "- RELATIONSHIPS: Detailed flow characteristics including packet statistics, timing, and behavioral patterns\n"
                "- BEHAVIORAL ANALYSIS: Packet size distributions, inter-arrival times, flag patterns, and bulk transfer characteristics\n"
                "- THREAT INDICATORS: Anomalous patterns, suspicious timing, unusual packet distributions\n"
                "- PERFORMANCE METRICS: Flow rates, window sizes, segment sizes, and connection efficiency\n\n"
                "QUERY EXAMPLES:\n"
                "- 'Show flows with unusual packet size distributions'\n"
                "- 'Find connections with high SYN flag counts (potential port scanning)'\n"
                "- 'Identify flows with abnormal inter-arrival times'\n"
                "- 'List high-volume data transfers with bulk characteristics'\n"
                "- 'Show flows with unusual flag patterns'\n"
                "- 'Find connections with suspicious timing patterns'\n"
                "- 'Identify potential DDoS attacks based on flow characteristics'\n"
                "- 'Show flows with unusual window size patterns'\n"
            ),
            "source_id": "overview",
            "source_chunk_index": 0,
        }
    )

    # First pass: collect entity statistics and behavior patterns
    entity_stats = {}
    entity_behaviors = {}
    traffic_patterns = {}

    try:
        for flow in flows:
            src_ip = str(flow.get(source_column, "0.0.0.0"))
            src_port = str(flow.get("Source Port", "0"))
            dst_ip = str(flow.get(target_column, "0.0.0.0"))
            dst_port = str(flow.get("Destination Port", "0"))
            protocol = str(flow.get("Protocol", "0"))

            src_entity = generate_entity_id(src_ip, src_port, protocol)
            dst_entity = generate_entity_id(dst_ip, dst_port, protocol)

            entity_stats[src_entity] = entity_stats.get(src_entity, 0) + 1
            entity_stats[dst_entity] = entity_stats.get(dst_entity, 0) + 1

            # Analyze flow behavior
            behavior = analyze_flow_behavior(flow)

            if src_entity not in entity_behaviors:
                entity_behaviors[src_entity] = []
            if dst_entity not in entity_behaviors:
                entity_behaviors[dst_entity] = []

            entity_behaviors[src_entity].append(behavior)
            entity_behaviors[dst_entity].append(behavior)

            # Track traffic patterns
            pattern_key = f"{protocol}:{dst_port}"
            if pattern_key not in traffic_patterns:
                traffic_patterns[pattern_key] = {
                    "count": 0,
                    "sources": set(),
                    "destinations": set(),
                    "total_fwd_packets": 0,
                    "total_bwd_packets": 0,
                    "total_fwd_bytes": 0,
                    "total_bwd_bytes": 0,
                    "anomaly_scores": [],
                }
            traffic_patterns[pattern_key]["count"] += 1
            traffic_patterns[pattern_key]["sources"].add(src_ip)
            traffic_patterns[pattern_key]["destinations"].add(dst_ip)
            traffic_patterns[pattern_key]["total_fwd_packets"] += int(
                flow.get("Total Fwd Packets", 0) or 0
            )
            traffic_patterns[pattern_key]["total_bwd_packets"] += int(
                flow.get("Total Backward Packets", 0) or 0
            )
            traffic_patterns[pattern_key]["total_fwd_bytes"] += int(
                flow.get("Total Length of Fwd Packets", 0) or 0
            )
            traffic_patterns[pattern_key]["total_bwd_bytes"] += int(
                flow.get("Total Length of Bwd Packets", 0) or 0
            )
            traffic_patterns[pattern_key]["anomaly_scores"].append(
                behavior["anomaly_score"]
            )

        # Second pass: create enhanced entities
        for flow in flows:
            flow_id = str(flow.get("Flow ID", str(uuid.uuid4())))
            source_id = f"flow-{flow_id}"

            src_ip = str(flow.get(source_column, "0.0.0.0"))
            src_port = str(flow.get("Source Port", "0"))
            dst_ip = str(flow.get(target_column, "0.0.0.0"))
            dst_port = str(flow.get("Destination Port", "0"))
            protocol = str(flow.get("Protocol", "0"))

            src_entity = generate_entity_id(src_ip, src_port, protocol)
            dst_entity = generate_entity_id(dst_ip, dst_port, protocol)

            # Create enhanced entities with behavioral context
            for endpoint, (ip, port, proto) in [
                (src_entity, (src_ip, src_port, protocol)),
                (dst_entity, (dst_ip, dst_port, protocol)),
            ]:
                if endpoint not in entity_map:
                    flow_count = entity_stats.get(endpoint, 1)
                    behaviors = entity_behaviors.get(endpoint, [])
                    avg_behavior = "normal"
                    avg_anomaly = 0
                    if behaviors:
                        avg_anomaly = sum(b["anomaly_score"] for b in behaviors) / len(
                            behaviors
                        )
                        if avg_anomaly >= 3:
                            avg_behavior = "suspicious"
                        elif avg_anomaly >= 1:
                            avg_behavior = "anomalous"

                    entity_map[endpoint] = {
                        "entity_name": endpoint,
                        "entity_type": get_entity_type(ip, port, proto),
                        "description": get_entity_description(
                            ip, port, proto, flow_count, avg_behavior
                        ),
                        "source_id": source_id,
                        "metadata": {
                            "ip": ip,
                            "port": port,
                            "protocol": proto,
                            "flow_count": flow_count,
                            "avg_behavior": avg_behavior,
                            "avg_anomaly_score": avg_anomaly,
                        },
                    }

            # Analyze current flow behavior
            behavior = analyze_flow_behavior(flow)
            threat_level = get_threat_level(flow, behavior)

            # Enhanced relationship with comprehensive flow characteristics
            flow_characteristics = []

            # Packet statistics
            total_fwd_packets = int(flow.get("Total Fwd Packets", 0) or 0)
            total_bwd_packets = int(flow.get("Total Backward Packets", 0) or 0)
            total_fwd_bytes = int(flow.get("Total Length of Fwd Packets", 0) or 0)
            total_bwd_bytes = int(flow.get("Total Length of Bwd Packets", 0) or 0)

            flow_characteristics.extend(
                [
                    f"Forward packets: {total_fwd_packets}",
                    f"Backward packets: {total_bwd_packets}",
                    f"Forward bytes: {total_fwd_bytes}",
                    f"Backward bytes: {total_bwd_bytes}",
                ]
            )

            # Timing characteristics
            flow_duration = int(flow.get("Flow Duration", 0) or 0)
            flow_bytes_per_sec = float(flow.get("Flow Bytes/s", 0) or 0)
            flow_packets_per_sec = float(flow.get("Flow Packets/s", 0) or 0)

            if flow_duration > 0:
                flow_characteristics.extend(
                    [
                        f"Duration: {flow_duration}ms",
                        f"Bytes/sec: {flow_bytes_per_sec:.2f}",
                        f"Packets/sec: {flow_packets_per_sec:.2f}",
                    ]
                )

            # Flag patterns
            syn_count = int(flow.get("SYN Flag Count", 0) or 0)
            fin_count = int(flow.get("FIN Flag Count", 0) or 0)
            rst_count = int(flow.get("RST Flag Count", 0) or 0)
            psh_count = int(flow.get("PSH Flag Count", 0) or 0)
            ack_count = int(flow.get("ACK Flag Count", 0) or 0)

            flow_characteristics.extend(
                [
                    f"SYN: {syn_count}, FIN: {fin_count}, RST: {rst_count}, PSH: {psh_count}, ACK: {ack_count}"
                ]
            )

            # Behavioral indicators
            if behavior["suspicious_patterns"]:
                flow_characteristics.append(
                    f"Suspicious patterns: {', '.join(behavior['suspicious_patterns'])}"
                )

            if behavior["threat_indicators"]:
                flow_characteristics.append(
                    f"Threat indicators: {', '.join(behavior['threat_indicators'])}"
                )

            relationship_text = "\n".join(flow_characteristics)

            # Create comprehensive relationship description
            src_type = get_entity_type(src_ip, src_port, protocol)
            dst_type = get_entity_type(dst_ip, dst_port, protocol)

            relationship_desc = (
                f"COMPREHENSIVE FLOW ANALYSIS\n"
                f"Source: {src_type} ({src_entity})\n"
                f"Destination: {dst_type} ({dst_entity})\n"
                f"Protocol: {protocol}\n"
                f"Ports: {src_port} → {dst_port}\n"
                f"Flow Characteristics:\n{relationship_text}"
            )

            # Enhanced keywords for comprehensive search
            keywords = []
            keywords.extend([protocol.lower(), src_port, dst_port, src_ip, dst_ip])
            keywords.extend([src_type.lower(), dst_type.lower()])
            keywords.extend([behavior["behavior_type"], threat_level.lower()])
            keywords.extend(behavior["suspicious_patterns"])
            keywords.extend(behavior["threat_indicators"])

            # Add flow-specific keywords
            if total_fwd_packets > 100:
                keywords.extend(["high_packet_count", "bulk_transfer"])
            if syn_count > 5:
                keywords.extend(["port_scanning", "syn_flood"])
            if flow_bytes_per_sec > 1000000:
                keywords.extend(["high_bandwidth", "data_exfiltration"])

            relationships.append(
                {
                    "src_id": src_entity,
                    "tgt_id": dst_entity,
                    "description": relationship_desc,
                    "keywords": ", ".join(filter(None, keywords)),
                    "weight": 1.0,
                    "source_id": source_id,
                    "metadata": {
                        "protocol": protocol,
                        "src_port": src_port,
                        "dst_port": dst_port,
                        "flow_id": flow_id,
                        "behavior_type": behavior["behavior_type"],
                        "threat_level": threat_level,
                        "anomaly_score": behavior["anomaly_score"],
                        "total_fwd_packets": total_fwd_packets,
                        "total_bwd_packets": total_bwd_packets,
                        "total_fwd_bytes": total_fwd_bytes,
                        "total_bwd_bytes": total_bwd_bytes,
                        "flow_duration": flow_duration,
                        "src_type": src_type,
                        "dst_type": dst_type,
                    },
                }
            )

            # Enhanced chunk with comprehensive analysis
            chunk_content = (
                f"COMPREHENSIVE NETWORK FLOW ANALYSIS\n"
                f"Flow ID: {flow_id}\n"
                f"Source: {src_type} ({src_entity})\n"
                f"Destination: {dst_type} ({dst_entity})\n"
                f"Protocol: {protocol}\n"
                f"Ports: {src_port} → {dst_port}\n"
                f"Duration: {flow_duration}ms\n"
                f"Data Transfer: {total_fwd_bytes + total_bwd_bytes} bytes ({total_fwd_packets + total_bwd_packets} packets)\n"
                f"Flow Rate: {flow_bytes_per_sec:.2f} bytes/sec, {flow_packets_per_sec:.2f} packets/sec\n"
                f"Flag Pattern: SYN:{syn_count} FIN:{fin_count} RST:{rst_count} PSH:{psh_count} ACK:{ack_count}\n"
                f"Behavior: {behavior['behavior_type']}"
            )

            chunks.append(
                {
                    "content": chunk_content,
                    "source_id": source_id,
                    "source_chunk_index": len(chunks),
                }
            )

        # Add entity-specific chunks with behavioral analysis
        for entity_id, entity in entity_map.items():
            behaviors = entity_behaviors.get(entity_id, [])
            avg_anomaly = entity["metadata"].get("avg_anomaly_score", 0)
            avg_behavior = entity["metadata"]["avg_behavior"]

            entity_chunk = (
                f"ENTITY BEHAVIORAL ANALYSIS: {entity['entity_name']}\n"
                f"Type: {entity['entity_type']}\n"
                f"Average Behavior: {avg_behavior}\n"
                f"Average Anomaly Score: {avg_anomaly:.2f}\n"
                f"Description: {entity['description']}\n"
                f"IP Address: {entity['metadata']['ip']}\n"
                f"Port: {entity['metadata']['port']}\n"
                f"Protocol: {entity['metadata']['protocol']}\n"
                f"Flow Count: {entity['metadata']['flow_count']}\n"
                f"Behavioral Notes: {avg_behavior} endpoint with {entity['metadata']['flow_count']} observed flows"
            )

            chunks.append(
                {
                    "content": entity_chunk,
                    "source_id": entity[
                        "source_id"
                    ],  # Reference the entity's source_id
                    "source_chunk_index": 0,
                }
            )

        # Add traffic pattern analysis chunks
        for pattern_key, pattern_data in traffic_patterns.items():
            protocol, port = pattern_key.split(":", 1)
            entity_type = get_entity_type("0.0.0.0", port, protocol)
            avg_anomaly = (
                sum(pattern_data["anomaly_scores"])
                / len(pattern_data["anomaly_scores"])
                if pattern_data["anomaly_scores"]
                else 0
            )

            # Find relationships that match this pattern
            pattern_relationships = [
                r
                for r in relationships
                if r["metadata"]["protocol"] == protocol
                and r["metadata"]["dst_port"] == port
            ]

            # Use the first relationship's source_id, or create a pattern-specific one
            pattern_source_id = (
                pattern_relationships[0]["source_id"]
                if pattern_relationships
                else f"pattern-{pattern_key}"
            )

            pattern_chunk = (
                f"NETWORK TRAFFIC PATTERN ANALYSIS\n"
                f"Pattern: {protocol.upper()} traffic to port {port}\n"
                f"Service Type: {entity_type}\n"
                f"Network Activity: {pattern_data['count']} total flows\n"
                f"Source Diversity: {len(pattern_data['sources'])} unique sources\n"
                f"Destination Diversity: {len(pattern_data['destinations'])} unique destinations\n"
                f"Traffic Volume: {pattern_data['total_fwd_packets']} forward packets, {pattern_data['total_bwd_packets']} backward packets\n"
                f"Data Transfer: {pattern_data['total_fwd_bytes']} forward bytes, {pattern_data['total_bwd_bytes']} backward bytes\n"
                f"Network Behavior Score: {avg_anomaly:.2f}\n"
                f"Average Forward Packets per Flow: {pattern_data['total_fwd_packets'] // pattern_data['count'] if pattern_data['count'] > 0 else 0}\n"
                f"Average Backward Packets per Flow: {pattern_data['total_bwd_packets'] // pattern_data['count'] if pattern_data['count'] > 0 else 0}\n"
                f"Network Characteristics: This pattern represents typical {protocol.upper()} network behavior with {pattern_data['count']} flows across {len(pattern_data['sources'])} sources"
            )

            chunks.append(
                {
                    "content": pattern_chunk,
                    "source_id": pattern_source_id,  # Reference the relationship's source_id
                    "source_chunk_index": 0,
                }
            )

        # Calculate pattern statistics
        total_pattern_flows = sum(
            pattern_data["count"] for pattern_data in traffic_patterns.values()
        )
        avg_pattern_anomaly = (
            sum(
                sum(pattern_data["anomaly_scores"])
                / len(pattern_data["anomaly_scores"])
                for pattern_data in traffic_patterns.values()
                if pattern_data["anomaly_scores"]
            )
            / len(traffic_patterns)
            if traffic_patterns
            else 0
        )

        # Get top patterns by flow count
        top_patterns = sorted(
            traffic_patterns.items(), key=lambda x: x[1]["count"], reverse=True
        )[:5]

        pattern_summary = (
            f"NETWORK TRAFFIC PATTERN ANALYSIS SUMMARY\n"
            f"Total Network Entities: {len(entity_map)}\n"
            f"Total Network Flows: {len(flows)}\n"
            f"Unique Traffic Patterns: {len(traffic_patterns)}\n"
            f"Total Pattern Flows: {total_pattern_flows}\n"
            f"Average Pattern Anomaly Score: {avg_pattern_anomaly:.2f}\n"
            f"Unique Protocols Observed: {len(set(r['metadata']['protocol'] for r in relationships))}\n\n"
            f"TOP TRAFFIC PATTERNS:\n"
        )

        for i, (pattern_key, pattern_data) in enumerate(top_patterns, 1):
            protocol, port = pattern_key.split(":", 1)
            pattern_summary += (
                f"{i}. {protocol.upper()} traffic to port {port}: "
                f"{pattern_data['count']} flows, "
                f"{len(pattern_data['sources'])} sources, "
                f"{len(pattern_data['destinations'])} destinations\n"
            )

        pattern_summary += (
            f"\nPATTERN ANALYSIS INSIGHTS:\n"
            f"- Most common protocol: {max(set(r['metadata']['protocol'] for r in relationships), key=lambda x: len([r for r in relationships if r['metadata']['protocol'] == x]))}\n"
            f"- Average flows per pattern: {total_pattern_flows // len(traffic_patterns) if traffic_patterns else 0}\n"
            f"- Pattern diversity: {len(traffic_patterns)} unique patterns across {len(flows)} total flows\n"
            f"- Network behavior analysis: {len(entity_map)} entities with varying traffic patterns\n"
            f"- Flow characteristics: Detailed packet and byte statistics available for each pattern"
        )

        # Find a representative relationship source_id for the summary
        summary_source_id = (
            relationships[0]["source_id"] if relationships else "pattern-summary"
        )

        chunks.append(
            {
                "content": pattern_summary,
                "source_id": summary_source_id,  # Reference a relationship's source_id
                "source_chunk_index": 0,
            }
        )

    except Exception as e:
        print(f"Error during knowledge graph construction: {e}")
        raise

    # Final KG structure
    custom_kg = {
        "entities": list(entity_map.values()),
        "relationships": relationships,
        "chunks": chunks,
    }

    try:
        await rag.ainsert_custom_kg(custom_kg=custom_kg, file_path=rag.working_dir)
        print(
            f"✅ Network Pattern Knowledge Graph inserted: {len(entity_map)} entities, {len(relationships)} relationships, {len(chunks)} chunks."
        )
        print(f"📊 Entity types: {set(e['entity_type'] for e in entity_map.values())}")
        print(f"🔗 Protocols: {set(r['metadata']['protocol'] for r in relationships)}")
        print(
            f"🎭 Behavior types: {set(r['metadata']['behavior_type'] for r in relationships)}"
        )
        print(f"📈 Traffic patterns: {len(traffic_patterns)} unique patterns")
        print(f"🌐 Network entities: {len(entity_map)} total entities")
        print(f"📊 Pattern diversity: {len(traffic_patterns)} unique traffic patterns")

        # Debug: Show source_id relationships
        unique_source_ids = set()
        for entity in entity_map.values():
            unique_source_ids.add(entity["source_id"])
        for relationship in relationships:
            unique_source_ids.add(relationship["source_id"])
        print(
            f"🔗 Unique source IDs: {len(unique_source_ids)} (entities and relationships)"
        )
        print(f"📄 Chunks created: {len(chunks)} with proper source_id references")

        # Validate source_id references
        entity_source_ids = {entity["source_id"] for entity in entity_map.values()}
        relationship_source_ids = {rel["source_id"] for rel in relationships}
        chunk_source_ids = {chunk["source_id"] for chunk in chunks}

        # Check if chunk source_ids reference valid entity/relationship source_ids
        valid_source_ids = entity_source_ids.union(relationship_source_ids)
        invalid_chunk_sources = chunk_source_ids - valid_source_ids

        if invalid_chunk_sources:
            print(
                f"⚠️  Warning: {len(invalid_chunk_sources)} chunks have source_ids not found in entities/relationships"
            )
            print(f"   Invalid source_ids: {invalid_chunk_sources}")
        else:
            print(
                f"✅ All chunks have valid source_id references to entities/relationships"
            )

    except Exception as e:
        print(f"❌ Failed to insert knowledge graph: {e}")
        raise


WORKING_DIR = "./email2a_vpn_kg"

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)

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
        # Use PCAP data (supports both .pcap and .csv files)
        flows = asyncio.run(pcap_to_json_list("your_pcap_file.pcap"))
        asyncio.run(
            build_kg(
                flows=flows,
                rag=rag,
                source_column="Source IP",
                target_column="Destination IP",
                relationship_columns=[
                    "Protocol",
                    "Length",
                    "Time",
                    "Timestamp",
                    "Flow Duration",
                    "Total Fwd Packets",
                    "Total Backward Packets",
                    "Total Length of Fwd Packets",
                    "Total Length of Bwd Packets",
                    "Fwd Packet Length Max",
                    "Fwd Packet Length Min",
                    "Fwd Packet Length Mean",
                    "Fwd Packet Length Std",
                    "Bwd Packet Length Max",
                    "Bwd Packet Length Min",
                    "Bwd Packet Length Mean",
                    "Bwd Packet Length Std",
                    "Flow Bytes/s",
                    "Flow Packets/s",
                    "Flow IAT Mean",
                    "Flow IAT Std",
                    "Flow IAT Max",
                    "Flow IAT Min",
                    "Fwd IAT Total",
                    "Fwd IAT Mean",
                    "Fwd IAT Std",
                    "Fwd IAT Max",
                    "Fwd IAT Min",
                    "Bwd IAT Total",
                    "Bwd IAT Mean",
                    "Bwd IAT Std",
                    "Bwd IAT Max",
                    "Bwd IAT Min",
                    "Fwd PSH Flags",
                    "Bwd PSH Flags",
                    "Fwd URG Flags",
                    "Bwd URG Flags",
                    "Fwd Header Length",
                    "Bwd Header Length",
                    "Fwd Packets/s",
                    "Bwd Packets/s",
                    "Min Packet Length",
                    "Max Packet Length",
                    "Packet Length Mean",
                    "Packet Length Std",
                    "Packet Length Variance",
                    "FIN Flag Count",
                    "SYN Flag Count",
                    "RST Flag Count",
                    "PSH Flag Count",
                    "ACK Flag Count",
                    "URG Flag Count",
                    "CWE Flag Count",
                    "ECE Flag Count",
                    "Down/Up Ratio",
                    "Average Packet Size",
                    "Avg Fwd Segment Size",
                    "Avg Bwd Segment Size",
                    "Fwd Avg Bytes/Bulk",
                    "Fwd Avg Packets/Bulk",
                    "Fwd Avg Bulk Rate",
                    "Bwd Avg Bytes/Bulk",
                    "Bwd Avg Packets/Bulk",
                    "Bwd Avg Bulk Rate",
                    "Subflow Fwd Packets",
                    "Subflow Fwd Bytes",
                    "Subflow Bwd Packets",
                    "Subflow Bwd Bytes",
                    "Init_Win_bytes_forward",
                    "Init_Win_bytes_backward",
                    "act_data_pkt_fwd",
                    "min_seg_size_forward",
                    "Active Mean",
                    "Active Std",
                    "Active Max",
                    "Active Min",
                    "Idle Mean",
                    "Idle Std",
                    "Idle Max",
                    "Idle Min",
                    "Label",
                    "Query Type",
                    "Query ID",
                    "Domain",
                    "Response IP",
                    "TCP Flags",
                ],
            )
        )

    print("PCAP-based knowledge graph inserted successfully.")
    print("Entities, relationships, and chunks have been added to the knowledge graph.")

    # Start interactive chat
    asyncio.run(interactive_chat(rag))


if __name__ == "__main__":
    main()
