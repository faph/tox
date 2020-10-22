import os
import select
from typing import IO, Callable

from .read_via_thread import ReadViaThread


class ReadViaThreadUnix(ReadViaThread):
    def __init__(self, stream: IO[bytes], handler: Callable[[bytes], None]) -> None:
        super().__init__(stream, handler)
        self.file_no = self.stream.fileno()

    def _read_stream(self) -> None:
        while not (self.stream.closed or self.stop.is_set()):
            # we need to drain the stream, but periodically give chance for the thread to break if the stop event has
            # been set (this is so that an interrupt can be handled)
            if self.has_bytes():
                data = os.read(self.file_no, 1)
                self.handler(data)

    def has_bytes(self) -> bool:
        read_available_list, _, __ = select.select([self.stream], [], [], 0.01)
        return len(read_available_list) != 0

    def _drain_stream(self) -> bytes:
        return self.stream.read()