// Package protocol defines the binary protocol constants for SAXS data exchange.
package protocol

const (
	// MagicNumber is the protocol identifier "SAXS" in ASCII
	MagicNumber uint32 = 0x53415853

	// ProtocolVersion is the current protocol version
	ProtocolVersion uint16 = 0x0001

	// Size constants
	HeaderSize = 16
	FooterSize = 4
)

// MessageType represents the type of message being transmitted
type MessageType byte

const (
	// SAXSSampleType indicates a SAXSSample message
	SAXSSampleType MessageType = 0x01

	// FlowMetadataType indicates a FlowMetadata message
	FlowMetadataType MessageType = 0x02

	// StageRequestType indicates a StageRequest message
	StageRequestType MessageType = 0x03

	// CombinedType indicates a combined SAXSSample + FlowMetadata message
	CombinedType MessageType = 0x04
)

// CompressionType represents the compression algorithm used
type CompressionType byte

const (
	// NoCompression indicates no compression
	NoCompression CompressionType = 0x00

	// LZ4Compression indicates LZ4 compression
	LZ4Compression CompressionType = 0x01

	// ZstdCompression indicates Zstandard compression
	ZstdCompression CompressionType = 0x02
)

// String returns the string representation of MessageType
func (m MessageType) String() string {
	switch m {
	case SAXSSampleType:
		return "SAXSSample"
	case FlowMetadataType:
		return "FlowMetadata"
	case StageRequestType:
		return "StageRequest"
	case CombinedType:
		return "Combined"
	default:
		return "Unknown"
	}
}

// String returns the string representation of CompressionType
func (c CompressionType) String() string {
	switch c {
	case NoCompression:
		return "None"
	case LZ4Compression:
		return "LZ4"
	case ZstdCompression:
		return "Zstd"
	default:
		return "Unknown"
	}
}