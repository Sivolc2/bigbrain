# Brain - Advanced Code Generation Agent

An advanced code-generation agent built using LangGraph and modern AI technologies.

## Project Structure

```
brain/
├── core/           # Main workflow and core functionality
├── llm/            # Prompt management and LLM interfaces
├── tools/          # Agent toolkit implementations
└── state/          # State management and persistence
```

## Features

- Task decomposition with priority handling
- Versioned state management
- Extensible tool system
- Comprehensive history tracking

## Setup

1. Make sure you have Python 3.10+ installed
2. Install Poetry if you haven't already:
   ```bash
   pip install poetry
   ```
3. Install dependencies:
   ```bash
   poetry install
   ```

## Development

This project uses Poetry for dependency management and packaging. Key dependencies:

- langchain-core
- langchain-anthropic
- langgraph
- pydantic
- instructor

## Version

Current version: 0.1.0

## License

MIT License
