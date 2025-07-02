# High-Volume PCAP Processing with CICFlowMeter

This document explains the optimizations made to handle PCAP files with millions of packets efficiently.

## 🚀 Key Optimizations

### 1. Memory Management
- **Flow Memory Limit**: Maximum 50,000 flows kept in memory at once
- **Aggressive Garbage Collection**: Automatic cleanup when memory limit is reached
- **Python GC Integration**: Forces Python garbage collection when needed

### 2. Flow Expiration
- **Reduced Timeout**: 15 seconds (vs. default 120 seconds)
- **Shorter Duration Limit**: 180 seconds (vs. default 300 seconds)
- **Faster Cleanup**: More frequent flow expiration for high-volume scenarios

### 3. Garbage Collection Frequency
- **Less Frequent GC**: Every 5,000 packets (vs. default 50)
- **Performance Focus**: Reduces overhead of frequent cleanup operations
- **Smart Triggering**: Additional GC when memory limits are reached

### 4. Processing Optimizations
- **Streaming CSV Reading**: Processes large CSV files without loading everything into memory
- **Progress Indicators**: Shows progress every 10,000 flows for large files
- **Packet Counting**: Tracks total packets processed for performance monitoring

## 📊 Performance Comparison

| Parameter | Standard Mode | High-Volume Mode | Improvement |
|-----------|---------------|------------------|-------------|
| Flow Timeout | 120s | 15s | 8x faster expiration |
| GC Frequency | 50 packets | 5000 packets | 100x less overhead |
| Memory Limit | Unlimited | 50,000 flows | Controlled memory usage |
| Duration Limit | 300s | 180s | 1.7x faster cleanup |

## 🔧 Usage

### Basic High-Volume Processing

```python
from examples.cicflowmeter_helpers import pcap_to_flows

# Process with high-volume optimizations
flows = await pcap_to_flows(
    pcap_file_path="large_capture.pcap",
    high_volume=True  # Enable high-volume mode
)
```

### Custom High-Volume Parameters

```python
from examples.cicflowmeter_helpers import pcap_to_flows_high_volume

# Custom high-volume processing with specific parameters
flows = await pcap_to_flows_high_volume(
    pcap_file_path="large_capture.pcap",
    expired_update=10,  # Even more aggressive (10 seconds)
    packets_per_gc=10000,  # Less frequent GC
    max_flows_in_memory=25000,  # Lower memory footprint
    max_flows=1000000  # Limit total flows processed
)
```

### Command Line Example

```bash
# Run the high-volume example script
python examples/high_volume_example.py
```

## 🎯 Recommended Settings for Different Scenarios

### Small Files (< 1M packets)
```python
# Use standard mode
flows = await pcap_to_flows(pcap_file_path="small.pcap")
```

### Medium Files (1M - 10M packets)
```python
# Use high-volume mode with default settings
flows = await pcap_to_flows(pcap_file_path="medium.pcap", high_volume=True)
```

### Large Files (10M+ packets)
```python
# Use custom high-volume parameters
flows = await pcap_to_flows_high_volume(
    pcap_file_path="large.pcap",
    expired_update=10,
    packets_per_gc=10000,
    max_flows_in_memory=25000
)
```

### Memory-Constrained Systems
```python
# Use very conservative settings
flows = await pcap_to_flows_high_volume(
    pcap_file_path="large.pcap",
    expired_update=5,
    packets_per_gc=2000,
    max_flows_in_memory=10000
)
```

## 📈 Performance Monitoring

The high-volume mode includes built-in monitoring:

```
🚀 HIGH-VOLUME MODE: Processing PCAP file: large_capture.pcap
⚡ Optimized parameters:
   - expired_update: 15s (aggressive)
   - packets_per_gc: 5000 (performance optimized)
   - max_flows_in_memory: 50000 (memory efficient)
   - chunk_size: 1000000 packets

📈 Processed 5000000 packets
📊 Processed 10000 flows...
📊 Processed 20000 flows...
🎉 Successfully converted 25000 flows from PCAP file
```

## ⚠️ Important Notes

1. **Memory Usage**: High-volume mode uses more aggressive memory management but may still require significant RAM for very large files
2. **Flow Accuracy**: Faster expiration may miss some long-lived flows, but captures more short-lived flows
3. **Processing Speed**: Trade-off between memory usage and processing speed
4. **File Size**: For files > 1GB, consider processing in chunks

## 🔍 Troubleshooting

### Out of Memory Errors
- Reduce `max_flows_in_memory` parameter
- Increase `expired_update` to reduce flow creation rate
- Process file in smaller chunks

### Slow Processing
- Increase `packets_per_gc` to reduce garbage collection overhead
- Reduce `expired_update` for faster flow expiration
- Use SSD storage for better I/O performance

### Missing Flows
- Increase `expired_update` to capture longer-lived flows
- Increase `max_flows_in_memory` to keep more flows in memory
- Check if flows are being filtered by packet filters

## 📚 Additional Resources

- [CICFlowMeter Documentation](https://github.com/ahlashkari/CICFlowMeter)
- [Scapy Documentation](https://scapy.readthedocs.io/)
- [Python Memory Management](https://docs.python.org/3/library/gc.html) 