# Chatty-CLI v0.1-alpha

**A local-first AI coding assistant that runs entirely offline using Ollama**

## What This Is

Chatty-CLI is a proof-of-concept that demonstrates local AI models can provide competitive coding assistance compared to cloud-based alternatives like Claude Code. It's intentionally simple and ugly, but it *works*.

## What Works ✅

- **Single-file code analysis** - Ask questions about any Python file
- **Local Ollama integration** - Uses Deepseek-Coder model running on your machine  
- **Basic CLI interface** - Simple command-line tool for code review and debugging
- **Offline operation** - No internet required once models are downloaded
- **Cost-free usage** - No API keys or subscription fees

## What's Missing ❌ (Planned for v0.2+)

- Multi-file project awareness
- Git integration  
- Enhanced terminal UI (TUI)
- Support for languages other than Python
- Comprehensive test coverage
- Package distribution on PyPI

## Installation

### Option 1: Direct Python Execution (Simplest)
```bash
# Just run the Python file directly
python chatty-cli.py --help
```

### Option 2: Pip Install
```bash
pip install -e .
chatty-cli --help
```

### Prerequisites
- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running
- Deepseek-Coder model downloaded: `ollama pull deepseek-coder`

## Usage

### Basic Analysis
```bash
python chatty-cli.py example.py "Explain this function"
```

### Code Review
```bash
python chatty-cli.py your_code.py "Review this code for potential bugs"
```

### Debugging Help
```bash
python chatty-cli.py problematic_file.py "Help me debug this error"
```

### Optimization
```bash
python chatty-cli.py slow_code.py "How can I optimize this code?"
```

## Why Local-First?

This project explores whether local AI models can provide:
- **Better privacy** - Your code never leaves your machine
- **Lower costs** - No API fees or usage limits  
- **Faster responses** - No network latency
- **Offline capability** - Works without internet
- **Better integration** - Terminal-native development workflow

## Technical Details

- **Models supported**: Deepseek-Coder (default), CodeLlama
- **Languages**: Primarily Python (extensible to others)
- **Dependencies**: Only `requests` and standard library
- **Performance**: Typically 2-5 second response times for code analysis

## Contributing

This is a proof-of-concept. Contributions welcome for:
- Adding support for more programming languages
- Improving the CLI interface
- Better error handling
- Documentation improvements

**Note**: This is intentionally minimal. If you want a production-ready tool, check out [Continue.dev](https://continue.dev/) or [Aider](https://github.com/paul-gauthier/aider).

## License

MIT License - feel free to use, modify, and distribute.

## Status

**v0.1-alpha**: Working proof-of-concept (October 2025)

This is real, functional code that proves the concept. It's not polished, but it works.

---

*Built as a learning exercise and proof-of-concept for local-first AI development workflows.*