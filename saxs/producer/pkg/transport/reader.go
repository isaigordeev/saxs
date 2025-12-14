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

// Iterator streams SAXS messages from an io.Reader sample by sample.
type Iterator struct {
	r      io.Reader
	sample *types.SAXSSample
	flow   *types.FlowMetadata
	err    error
}

// NewIterator creates a new streaming SAXS iterator.
func NewIterator(r io.Reader) *Iterator {
	return &Iterator{r: r}
}

// Next reads the next sample + flow metadata.
// Returns false on EOF or any read/deserialization error.
func (it *Iterator) Next() bool {
	if it.err != nil {
		return false
	}

	hdr, err := it.readHeader()
	if err != nil {
		if err == io.EOF {
			return false
		}
		it.err = fmt.Errorf("read header: %w", err)
		return false
	}

	if err := it.validateHeader(hdr); err != nil {
		it.err = err
		return false
	}

	payload, err := it.readPayload(hdr.payloadLen)
	if err != nil {
		it.err = fmt.Errorf("read payload: %w", err)
		return false
	}

	if err := it.validateCRC(payload); err != nil {
		it.err = err
		return false
	}

	if hdr.compression != protocol.NoCompression {
		payload, err = decompress(payload, hdr.compression)
		if err != nil {
			it.err = fmt.Errorf("decompress: %w", err)
			return false
		}
	}

	msg, err := it.deserialize(payload)
	if err != nil {
		it.err = fmt.Errorf("deserialize: %w", err)
		return false
	}

	if err := msg.Sample.Validate(); err != nil {
		it.err = fmt.Errorf("invalid sample: %w", err)
		return false
	}

	it.sample = &msg.Sample
	it.flow = &msg.FlowMetadata
	return true
}

// Sample returns the last successfully read SAXSSample.
func (it *Iterator) Sample() *types.SAXSSample { return it.sample }

// Metadata returns the last successfully read FlowMetadata.
func (it *Iterator) Metadata() *types.FlowMetadata { return it.flow }

// Err returns the first error encountered while iterating.
func (it *Iterator) Err() error { return it.err }

// --- internal helpers ---

func (it *Iterator) readHeader() (*header, error) {
	buf := make([]byte, protocol.HeaderSize)
	if _, err := io.ReadFull(it.r, buf); err != nil {
		return nil, err
	}
	return &header{
		magic:       binary.LittleEndian.Uint32(buf[0:4]),
		version:     binary.LittleEndian.Uint16(buf[4:6]),
		msgType:     protocol.MessageType(buf[6]),
		compression: protocol.CompressionType(buf[7]),
		payloadLen:  binary.LittleEndian.Uint64(buf[8:16]),
	}, nil
}

func (it *Iterator) validateHeader(h *header) error {
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

func (it *Iterator) readPayload(length uint64) ([]byte, error) {
	payload := make([]byte, length)
	_, err := io.ReadFull(it.r, payload)
	return payload, err
}

func (it *Iterator) validateCRC(payload []byte) error {
	footer := make([]byte, protocol.FooterSize)
	if _, err := io.ReadFull(it.r, footer); err != nil {
		return err
	}

	expected := binary.LittleEndian.Uint32(footer)
	actual := crc32.ChecksumIEEE(payload)
	if actual != expected {
		return fmt.Errorf("%w: got %#x, want %#x", types.ErrCRCMismatch, actual, expected)
	}
	return nil
}

func (it *Iterator) deserialize(payload []byte) (*types.CombinedMessage, error) {
	var msg types.CombinedMessage
	if err := msgpack.Unmarshal(payload, &msg); err != nil {
		return nil, err
	}
	return &msg, nil
}

func decompress(data []byte, c protocol.CompressionType) ([]byte, error) {
	switch c {
	case protocol.NoCompression:
		return data, nil
	case protocol.LZ4Compression:
		return nil, fmt.Errorf("LZ4 decompression not implemented")
	case protocol.ZstdCompression:
		return nil, fmt.Errorf("Zstd decompression not implemented")
	default:
		return nil, fmt.Errorf("unsupported compression type: %v", c)
	}
}

// header internal struct
type header struct {
	magic       uint32
	version     uint16
	msgType     protocol.MessageType
	compression protocol.CompressionType
	payloadLen  uint64
}
