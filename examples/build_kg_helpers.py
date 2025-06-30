import csv
import os
import re
from typing import Any, Dict, List

# Add scapy import for PCAP file handling
try:
    from scapy.all import rdpcap, IP, TCP, UDP, DNS

    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("Warning: scapy not available. PCAP files will not be supported.")


async def determine_entity_type(value: str, flow: Dict[str, Any]) -> str:
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
    return "Network Endpoint"


def generate_entity_id(ip: str, port: str, proto: str) -> str:
    """Generate a standardized entity ID with protocol context."""
    return f"{ip}:{port}/{proto}".lower()


def get_entity_type(ip: str, port: str, protocol: str) -> str:
    """Determine entity type based on port and protocol with behavioral context."""
    try:
        protocol_lower = str(protocol).lower()
        port_str = str(port)

        # Web services
        if protocol_lower in ["http", "https", "80", "443"] or port_str in [
            "80",
            "443",
            "8080",
            "8443",
        ]:
            return "Web Server"
        # Management services
        elif protocol_lower in ["ssh", "22"] or port_str == "22":
            return "SSH Server"
        elif protocol_lower in ["telnet", "23"] or port_str == "23":
            return "Telnet Server"
        elif protocol_lower in ["rdp", "3389"] or port_str == "3389":
            return "Remote Desktop Server"
        # File transfer
        elif protocol_lower in ["ftp", "21"] or port_str == "21":
            return "FTP Server"
        elif protocol_lower in ["sftp", "22"]:
            return "SFTP Server"
        # Network services
        elif protocol_lower in ["dns", "53"] or port_str == "53":
            return "DNS Server"
        elif protocol_lower in ["dhcp", "67", "68"] or port_str in ["67", "68"]:
            return "DHCP Server"
        # Mail services
        elif protocol_lower in ["smtp", "25", "587"] or port_str in ["25", "587"]:
            return "Mail Server"
        elif protocol_lower in ["pop3", "110", "995"] or port_str in ["110", "995"]:
            return "POP3 Server"
        elif protocol_lower in ["imap", "143", "993"] or port_str in ["143", "993"]:
            return "IMAP Server"
        # Database services
        elif port_str in ["3306", "5432", "1433", "1521"]:
            return "Database Server"
        # Common application ports
        elif port_str in ["22", "23", "3389", "5900"]:
            return "Management Server"
        elif port_str in ["80", "443", "8080", "8443", "3000", "5000"]:
            return "Web Service"
        else:
            return "Network Endpoint"
    except Exception:
        return "Network Endpoint"


def analyze_flow_behavior(flow: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze flow behavior patterns for threat detection."""
    try:
        behavior = {
            "anomaly_score": 0,
            "suspicious_patterns": [],
            "behavior_type": "normal",
            "threat_indicators": [],
        }

        # Analyze packet size patterns
        fwd_packet_mean = float(flow.get("Fwd Packet Length Mean", 0) or 0)
        bwd_packet_mean = float(flow.get("Bwd Packet Length Mean", 0) or 0)
        packet_std = float(flow.get("Packet Length Std", 0) or 0)

        if packet_std > 1000:  # High variance in packet sizes
            behavior["suspicious_patterns"].append("high_packet_size_variance")
            behavior["anomaly_score"] += 2

        # Analyze flag patterns
        syn_count = int(flow.get("SYN Flag Count", 0) or 0)
        fin_count = int(flow.get("FIN Flag Count", 0) or 0)
        rst_count = int(flow.get("RST Flag Count", 0) or 0)
        psh_count = int(flow.get("PSH Flag Count", 0) or 0)

        if syn_count > 10:  # Potential port scanning
            behavior["suspicious_patterns"].append("high_syn_count")
            behavior["threat_indicators"].append("potential_port_scanning")
            behavior["anomaly_score"] += 3

        if rst_count > 5:  # Connection resets
            behavior["suspicious_patterns"].append("high_rst_count")
            behavior["anomaly_score"] += 1

        # Analyze timing patterns
        flow_iat_mean = float(flow.get("Flow IAT Mean", 0) or 0)
        flow_iat_std = float(flow.get("Flow IAT Std", 0) or 0)

        if flow_iat_std > 1000000:  # High timing variance
            behavior["suspicious_patterns"].append("irregular_timing")
            behavior["anomaly_score"] += 2

        # Analyze bulk transfer patterns
        fwd_bulk_rate = float(flow.get("Fwd Avg Bulk Rate", 0) or 0)
        bwd_bulk_rate = float(flow.get("Bwd Avg Bulk Rate", 0) or 0)

        if fwd_bulk_rate > 1000000 or bwd_bulk_rate > 1000000:  # High bulk transfer
            behavior["suspicious_patterns"].append("high_bulk_transfer")
            behavior["anomaly_score"] += 2

        # Determine behavior type
        if behavior["anomaly_score"] >= 5:
            behavior["behavior_type"] = "suspicious"
        elif behavior["anomaly_score"] >= 3:
            behavior["behavior_type"] = "anomalous"
        else:
            behavior["behavior_type"] = "normal"

        return behavior
    except Exception as e:
        print(f"Error in analyze_flow_behavior: {e}")
        return {
            "anomaly_score": 0,
            "suspicious_patterns": [],
            "behavior_type": "normal",
            "threat_indicators": [],
        }


def get_threat_level(flow: Dict[str, Any], behavior: Dict[str, Any]) -> str:
    """Determine threat level based on flow characteristics and behavior."""
    try:
        anomaly_score = behavior["anomaly_score"]
        protocol = str(flow.get("Protocol", "")).lower()
        dst_port = str(flow.get("Destination Port", ""))

        # High-risk services
        if dst_port in ["22", "23", "3389", "5900"] or protocol in [
            "ssh",
            "telnet",
            "rdp",
        ]:
            if anomaly_score >= 3:
                return "HIGH"
            elif anomaly_score >= 1:
                return "MEDIUM"
            else:
                return "LOW"

        # Web services
        elif dst_port in ["80", "443", "8080", "8443"]:
            if anomaly_score >= 4:
                return "HIGH"
            elif anomaly_score >= 2:
                return "MEDIUM"
            else:
                return "LOW"

        # Database services
        elif dst_port in ["3306", "5432", "1433", "1521"]:
            if anomaly_score >= 2:
                return "HIGH"
            elif anomaly_score >= 1:
                return "MEDIUM"
            else:
                return "LOW"

        else:
            if anomaly_score >= 5:
                return "HIGH"
            elif anomaly_score >= 3:
                return "MEDIUM"
            else:
                return "LOW"
    except Exception:
        return "LOW"


def get_entity_description(
    ip: str, port: str, protocol: str, flow_count: int, avg_behavior: str
) -> str:
    """Generate detailed entity description with behavioral context."""
    try:
        entity_type = get_entity_type(ip, port, protocol)

        return (
            f"{entity_type} at {ip}:{port} using {protocol} protocol.\n"
            f"Observed in {flow_count} network flow(s).\n"
            f"Typical behavior: {avg_behavior}.\n"
            f"Service type: {entity_type.lower()}"
        )
    except Exception:
        return f"Network endpoint at {ip}:{port} using {protocol} protocol. Observed in {flow_count} flows."


async def _parse_pcap_file(
    file_path: str, max_rows: int = None
) -> List[Dict[str, Any]]:
    """Parse binary PCAP file using scapy."""
    try:
        # Read PCAP file
        packets = rdpcap(file_path)
        if max_rows:
            packets = packets[:max_rows]

        json_data = []

        for i, packet in enumerate(packets):
            packet_data = {
                "Packet No.": str(i + 1),
                "Time": str(packet.time),
                "Source IP": "0.0.0.0",
                "Source Port": "0",
                "Destination IP": "0.0.0.0",
                "Destination Port": "0",
                "Protocol": "Unknown",
                "Length": str(len(packet)),
                "Info": "",
                "Flow ID": f"pcap-{i+1}",
                "Timestamp": float(packet.time),
                "Flow Duration": 0,
                "Total Fwd Packets": 1,
                "Total Backward Packets": 0,
                "Total Length of Fwd Packets": len(packet),
                "Total Length of Bwd Packets": 0,
                "Fwd Packet Length Max": len(packet),
                "Fwd Packet Length Min": len(packet),
                "Fwd Packet Length Mean": len(packet),
                "Fwd Packet Length Std": 0,
                "Bwd Packet Length Max": 0,
                "Bwd Packet Length Min": 0,
                "Bwd Packet Length Mean": 0,
                "Bwd Packet Length Std": 0,
                "Flow Bytes/s": 0,
                "Flow Packets/s": 0,
                "Flow IAT Mean": 0,
                "Flow IAT Std": 0,
                "Flow IAT Max": 0,
                "Flow IAT Min": 0,
                "Fwd IAT Total": 0,
                "Fwd IAT Mean": 0,
                "Fwd IAT Std": 0,
                "Fwd IAT Max": 0,
                "Fwd IAT Min": 0,
                "Bwd IAT Total": 0,
                "Bwd IAT Mean": 0,
                "Bwd IAT Std": 0,
                "Bwd IAT Max": 0,
                "Bwd IAT Min": 0,
                "Fwd PSH Flags": 0,
                "Bwd PSH Flags": 0,
                "Fwd URG Flags": 0,
                "Bwd URG Flags": 0,
                "Fwd Header Length": 0,
                "Bwd Header Length": 0,
                "Fwd Packets/s": 0,
                "Bwd Packets/s": 0,
                "Min Packet Length": len(packet),
                "Max Packet Length": len(packet),
                "Packet Length Mean": len(packet),
                "Packet Length Std": 0,
                "Packet Length Variance": 0,
                "FIN Flag Count": 0,
                "SYN Flag Count": 0,
                "RST Flag Count": 0,
                "PSH Flag Count": 0,
                "ACK Flag Count": 0,
                "URG Flag Count": 0,
                "CWE Flag Count": 0,
                "ECE Flag Count": 0,
                "Down/Up Ratio": 0,
                "Average Packet Size": len(packet),
                "Avg Fwd Segment Size": 0,
                "Avg Bwd Segment Size": 0,
                "Fwd Avg Bytes/Bulk": 0,
                "Fwd Avg Packets/Bulk": 0,
                "Fwd Avg Bulk Rate": 0,
                "Bwd Avg Bytes/Bulk": 0,
                "Bwd Avg Packets/Bulk": 0,
                "Bwd Avg Bulk Rate": 0,
                "Subflow Fwd Packets": 0,
                "Subflow Fwd Bytes": 0,
                "Subflow Bwd Packets": 0,
                "Subflow Bwd Bytes": 0,
                "Init_Win_bytes_forward": 0,
                "Init_Win_bytes_backward": 0,
                "act_data_pkt_fwd": 0,
                "min_seg_size_forward": 0,
                "Active Mean": 0,
                "Active Std": 0,
                "Active Max": 0,
                "Active Min": 0,
                "Idle Mean": 0,
                "Idle Std": 0,
                "Idle Max": 0,
                "Idle Min": 0,
                "Label": "normal",
                "Query Type": None,
                "Query ID": None,
                "Domain": None,
                "Response IP": None,
                "TCP Flags": "",
            }

            # Extract IP layer information
            if IP in packet:
                packet_data["Source IP"] = packet[IP].src
                packet_data["Destination IP"] = packet[IP].dst

                # Extract TCP information
                if TCP in packet:
                    packet_data["Protocol"] = "TCP"
                    packet_data["Source Port"] = str(packet[TCP].sport)
                    packet_data["Destination Port"] = str(packet[TCP].dport)
                    packet_data["Query Type"] = "TCP_CONNECTION"

                    # Extract TCP flags
                    flags = []
                    if packet[TCP].flags & 0x02:  # SYN
                        flags.append("SYN")
                        packet_data["SYN Flag Count"] = 1
                    if packet[TCP].flags & 0x10:  # ACK
                        flags.append("ACK")
                        packet_data["ACK Flag Count"] = 1
                    if packet[TCP].flags & 0x01:  # FIN
                        flags.append("FIN")
                        packet_data["FIN Flag Count"] = 1
                    if packet[TCP].flags & 0x04:  # RST
                        flags.append("RST")
                        packet_data["RST Flag Count"] = 1
                    if packet[TCP].flags & 0x08:  # PSH
                        flags.append("PSH")
                        packet_data["PSH Flag Count"] = 1
                        packet_data["Fwd PSH Flags"] = 1
                    if packet[TCP].flags & 0x20:  # URG
                        flags.append("URG")
                        packet_data["URG Flag Count"] = 1
                        packet_data["Fwd URG Flags"] = 1

                    packet_data["TCP Flags"] = ", ".join(flags)

                # Extract UDP information
                elif UDP in packet:
                    packet_data["Protocol"] = "UDP"
                    packet_data["Source Port"] = str(packet[UDP].sport)
                    packet_data["Destination Port"] = str(packet[UDP].dport)
                    packet_data["Query Type"] = "UDP"

                    # Check for DNS
                    if packet[UDP].dport == 53 or packet[UDP].sport == 53:
                        packet_data["Protocol"] = "DNS"
                        packet_data["Query Type"] = "DNS_QUERY"

                        # Try to extract DNS information
                        if DNS in packet:
                            dns = packet[DNS]
                            if hasattr(dns, "qd") and dns.qd:
                                qname = dns.qd.qname.decode(
                                    "utf-8", errors="ignore"
                                ).rstrip(".")
                                packet_data["Domain"] = qname
                                packet_data["Info"] = f"DNS query for {qname}"

            json_data.append(packet_data)

        return json_data

    except Exception as e:
        raise Exception(f"Error parsing PCAP file: {e}")


async def _parse_csv_file(file_path: str, max_rows: int = None) -> List[Dict[str, Any]]:
    """Parse CSV file exported from Wireshark/tshark."""
    # Try different encodings to handle various PCAP export formats
    encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]

    for encoding in encodings:
        try:
            with open(file_path, mode="r", encoding=encoding) as f:
                reader = csv.DictReader(f)
                if max_rows:
                    rows = list(reader)[:max_rows]
                else:
                    rows = list(reader)
            print(f"Successfully read file with {encoding} encoding")
            break
        except UnicodeDecodeError:
            print(f"Failed to read with {encoding} encoding, trying next...")
            continue
        except Exception as e:
            print(f"Error reading file with {encoding}: {e}")
            continue
    else:
        # If all encodings fail, try with error handling
        try:
            with open(file_path, mode="r", encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                if max_rows:
                    rows = list(reader)[:max_rows]
                else:
                    rows = list(reader)
            print("Successfully read file with utf-8 encoding (ignoring errors)")
        except Exception as e:
            raise Exception(f"Failed to read PCAP file with any encoding: {e}")

    def clean(s: str) -> str:
        """Clean string values by removing quotes and extra whitespace."""
        if s is None:
            return ""
        # Remove any non-printable characters that might cause issues
        cleaned = s.strip().replace('"', "").replace("'", "")
        # Remove any control characters except newlines and tabs
        cleaned = "".join(
            char for char in cleaned if char.isprintable() or char in "\n\t"
        )
        return cleaned

    def parse_info_field(info: str) -> Dict[str, Any]:
        """Parse the Info field to extract additional packet details."""
        info_clean = clean(info)
        parsed_info = {
            "raw_info": info_clean,
            "query_type": None,
            "port_src": None,
            "port_dst": None,
            "flags": [],
            "query_id": None,
            "domain": None,
            "response_ip": None,
        }

        # Parse DNS queries
        if "Standard query" in info_clean and "response" not in info_clean:
            # Extract query ID (hex value)
            query_match = re.search(r"0x([0-9a-fA-F]+)", info_clean)
            if query_match:
                parsed_info["query_id"] = query_match.group(1)
                parsed_info["query_type"] = "DNS_QUERY"

            # Extract domain name
            domain_match = re.search(r"([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", info_clean)
            if domain_match:
                parsed_info["domain"] = domain_match.group(1)

        # Parse DNS responses
        elif "Standard query response" in info_clean:
            parsed_info["query_type"] = "DNS_RESPONSE"
            # Extract query ID
            query_match = re.search(r"0x([0-9a-fA-F]+)", info_clean)
            if query_match:
                parsed_info["query_id"] = query_match.group(1)

            # Extract domain and response IP
            domain_match = re.search(r"([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", info_clean)
            if domain_match:
                parsed_info["domain"] = domain_match.group(1)

            ip_match = re.search(
                r"A\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", info_clean
            )
            if ip_match:
                parsed_info["response_ip"] = ip_match.group(1)

        # Parse TCP connections
        elif "TCP" in info_clean or re.search(r"\d+\s*>\s*\d+", info_clean):
            parsed_info["query_type"] = "TCP_CONNECTION"
            # Extract ports - fix the regex pattern
            port_match = re.search(r"(\d+)\s*>\s*(\d+)", info_clean)
            if port_match:
                parsed_info["port_src"] = port_match.group(1)
                parsed_info["port_dst"] = port_match.group(2)

            # Extract TCP flags
            if "[SYN]" in info_clean:
                parsed_info["flags"].append("SYN")
            if "[ACK]" in info_clean:
                parsed_info["flags"].append("ACK")
            if "[FIN]" in info_clean:
                parsed_info["flags"].append("FIN")
            if "[RST]" in info_clean:
                parsed_info["flags"].append("RST")
            if "[PSH]" in info_clean:
                parsed_info["flags"].append("PSH")
            if "[URG]" in info_clean:
                parsed_info["flags"].append("URG")

        # Parse other protocols
        elif "UDP" in info_clean:
            parsed_info["query_type"] = "UDP"
            port_match = re.search(r"(\d+)\s*>\s*(\d+)", info_clean)
            if port_match:
                parsed_info["port_src"] = port_match.group(1)
                parsed_info["port_dst"] = port_match.group(2)

        return parsed_info

    def extract_ports_from_addresses(
        source: str, destination: str, info_parsed: Dict[str, Any]
    ) -> tuple:
        """Extract source and destination ports from addresses and info field."""
        src_port = None
        dst_port = None

        # Try to get ports from info field first
        if info_parsed.get("port_src"):
            src_port = info_parsed["port_src"]
        if info_parsed.get("port_dst"):
            dst_port = info_parsed["port_dst"]

        # If not found in info, try to extract from addresses
        if not src_port:
            src_match = re.search(r":(\d+)$", source)
            if src_match:
                src_port = src_match.group(1)
            else:
                src_port = "0"  # Default port

        if not dst_port:
            dst_match = re.search(r":(\d+)$", destination)
            if dst_match:
                dst_port = dst_match.group(1)
            else:
                dst_port = "0"  # Default port

        return src_port, dst_port

    def clean_ip_address(address: str) -> str:
        """Extract clean IP address from address field."""
        # Remove port if present
        ip_match = re.match(r"^([0-9.]+)", address)
        if ip_match:
            return ip_match.group(1)
        return address

    json_data = []

    for row in rows:
        # Clean basic fields
        packet_no = clean(row.get("No.", ""))
        time = clean(row.get("Time", ""))
        source = clean(row.get("Source", ""))
        destination = clean(row.get("Destination", ""))
        protocol = clean(row.get("Protocol", ""))
        length = clean(row.get("Length", ""))
        info = clean(row.get("Info", ""))

        # Parse info field for additional details
        info_parsed = parse_info_field(info)

        # Extract ports
        src_port, dst_port = extract_ports_from_addresses(
            source, destination, info_parsed
        )

        # Clean IP addresses
        src_ip = clean_ip_address(source)
        dst_ip = clean_ip_address(destination)

        # Create packet record
        packet_data = {
            "Packet No.": packet_no,
            "Time": time,
            "Source IP": src_ip,
            "Source Port": src_port,
            "Destination IP": dst_ip,
            "Destination Port": dst_port,
            "Protocol": protocol,
            "Length": length,
            "Info": info,
            "Flow ID": f"pcap-{packet_no}",
            "Timestamp": (
                float(time) if time.replace(".", "").replace("-", "").isdigit() else 0.0
            ),
            "Flow Duration": 0,  # PCAP doesn't provide flow duration
            "Total Fwd Packets": 1,  # Each packet is counted as 1
            "Total Backward Packets": 0,
            "Total Length of Fwd Packets": int(length) if length.isdigit() else 0,
            "Total Length of Bwd Packets": 0,
            "Fwd Packet Length Max": int(length) if length.isdigit() else 0,
            "Fwd Packet Length Min": int(length) if length.isdigit() else 0,
            "Fwd Packet Length Mean": int(length) if length.isdigit() else 0,
            "Fwd Packet Length Std": 0,
            "Bwd Packet Length Max": 0,
            "Bwd Packet Length Min": 0,
            "Bwd Packet Length Mean": 0,
            "Bwd Packet Length Std": 0,
            "Flow Bytes/s": 0,
            "Flow Packets/s": 0,
            "Flow IAT Mean": 0,
            "Flow IAT Std": 0,
            "Flow IAT Max": 0,
            "Flow IAT Min": 0,
            "Fwd IAT Total": 0,
            "Fwd IAT Mean": 0,
            "Fwd IAT Std": 0,
            "Fwd IAT Max": 0,
            "Fwd IAT Min": 0,
            "Bwd IAT Total": 0,
            "Bwd IAT Mean": 0,
            "Bwd IAT Std": 0,
            "Bwd IAT Max": 0,
            "Bwd IAT Min": 0,
            "Fwd PSH Flags": 1 if "PSH" in info_parsed["flags"] else 0,
            "Bwd PSH Flags": 0,
            "Fwd URG Flags": 1 if "URG" in info_parsed["flags"] else 0,
            "Bwd URG Flags": 0,
            "Fwd Header Length": 0,
            "Bwd Header Length": 0,
            "Fwd Packets/s": 0,
            "Bwd Packets/s": 0,
            "Min Packet Length": int(length) if length.isdigit() else 0,
            "Max Packet Length": int(length) if length.isdigit() else 0,
            "Packet Length Mean": int(length) if length.isdigit() else 0,
            "Packet Length Std": 0,
            "Packet Length Variance": 0,
            "FIN Flag Count": 1 if "FIN" in info_parsed["flags"] else 0,
            "SYN Flag Count": 1 if "SYN" in info_parsed["flags"] else 0,
            "RST Flag Count": 1 if "RST" in info_parsed["flags"] else 0,
            "PSH Flag Count": 1 if "PSH" in info_parsed["flags"] else 0,
            "ACK Flag Count": 1 if "ACK" in info_parsed["flags"] else 0,
            "URG Flag Count": 1 if "URG" in info_parsed["flags"] else 0,
            "CWE Flag Count": 0,
            "ECE Flag Count": 0,
            "Down/Up Ratio": 0,
            "Average Packet Size": int(length) if length.isdigit() else 0,
            "Avg Fwd Segment Size": 0,
            "Avg Bwd Segment Size": 0,
            "Fwd Avg Bytes/Bulk": 0,
            "Fwd Avg Packets/Bulk": 0,
            "Fwd Avg Bulk Rate": 0,
            "Bwd Avg Bytes/Bulk": 0,
            "Bwd Avg Packets/Bulk": 0,
            "Bwd Avg Bulk Rate": 0,
            "Subflow Fwd Packets": 0,
            "Subflow Fwd Bytes": 0,
            "Subflow Bwd Packets": 0,
            "Subflow Bwd Bytes": 0,
            "Init_Win_bytes_forward": 0,
            "Init_Win_bytes_backward": 0,
            "act_data_pkt_fwd": 0,
            "min_seg_size_forward": 0,
            "Active Mean": 0,
            "Active Std": 0,
            "Active Max": 0,
            "Active Min": 0,
            "Idle Mean": 0,
            "Idle Std": 0,
            "Idle Max": 0,
            "Idle Min": 0,
            "Label": "normal",  # Default label
            # Additional PCAP-specific fields
            "Query Type": info_parsed.get("query_type"),
            "Query ID": info_parsed.get("query_id"),
            "Domain": info_parsed.get("domain"),
            "Response IP": info_parsed.get("response_ip"),
            "TCP Flags": (
                ", ".join(info_parsed["flags"]) if info_parsed["flags"] else ""
            ),
        }

        json_data.append(packet_data)

    return json_data


async def fetch_graph_folders_names_from_os():
    """Fetch the names of the folders in the ./AppDbStore directory. and sort them by creation date."""
    folders = os.listdir("./AppDbStore")
    folders.sort(
        key=lambda x: os.path.getctime(os.path.join("./AppDbStore", x)), reverse=True
    )
    return folders
