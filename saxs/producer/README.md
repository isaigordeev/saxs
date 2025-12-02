# SAXS Producer (Go)

High-performance Go implementation for SAXS (Small-Angle X-ray Scattering) data processing with Python interoperability via binary I/O streams.

## Architecture

```
saxs/producer/
├── cmd/
│   └── saxs-process/          # Command-line binary for Python integration
├── pkg/
│   ├── transport/             # I/O transport layer (Reader/Writer)
│   ├── types/                 # Data structures and validation
│   └── peakfit/              # Peak fitting algorithms (TODO)
├── internal/
│   └── protocol/             # Binary protocol constants
├── go.mod
└── README.md
```

## Protocol

The transport layer uses a binary protocol for efficient Python ↔ Go communication:

### Message Format

```
┌─────────────────────────────────────────────────────────────┐
│                      Protocol Message                       │
└─────────────────────────────────────────────────────────────┘

[Header: 16 bytes]
├─ Magic Number    (4 bytes): 0x53415853 ("SAXS")
├─ Version         (2 bytes): 0x0001
├─ Message Type    (1 byte):  0x01 = SAXSSample
│                             0x02 = FlowMetadata
│                             0x03 = StageRequest
│                             0x04 = Combined (Sample + Flow)
├─ Compression     (1 byte):  0x00 = None, 0x01 = LZ4, 0x02 = Zstd
├─ Payload Length  (8 bytes): uint64 (little-endian)

[Payload: Variable length]
├─ MessagePack serialized data

[Footer: 4 bytes]
└─ CRC32 Checksum  (4 bytes): IEEE polynomial
```

## Usage

### As Library

```go
package main

import (
    "os"
    "saxs/producer/pkg/transport"
    "saxs/producer/pkg/types"
)

func main() {
    // Read from stdin
    reader := transport.NewReader(os.Stdin)
    sample, flow, err := reader.ReadCombined()
    if err != nil {
        panic(err)
    }

    // Process data
    // ... your processing logic ...

    // Write to stdout
    writer := transport.NewWriter(os.Stdout)
    if _, err := writer.WriteCombined(sample, flow); err != nil {
        panic(err)
    }
}
```

### From Python

```python
import io
import subprocess
from saxs.saxs.core.transport.io_transport import SAXSWriter, SAXSReader

# Prepare data
input_stream = io.BytesIO()
writer = SAXSWriter(input_stream)
writer.write_sample(sample, flow_metadata)

# Call Go binary
process = subprocess.Popen(
    ['./saxs-process', 'command'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE
)

stdout, _ = process.communicate(input=input_stream.getvalue())

# Read result
output_stream = io.BytesIO(stdout)
reader = SAXSReader(output_stream)
result_sample, result_flow = reader.read_sample()
```

## Building

```bash
# Install dependencies
go mod download

# Run tests
go test ./...

# Build binary
go build -o bin/saxs-process ./cmd/saxs-process

# Run tests with coverage
go test -cover ./pkg/...
```

## Dependencies

- `github.com/vmihailenco/msgpack/v5` - MessagePack serialization
- `gonum.org/v1/gonum` - Numerical computing (for future peak fitting)

## Module Structure

### `pkg/transport`

Provides `Reader` and `Writer` for binary I/O:

- **Reader**: Reads protocol messages from `io.Reader`
  - `ReadCombined()` - Read SAXSSample + FlowMetadata
  - Validates magic number, version, CRC32
  - Supports decompression (TODO: LZ4/Zstd)

- **Writer**: Writes protocol messages to `io.Writer`
  - `WriteCombined()` - Write SAXSSample + FlowMetadata
  - Automatic CRC32 computation
  - Supports compression (TODO: LZ4/Zstd)

### `pkg/types`

Data structures matching Python SAXS types:

- **SAXSSample**: Q-values, intensity, errors, metadata
  - `Validate()` - Data validation
  - `Len()` - Number of data points
  - `HasErrors()` - Check if error data present

- **FlowMetadata**: Inter-stage pipeline metadata
- **CombinedMessage**: Sample + Flow wrapper

### `internal/protocol`

Protocol constants and types (not exported):

- Magic number, version, sizes
- MessageType enum (SAXSSample, FlowMetadata, Combined, etc.)
- CompressionType enum (None, LZ4, Zstd)

## Performance

Expected performance characteristics:

- **Serialization**: ~50 μs per message (500-point sample)
- **Deserialization**: ~60 μs per message
- **CRC32 validation**: < 5 μs
- **Total overhead**: < 150 μs (0.15 ms)

For typical SAXS processing (1-5 seconds), protocol overhead is < 0.01%.

## Testing

```bash
# Unit tests
go test ./pkg/transport -v

# Benchmarks
go test -bench=. ./pkg/transport

# With race detector
go test -race ./...
```

### Test Coverage

- Protocol header validation
- CRC32 checksum validation
- Invalid magic number handling
- Array length validation
- Round-trip serialization

## TODO

- [ ] Implement LZ4 compression/decompression
- [ ] Implement Zstd compression/decompression
- [ ] Add parallel peak fitting (pkg/peakfit)
- [ ] Add benchmarks
- [ ] Command-line binary (cmd/saxs-process)
- [ ] Integration tests with Python

## Design Decisions

### Why MessagePack?

- **Binary format**: 5-10x smaller than JSON
- **Fast**: Serialization faster than JSON
- **Type preserving**: Handles floats, ints, bytes correctly
- **Wide support**: Both Python and Go libraries

### Why CRC32?

- **Fast**: < 5 μs for typical payloads
- **Sufficient**: Detects transmission errors
- **Standard**: IEEE polynomial widely used

### Why Not Protocol Buffers?

- **Simplicity**: MessagePack easier to debug (human-readable with tools)
- **Dynamic**: No .proto files to maintain
- **Flexibility**: Python dicts map naturally to MessagePack

## License

MIT