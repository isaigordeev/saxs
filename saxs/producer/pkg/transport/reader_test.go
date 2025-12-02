package transport

import (
	"bytes"
	"encoding/binary"
	"testing"

	"saxs/producer/internal/protocol"
	"saxs/producer/pkg/types"

	"github.com/vmihailenco/msgpack/v5"
)

func TestReader_ReadCombined(t *testing.T) {
	tests := []struct {
		name        string
		sample      *types.SAXSSample
		flow        *types.FlowMetadata
		wantErr     bool
		errContains string
	}{
		{
			name: "valid message",
			sample: &types.SAXSSample{
				QValues:      []float64{0.1, 0.2, 0.3},
				Intensity:    []float64{100.0, 150.0, 120.0},
				IntensityErr: []float64{5.0, 7.0, 6.0},
				Metadata:     map[string]any{"experiment": "test-001"},
				Shape:        3,
			},
			flow: &types.FlowMetadata{
				Sample:           "test_sample",
				ProcessedPeaks:   map[int]float64{},
				UnprocessedPeaks: map[int]float64{1: 100.0},
				Current:          map[int]float64{},
			},
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Create a valid protocol message
			buf := createProtocolMessage(t, tt.sample, tt.flow)

			// Read the message
			reader := NewReader(buf)
			sample, flow, err := reader.ReadCombined()

			if tt.wantErr {
				if err == nil {
					t.Fatalf("expected error containing %q, got nil", tt.errContains)
				}
				if tt.errContains != "" &&
					!contains(err.Error(), tt.errContains) {
					t.Fatalf("expected error containing %q, got %q", tt.errContains, err.Error())
				}
				return
			}

			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}

			// Validate sample
			if len(sample.QValues) != len(tt.sample.QValues) {
				t.Errorf("QValues length = %d, want %d", len(sample.QValues), len(tt.sample.QValues))
			}
			if len(sample.Intensity) != len(tt.sample.Intensity) {
				t.Errorf("Intensity length = %d, want %d", len(sample.Intensity), len(tt.sample.Intensity))
			}

			// Validate flow
			if flow.Sample != tt.flow.Sample {
				t.Errorf("Sample = %q, want %q", flow.Sample, tt.flow.Sample)
			}
		})
	}
}

func TestReader_InvalidMagicNumber(t *testing.T) {
	buf := new(bytes.Buffer)

	// Write invalid magic number
	binary.Write(buf, binary.LittleEndian, uint32(0xDEADBEEF))
	binary.Write(buf, binary.LittleEndian, protocol.ProtocolVersion)
	buf.WriteByte(byte(protocol.CombinedType))
	buf.WriteByte(byte(protocol.NoCompression))
	binary.Write(buf, binary.LittleEndian, uint64(0))

	reader := NewReader(buf)
	_, _, err := reader.ReadCombined()

	if err == nil {
		t.Fatal("expected error for invalid magic number")
	}

	if !contains(err.Error(), "invalid magic number") {
		t.Errorf("expected 'invalid magic number' error, got: %v", err)
	}
}

func TestReader_CRCMismatch(t *testing.T) {
	sample := &types.SAXSSample{
		QValues:   []float64{0.1},
		Intensity: []float64{100.0},
		Shape:     1,
	}
	flow := &types.FlowMetadata{Sample: "test"}

	// Serialize
	msg := types.CombinedMessage{Sample: *sample, FlowMetadata: *flow}
	payload, err := msgpack.Marshal(msg)
	if err != nil {
		t.Fatalf("marshal failed: %v", err)
	}

	buf := new(bytes.Buffer)

	// Write header
	header := make([]byte, protocol.HeaderSize)
	binary.LittleEndian.PutUint32(header[0:4], protocol.MagicNumber)
	binary.LittleEndian.PutUint16(header[4:6], protocol.ProtocolVersion)
	header[6] = byte(protocol.CombinedType)
	header[7] = byte(protocol.NoCompression)
	binary.LittleEndian.PutUint64(header[8:16], uint64(len(payload)))
	buf.Write(header)

	// Write payload
	buf.Write(payload)

	// Write WRONG CRC
	footer := make([]byte, 4)
	binary.LittleEndian.PutUint32(footer, uint32(0xBADBAD))
	buf.Write(footer)

	reader := NewReader(buf)
	_, _, err = reader.ReadCombined()

	if err == nil {
		t.Fatal("expected CRC mismatch error")
	}

	if !contains(err.Error(), "CRC checksum mismatch") {
		t.Errorf("expected 'CRC checksum mismatch' error, got: %v", err)
	}
}

// Helper function to create a valid protocol message
func createProtocolMessage(t *testing.T, sample *types.SAXSSample, flow *types.FlowMetadata) *bytes.Buffer {
	t.Helper()

	buf := new(bytes.Buffer)
	writer := NewWriter(buf)

	// For invalid samples, writer will fail - return empty buffer
	// This causes reader to get EOF, which is expected behavior
	_, _ = writer.WriteCombined(sample, flow)

	return buf
}

// Helper to check if string contains substring
func contains(s, substr string) bool {
	return len(s) >= len(substr) && (s == substr || len(substr) == 0 ||
		(len(s) > 0 && len(substr) > 0 && findSubstring(s, substr)))
}

func findSubstring(s, substr string) bool {
	for i := 0; i <= len(s)-len(substr); i++ {
		if s[i:i+len(substr)] == substr {
			return true
		}
	}
	return false
}
