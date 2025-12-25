"""Duplex pipe connector for Go SAXS stream producer."""

from __future__ import annotations

import struct
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Iterator

import msgpack

if TYPE_CHECKING:
    from types import TracebackType


# Protocol constants (must match Go producer/internal/protocol/constants.go)
MAGIC_NUMBER = 0x53415853  # "SAXS"
HEADER_SIZE = 16
FOOTER_SIZE = 4


@dataclass
class SAXSSample:
    """SAXS sample data from Go stream."""

    id: str
    q: list[float]
    intensity: list[float]
    error: list[float]


@dataclass
class FlowMetadata:
    """Flow metadata from Go stream."""

    sample: str
    processed_peaks: dict[int, float]
    unprocessed_peaks: dict[int, float]
    current: dict[int, float]


class GoStreamConnector:
    """Duplex pipe connector to Go SAXS stream producer.

    Usage
    -----
    >>> with GoStreamConnector() as conn:
    ...     for sample, meta in conn.stream():
    ...         process(sample)

    """

    def __init__(
        self,
        binary_path: str | Path = "./dbreader",
        database_url: str | None = None,
    ) -> None:
        self.binary_path = Path(binary_path)
        self.database_url = database_url
        self._proc: subprocess.Popen[bytes] | None = None

    def __enter__(self) -> GoStreamConnector:
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
        env = None
        if self.database_url:
            import os

            env = {**os.environ, "DATABASE_URL": self.database_url}

        self._proc = subprocess.Popen(
            [str(self.binary_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )

    def stop(self) -> None:
        """Stop the Go producer process."""
        if self._proc:
            self._proc.terminate()
            self._proc.wait(timeout=5)
            self._proc = None

    def send_command(self, command: dict) -> None:
        """Send a command to the Go process via stdin."""
        if not self._proc or not self._proc.stdin:
            msg = "Process not started"
            raise RuntimeError(msg)

        data = msgpack.packb(command)
        # Write length-prefixed message
        self._proc.stdin.write(struct.pack("<I", len(data)))
        self._proc.stdin.write(data)
        self._proc.stdin.flush()

    def stream(self) -> Iterator[tuple[SAXSSample, FlowMetadata]]:
        """Stream SAXS samples from Go producer.

        Yields
        ------
        tuple[SAXSSample, FlowMetadata]
            Sample data and flow metadata for each record.

        """
        if not self._proc or not self._proc.stdout:
            msg = "Process not started"
            raise RuntimeError(msg)

        stdout = self._proc.stdout

        while True:
            # Read header (16 bytes)
            header = stdout.read(HEADER_SIZE)
            if not header:
                break
            if len(header) < HEADER_SIZE:
                msg = f"Incomplete header: {len(header)} bytes"
                raise RuntimeError(msg)

            # Parse header
            magic, version, msg_type, compression, payload_len = struct.unpack(
                "<IHBBQ",
                header,
            )

            if magic != MAGIC_NUMBER:
                msg = f"Invalid magic number: {magic:#x}"
                raise RuntimeError(msg)

            # Read payload
            payload = stdout.read(payload_len)
            if len(payload) < payload_len:
                msg = f"Incomplete payload: {len(payload)}/{payload_len}"
                raise RuntimeError(msg)

            # Read footer (CRC32)
            footer = stdout.read(FOOTER_SIZE)
            if len(footer) < FOOTER_SIZE:
                msg = "Incomplete footer"
                raise RuntimeError(msg)

            # Decompress if needed
            if compression != 0:
                payload = self._decompress(payload, compression)

            # Decode msgpack
            msg_data = msgpack.unpackb(payload, raw=False)

            sample_data = msg_data.get("sample", {})
            flow_data = msg_data.get("flow_metadata", {})

            sample = SAXSSample(
                id=sample_data.get("ID", ""),
                q=sample_data.get("Q", []),
                intensity=sample_data.get("I", []),
                error=sample_data.get("Err", []),
            )

            meta = FlowMetadata(
                sample=flow_data.get("sample", ""),
                processed_peaks=flow_data.get("processed_peaks", {}),
                unprocessed_peaks=flow_data.get("unprocessed_peaks", {}),
                current=flow_data.get("current", {}),
            )

            yield sample, meta

    def _decompress(self, data: bytes, compression_type: int) -> bytes:
        """Decompress payload based on compression type."""
        if compression_type == 1:  # LZ4
            import lz4.frame

            return lz4.frame.decompress(data)
        if compression_type == 2:  # Zstd
            import zstandard

            return zstandard.decompress(data)
        msg = f"Unknown compression type: {compression_type}"
        raise ValueError(msg)
    
    def handshake(self) -> bool:
        """
        Perform handshake with Go server to ensure it's ready.

        Returns
        -------
        bool
            True if handshake succeeded.

        Raises
        ------
        RuntimeError
            If handshake fails after retries.
        """
        for attempt in range(self.handshake_retries):
            try:
                # Отправляем команду инициализации
                self.send_command({"cmd": "init", "version": 1})

                # Ждём ответный заголовок
                header = self._proc.stdout.read(HEADER_SIZE)
                if not header or len(header) < HEADER_SIZE:
                    raise RuntimeError("Handshake: incomplete header")

                magic, version, msg_type, _, payload_len = struct.unpack("<IHBBQ", header)

                if magic != MAGIC_NUMBER:
                    raise RuntimeError(f"Handshake: invalid magic {magic:#x}")

                # Читаем payload (должен быть ответ от сервера)
                payload = self._proc.stdout.read(payload_len)
                if len(payload) < payload_len:
                    raise RuntimeError("Handshake: incomplete payload")

                # Декодируем ответ
                response = msgpack.unpackb(payload, raw=False)
                if response.get("status") == "ok":
                    return True  # Успешное рукопожатие

            except Exception as e:
                if attempt == self.handshake_retries - 1:
                    raise RuntimeError(f!Handshake failed after {self.handshake_retries} attempts: {e}") from e
                time.sleep(0.1)  # пауза перед повторной попыткой

        return False

    def send_command(self, command: dict) -> None:
        """Send a command to the Go process via stdin."""
        if not self._proc or not self._proc.stdin:
            msg = "Process not started"
            raise RuntimeError(msg)

        data = msgpack.packb(command)
        # Write length-prefixed message
        self._proc.stdin.write(struct.pack("<I", len(data)))
        self._proc.stdin.write(data)
        self._proc.stdin.flush()


if __name__ == "__main__":
    # Example usage
    db_url = "postgres://postgres:postgres@localhost:5433/saxs?sslmode=disable"

    with GoStreamConnector(
        binary_path="./dbreader",
        database_url=db_url,
    ) as conn:
        for i, (sample, meta) in enumerate(conn.stream()):
            print(f"Sample {i}: id={sample.id}, points={len(sample.q)}")
            if i >= 10:
                break