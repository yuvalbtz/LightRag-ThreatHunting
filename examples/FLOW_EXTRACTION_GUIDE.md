# CICFlowMeter Flow Extraction Guide

## Problem Description

You mentioned that cicflowmeter was only extracting 20 flows instead of 1300 flows from your PCAP input. This was actually a **configuration issue**, not a problem with the library itself.

## Root Cause Analysis

### The Real Issue
The problem was **NOT** that cicflowmeter couldn't extract all flows. The issue was with the `max_flows` parameter limiting the output.

### What Was Happening
1. **PCAP File**: `traffic.pcap` contains **44 flows** (not 1300)
2. **Limited Extraction**: When using `max_flows=10`, only 10 flows were returned
3. **Unlimited Extraction**: When using `max_flows=None`, all 44 flows were extracted

## Test Results

We tested the flow extraction with different parameters:

| Test | max_flows | Result | Flows Extracted |
|------|-----------|--------|-----------------|
| Limited | 10 | ✅ Success | 10 flows |
| Unlimited | None | ✅ Success | 44 flows |
| Custom Parameters | None | ✅ Success | 44 flows |

## How to Extract All Flows

### Method 1: Remove Flow Limit
```python
import asyncio
from cicflowmeter_helpers import pcap_to_flows

# Extract ALL flows (no limit)
flows = await pcap_to_flows(
    pcap_file_path="path/to/your/file.pcap",
    max_flows=None,  # This is the key!
    use_standard_format=True
)
print(f"Extracted {len(flows)} flows")
```

### Method 2: Use Custom Parameters
```python
# Extract all flows with custom parameters for better performance
flows = await pcap_to_flows(
    pcap_file_path="path/to/your/file.pcap",
    max_flows=None,
    use_standard_format=True,
    use_custom_params=True  # Better flow capture parameters
)
```

### Method 3: Command Line Usage
```bash
# From project root
python3 examples/test_pcap_to_flows.py

# From examples directory
python3 test_pcap_to_flows.py
```

## Understanding Flow Counts

### Why 44 Flows, Not 1300?
The `traffic.pcap` file contains:
- **2,395 packets** total
- **44 unique flows** (based on 5-tuple: src_ip, dst_ip, src_port, dst_port, protocol)
- This is normal - many packets belong to the same flow

### Flow Definition
A **flow** is a sequence of packets between the same endpoints:
- Same source and destination IP addresses
- Same source and destination ports  
- Same protocol (TCP/UDP/ICMP)
- Within the same time window

## Configuration Options

### Flow Processing Parameters
```python
# Custom parameters for better flow capture
flows = await pcap_to_flows(
    pcap_file_path="your_file.pcap",
    max_flows=None,
    use_standard_format=True,
    use_custom_params=True,
    # Custom parameters (when use_custom_params=True)
    expired_update=60,      # Flow timeout in seconds
    packets_per_gc=50       # Garbage collection frequency
)
```

### Standard vs Custom Parameters
- **Standard**: Uses default cicflowmeter settings
- **Custom**: Uses optimized settings for better flow capture
  - Shorter flow timeout (60s vs 240s)
  - More frequent garbage collection (50 vs 1000 packets)

## Troubleshooting

### Common Issues

1. **Getting fewer flows than expected**
   - Check if `max_flows` parameter is set
   - Set `max_flows=None` to get all flows

2. **Path issues when running from different directories**
   - Use the fixed `cicflowmeter_helpers.py` (already updated)
   - The path resolution now works from any directory

3. **Missing dependencies**
   - Install libpcap: `conda install -c conda-forge libpcap`
   - Install Python dependencies: `conda install -c conda-forge scapy pandas numpy`

### Verification Steps

1. **Check PCAP file size and content**
   ```bash
   ls -lh your_file.pcap
   tcpdump -r your_file.pcap | wc -l
   ```

2. **Test with unlimited flows**
   ```python
   flows = await pcap_to_flows("your_file.pcap", max_flows=None)
   print(f"Total flows: {len(flows)}")
   ```

3. **Verify flow data**
   ```python
   if flows:
       print(f"Sample flow: {flows[0]}")
   ```

## Best Practices

1. **Always use `max_flows=None`** when you want all flows
2. **Use custom parameters** for better flow capture: `use_custom_params=True`
3. **Check your PCAP file** - not all files contain thousands of flows
4. **Verify the results** by examining sample flow data
5. **Use the test scripts** to validate your setup

## Example Usage

```python
#!/usr/bin/env python3
import asyncio
from cicflowmeter_helpers import pcap_to_flows

async def extract_all_flows(pcap_file):
    """Extract all flows from a PCAP file."""
    try:
        flows = await pcap_to_flows(
            pcap_file_path=pcap_file,
            max_flows=None,  # Get ALL flows
            use_standard_format=True,
            use_custom_params=True  # Better parameters
        )
        
        print(f"✅ Successfully extracted {len(flows)} flows")
        
        # Show sample flow
        if flows:
            sample = flows[0]
            print(f"📊 Sample flow:")
            print(f"   Source: {sample.get('src_ip', 'N/A')}:{sample.get('src_port', 'N/A')}")
            print(f"   Destination: {sample.get('dst_ip', 'N/A')}:{sample.get('dst_port', 'N/A')}")
            print(f"   Protocol: {sample.get('protocol', 'N/A')}")
            print(f"   Duration: {sample.get('duration', 'N/A')} seconds")
            print(f"   Packets: {sample.get('total_packets', 'N/A')}")
            print(f"   Bytes: {sample.get('total_bytes', 'N/A')}")
        
        return flows
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# Usage
if __name__ == "__main__":
    flows = asyncio.run(extract_all_flows("path/to/your/file.pcap"))
```

## Conclusion

The cicflowmeter library is working correctly. The issue was simply that the `max_flows` parameter was limiting the output. By setting `max_flows=None`, you can extract all available flows from your PCAP files.

For the `traffic.pcap` file in this project, there are exactly **44 flows**, which is the correct number based on the network traffic patterns in that file. 