#!/usr/bin/env python3
"""
Demonstration script showing why 2,397 packets = 44 flows.
This script analyzes the PCAP file and shows how multiple packets belong to the same flow.
"""

import subprocess
import re
from collections import defaultdict
import sys
import os


def run_tcpdump_analysis(pcap_file):
    """Run tcpdump analysis to extract packet information."""
    try:
        # Run tcpdump to get packet details
        cmd = f"tcpdump -r {pcap_file} -n"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ Error running tcpdump: {result.stderr}")
            return None

        return result.stdout
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def extract_flows_from_packets(tcpdump_output):
    """Extract unique flows from tcpdump output."""
    flows = defaultdict(list)

    # Parse tcpdump output
    lines = tcpdump_output.strip().split("\n")

    for line in lines:
        if not line.strip():
            continue

        # Extract IP addresses and ports
        # Pattern: timestamp IP src.port > dst.port: flags, seq, win, length
        match = re.search(
            r"IP (\d+\.\d+\.\d+\.\d+)\.(\d+) > (\d+\.\d+\.\d+\.\d+)\.(\d+):", line
        )
        if match:
            src_ip, src_port, dst_ip, dst_port = match.groups()

            # Create flow key (5-tuple: src_ip, src_port, dst_ip, dst_port, protocol)
            # For simplicity, we'll assume TCP for this analysis
            flow_key = f"{src_ip}:{src_port} -> {dst_ip}:{dst_port} (TCP)"

            # Add packet info to this flow
            flows[flow_key].append(line.strip())

    return flows


def analyze_flow_distribution(flows):
    """Analyze the distribution of packets across flows."""
    print("🔍 FLOW ANALYSIS RESULTS")
    print("=" * 60)

    total_packets = sum(len(packets) for packets in flows.values())
    total_flows = len(flows)

    print(f"📊 Total packets in PCAP: {total_packets}")
    print(f"📊 Total unique flows: {total_flows}")
    print(f"📊 Average packets per flow: {total_packets / total_flows:.1f}")
    print()

    # Show top flows by packet count
    sorted_flows = sorted(flows.items(), key=lambda x: len(x[1]), reverse=True)

    print("🏆 TOP 10 FLOWS BY PACKET COUNT:")
    print("-" * 60)

    for i, (flow_key, packets) in enumerate(sorted_flows[:10], 1):
        packet_count = len(packets)
        print(f"{i:2d}. {flow_key}")
        print(f"    📦 Packets: {packet_count}")

        # Show first few packets as example
        if packets:
            first_packet = packets[0]
            # Extract timestamp and flags
            timestamp_match = re.search(r"(\d+:\d+:\d+\.\d+)", first_packet)
            flags_match = re.search(r"Flags \[([^\]]+)\]", first_packet)

            timestamp = timestamp_match.group(1) if timestamp_match else "N/A"
            flags = flags_match.group(1) if flags_match else "N/A"

            print(f"    ⏰ First packet: {timestamp} (Flags: {flags})")
        print()

    # Show flow distribution
    print("📈 FLOW DISTRIBUTION:")
    print("-" * 60)

    packet_counts = [len(packets) for packets in flows.values()]
    packet_counts.sort()

    print(f"Min packets per flow: {min(packet_counts)}")
    print(f"Max packets per flow: {max(packet_counts)}")
    print(f"Median packets per flow: {packet_counts[len(packet_counts)//2]}")

    # Count flows by packet range
    ranges = {"1-5 packets": 0, "6-10 packets": 0, "11-20 packets": 0, "21+ packets": 0}

    for count in packet_counts:
        if count <= 5:
            ranges["1-5 packets"] += 1
        elif count <= 10:
            ranges["6-10 packets"] += 1
        elif count <= 20:
            ranges["11-20 packets"] += 1
        else:
            ranges["21+ packets"] += 1

    print("\n📊 FLOWS BY PACKET COUNT RANGE:")
    for range_name, count in ranges.items():
        percentage = (count / total_flows) * 100
        print(f"   {range_name}: {count} flows ({percentage:.1f}%)")


def demonstrate_single_flow(flows):
    """Demonstrate how multiple packets belong to one flow."""
    print("\n🔬 SINGLE FLOW DEMONSTRATION:")
    print("=" * 60)

    # Find a flow with multiple packets
    multi_packet_flows = [(k, v) for k, v in flows.items() if len(v) > 5]

    if not multi_packet_flows:
        print("❌ No flows with multiple packets found")
        return

    # Use the flow with the most packets
    flow_key, packets = max(multi_packet_flows, key=lambda x: len(x[1]))

    print(f"🎯 Selected Flow: {flow_key}")
    print(f"📦 Total Packets: {len(packets)}")
    print()

    print("📋 PACKET SEQUENCE:")
    print("-" * 60)

    for i, packet in enumerate(packets[:10], 1):  # Show first 10 packets
        # Extract key information
        timestamp_match = re.search(r"(\d+:\d+:\d+\.\d+)", packet)
        flags_match = re.search(r"Flags \[([^\]]+)\]", packet)
        length_match = re.search(r"length (\d+)", packet)

        timestamp = timestamp_match.group(1) if timestamp_match else "N/A"
        flags = flags_match.group(1) if flags_match else "N/A"
        length = length_match.group(1) if length_match else "0"

        print(f"{i:2d}. {timestamp} - Flags: [{flags}] - Length: {length}")

        # Add description for common flags
        if "S" in flags:
            print("     → TCP SYN (Connection initiation)")
        elif "S." in flags:
            print("     → TCP SYN-ACK (Connection establishment)")
        elif "A" in flags and "S" not in flags and "F" not in flags:
            print("     → TCP ACK (Acknowledgement)")
        elif "F" in flags:
            print("     → TCP FIN (Connection termination)")
        elif "P" in flags:
            print("     → TCP PSH (Data push)")
        print()

    if len(packets) > 10:
        print(f"... and {len(packets) - 10} more packets")

    print("💡 CONCLUSION:")
    print(f"   This single flow contains {len(packets)} packets!")
    print("   Multiple packets = One flow (same 5-tuple)")


def main():
    """Main function to demonstrate flows vs packets."""
    pcap_file = "../cicflowmeter/traffic.pcap"

    if not os.path.exists(pcap_file):
        print(f"❌ PCAP file not found: {pcap_file}")
        return

    print("🚀 DEMONSTRATING: Why 2,397 Packets = 44 Flows")
    print("=" * 60)
    print()

    # Run tcpdump analysis
    print("🔍 Analyzing PCAP file...")
    tcpdump_output = run_tcpdump_analysis(pcap_file)

    if not tcpdump_output:
        print("❌ Failed to analyze PCAP file")
        return

    # Extract flows
    flows = extract_flows_from_packets(tcpdump_output)

    if not flows:
        print("❌ No flows found in PCAP file")
        return

    # Analyze and display results
    analyze_flow_distribution(flows)
    demonstrate_single_flow(flows)

    print("\n" + "=" * 60)
    print("✅ DEMONSTRATION COMPLETE")
    print("   This shows why multiple packets belong to the same flow!")
    print("   Each unique 5-tuple (src_ip:port -> dst_ip:port) = 1 flow")


if __name__ == "__main__":
    main()
