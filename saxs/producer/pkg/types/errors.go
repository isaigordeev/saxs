// Package types defines errors for SAXS data processing.
package types

import "errors"

var (
	// ErrEmptyQValues indicates q_values array is empty
	ErrEmptyQValues = errors.New("q_values array is empty")

	// ErrEmptyIntensity indicates intensity array is empty
	ErrEmptyIntensity = errors.New("intensity array is empty")

	// ErrLengthMismatch indicates array length mismatch
	ErrLengthMismatch = errors.New("array lengths do not match")

	// ErrShapeMismatch indicates shape field doesn't match data length
	ErrShapeMismatch = errors.New("shape field does not match data length")

	// ErrInvalidMagicNumber indicates invalid protocol magic number
	ErrInvalidMagicNumber = errors.New("invalid magic number in protocol header")

	// ErrUnsupportedVersion indicates unsupported protocol version
	ErrUnsupportedVersion = errors.New("unsupported protocol version")

	// ErrUnsupportedMessageType indicates unsupported message type
	ErrUnsupportedMessageType = errors.New("unsupported message type")

	// ErrCRCMismatch indicates CRC checksum mismatch
	ErrCRCMismatch = errors.New("CRC checksum mismatch")

	// ErrIncompleteRead indicates incomplete data read
	ErrIncompleteRead = errors.New("incomplete data read from stream")
)