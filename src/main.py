"""
Entry point for the data processing tool.
Run with: python -m src.main [options]
"""

import argparse
import sys

from src.processor import process


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Command-line data processing tool"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Path to the input file (or leave blank to read from stdin)",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Path to the output file (default: stdout)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        process(
            input_path=args.input,
            output_path=args.output,
            verbose=args.verbose,
        )
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
