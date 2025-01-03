# Contributing to Book Tracker

Thank you for your interest in contributing to Book Tracker! This document outlines the process and guidelines for contributing to this project.

## Getting Started

1. Fork the repository
2. Clone your fork:
```bash
git clone https://github.com/joereg4/book_tracker.git
```
3. Create a new branch for your feature:
```bash
git checkout -b feature/your-feature-name
```

## Development Setup

1. Follow the installation instructions in the README.md
2. Set up your virtual environment:
```bash
python -m venv books
source books/bin/activate  # On Unix/macOS
books\Scripts\activate     # On Windows
```
3. Install development dependencies:
```bash
pip install -r requirements.txt
pip install pytest pytest-cov flake8 black
```
4. Set up pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```
5. Make sure all tests pass:
```bash
pytest
```

## Testing

1. Run the test suite:
```bash
pytest
```
2. Check code coverage:
```bash
pytest --cov=.
```
3. Run linting:
```bash
flake8 .
```
4. Format code:
```bash
black .
```

## Making Changes

1. Write clear, concise commit messages
2. Follow the existing code style and conventions
3. Comment your code where necessary
4. Update documentation as needed
5. Add tests for new functionality

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Ensure your code passes all tests
3. Update the CHANGELOG.md if applicable
4. Submit a pull request with a clear description of the changes

## Code Style Guidelines

- Follow PEP 8 style guide for Python code
- Use meaningful variable and function names
- Keep functions focused and single-purpose
- Add type hints where possible
- Document complex logic

## Reporting Issues

- Use the GitHub issue tracker
- Check if the issue already exists
- Include detailed steps to reproduce
- Provide system/environment details
- Include relevant logs or screenshots

## Code of Conduct

This project follows a standard Code of Conduct. By participating, you are expected to:

- Be respectful and inclusive
- Be collaborative
- Focus on what is best for the community
- Show empathy towards others

## Questions?

Feel free to create an issue for any questions not covered here.

Thank you for contributing to Book Tracker! 