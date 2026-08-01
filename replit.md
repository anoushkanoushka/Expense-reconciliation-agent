# Data Processor

A command-line data processing tool written in plain Python — no web server, no framework.

## Run & Operate

- `python -m src.main <input_file>` — process a file and print results to stdout
- `python -m src.main <input_file> -o <output_file>` — write results to a file
- `python -m src.main -v` — enable verbose mode
- `python -m pytest` — run the test suite
- `pip install -r requirements.txt` — install dependencies

## Stack

- Python 3.11+
- No web framework — pure CLI tool
- `pyproject.toml` for project metadata and tool config
- `pytest` for testing

## Where things live

_Populate as you build — short repo map plus pointers to the source-of-truth file for DB schema, API contracts, theme files, etc._

## Architecture decisions

_Populate as you build — non-obvious choices a reader couldn't infer from the code (3-5 bullets)._

## Product

_Describe the high-level user-facing capabilities of this app once they exist._

## User preferences

_Populate as you build — explicit user instructions worth remembering across sessions._

## Gotchas

_Populate as you build — sharp edges, "always run X before Y" rules._

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
