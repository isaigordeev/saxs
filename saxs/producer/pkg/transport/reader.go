package transport

import (
	"saxs/producer/pkg/types"
)

type ChannelIterator struct {
	ch     <-chan types.SAXSSample
	curr   *types.SAXSSample
	err    error
	closed bool
}

// NewChannelIterator creates a new streaming SAXS iterator.
func NewChannelIterator(ch <-chan types.SAXSSample) *ChannelIterator {
	return &ChannelIterator{ch: ch}
}

// Next reads the next sample + flow metadata.
// Returns false on EOF or any read/deserialization error.
func (it *ChannelIterator) Next() bool {
	if it.closed || it.err != nil {
		return false
	}

	sample, open := <-it.ch

	if !open {
		it.closed = true
		return false
	}

	it.curr = &sample
	return true
}

func (it *ChannelIterator) Sample() *types.SAXSSample { return it.curr }

// Err returns the first error encountered (optional).
func (it *ChannelIterator) Err() error { return it.err }
