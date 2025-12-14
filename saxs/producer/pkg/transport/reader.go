// Package transport provides I/O transport for SAXS data using MessagePack binary protocol.
package transport

import (
	"encoding/binary"
	"fmt"
	"hash/crc32"
	"io"

	"saxs/producer/internal/protocol"
	"saxs/producer/pkg/types"

	"github.com/vmihailenco/msgpack/v5"
)

// Reader reads SAXS protocol messages from an io.Reader.
type Reader struct {
	r io.Reader
}

// NewReader creates a new SAXS protocol reader.
func NewReader(r io.Reader) *Reader {
	return &Reader{r: r}
}

// ReadCombined reads a combined SAXSSample + FlowMetadata message from the stream.
//
// The method:
// 1. Reads and validates the protocol header
// 2. Reads the payload
// 3. Validates CRC32 checksum
// 4. Decompresses if needed
// 5. Deserializes MessagePack data
//
// Returns the sample, flow metadata, and any error encountered.
func (r *Reader) ReadCombined() (*types.SAXSSample, *types.FlowMetadata, error) {
	// Read header
	header, err := r.readHeader()
	if err != nil {
		return nil, nil, fmt.Errorf("read header: %w", err)
	}

	// Validate header
	if err := r.validateHeader(header); err != nil {
		return nil, nil, err
	}

	// Read payload
	payload, err := r.readPayload(header.payloadLen)
	if err != nil {
		return nil, nil, fmt.Errorf("read payload: %w", err)
	}

	// Read and validate CRC
	if err := r.validateCRC(payload); err != nil {
		return nil, nil, err
	}

	// Decompress if needed
	if header.compression != protocol.NoCompression {
		payload, err = decompress(payload, header.compression)
		if err != nil {
			return nil, nil, fmt.Errorf("decompress: %w", err)
		}
	}

	// Deserialize
	msg, err := r.deserialize(payload)
	if err != nil {
		return nil, nil, fmt.Errorf("deserialize: %w", err)
	}

	// Validate sample data
	if err := msg.Sample.Validate(); err != nil {
		return nil, nil, fmt.Errorf("invalid sample: %w", err)
	}

	return &msg.Sample, &msg.FlowMetadata, nil
}

// header represents the parsed protocol header.
type header struct {
	magic       uint32
	version     uint16
	msgType     protocol.MessageType
	compression protocol.CompressionType
	payloadLen  uint64
}

// readHeader reads and parses the protocol header.
func (r *Reader) readHeader() (*header, error) {
	buf := make([]byte, protocol.HeaderSize)
	if _, err := io.ReadFull(r.r, buf); err != nil {
		if err == io.EOF {
			return nil, io.EOF
		}
		return nil, fmt.Errorf("%w: %v", types.ErrIncompleteRead, err)
	}

	h := &header{
		magic:       binary.LittleEndian.Uint32(buf[0:4]),
		version:     binary.LittleEndian.Uint16(buf[4:6]),
		msgType:     protocol.MessageType(buf[6]),
		compression: protocol.CompressionType(buf[7]),
		payloadLen:  binary.LittleEndian.Uint64(buf[8:16]),
	}

	return h, nil
}

// validateHeader validates the protocol header fields.
func (r *Reader) validateHeader(h *header) error {
	if h.magic != protocol.MagicNumber {
		return fmt.Errorf("%w: got %#x, want %#x",
			types.ErrInvalidMagicNumber, h.magic, protocol.MagicNumber)
	}

	if h.version != protocol.ProtocolVersion {
		return fmt.Errorf("%w: got %#x, want %#x",
			types.ErrUnsupportedVersion, h.version, protocol.ProtocolVersion)
	}

	if h.msgType != protocol.CombinedType {
		return fmt.Errorf("%w: got %s, want %s",
			types.ErrUnsupportedMessageType, h.msgType, protocol.CombinedType)
	}

	return nil
}

// readPayload reads the payload data.
func (r *Reader) readPayload(length uint64) ([]byte, error) {
	payload := make([]byte, length)
	if _, err := io.ReadFull(r.r, payload); err != nil {
		return nil, fmt.Errorf("%w: %v", types.ErrIncompleteRead, err)
	}
	return payload, nil
}

// validateCRC reads the footer and validates CRC32 checksum.
func (r *Reader) validateCRC(payload []byte) error {
	footer := make([]byte, protocol.FooterSize)
	if _, err := io.ReadFull(r.r, footer); err != nil {
		return fmt.Errorf("%w: %v", types.ErrIncompleteRead, err)
	}

	expectedCRC := binary.LittleEndian.Uint32(footer)
	actualCRC := crc32.ChecksumIEEE(payload)

	if actualCRC != expectedCRC {
		return fmt.Errorf("%w: got %#x, want %#x",
			types.ErrCRCMismatch, actualCRC, expectedCRC)
	}

	return nil
}

// deserialize deserializes MessagePack payload into CombinedMessage.
func (r *Reader) deserialize(payload []byte) (*types.CombinedMessage, error) {
	var msg types.CombinedMessage
	if err := msgpack.Unmarshal(payload, &msg); err != nil {
		return nil, fmt.Errorf("msgpack unmarshal: %w", err)
	}
	return &msg, nil
}

// decompress decompresses the payload based on compression type.
func decompress(data []byte, compression protocol.CompressionType) ([]byte, error) {
	switch compression {
	case protocol.NoCompression:
		return data, nil
	case protocol.LZ4Compression:
		// TODO: Implement LZ4 decompression
		// Use: github.com/pierrec/lz4/v4
		return nil, fmt.Errorf("LZ4 decompression not implemented")
	case protocol.ZstdCompression:
		// TODO: Implement Zstd decompression
		// Use: github.com/klauspost/compress/zstd
		return nil, fmt.Errorf("Zstd decompression not implemented")
	default:
		return nil, fmt.Errorf("unsupported compression type: %v", compression)
	}
}
