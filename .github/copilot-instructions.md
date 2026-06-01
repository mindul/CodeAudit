# Copilot Instructions for CodeAudit

This repository is a small security/audit tool workspace with two main purposes:
- `scan.py` / `scan_dir.py`: CLI wrappers that send source code to a local Ollama inference API for vulnerability analysis.
- `target0.py`: a Flask-based scanning web app that exposes multiple `/api/scan/*` endpoints.

## Key files and behavior
- `scan.py`: analyze a single file via `http://localhost:11434/api/generate` using `requests`.
- `scan_dir.py`: scan a directory for source files (`.py`, `.js`, `.java`, `.c`, `.php`) and write reports into `scan_reports/`.
- `target0.py`: Flask entrypoint started on `0.0.0.0:5657`, with SSE-style streaming responses in several scan endpoints.
- `test/`: sample PHP target files that show the kinds of code and request handling this repo works with.

## Project-specific patterns
- Most scan functions construct a prompt in Korean and post it to a local Ollama server.
- `scan_dir.py` uses `glob.glob()` to collect files and writes one output report per source file.
- `target0.py` handles JSON POST bodies and supports CIDR targets with a 256-host cap.
- Some imports in `target0.py` are lazy-loaded inside endpoint handlers (`port_scanner_core`, `ssl_tls_scanner_core`, etc.), so module resolution is endpoint-specific.
- Streaming scan endpoints return `Response(stream_with_context(generate()), mimetype='text/event-stream')` and emit JSON blobs as SSE data.

## Commands and workflows
- Run a single file scan: `python scan.py path/to/file.py`
- Run batch directory scanning: `python scan_dir.py path/to/dir`
- Start the Flask scanner app: `python target0.py`
- The environment assumes `requests` and `Flask` are installed and that a local Ollama server is available on port `11434`.

## What matters for edits
- Keep the existing Korean CLI/help strings in `scan.py` and `scan_dir.py`.
- Preserve the report output folder behavior in `scan_dir.py`.
- In `target0.py`, avoid changing streaming response semantics unless explicitly requested.
- Do not assume any build system or package manifest is present; this repo uses direct Python execution.

## Notes for the agent
- There is no existing `.github/copilot-instructions.md` in this repo, so this file should be the authoritative guidance.
- Focus on the actual files present: `scan.py`, `scan_dir.py`, `target0.py`, and the `test/` PHP examples.
- Do not invent additional services or tooling beyond the local Ollama API and Flask runtime.
