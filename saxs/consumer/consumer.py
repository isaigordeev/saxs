"""Python consumer for Go SAXS stream producer via duplex pipes."""

from __future__ import annotations

import struct
import subprocess
import zlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import msgpack

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from types import TracebackType


# Protocol constants (must match Go producer/internal/protocol/constants.go)
MAGIC_NUMBER = 0x53415853  # "SAXS"
PROTOCOL_VERSION = 0x0001
HEADER_SIZE = 16
FOOTER_SIZE = 4

# Message types
MSG_TYPE_SAMPLE = 0x01
MSG_TYPE_FLOW_METADATA = 0x02
MSG_TYPE_STAGE_REQUEST = 0x03
MSG_TYPE_COMBINED = 0x04

# Compression types
COMPRESSION_NONE = 0x00
COMPRESSION_LZ4 = 0x01
COMPRESSION_ZSTD = 0x02


@dataclass
class SAXSSample:
    """SAXS sample data from Go stream."""

    id: str
    q: list[float] = field(default_factory=list)
    intensity: list[float] = field(default_factory=list)
    error: list[float] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.q)


@dataclass
class FlowMetadata:
    """Flow metadata from Go stream."""

    sample: str = ""
    processed_peaks: dict[int, float] = field(default_factory=dict)
    unprocessed_peaks: dict[int, float] = field(default_factory=dict)
    current: dict[int, float] = field(default_factory=dict)


@dataclass
class Message:
    """Parsed message from the stream."""

    msg_type: int
    version: int
    compression: int
    sample: SAXSSample | None = None
    flow_metadata: FlowMetadata | None = None
    raw_payload: bytes = b""


class SampleHandler(ABC):
    """Abstract base class for sample handlers."""

    @abstractmethod
    def on_sample(self, sample: SAXSSample, metadata: FlowMetadata) -> None:
        """Called when a sample is received."""

    def on_error(self, error: Exception) -> None:
        """Called when an error occurs. Override for custom error handling."""

    def on_complete(self) -> None:
        """Called when the stream completes."""


class GoStreamConsumer:
    """Consumer for Go SAXS stream producer via duplex stdio pipes.

    The consumer spawns a Go binary that reads from a database and streams
    SAXS samples via stdout using a binary protocol. Commands can be sent
    to the Go process via stdin.

    Protocol format:
        Header (16 bytes):
            - Magic number: 4 bytes (0x53415853 = "SAXS")
            - Protocol version: 2 bytes
            - Message type: 1 byte
            - Compression type: 1 byte
            - Payload length: 8 bytes
        Payload: MessagePack-encoded data
        Footer: 4 bytes (CRC32 checksum)

    Usage
    -----
    >>> consumer = GoStreamConsumer(binary_path="./dbreader")
    >>> with consumer:
    ...     for sample, meta in consumer.consume():
    ...         process(sample)

    Or with a handler:

    >>> class MyHandler(SampleHandler):
    ...     def on_sample(self, sample, meta):
    ...         print(f"Got sample: {sample.id}")
    ...
    >>> consumer = GoStreamConsumer(binary_path="./dbreader")
    >>> consumer.run(MyHandler())

    """

    def __init__(
        self,
        binary_path: str | Path = "./dbreader",
        database_url: str | None = None,
        verify_crc: bool = True,
    ) -> None:
        self.binary_path = Path(binary_path)
        self.database_url = database_url
        self.verify_crc = verify_crc
        self._proc: subprocess.Popen[bytes] | None = None

    def __enter__(self) -> GoStreamConsumer:
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.stop()

    def start(self) -> None:
        """Start the Go producer process."""
        import os

        env = dict(os.environ)
        if self.database_url:
            env["DATABASE_URL"] = self.database_url

        self._proc = subprocess.Popen(
            [str(self.binary_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )

    def stop(self) -> None:
        """Stop the Go producer process gracefully."""
        if self._proc:
            # Try graceful shutdown first
            if self._proc.stdin:
                try:
                    self._proc.stdin.close()
                except OSError:
                    pass

            try:
                self._proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self._proc.terminate()
                try:
                    self._proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self._proc.kill()
                    self._proc.wait()

            self._proc = None

    def send_command(self, command: dict) -> None:
        """Send a command to the Go process via stdin.

        Commands are length-prefixed MessagePack messages.
        """
        if not self._proc or not self._proc.stdin:
            msg = "Process not started"
            raise RuntimeError(msg)

        data = msgpack.packb(command)
        # Write length-prefixed message (4-byte little-endian length)
        self._proc.stdin.write(struct.pack("<I", len(data)))
        self._proc.stdin.write(data)
        self._proc.stdin.flush()

    def consume(self) -> Iterator[tuple[SAXSSample, FlowMetadata]]:
        """Consume SAXS samples from Go producer.

        Yields
        ------
        tuple[SAXSSample, FlowMetadata]
            Sample data and flow metadata for each record.

        Raises
        ------
        RuntimeError
            If process not started or protocol error occurs.
        ProtocolError
            If message format is invalid.

        """
        if not self._proc or not self._proc.stdout:
            msg = "Process not started"
            raise RuntimeError(msg)

        for msg in self._read_messages():
            if msg.sample and msg.flow_metadata:
                yield msg.sample, msg.flow_metadata
            elif msg.sample:
                yield msg.sample, FlowMetadata()

    def run(self, handler: SampleHandler) -> None:
        """Run the consumer with a handler.

        This method starts the process, consumes all samples,
        and calls the handler for each sample.

        Parameters
        ----------
        handler
            Handler to process samples.

        """
        try:
            self.start()
            for sample, meta in self.consume():
                try:
                    handler.on_sample(sample, meta)
                except Exception as e:
                    handler.on_error(e)
            handler.on_complete()
        finally:
            self.stop()

    def _read_messages(self) -> Iterator[Message]:
        """Read and parse messages from the Go producer."""
        stdout = self._proc.stdout

        while True:
            # Read header
            header = self._read_exact(stdout, HEADER_SIZE)
            if not header:
                break  # EOF

            # Parse header
            magic, version, msg_type, compression, payload_len = struct.unpack(
                "<IHBBQ",
                header,
            )

            if magic != MAGIC_NUMBER:
                raise ProtocolError(
                    f"Invalid magic number: {magic:#x}, expected {MAGIC_NUMBER:#x}"
                )

            if version != PROTOCOL_VERSION:
                raise ProtocolError(
                    f"Unsupported protocol version: {version:#x}"
                )

            # Read payload
            payload = self._read_exact(stdout, payload_len)
            if len(payload) < payload_len:
                raise ProtocolError(
                    f"Incomplete payload: {len(payload)}/{payload_len}"
                )

            # Read footer (CRC32)
            footer = self._read_exact(stdout, FOOTER_SIZE)
            if len(footer) < FOOTER_SIZE:
                raise ProtocolError("Incomplete footer")

            # Verify CRC if enabled
            if self.verify_crc:
                expected_crc = struct.unpack("<I", footer)[0]
                actual_crc = zlib.crc32(payload) & 0xFFFFFFFF
                if expected_crc != actual_crc:
                    raise ProtocolError(
                        f"CRC mismatch: expected {expected_crc:#x}, got {actual_crc:#x}"
                    )

            # Decompress if needed
            if compression != COMPRESSION_NONE:
                payload = self._decompress(payload, compression)

            # Parse message
            yield self._parse_message(msg_type, version, compression, payload)

    def _read_exact(self, stream, size: int) -> bytes:
        """Read exactly size bytes from stream."""
        data = b""
        remaining = size
        while remaining > 0:
            chunk = stream.read(remaining)
            if not chunk:
                break
            data += chunk
            remaining -= len(chunk)
        return data

    def _decompress(self, data: bytes, compression_type: int) -> bytes:
        """Decompress payload based on compression type."""
        if compression_type == COMPRESSION_LZ4:
            try:
                import lz4.frame

                return lz4.frame.decompress(data)
            except ImportError as e:
                raise RuntimeError(
                    "lz4 package required for LZ4 decompression"
                ) from e

        if compression_type == COMPRESSION_ZSTD:
            try:
                import zstandard

                return zstandard.decompress(data)
            except ImportError as e:
                raise RuntimeError(
                    "zstandard package required for Zstd decompression"
                ) from e

        raise ProtocolError(f"Unknown compression type: {compression_type}")

    def _parse_message(
        self, msg_type: int, version: int, compression: int, payload: bytes
    ) -> Message:
        """Parse a message from its payload."""
        msg_data = msgpack.unpackb(payload, raw=False)

        msg = Message(
            msg_type=msg_type,
            version=version,
            compression=compression,
            raw_payload=payload,
        )

        if msg_type == MSG_TYPE_COMBINED:
            # Combined message has both sample and flow_metadata
            sample_data = msg_data.get("Sample", msg_data.get("sample", {}))
            flow_data = msg_data.get(
                "FlowMetadata", msg_data.get("flow_metadata", {})
            )

            msg.sample = SAXSSample(
                id=sample_data.get("ID", sample_data.get("id", "")),
                q=sample_data.get("Q", sample_data.get("q", [])),
                intensity=sample_data.get(
                    "I", sample_data.get("intensity", [])
                ),
                error=sample_data.get("Err", sample_data.get("error", [])),
            )

            msg.flow_metadata = FlowMetadata(
                sample=flow_data.get("Sample", flow_data.get("sample", "")),
                processed_peaks=flow_data.get(
                    "ProcessedPeaks", flow_data.get("processed_peaks", {})
                ),
                unprocessed_peaks=flow_data.get(
                    "UnprocessedPeaks", flow_data.get("unprocessed_peaks", {})
                ),
                current=flow_data.get("Current", flow_data.get("current", {})),
            )

        elif msg_type == MSG_TYPE_SAMPLE:
            msg.sample = SAXSSample(
                id=msg_data.get("ID", msg_data.get("id", "")),
                q=msg_data.get("Q", msg_data.get("q", [])),
                intensity=msg_data.get("I", msg_data.get("intensity", [])),
                error=msg_data.get("Err", msg_data.get("error", [])),
            )

        elif msg_type == MSG_TYPE_FLOW_METADATA:
            msg.flow_metadata = FlowMetadata(
                sample=msg_data.get("Sample", msg_data.get("sample", "")),
                processed_peaks=msg_data.get(
                    "ProcessedPeaks", msg_data.get("processed_peaks", {})
                ),
                unprocessed_peaks=msg_data.get(
                    "UnprocessedPeaks", msg_data.get("unprocessed_peaks", {})
                ),
                current=msg_data.get("Current", msg_data.get("current", {})),
            )

        return msg


class ProtocolError(Exception):
    """Raised when a protocol error occurs."""


class PrintHandler(SampleHandler):
    """Simple handler that prints samples."""

    def __init__(self, max_samples: int | None = None) -> None:
        self.max_samples = max_samples
        self.count = 0

    def on_sample(self, sample: SAXSSample, metadata: FlowMetadata) -> None:
        self.count += 1
        print(f"Sample {self.count}: id={sample.id}, points={len(sample)}")
        if self.max_samples and self.count >= self.max_samples:
            raise StopIteration

    def on_complete(self) -> None:
        print(f"Stream complete. Total samples: {self.count}")


class CollectHandler(SampleHandler):
    """Handler that collects samples into a list."""

    def __init__(self, max_samples: int | None = None) -> None:
        self.max_samples = max_samples
        self.samples: list[tuple[SAXSSample, FlowMetadata]] = []

    def on_sample(self, sample: SAXSSample, metadata: FlowMetadata) -> None:
        self.samples.append((sample, metadata))
        if self.max_samples and len(self.samples) >= self.max_samples:
            raise StopIteration

    def on_complete(self) -> None:
        pass


class CallbackHandler(SampleHandler):
    """Handler that calls a callback function for each sample."""

    def __init__(
        self,
        callback: Callable[[SAXSSample, FlowMetadata], None],
        on_error: Callable[[Exception], None] | None = None,
        on_complete: Callable[[], None] | None = None,
    ) -> None:
        self._callback = callback
        self._on_error = on_error
        self._on_complete = on_complete

    def on_sample(self, sample: SAXSSample, metadata: FlowMetadata) -> None:
        self._callback(sample, metadata)

    def on_error(self, error: Exception) -> None:
        if self._on_error:
            self._on_error(error)

    def on_complete(self) -> None:
        if self._on_complete:
            self._on_complete()


if __name__ == "__main__":
    # Example usage
    db_url = "postgres://postgres:postgres@localhost:5433/saxs?sslmode=disable"

    # Using context manager and iterator
    with GoStreamConsumer(
        binary_path="./dbreader",
        database_url=db_url,
    ) as consumer:
        for i, (sample, meta) in enumerate(consumer.consume()):
            print(f"Sample {i}: id={sample.id}, points={len(sample)}")
            if i >= 10:
                break
