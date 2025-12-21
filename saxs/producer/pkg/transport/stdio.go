package transport

import (
	"context"
	"errors"
	"io"
	"os"
)

type Transport interface {
	Connect(ctx context.Context) (Connection, error)
}

type StdioTransport struct{}

type Connection interface {
	Read()
	Write()
	Close() error
}

type nopCloserWriter struct {
	io.Writer
}

func (nopCloserWriter) Close() error {
	return nil
}

type ioConn struct {
	protocolVersion string // protocol version for SAXS streams

	rwc io.ReadWriteCloser // stream for data

	incoming <-chan msgOrErr
}

type msgOrErr struct {
}

func newIOConn(rwc io.ReadWriteCloser) *ioConn {
	return &ioConn{}
}

func (c *ioConn) Close() error {
	return nil
}
func (c *ioConn) Write() {
}

func (c *ioConn) Read() {
}

type rwc struct {
	rc io.ReadCloser
	wc io.WriteCloser
}

func (r rwc) Read(p []byte) (n int, err error) {
	return r.rc.Read(p)
}

func (r rwc) Write(p []byte) (n int, err error) {
	return r.wc.Write(p)
}

func (r rwc) Close() error {
	rcErr := r.rc.Close()

	var wcErr error
	if r.wc != nil { // we only allow a nil writer in unit tests
		wcErr = r.wc.Close()
	}

	return errors.Join(rcErr, wcErr)
}

// Connect implements the [Transport] interface.
func (*StdioTransport) Connect(context.Context) (Connection, error) {
	return newIOConn(rwc{os.Stdin, nopCloserWriter{os.Stdout}}), nil
}
