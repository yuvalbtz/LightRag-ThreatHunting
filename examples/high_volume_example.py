#!/usr/bin/env python3
"""
High-Volume PCAP Processing Example

This script demonstrates how to use the optimized CICFlowMeter parameters
to handle PCAP files with millions of packets efficiently.

Key optimizations:
- Aggressive flow expiration (15 seconds)
- Less frequent garbage collection (every 5000 packets)
- Memory management with flow limits
- Streaming CSV processing
- Progress indicators for large files
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Add the parent directory to the path to import the helpers
sys.path.append(str(Path(__file__).parent.parent))

from examples.cicflowmeter_helpers import pcap_to_flows


async def process_large_pcap(pcap_file_path: str, max_flows: int = None):
    """
    Process a large PCAP file using high-volume optimized parameters.

    Args:
        pcap_file_path: Path to the PCAP file
        max_flows: Maximum number of flows to process (optional)
    """
    print("🚀 Starting High-Volume PCAP Processing")
    print("=" * 60)

    # Check if file exists
    if not os.path.exists(pcap_file_path):
        print(f"❌ PCAP file not found: {pcap_file_path}")
        return

    # Get file size for reference
    file_size = os.path.getsize(pcap_file_path)
    print(f"📁 PCAP file: {pcap_file_path}")
    print(f"📏 File size: {file_size / (1024*1024):.2f} MB")

    start_time = time.time()

    try:
        # Use high-volume processing mode
        flows = await pcap_to_flows(
            pcap_file_path=pcap_file_path,
            max_flows=max_flows,
            use_standard_format=True,
            use_custom_params=True,
            high_volume=True,  # Enable high-volume mode
        )

        end_time = time.time()
        processing_time = end_time - start_time

        print("\n" + "=" * 60)
        print("🎉 Processing Complete!")
        print(f"⏱️  Total processing time: {processing_time:.2f} seconds")
        print(f"📊 Total flows extracted: {len(flows)}")
        print(f"⚡ Processing rate: {len(flows)/processing_time:.2f} flows/second")

        if flows:
            # Show some sample data
            print(f"\n📋 Sample flow data (first flow):")
            sample_flow = flows[0]
            for key, value in list(sample_flow.items())[:10]:  # Show first 10 fields
                print(f"   {key}: {value}")

            # Show flow statistics
            print(f"\n📈 Flow Statistics:")
            protocols = {}
            for flow in flows:
                protocol = flow.get("protocol", "unknown")
                protocols[protocol] = protocols.get(protocol, 0) + 1

            for protocol, count in protocols.items():
                print(f"   {protocol}: {count} flows")

        return flows

    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")
        return None


async def main():
    """Main function to demonstrate high-volume processing."""
    print("🔧 CICFlowMeter High-Volume Processing Demo")
    print("=" * 60)

    # Example usage
    pcap_file = input("Enter path to PCAP file: ").strip()

    if not pcap_file:
        print("❌ No PCAP file specified")
        return

    # Optional: limit number of flows for testing
    max_flows_input = input(
        "Enter max flows to process (press Enter for all): "
    ).strip()
    max_flows = int(max_flows_input) if max_flows_input else None

    if max_flows:
        print(f"🔢 Limiting processing to {max_flows} flows")

    # Process the PCAP file
    flows = await process_large_pcap(pcap_file, max_flows)

    if flows:
        print(f"\n✅ Successfully processed {len(flows)} flows!")
        print(
            "💡 Tip: For even larger files, consider processing in chunks or using streaming approaches."
        )
    else:
        print("\n❌ Processing failed")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
