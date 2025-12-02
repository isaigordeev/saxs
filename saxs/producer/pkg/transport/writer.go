// Package transport provides I/O transport for SAXS data using MessagePack binary protocol.
package transport

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"hash/crc32"
	"io"

	"github.com/vmihailenco/msgpack/v5"
	"saxs/producer/internal/protocol"
	"saxs/producer/pkg/types"
)

// Writer writes SAXS protocol messages to an io.Writer.
type Writer struct {
	w           io.Writer
	compression protocol.CompressionType
}

// NewWriter creates a new SAXS protocol writer.
func NewWriter(w io.Writer) *Writer {
	return &Writer{
		w:           w,
		compression: protocol.NoCompression,
	}
}

// NewWriterWithCompression creates a new SAXS protocol writer with specified compression.
func NewWriterWithCompression(w io.Writer, compression protocol.CompressionType) *Writer {
	return &Writer{
		w:           w,
		compression: compression,
	}
}

// WriteCombined writes a combined SAXSSample + FlowMetadata message to the stream.
//
// The method:
// 1. Validates sample data
// 2. Serializes to MessagePack
// 3. Compresses if enabled
// 4. Builds protocol header
// 5. Computes CRC32 checksum
// 6. Writes header + payload + footer
//
// Returns the number of bytes written and any error encountered.
func (w *Writer) WriteCombined(sample *types.SAXSSample, flow *types.FlowMetadata) (int, error) {
	// Validate sample
	if err := sample.Validate(); err != nil {
		return 0, fmt.Errorf("invalid sample: %w", err)
	}

	// Serialize to MessagePack
	payload, err := w.serialize(sample, flow)
	if err != nil {
		return 0, fmt.Errorf("serialize: %w", err)
	}

	// Compress if enabled
	if w.compression != protocol.NoCompression {
		payload, err = compress(payload, w.compression)
		if err != nil {
			return 0, fmt.Errorf("compress: %w", err)
		}
	}

	// Build header
	header := w.buildHeader(payload)

	// Compute CRC
	crc := crc32.ChecksumIEEE(payload)
	footer := make([]byte, protocol.FooterSize)
	binary.LittleEndian.PutUint32(footer, crc)

	// Write all parts
	buf := bytes.NewBuffer(make([]byte, 0, len(header)+len(payload)+len(footer)))
	buf.Write(header)
	buf.Write(payload)
	buf.Write(footer)

	return w.w.Write(buf.Bytes())
}

// serialize serializes SAXSSample and FlowMetadata to MessagePack.
func (w *Writer) serialize(sample *types.SAXSSample, flow *types.FlowMetadata) ([]byte, error) {
	msg := types.CombinedMessage{
		Sample:       *sample,
		FlowMetadata: *flow,
	}

	data, err := msgpack.Marshal(msg)
	if err != nil {
		return nil, fmt.Errorf("msgpack marshal: %w", err)
	}

	return data, nil
}

// buildHeader builds the protocol header for the given payload.
func (w *Writer) buildHeader(payload []byte) []byte {
	header := make([]byte, protocol.HeaderSize)

	// Magic number (4 bytes)
	binary.LittleEndian.PutUint32(header[0:4], protocol.MagicNumber)

	// Protocol version (2 bytes)
	binary.LittleEndian.PutUint16(header[4:6], protocol.ProtocolVersion)

	// Message type (1 byte)
	header[6] = byte(protocol.CombinedType)

	// Compression type (1 byte)
	header[7] = byte(w.compression)

	// Payload length (8 bytes)
	binary.LittleEndian.PutUint64(header[8:16], uint64(len(payload)))

	return header
}

// compress compresses the payload based on compression type.
func compress(data []byte, compression protocol.CompressionType) ([]byte, error) {
	switch compression {
	case protocol.NoCompression:
		return data, nil
	case protocol.LZ4Compression:
		// TODO: Implement LZ4 compression
		// Use: github.com/pierrec/lz4/v4
		return nil, fmt.Errorf("LZ4 compression not implemented")
	case protocol.ZstdCompression:
		// TODO: Implement Zstd compression
		// Use: github.com/klauspost/compress/zstd
		return nil, fmt.Errorf("Zstd compression not implemented")
	default:
		return nil, fmt.Errorf("unsupported compression type: %v", compression)
	}
}