// Package types defines the data structures for SAXS processing.
package types

// SAXSSample represents a Small-Angle X-ray Scattering sample with
// q-values (scattering vector), intensity measurements, and associated metadata.

type SAXSSample struct {
	ID  string
	Q   []float64
	I   []float64
	Err []float64
}

// FlowMetadata represents inter-stage metadata that flows through the pipeline.
type FlowMetadata struct {
	Sample           string          `msgpack:"sample"`
	ProcessedPeaks   map[int]float64 `msgpack:"processed_peaks"`
	UnprocessedPeaks map[int]float64 `msgpack:"unprocessed_peaks"`
	Current          map[int]float64 `msgpack:"current"`
}

// CombinedMessage contains both sample data and flow metadata.
type CombinedMessage struct {
	Sample       SAXSSample   `msgpack:"sample"`
	FlowMetadata FlowMetadata `msgpack:"flow_metadata"`
}

// Validate checks if the SAXSSample data is valid.
func (s *SAXSSample) Validate() error {
	if len(s.Q) == 0 {
		return ErrEmptyQValues
	}
	if len(s.I) == 0 {
		return ErrEmptyIntensity
	}
	if len(s.Q) != len(s.I) {
		return ErrLengthMismatch
	}
	if len(s.Err) > 0 && len(s.Err) != len(s.Q) {
		return ErrLengthMismatch
	}
	return nil
}

// Len returns the number of data points in the sample.
func (s *SAXSSample) Len() int {
	return len(s.Q)
}

// HasErrors returns true if the sample has intensity error data.
func (s *SAXSSample) HasErrors() bool {
	return len(s.I) > 0
}
