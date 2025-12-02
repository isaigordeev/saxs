// Package types defines the data structures for SAXS processing.
package types

// SAXSSample represents a Small-Angle X-ray Scattering sample with
// q-values (scattering vector), intensity measurements, and associated metadata.
type SAXSSample struct {
	QValues      []float64              `msgpack:"q_values"`
	Intensity    []float64              `msgpack:"intensity"`
	IntensityErr []float64              `msgpack:"intensity_err"`
	Metadata     map[string]interface{} `msgpack:"metadata"`
	Shape        int                    `msgpack:"shape"`
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
	if len(s.QValues) == 0 {
		return ErrEmptyQValues
	}
	if len(s.Intensity) == 0 {
		return ErrEmptyIntensity
	}
	if len(s.QValues) != len(s.Intensity) {
		return ErrLengthMismatch
	}
	if len(s.IntensityErr) > 0 && len(s.IntensityErr) != len(s.QValues) {
		return ErrLengthMismatch
	}
	if s.Shape > 0 && s.Shape != len(s.QValues) {
		return ErrShapeMismatch
	}
	return nil
}

// Len returns the number of data points in the sample.
func (s *SAXSSample) Len() int {
	return len(s.QValues)
}

// HasErrors returns true if the sample has intensity error data.
func (s *SAXSSample) HasErrors() bool {
	return len(s.IntensityErr) > 0
}
