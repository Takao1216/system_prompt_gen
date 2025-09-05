# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**System Prompt Generator for AI Engineers** - A comprehensive Jupyter Notebook-based tool for generating, evaluating, and improving prompts for AI/LLM applications, specifically designed for engineers doing Proof of Concept (PoC) development.

## Current Repository State

The project is fully functional with:
- **Main Interface**: Jupyter Notebook with interactive prompt generation
- **Core Modules**: `src/generator.py`, `src/evaluator.py`, `src/templates/`
- **API Integration**: Claude API (Anthropic) for prompt generation and improvement
- **Testing**: Validation script (`validate.py`) for system verification
- **Documentation**: Comprehensive guides in `docs/` and root directory

## Version Management

### Notebook Versioning
- **File Naming**: `notebook_v{MAJOR}.{MINOR}.{PATCH}[-{STAGE}].ipynb`
- **Current Stable**: `notebook_v1.0.0.ipynb` (in `notebooks/stable/`)
- **Current Development**: `notebook_v1.1.0-dev.ipynb` (in `notebooks/current/`)
- **Quick Access**: 
  - `notebook_stable.ipynb` → symlink to current stable version
  - `notebook_dev.ipynb` → symlink to current development version

### Release Versioning
- **Directory Structure**: `release/v{MAJOR}.{MINOR}.{PATCH}/`
- **Current Release**: `v1.0.0` (2025-01-05)
- **Version Files**: `VERSION`, `RELEASE_NOTES.md`, `CHANGELOG.md`, `MANIFEST.md`

### Version Control Documents
- `NOTEBOOK_VERSION_CONTROL.md` - Notebook version management guide
- `release/VERSION_GUIDE.md` - Release package management guide

### v1.1.0 Development Features (New)
- **Prompt History Tracking** (`src/prompt_history.py`):
  - Save and search generated prompts
  - Quality score tracking
  - Export/import capabilities
  - Tag-based filtering
  
- **Batch Processing** (`src/batch_processor.py`):
  - Process multiple prompts concurrently
  - Parallel and async execution modes
  - CSV batch import
  - Multiple export formats (JSON, CSV, Markdown)
  
- **Code Input and Analysis** (`src/code_input_handler.py`, `src/code_analyzer.py`):
  - Interactive code input UI with ipywidgets
  - Automatic language detection
  - Syntax highlighting with Pygments
  - Code metrics calculation (complexity, maintainability)
  - Design pattern detection
  - Code smell identification
  - Prompt generation from code context
  
- **Enhanced Notebook Features**:
  - Version metadata cell with development status
  - History visualization with charts
  - Statistics dashboard
  - Interactive demos for new features
  - Code metrics visualization

## Development Setup

### Prerequisites
1. Python 3.8+
2. Claude API Key from Anthropic
3. Jupyter Notebook

### Quick Start
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 3. Verify setup
python validate.py

# 4. Launch notebook (development version)
jupyter notebook notebook_dev.ipynb
```

## Architecture Notes

### Core Components
- **PromptGenerator** (`src/generator.py`): Generates prompts using Claude API
- **PromptEvaluator** (`src/evaluator.py`): Evaluates prompt quality with 5 metrics
- **TemplateManager** (`src/templates/template_manager.py`): Manages 5 built-in templates
- **LangGraph Workflow**: Optional iterative prompt improvement system

### Template Categories
1. Data Analysis PoC
2. Image Recognition PoC
3. Text Processing PoC
4. Requirements Analysis
5. API Testing

### Quality Metrics
- Clarity
- Specificity
- Completeness
- Efficiency
- Reproducibility

## Development Workflow

### For Notebook Development
1. Work on `notebook_dev.ipynb` (symlink to current dev version)
2. Test changes with `python validate.py`
3. Update version metadata in first cell
4. Progress through stages: `-dev` → `-alpha` → `-beta` → `-rc` → release
5. Move to stable when ready

### For Code Changes
1. Modify source files in `src/`
2. Run validation: `python validate.py`
3. Test in notebook environment
4. Update documentation if needed

### For Releases
1. Clear notebook outputs
2. Remove all personal information/API keys
3. Copy to `release/vX.X.X/`
4. Update version files and documentation
5. Create distribution package

## Important Commands

```bash
# Development
jupyter notebook notebook_dev.ipynb    # Open development notebook
python validate.py                      # Validate system setup

# Testing - Core Modules
python -c "from src.generator import PromptGenerator; print('✅')"
python -c "from src.evaluator import PromptEvaluator; print('✅')"

# Testing - v1.1.0 New Modules
python -c "from src.prompt_history import PromptHistory; print('✅ History')"
python -c "from src.batch_processor import BatchProcessor; print('✅ Batch')"

# Release Preparation
python validate.py                      # Full system check
# Clear notebook outputs programmatically
# Copy to release directory
```

## Configuration

### Environment Variables (.env)
- `ANTHROPIC_API_KEY` (required): Your Claude API key
- `DEFAULT_MODEL`: `claude-3-5-sonnet-20241022`
- `MAX_TOKENS`: 4000
- `TEMPERATURE`: 0.7

### Optional Dependencies
- LangChain/LangGraph (for advanced workflows)
- FastAPI (for REST API server)
- LangSmith (for tracing)

## Development Notes

- **Git Branches**: `develop` (current), `main` (production)
- **Model**: Uses `claude-3-5-sonnet-20241022` (latest available)
- **Security**: Never commit `.env` files or API keys
- **Testing**: Always run `validate.py` before releases
- **Documentation**: Keep guides synchronized with code changes

## Directory Structure

```
system_prompt_gen/
├── notebooks/              # Versioned notebooks
│   ├── current/           # Development versions
│   ├── stable/            # Stable versions
│   └── archive/           # Historical versions
├── src/                   # Source code
│   ├── generator.py
│   ├── evaluator.py
│   └── templates/
├── release/               # Release packages
│   ├── v1.0.0/
│   └── VERSION_GUIDE.md
├── docs/                  # Documentation
├── validate.py           # System validation
└── requirements.txt      # Dependencies
```

## Support Files

- `QUICKSTART.md` - 5-minute setup guide
- `NOTEBOOK_GUIDE.md` - Complete notebook usage guide
- `SETUP_CHECKLIST.md` - Installation verification checklist
- `NOTEBOOK_VERSION_CONTROL.md` - Notebook versioning guide

---

Last Updated: 2025-01-05
Current Stable: v1.0.0
Current Development: v1.1.0-dev