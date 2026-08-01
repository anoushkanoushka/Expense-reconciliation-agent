"""
Core data processing logic.
Add your transformation and analysis functions here.
"""

import sys
from typing import IO


def process(
    input_path: str | None,
    output_path: str | None,
    verbose: bool = False,
) -> None:
    """
    Read data from *input_path* (or stdin), process it, and write the
    result to *output_path* (or stdout).
    """
    in_stream = _open_input(input_path)
    out_stream = _open_output(output_path)

    try:
        for line in in_stream:
            result = transform(line)
            if verbose:
                print(f"[verbose] {line.rstrip()!r} -> {result!r}", file=sys.stderr)
            out_stream.write(result + "\n")
    finally:
        if input_path:
            in_stream.close()
        if output_path:
            out_stream.close()


def transform(line: str) -> str:
    """
    Apply a transformation to a single line of input.
    Replace this with your own logic.
    """
    return line.rstrip().upper()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _open_input(path: str | None) -> IO[str]:
    return open(path, "r", encoding="utf-8") if path else sys.stdin


def _open_output(path: str | None) -> IO[str]:
    return open(path, "w", encoding="utf-8") if path else sys.stdout
