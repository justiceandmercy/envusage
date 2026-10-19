# envusage

A small CLI that scans source code for environment variable references and compares them against a declared `.env` template (such as `.env.example`), reporting variables that are used in code but missing from the template, and variables declared in the template but never referenced.

## Features

- Scans common source extensions (Python, JavaScript/TypeScript, Go, Ruby, Rust, Java, Shell).
- Recognizes popular access idioms: `process.env.VAR`, `process.env['VAR']`, `os.environ[...]`, `os.getenv(...)`, `getenv(...)`, and more.
- Auto-detects `.env.example`, `.env.sample`, or `.env.template` in the project root.
- Reports undeclared (used but not declared) and unused (declared but not used) variables.
- Optional JSON output for CI integration.
- Zero external dependencies.

## Install

```bash
pip install .
```

Or run directly:

```bash
python -m envusage.cli .
```

## Usage

```bash
# Scan current directory, auto-detect template
envusage .

# Specify a template explicitly
envusage . -t .env.example

# JSON output for CI
envusage . --json
```

### Example output

```
Scanned 42 files. Found 12 env var references.
Declared in template: 10

Undeclared (used in code but not in template):
  - STRIPE_WEBHOOK_SECRET

Unused (declared but not referenced in code):
  - LEGACY_API_KEY
```

## License

MIT
