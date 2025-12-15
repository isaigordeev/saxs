package transport

import (
	"context"
	"io"
	"os"
)

type StdioTransport struct{}

type Connection interface {
	Read()
	Write()
	Close() error
}

type ioConn struct{}

func newIOConn(rwc io.ReadWriteCloser) *ioConn

func (c *ioConn) Close() error {
	return nil
}
func (c *ioConn) Write() {
	return
}

func (c *ioConn) Read() {
	return
}

// Connect implements the [Transport] interface.
func (*StdioTransport) Connect(context.Context) (Connection, error) {
	return newIOConn(rwc{os.Stdin, nopCloserWriter{os.Stdout}}), nil
}
