# Contributing to Omni Multi-Agent System

Thank you for your interest in contributing! This is primarily a portfolio project, but feedback and suggestions are welcome.

## How to Contribute

### Reporting Issues

If you find a bug or have a suggestion:

1. Check if the issue already exists in [GitHub Issues](https://github.com/yourusername/omni_multi_agent/issues)
2. If not, create a new issue with:
   - Clear description of the problem or suggestion
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Your environment (Python version, OS, etc.)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:
- **Use case**: What problem does this solve?
- **Proposed solution**: How should it work?
- **Alternatives considered**: Other approaches you thought about

### Pull Requests

While this is a portfolio project, PRs are welcome for:
- Bug fixes
- Documentation improvements
- Test coverage improvements
- Performance optimizations

**Before submitting a PR:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages (`git commit -m 'feat: add amazing feature'`)
6. Push to your fork (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

Examples:
```
feat: add reminders agent
fix: correct task changelog timestamp format
docs: update setup guide for Windows
refactor: simplify orchestrator planning logic
```

## Development Setup

See [docs/SETUP.md](docs/SETUP.md) for complete setup instructions.

Quick version:
```bash
git clone https://github.com/yourusername/omni_multi_agent.git
cd omni_multi_agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
letta server  # In separate terminal
```

## Code Style

- **Python**: Follow PEP 8
- **Line length**: 100 characters (configured in pyproject.toml)
- **Formatting**: Use `black` for consistent formatting
- **Linting**: Use `ruff` for code quality

Run formatters:
```bash
black .
ruff check --fix .
```

## Testing

Currently, this project doesn't have a comprehensive test suite (see [Future Enhancements](README.md#-future-enhancements)).

If you add tests:
```bash
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html
```

## Documentation

When adding features:
- Update relevant docs in `docs/`
- Add docstrings to new functions/classes
- Update README.md if user-facing changes
- Add examples if demonstrating new workflows

## Questions?

- Open a [GitHub Issue](https://github.com/yourusername/omni_multi_agent/issues)
- Contact: [Your Email]

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
