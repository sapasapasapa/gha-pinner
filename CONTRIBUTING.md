# Contributing to gha-pinner

Thank you for your interest in contributing to gha-pinner! 🎉

## 🚀 Quick Start

1. **Fork and clone** the repository
2. **Set up development environment:**
   ```bash
   # Install mise (if not already installed)
   curl https://mise.run | sh
   
   # Install dependencies
   mise install
   poetry install
   ```
3. **Make your changes** and add tests if needed
4. **Run tests and linting:**
   ```bash
   poetry run pytest src/test -v
   poetry run ruff format .
   poetry run ruff check --fix
   ```
5. **Submit a pull request** with a clear description

## 📝 Development Guidelines

- **Code Style**: We use Ruff for formatting and linting
- **Testing**: Add tests for new features in `src/test/`
- **Commits**: Use clear, descriptive commit messages
- **Documentation**: Update README.md if adding new features

## 🐛 Bug Reports

Found a bug? Please [open an issue](https://github.com/sapasapasapa/gha-pinner/issues/new/choose) with:
- Steps to reproduce
- Expected vs actual behavior
- Your environment details

## 💡 Feature Requests

Have an idea? We'd love to hear it! [Create a feature request](https://github.com/sapasapasapa/gha-pinner/issues/new/choose) explaining:
- The problem you're trying to solve
- Your proposed solution
- Any alternatives considered

## 🔍 Project Structure

```
src/
├── main.py          # CLI entry point
├── retriever.py     # GitHub API interactions
├── editor.py        # Workflow file processing
├── common/          # Shared constants
└── test/           # Test suite
```

## 🤝 Code of Conduct

Be respectful, constructive, and helpful. We're all here to make GitHub Actions more secure! 🔐 