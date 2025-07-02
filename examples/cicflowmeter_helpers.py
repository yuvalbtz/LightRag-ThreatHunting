import csv
import os
import re
import sys
import tempfile
from typing import Any, Dict, List

# Add local cicflowmeter library to path
# Use the script's directory as reference point to make it work from any directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CICFLOWMETER_PATH = os.path.join(SCRIPT_DIR, "..", "cicflowmeter", "src")
if CICFLOWMETER_PATH not in sys.path:
    sys.path.insert(0, CICFLOWMETER_PATH)

# Import from local cicflowmeter library
try:
    from cicflowmeter.flow_session import FlowSession
    from cicflowmeter.sniffer import create_sniffer
    from cicflowmeter.writer import CSVWriter, output_writer_factory
    from cicflowmeter.constants import EXPIRED_UPDATE, PACKETS_PER_GC

    CICFLOWMETER_AVAILABLE = True
except ImportError as e:
    CICFLOWMETER_AVAILABLE = False
    print(f"Warning: Local cicflowmeter library not available: {e}")
    print(f"Expected path: {CICFLOWMETER_PATH}")


def get_cicflowmeter_to_standard_mapping() -> Dict[str, str]:
    """
    Get mapping from cicflowmeter feature names to standard flow feature names.
    Based on the actual cicflowmeter flow.py output format.

    Returns:
        Dict[str, str]: Mapping from cicflowmeter features to standard features
    """
    return {
        # Basic flow information - these are already in standard format
        "Source IP": "Source IP",
        "Destination IP": "Destination IP",
        "Source Port": "Source Port",
        "Destination Port": "Destination Port",
        "Protocol": "Protocol",
        "Timestamp": "Timestamp",
        "Flow Duration": "Flow Duration",
        # Flow statistics - some need aliasing
        "Flow Bytes/s": "Flow Bytes/s",
        "Flow Packets/s": "Flow Packets/s",
        "fwd_pkts_s": "Fwd Packets/s",
        "bwd_pkts_s": "Bwd Packets/s",
        "Total Fwd Packets": "Total Fwd Packets",
        "tot_bwd_pkts": "Total Backward Packets",
        "totlen_fwd_pkts": "Total Length of Fwd Packets",
        "totlen_bwd_pkts": "Total Length of Bwd Packets",
        # Forward packet statistics
        "fwd_pkt_len_max": "Fwd Packet Length Max",
        "fwd_pkt_len_min": "Fwd Packet Length Min",
        "fwd_pkt_len_mean": "Fwd Packet Length Mean",
        "fwd_pkt_len_std": "Fwd Packet Length Std",
        # Backward packet statistics
        "bwd_pkt_len_max": "Bwd Packet Length Max",
        "bwd_pkt_len_min": "Bwd Packet Length Min",
        "bwd_pkt_len_mean": "Bwd Packet Length Mean",
        "bwd_pkt_len_std": "Bwd Packet Length Std",
        # Overall packet statistics
        "pkt_len_max": "Max Packet Length",
        "pkt_len_min": "Min Packet Length",
        "pkt_len_mean": "Packet Length Mean",
        "pkt_len_std": "Packet Length Std",
        "pkt_len_var": "Packet Length Variance",
        # Header information
        "fwd_header_len": "Fwd Header Length",
        "bwd_header_len": "Bwd Header Length",
        "fwd_seg_size_min": "min_seg_size_forward",
        "fwd_act_data_pkts": "act_data_pkt_fwd",
        # Flow inter-arrival times
        "flow_iat_mean": "Flow IAT Mean",
        "flow_iat_max": "Flow IAT Max",
        "flow_iat_min": "Flow IAT Min",
        "flow_iat_std": "Flow IAT Std",
        # Forward inter-arrival times
        "fwd_iat_tot": "Fwd IAT Total",
        "fwd_iat_max": "Fwd IAT Max",
        "fwd_iat_min": "Fwd IAT Min",
        "fwd_iat_mean": "Fwd IAT Mean",
        "fwd_iat_std": "Fwd IAT Std",
        # Backward inter-arrival times
        "bwd_iat_tot": "Bwd IAT Total",
        "bwd_iat_max": "Bwd IAT Max",
        "bwd_iat_min": "Bwd IAT Min",
        "bwd_iat_mean": "Bwd IAT Mean",
        "bwd_iat_std": "Bwd IAT Std",
        # TCP flags
        "fwd_psh_flags": "Fwd PSH Flags",
        "bwd_psh_flags": "Bwd PSH Flags",
        "fwd_urg_flags": "Fwd URG Flags",
        "bwd_urg_flags": "Bwd URG Flags",
        "fin_flag_cnt": "FIN Flag Count",
        "syn_flag_cnt": "SYN Flag Count",
        "rst_flag_cnt": "RST Flag Count",
        "psh_flag_cnt": "PSH Flag Count",
        "ack_flag_cnt": "ACK Flag Count",
        "urg_flag_cnt": "URG Flag Count",
        "ece_flag_cnt": "ECE Flag Count",
        "cwr_flag_count": "CWE Flag Count",
        # Flow ratios and averages
        "down_up_ratio": "Down/Up Ratio",
        "pkt_size_avg": "Average Packet Size",
        # Window sizes
        "init_fwd_win_byts": "Init_Win_bytes_forward",
        "init_bwd_win_byts": "Init_Win_bytes_backward",
        # Active/Idle periods
        "active_max": "Active Max",
        "active_min": "Active Min",
        "active_mean": "Active Mean",
        "active_std": "Active Std",
        "idle_max": "Idle Max",
        "idle_min": "Idle Min",
        "idle_mean": "Idle Mean",
        "idle_std": "Idle Std",
        # Bulk transfer statistics
        "fwd_byts_b_avg": "Fwd Avg Bytes/Bulk",
        "fwd_pkts_b_avg": "Fwd Avg Packets/Bulk",
        "bwd_byts_b_avg": "Bwd Avg Bytes/Bulk",
        "bwd_pkts_b_avg": "Bwd Avg Packets/Bulk",
        "fwd_blk_rate_avg": "Fwd Avg Bulk Rate",
        "bwd_blk_rate_avg": "Bwd Avg Bulk Rate",
        # Segment sizes
        "fwd_seg_size_avg": "Avg Fwd Segment Size",
        "bwd_seg_size_avg": "Avg Bwd Segment Size",
        # Subflow statistics
        "subflow_fwd_pkts": "Subflow Fwd Packets",
        "subflow_bwd_pkts": "Subflow Bwd Packets",
        "subflow_fwd_byts": "Subflow Fwd Bytes",
        "subflow_bwd_byts": "Subflow Bwd Bytes",
    }


def get_standard_to_cicflowmeter_mapping() -> Dict[str, str]:
    """
    Get mapping from standard flow feature names to cicflowmeter feature names.

    Returns:
        Dict[str, str]: Mapping from standard features to cicflowmeter features
    """
    cicflowmeter_to_standard = get_cicflowmeter_to_standard_mapping()
    return {v: k for k, v in cicflowmeter_to_standard.items()}


def transform_cicflowmeter_to_standard(flow_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform flow data from cicflowmeter format to standard format.

    Args:
        flow_data: Dictionary with cicflowmeter feature names

    Returns:
        Dict[str, Any]: Dictionary with standard feature names
    """
    mapping = get_cicflowmeter_to_standard_mapping()
    transformed_data = {}

    for cicflowmeter_key, value in flow_data.items():
        if cicflowmeter_key in mapping:
            standard_key = mapping[cicflowmeter_key]
            transformed_data[standard_key] = value
        else:
            # Keep original key if no mapping found
            transformed_data[cicflowmeter_key] = value

    return transformed_data


def transform_standard_to_cicflowmeter(flow_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform flow data from standard format to cicflowmeter format.

    Args:
        flow_data: Dictionary with standard feature names

    Returns:
        Dict[str, Any]: Dictionary with cicflowmeter feature names
    """
    mapping = get_standard_to_cicflowmeter_mapping()
    transformed_data = {}

    for standard_key, value in flow_data.items():
        if standard_key in mapping:
            cicflowmeter_key = mapping[standard_key]
            transformed_data[cicflowmeter_key] = value
        else:
            # Keep original key if no mapping found
            transformed_data[standard_key] = value

    return transformed_data


def get_cicflowmeter_features() -> List[str]:
    """
    Get the list of cicflowmeter feature names as they appear in the actual output.
    Based on the flow.py get_data() method.

    Returns:
        List[str]: List of cicflowmeter feature names
    """
    return [
        # Basic IP information
        "Source IP",
        "Destination IP",
        "Source Port",
        "Destination Port",
        "Protocol",
        # Basic information from packet times
        "Timestamp",
        "Flow Duration",
        "Flow Bytes/s",
        "Flow Packets/s",
        "fwd_pkts_s",
        "bwd_pkts_s",
        "Total Fwd Packets",
        "tot_bwd_pkts",
        "totlen_fwd_pkts",
        "totlen_bwd_pkts",
        "fwd_pkt_len_max",
        "fwd_pkt_len_min",
        "fwd_pkt_len_mean",
        "fwd_pkt_len_std",
        "bwd_pkt_len_max",
        "bwd_pkt_len_min",
        "bwd_pkt_len_mean",
        "bwd_pkt_len_std",
        "pkt_len_max",
        "pkt_len_min",
        "pkt_len_mean",
        "pkt_len_std",
        "pkt_len_var",
        "fwd_header_len",
        "bwd_header_len",
        "fwd_seg_size_min",
        "fwd_act_data_pkts",
        "flow_iat_mean",
        "flow_iat_max",
        "flow_iat_min",
        "flow_iat_std",
        "fwd_iat_tot",
        "fwd_iat_max",
        "fwd_iat_min",
        "fwd_iat_mean",
        "fwd_iat_std",
        "bwd_iat_tot",
        "bwd_iat_max",
        "bwd_iat_min",
        "bwd_iat_mean",
        "bwd_iat_std",
        "fwd_psh_flags",
        "bwd_psh_flags",
        "fwd_urg_flags",
        "bwd_urg_flags",
        "fin_flag_cnt",
        "syn_flag_cnt",
        "rst_flag_cnt",
        "psh_flag_cnt",
        "ack_flag_cnt",
        "urg_flag_cnt",
        "ece_flag_cnt",
        "down_up_ratio",
        "pkt_size_avg",
        "init_fwd_win_byts",
        "init_bwd_win_byts",
        "active_max",
        "active_min",
        "active_mean",
        "active_std",
        "idle_max",
        "idle_min",
        "idle_mean",
        "idle_std",
        "fwd_byts_b_avg",
        "fwd_pkts_b_avg",
        "bwd_byts_b_avg",
        "bwd_pkts_b_avg",
        "fwd_blk_rate_avg",
        "bwd_blk_rate_avg",
        "fwd_seg_size_avg",
        "bwd_seg_size_avg",
        "cwr_flag_count",
        "subflow_fwd_pkts",
        "subflow_bwd_pkts",
        "subflow_fwd_byts",
        "subflow_bwd_byts",
    ]


def get_standard_features() -> List[str]:
    """
    Get the list of standard flow feature names.

    Returns:
        List[str]: List of standard flow feature names
    """
    return [
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


async def pcap_to_flows_using_local_library(
    pcap_file_path: str, max_flows: int = None, use_standard_format: bool = True
) -> List[Dict[str, Any]]:
    """
    Convert PCAP file to flow data using the local cicflowmeter library.

    Args:
        pcap_file_path: Path to the input PCAP file
        max_flows: Maximum number of flows to process (optional)
        use_standard_format: If True, return data in standard format, else in cicflowmeter format

    Returns:
        List[Dict[str, Any]]: List of flow dictionaries with flow attributes
    """
    if not CICFLOWMETER_AVAILABLE:
        raise Exception("Local cicflowmeter library is not available")

    if not os.path.exists(pcap_file_path):
        raise Exception(f"PCAP file not found: {pcap_file_path}")

    csv_path = None
    try:
        # Create temporary CSV file
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
        csv_path = temp_file.name
        temp_file.close()

        print(f"Processing PCAP file: {pcap_file_path}")
        print(f"Output CSV: {csv_path}")

        # Create sniffer using the correct API, pass csv_path as output
        sniffer, session = create_sniffer(
            input_file=pcap_file_path,
            input_interface=None,
            output_mode="csv",
            output=csv_path,
            verbose=True,  # Enable verbose to see more details
        )

        # Process the PCAP file
        print("Starting packet processing...")
        sniffer.start()

        # Wait for processing to complete
        print("Waiting for processing to complete...")
        sniffer.join()

        # Flush remaining flows
        print("Flushing remaining flows...")
        session.flush_flows()

        # Check if CSV file was created and has content
        if not os.path.exists(csv_path):
            raise Exception("CSV file was not created")

        print(f"CSV file created: {csv_path}")
        print(f"CSV file size: {os.path.getsize(csv_path)} bytes")

        # If CSV is empty, return empty list
        if os.path.getsize(csv_path) == 0:
            print("CSV file is empty - no flows generated from PCAP")
            return []

        # Read and print the CSV headers first
        with open(csv_path, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
            if first_line:
                headers = first_line.split(",")
                print(f"[DEBUG] CSV headers: {headers}")
                print(f"[DEBUG] Number of headers: {len(headers)}")
            else:
                print("CSV file is empty - no flows generated from PCAP")
                return []

        # Read the generated CSV file
        flows = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if max_flows is not None and i >= max_flows:
                    break
                print(f"[DEBUG] Processing row {i+1}")
                # Convert all values to appropriate types
                flow_data = {}
                for key, value in row.items():
                    # Skip empty values
                    if not value or value.strip() == "":
                        flow_data[key] = None
                        continue

                    # Try to convert to numeric types, but preserve strings for non-numeric data
                    try:
                        # Check if it's a float (contains decimal point)
                        if (
                            "." in value
                            and value.replace(".", "")
                            .replace("-", "")
                            .replace("e", "")
                            .replace("E", "")
                            .isdigit()
                        ):
                            flow_data[key] = float(value)
                        # Check if it's an integer
                        elif value.replace("-", "").isdigit():
                            flow_data[key] = int(value)
                        else:
                            # Keep as string for non-numeric data (IPs, protocols, etc.)
                            flow_data[key] = value
                    except (ValueError, TypeError):
                        # If conversion fails, keep as string
                        flow_data[key] = value
                if use_standard_format:
                    flow_data = transform_cicflowmeter_to_standard(flow_data)
                flows.append(flow_data)

        # Keep the CSV file for inspection
        print(f"Successfully converted {len(flows)} flows from PCAP file")
        print(f"CSV file kept for inspection: {csv_path}")
        if use_standard_format:
            print("Data returned in standard format")
        else:
            print("Data returned in cicflowmeter format")

        return flows

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        if csv_path and os.path.exists(csv_path):
            print(f"CSV file exists: {csv_path}")
            print(f"CSV file size: {os.path.getsize(csv_path)} bytes")
            try:
                with open(csv_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    print(f"CSV content (first 500 chars): {content[:500]}")
            except Exception as read_error:
                print(f"Could not read CSV file: {read_error}")
        else:
            print(f"CSV file does not exist: {csv_path}")

        # Keep the CSV file for inspection even on error
        print(f"CSV file kept for inspection: {csv_path}")
        raise Exception(f"Error converting PCAP to flows: {str(e)}")


async def pcap_to_flows(
    pcap_file_path: str,
    max_flows: int = None,
    use_standard_format: bool = True,
    use_custom_params: bool = True,
    high_volume: bool = False,  # New parameter for high-volume processing
) -> List[Dict[str, Any]]:
    """
    Convert PCAP file to flow data using cicflowmeter and return as list of dictionaries.
    Uses local library if available, falls back to command-line tool.

    Args:
        pcap_file_path: Path to the input PCAP file
        max_flows: Maximum number of flows to process (optional)
        use_standard_format: If True, return data in standard format, else in cicflowmeter format
        use_custom_params: If True, use custom parameters for better flow capture (default: True)
        high_volume: If True, use ultra-optimized parameters for processing millions of packets

    Returns:
        List[Dict[str, Any]]: List of flow dictionaries with flow attributes
    """
    try:
        # Try to use local library first
        if CICFLOWMETER_AVAILABLE:
            if high_volume:
                print(
                    "🚀 Using ultra-optimized parameters for high-volume processing (millions of packets)..."
                )
                return await pcap_to_flows_high_volume(
                    pcap_file_path, max_flows, use_standard_format
                )
            elif use_custom_params:
                print("Using custom cicflowmeter parameters for better flow capture...")
                return await pcap_to_flows_using_custom_library(
                    pcap_file_path, max_flows, use_standard_format
                )
            else:
                return await pcap_to_flows_using_local_library(
                    pcap_file_path, max_flows, use_standard_format
                )
        else:
            # Fall back to command-line tool if local library not available
            print(
                "Local cicflowmeter library not available, falling back to command-line tool"
            )
            return await pcap_to_flows_using_command_line(
                pcap_file_path, max_flows, use_standard_format
            )
    except Exception as e:
        raise Exception(f"Error converting PCAP to flows: {str(e)}")


async def pcap_to_flows_using_command_line(
    pcap_file_path: str, max_flows: int = None, use_standard_format: bool = True
) -> List[Dict[str, Any]]:
    """
    Convert PCAP file to flow data using cicflowmeter command-line tool.

    Args:
        pcap_file_path: Path to the input PCAP file
        max_flows: Maximum number of flows to process (optional)
        use_standard_format: If True, return data in standard format, else in cicflowmeter format

    Returns:
        List[Dict[str, Any]]: List of flow dictionaries with flow attributes
    """
    try:
        # Create temporary CSV file
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
        csv_path = temp_file.name
        temp_file.close()

        # Prepare cicflowmeter command
        cmd = ["cicflowmeter", "-i", pcap_file_path, "-c", csv_path]

        # Add max flows limit if specified
        if max_flows:
            cmd.extend(["-m", str(max_flows)])

        print(f"Running cicflowmeter command: {' '.join(cmd)}")

        # Execute cicflowmeter
        import subprocess

        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300  # 5 minute timeout
        )

        if result.returncode != 0:
            raise Exception(f"cicflowmeter failed with error: {result.stderr}")

        print(f"Successfully converted PCAP to CSV: {csv_path}")

        # Read the CSV file and convert to list of dictionaries
        flows = []

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert all values to appropriate types
                flow_data = {}
                for key, value in row.items():
                    # Skip empty values
                    if not value or value.strip() == "":
                        flow_data[key] = None
                        continue

                    # Try to convert to numeric types, but preserve strings for non-numeric data
                    try:
                        # Check if it's a float (contains decimal point)
                        if (
                            "." in value
                            and value.replace(".", "")
                            .replace("-", "")
                            .replace("e", "")
                            .replace("E", "")
                            .isdigit()
                        ):
                            flow_data[key] = float(value)
                        # Check if it's an integer
                        elif value.replace("-", "").isdigit():
                            flow_data[key] = int(value)
                        else:
                            # Keep as string for non-numeric data (IPs, protocols, etc.)
                            flow_data[key] = value
                    except (ValueError, TypeError):
                        # If conversion fails, keep as string
                        flow_data[key] = value

                # Transform to standard format if requested
                if use_standard_format:
                    flow_data = transform_cicflowmeter_to_standard(flow_data)

                flows.append(flow_data)

        # Clean up temporary file
        try:
            os.unlink(csv_path)
        except:
            pass  # Ignore cleanup errors

        print(f"Successfully converted {len(flows)} flows from PCAP file")
        if use_standard_format:
            print("Data returned in standard format")
        else:
            print("Data returned in cicflowmeter format")
        return flows

    except Exception as e:
        # Clean up temporary file in case of error
        if "csv_path" in locals():
            try:
                os.unlink(csv_path)
            except:
                pass
        raise Exception(f"Error converting PCAP to flows: {str(e)}")


def validate_cicflowmeter_installation() -> bool:
    """
    Validate that cicflowmeter is properly installed and accessible.

    Returns:
        bool: True if cicflowmeter is available, False otherwise
    """
    if CICFLOWMETER_AVAILABLE:
        return True

    try:
        # Test if cicflowmeter command is available
        import subprocess

        result = subprocess.run(
            ["cicflowmeter", "--help"], capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return False


def get_cicflowmeter_version() -> str:
    """
    Get the version of cicflowmeter available.

    Returns:
        str: Version string or "Unknown" if not available
    """
    if CICFLOWMETER_AVAILABLE:
        return "Local Library"

    try:
        import subprocess

        result = subprocess.run(
            ["cicflowmeter", "--version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return "Unknown"
    except:
        return "Unknown"


def test_mapping_with_sample_data():
    """Test the mapping functions with sample data to verify they work correctly."""
    print("🧪 Testing mapping functions with sample data")
    print("=" * 50)

    # Create sample cicflowmeter data
    sample_cicflowmeter_data = {
        "Source IP": "192.168.1.100",
        "Destination IP": "8.8.8.8",
        "Source Port": "12345",
        "Destination Port": "53",
        "Protocol": "UDP",
        "Timestamp": "1234567890.123",
        "Flow Duration": "1.5",
        "tot_fwd_pkts": "5",
        "tot_bwd_pkts": "1",
        "totlen_fwd_pkts": "500",
        "totlen_bwd_pkts": "100",
        "fwd_pkt_len_max": "150",
        "fwd_pkt_len_min": "50",
        "fwd_pkt_len_mean": "100.0",
        "fwd_pkt_len_std": "25.0",
        "flow_iat_mean": "0.5",
        "flow_iat_max": "2.0",
        "flow_iat_min": "0.1",
        "flow_iat_std": "0.3",
        "fin_flag_cnt": "0",
        "syn_flag_cnt": "0",
        "rst_flag_cnt": "0",
        "psh_flag_cnt": "0",
        "ack_flag_cnt": "0",
        "urg_flag_cnt": "0",
        "ece_flag_cnt": "0",
        "down_up_ratio": "5.0",
        "pkt_size_avg": "100.0",
        "init_fwd_win_byts": "8192",
        "init_bwd_win_byts": "8192",
        "active_max": "1.0",
        "active_min": "0.1",
        "active_mean": "0.5",
        "active_std": "0.2",
        "idle_max": "0.5",
        "idle_min": "0.1",
        "idle_mean": "0.2",
        "idle_std": "0.1",
    }

    print(f"Sample CICFlowMeter data keys: {list(sample_cicflowmeter_data.keys())}")

    # Test transformation to standard format
    try:
        standard_data = transform_cicflowmeter_to_standard(sample_cicflowmeter_data)
        print(f"✅ Transformation to standard format successful")
        print(f"   Standard data keys: {list(standard_data.keys())}")
        print(f"   Sample mappings:")
        print(
            f"     'tot_fwd_pkts' -> '{standard_data.get('Total Fwd Packets', 'NOT_FOUND')}'"
        )
        print(
            f"     'tot_bwd_pkts' -> '{standard_data.get('Total Backward Packets', 'NOT_FOUND')}'"
        )
        print(
            f"     'totlen_fwd_pkts' -> '{standard_data.get('Total Length of Fwd Packets', 'NOT_FOUND')}'"
        )
    except Exception as e:
        print(f"❌ Error in transformation to standard format: {e}")

    # Test transformation back to cicflowmeter format
    try:
        cicflowmeter_data = transform_standard_to_cicflowmeter(standard_data)
        print(f"✅ Transformation back to CICFlowMeter format successful")
        print(f"   CICFlowMeter data keys: {list(cicflowmeter_data.keys())}")
    except Exception as e:
        print(f"❌ Error in transformation back to CICFlowMeter format: {e}")

    print("=" * 50)
    return True


class CustomFlowSession(FlowSession):
    """Custom FlowSession with optimized parameters for handling millions of packets."""

    def __init__(
        self,
        output_mode=None,
        output=None,
        fields=None,
        verbose=False,
        expired_update=30,  # Reduced from 120 to 30 seconds for faster flow expiration
        packets_per_gc=1000,  # Increased from 100 to 1000 for less frequent GC
        max_flows_in_memory=100000,  # New parameter to limit memory usage
        *args,
        **kwargs,
    ):
        # Override the constants for better flow capture
        self.EXPIRED_UPDATE = expired_update
        self.PACKETS_PER_GC = packets_per_gc
        self.MAX_FLOWS_IN_MEMORY = max_flows_in_memory
        self.packet_count = 0

        super().__init__(
            output_mode=output_mode,
            output=output,
            fields=fields,
            verbose=verbose,
            *args,
            **kwargs,
        )

    def process(self, packet):
        """Override process method to add packet counting and memory management."""
        self.packet_count += 1

        # Force garbage collection if we have too many flows in memory
        if len(self.flows) > self.MAX_FLOWS_IN_MEMORY:
            if self.verbose:
                print(
                    f"[WARNING] Too many flows in memory ({len(self.flows)}), forcing garbage collection"
                )
            self.garbage_collect(None)

        # Call parent process method
        super().process(packet)

    def garbage_collect(self, latest_time) -> None:
        """Enhanced garbage collection with better memory management."""
        flows_to_remove = []

        for k, flow in self.flows.items():
            if not flow:
                flows_to_remove.append(k)
                continue

            # More aggressive flow expiration for high-volume processing
            if latest_time is not None:
                time_since_last = latest_time - flow.latest_timestamp
                # Expire flows more quickly for high-volume scenarios
                if (
                    time_since_last > self.EXPIRED_UPDATE or flow.duration > 180
                ):  # Reduced from 300 to 180 seconds
                    flows_to_remove.append(k)
                    self.output_writer.write(flow.get_data(self.fields))

        # Remove expired flows
        for k in flows_to_remove:
            del self.flows[k]

        if self.verbose and flows_to_remove:
            print(
                f"[GC] Removed {len(flows_to_remove)} flows. Remaining: {len(self.flows)}"
            )

        # Force Python garbage collection if we have too many flows
        if len(self.flows) > self.MAX_FLOWS_IN_MEMORY * 0.8:
            import gc

            gc.collect()
            if self.verbose:
                print(
                    f"[GC] Forced Python garbage collection. Flows in memory: {len(self.flows)}"
                )


def create_custom_sniffer(
    input_file,
    input_interface,
    output_mode,
    output,
    fields=None,
    verbose=False,
    expired_update=30,  # Optimized for high-volume processing
    packets_per_gc=1000,  # Optimized for high-volume processing
    max_flows_in_memory=100000,  # New parameter for memory management
):
    """Create a sniffer with custom flow session parameters."""
    from scapy.sendrecv import AsyncSniffer

    assert (input_file is None) ^ (
        input_interface is None
    ), "Either provide interface input or file input not both"
    if fields is not None:
        fields = fields.split(",")

    # Pass config to CustomFlowSession constructor
    session = CustomFlowSession(
        output_mode=output_mode,
        output=output,
        fields=fields,
        verbose=verbose,
        expired_update=expired_update,
        packets_per_gc=packets_per_gc,
        max_flows_in_memory=max_flows_in_memory,
    )

    if input_file:
        sniffer = AsyncSniffer(
            offline=input_file,
            filter="ip and (tcp or udp)",
            prn=session.process,
            store=False,
        )
    else:
        sniffer = AsyncSniffer(
            iface=input_interface,
            filter="ip and (tcp or udp)",
            prn=session.process,
            store=False,
        )
    return sniffer, session


async def pcap_to_flows_using_custom_library(
    pcap_file_path: str,
    max_flows: int = None,
    use_standard_format: bool = True,
    expired_update: int = 30,  # Optimized for high-volume processing
    packets_per_gc: int = 1000,  # Optimized for high-volume processing
    max_flows_in_memory: int = 100000,  # Memory limit for high-volume processing
) -> List[Dict[str, Any]]:
    """
    Convert PCAP file to flow data using custom cicflowmeter parameters for better flow capture.

    Args:
        pcap_file_path: Path to the input PCAP file
        max_flows: Maximum number of flows to process (optional)
        use_standard_format: If True, return data in standard format, else in cicflowmeter format
        expired_update: Flow timeout in seconds (default: 60, lower = more flows)
        packets_per_gc: Garbage collection frequency (default: 50, lower = more frequent GC)

    Returns:
        List[Dict[str, Any]]: List of flow dictionaries with flow attributes
    """
    if not CICFLOWMETER_AVAILABLE:
        raise Exception("Local cicflowmeter library is not available")

    if not os.path.exists(pcap_file_path):
        raise Exception(f"PCAP file not found: {pcap_file_path}")

    csv_path = None
    try:
        # Create temporary CSV file
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
        csv_path = temp_file.name
        temp_file.close()

        print(f"Processing PCAP file: {pcap_file_path}")
        print(f"Output CSV: {csv_path}")
        print(
            f"Using optimized parameters for high-volume processing: expired_update={expired_update}s, packets_per_gc={packets_per_gc}, max_flows_in_memory={max_flows_in_memory}"
        )

        # Create custom sniffer with optimized parameters for high-volume processing
        sniffer, session = create_custom_sniffer(
            input_file=pcap_file_path,
            input_interface=None,
            output_mode="csv",
            output=csv_path,
            verbose=True,  # Enable verbose to see more details
            expired_update=expired_update,
            packets_per_gc=packets_per_gc,
            max_flows_in_memory=max_flows_in_memory,
        )

        # Process the PCAP file
        print("Starting packet processing with custom parameters...")
        sniffer.start()

        # Wait for processing to complete
        print("Waiting for processing to complete...")
        sniffer.join()

        # Flush remaining flows
        print("Flushing remaining flows...")
        session.flush_flows()

        # Check if CSV file was created and has content
        if not os.path.exists(csv_path):
            raise Exception("CSV file was not created")

        print(f"CSV file created: {csv_path}")
        print(f"CSV file size: {os.path.getsize(csv_path)} bytes")

        # If CSV is empty, return empty list
        if os.path.getsize(csv_path) == 0:
            print("CSV file is empty - no flows generated from PCAP")
            return []

        # Read and print the CSV headers first
        with open(csv_path, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
            if first_line:
                headers = first_line.split(",")
                print(f"[DEBUG] CSV headers: {headers}")
                print(f"[DEBUG] Number of headers: {len(headers)}")
            else:
                print("CSV file is empty - no flows generated from PCAP")
                return []

        # Read the generated CSV file
        flows = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if max_flows is not None and i >= max_flows:
                    break
                print(f"[DEBUG] Processing row {i+1}")
                # Convert all values to appropriate types
                flow_data = {}
                for key, value in row.items():
                    # Skip empty values
                    if not value or value.strip() == "":
                        flow_data[key] = None
                        continue

                    # Try to convert to numeric types, but preserve strings for non-numeric data
                    try:
                        # Check if it's a float (contains decimal point)
                        if (
                            "." in value
                            and value.replace(".", "")
                            .replace("-", "")
                            .replace("e", "")
                            .replace("E", "")
                            .isdigit()
                        ):
                            flow_data[key] = float(value)
                        # Check if it's an integer
                        elif value.replace("-", "").isdigit():
                            flow_data[key] = int(value)
                        else:
                            # Keep as string for non-numeric data (IPs, protocols, etc.)
                            flow_data[key] = value
                    except (ValueError, TypeError):
                        # If conversion fails, keep as string
                        flow_data[key] = value
                if use_standard_format:
                    flow_data = transform_cicflowmeter_to_standard(flow_data)
                flows.append(flow_data)

        # Keep the CSV file for inspection
        print(f"Successfully converted {len(flows)} flows from PCAP file")
        print(f"CSV file kept for inspection: {csv_path}")
        if use_standard_format:
            print("Data returned in standard format")
        else:
            print("Data returned in cicflowmeter format")

        return flows

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        if csv_path and os.path.exists(csv_path):
            print(f"CSV file exists: {csv_path}")
            print(f"CSV file size: {os.path.getsize(csv_path)} bytes")
            try:
                with open(csv_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    print(f"CSV content (first 500 chars): {content[:500]}")
            except Exception as read_error:
                print(f"Could not read CSV file: {read_error}")
        else:
            print(f"CSV file does not exist: {csv_path}")

        # Keep the CSV file for inspection even on error
        print(f"CSV file kept for inspection: {csv_path}")
        raise Exception(f"Error converting PCAP to flows: {str(e)}")


async def pcap_to_flows_high_volume(
    pcap_file_path: str,
    max_flows: int = None,
    use_standard_format: bool = True,
    chunk_size: int = 1000000,  # Process in chunks of 1M packets
    expired_update: int = 15,  # Very aggressive flow expiration
    packets_per_gc: int = 5000,  # Less frequent GC for better performance
    max_flows_in_memory: int = 50000,  # Lower memory footprint
) -> List[Dict[str, Any]]:
    """
    Convert PCAP file to flow data optimized for processing millions of packets.
    Uses streaming approach and aggressive memory management.

    Args:
        pcap_file_path: Path to the input PCAP file
        max_flows: Maximum number of flows to process (optional)
        use_standard_format: If True, return data in standard format, else in cicflowmeter format
        chunk_size: Number of packets to process before forcing memory cleanup
        expired_update: Flow timeout in seconds (very aggressive for high volume)
        packets_per_gc: Garbage collection frequency (optimized for performance)
        max_flows_in_memory: Maximum flows to keep in memory

    Returns:
        List[Dict[str, Any]]: List of flow dictionaries with flow attributes
    """
    if not CICFLOWMETER_AVAILABLE:
        raise Exception("Local cicflowmeter library is not available")

    if not os.path.exists(pcap_file_path):
        raise Exception(f"PCAP file not found: {pcap_file_path}")

    csv_path = None
    try:
        # Create temporary CSV file
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
        csv_path = temp_file.name
        temp_file.close()

        print(f"🚀 HIGH-VOLUME MODE: Processing PCAP file: {pcap_file_path}")
        print(f"📊 Output CSV: {csv_path}")
        print(f"⚡ Optimized parameters:")
        print(f"   - expired_update: {expired_update}s (aggressive)")
        print(f"   - packets_per_gc: {packets_per_gc} (performance optimized)")
        print(f"   - max_flows_in_memory: {max_flows_in_memory} (memory efficient)")
        print(f"   - chunk_size: {chunk_size} packets")

        # Create custom sniffer with ultra-optimized parameters
        sniffer, session = create_custom_sniffer(
            input_file=pcap_file_path,
            input_interface=None,
            output_mode="csv",
            output=csv_path,
            verbose=True,
            expired_update=expired_update,
            packets_per_gc=packets_per_gc,
            max_flows_in_memory=max_flows_in_memory,
        )

        # Process the PCAP file
        print("🚀 Starting high-volume packet processing...")
        sniffer.start()

        # Wait for processing to complete
        print("⏳ Waiting for processing to complete...")
        sniffer.join()

        # Flush remaining flows
        print("🧹 Flushing remaining flows...")
        session.flush_flows()

        # Check if CSV file was created and has content
        if not os.path.exists(csv_path):
            raise Exception("CSV file was not created")

        print(f"✅ CSV file created: {csv_path}")
        print(f"📏 CSV file size: {os.path.getsize(csv_path)} bytes")
        print(f"📈 Processed {session.packet_count} packets")

        # If CSV is empty, return empty list
        if os.path.getsize(csv_path) == 0:
            print("⚠️ CSV file is empty - no flows generated from PCAP")
            return []

        # Read the generated CSV file with streaming approach for large files
        flows = []
        print("📖 Reading CSV file...")

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if max_flows is not None and i >= max_flows:
                    break

                # Progress indicator for large files
                if i % 10000 == 0 and i > 0:
                    print(f"📊 Processed {i} flows...")

                # Convert all values to appropriate types
                flow_data = {}
                for key, value in row.items():
                    # Skip empty values
                    if not value or value.strip() == "":
                        flow_data[key] = None
                        continue

                    # Try to convert to numeric types, but preserve strings for non-numeric data
                    try:
                        # Check if it's a float (contains decimal point)
                        if (
                            "." in value
                            and value.replace(".", "")
                            .replace("-", "")
                            .replace("e", "")
                            .replace("E", "")
                            .isdigit()
                        ):
                            flow_data[key] = float(value)
                        # Check if it's an integer
                        elif value.replace("-", "").isdigit():
                            flow_data[key] = int(value)
                        else:
                            # Keep as string for non-numeric data (IPs, protocols, etc.)
                            flow_data[key] = value
                    except (ValueError, TypeError):
                        # If conversion fails, keep as string
                        flow_data[key] = value

                if use_standard_format:
                    flow_data = transform_cicflowmeter_to_standard(flow_data)
                flows.append(flow_data)

        # Keep the CSV file for inspection
        print(f"🎉 Successfully converted {len(flows)} flows from PCAP file")
        print(f"📁 CSV file kept for inspection: {csv_path}")
        if use_standard_format:
            print("📋 Data returned in standard format")
        else:
            print("📋 Data returned in cicflowmeter format")

        return flows

    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        if csv_path and os.path.exists(csv_path):
            print(f"📁 CSV file exists: {csv_path}")
            print(f"📏 CSV file size: {os.path.getsize(csv_path)} bytes")
        else:
            print(f"📁 CSV file does not exist: {csv_path}")

        # Keep the CSV file for inspection even on error
        print(f"📁 CSV file kept for inspection: {csv_path}")
        raise Exception(f"Error converting PCAP to flows: {str(e)}")
