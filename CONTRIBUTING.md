# Contributing to Stereopair

Thank you for your interest in contributing to Stereopair! This document provides guidelines for contributing to the project.

## Getting Started

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/endarthur/stereopair.git
cd stereopair
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -e .
```

4. Install development dependencies:
```bash
pip install pytest pytest-cov black flake8
```

## Development Workflow

### Running Tests

Run the test suite:
```bash
python tests/test_basic.py
```

Or with pytest:
```bash
pytest tests/
```

### Code Style

We follow PEP 8 style guidelines. Before submitting a PR:

1. Format your code with Black:
```bash
black stereopair/ tests/ examples/
```

2. Check for style issues:
```bash
flake8 stereopair/ tests/ examples/
```

### Testing Your Changes

1. Run existing tests to ensure you haven't broken anything
2. Add new tests for new features
3. Test with the example scripts:
```bash
python examples/demo_offline.py
```

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear, descriptive title
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Your environment (OS, Python version, etc.)
- Any error messages or stack traces

### Suggesting Enhancements

Enhancement suggestions are welcome! Please open an issue with:
- A clear description of the enhancement
- Why this enhancement would be useful
- Examples of how it would be used
- Any relevant references or examples from other projects

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature:
```bash
git checkout -b feature/your-feature-name
```

3. Make your changes:
   - Write clear, commented code
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation as needed

4. Test your changes:
```bash
python tests/test_basic.py
```

5. Commit your changes:
```bash
git add .
git commit -m "Add feature: brief description"
```

6. Push to your fork:
```bash
git push origin feature/your-feature-name
```

7. Open a Pull Request with:
   - Clear title and description
   - Reference to any related issues
   - Summary of changes made
   - Any breaking changes noted

## Contribution Ideas

Here are some areas where contributions would be especially welcome:

### New Features
- Additional imagery providers (Mapbox, Planet, etc.)
- More DEM sources (ALOS, TanDEM-X, etc.)
- Advanced orthorectification algorithms
- Support for different coordinate systems
- Batch processing capabilities
- GUI interface

### Improvements
- Better error handling and validation
- Performance optimizations
- More comprehensive tests
- Better documentation and examples
- Support for additional image formats

### Documentation
- More usage examples
- Tutorial notebooks
- Video tutorials
- API documentation improvements
- Translation to other languages

## Code Guidelines

### Python Style
- Follow PEP 8
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep functions focused and modular

### Documentation
- Update README.md for user-facing changes
- Update API.md for API changes
- Include docstrings with examples
- Comment complex algorithms

### Testing
- Write tests for new features
- Maintain test coverage
- Test edge cases
- Include integration tests where appropriate

### Commit Messages
- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, etc.)
- Reference issues when applicable
- Keep first line under 72 characters

Example:
```
Add support for Mapbox imagery provider

- Implement MapboxImageryProvider class
- Add API key authentication
- Update documentation with usage examples
- Add tests for new provider

Fixes #123
```

## Review Process

1. All PRs require review before merging
2. Automated tests must pass
3. Code must follow style guidelines
4. Documentation must be updated
5. Changes should be backwards compatible when possible

## Code of Conduct

### Our Standards
- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions
- Be patient and helpful

### Unacceptable Behavior
- Harassment or discrimination
- Trolling or insulting comments
- Personal attacks
- Publishing private information
- Other unprofessional conduct

## Questions?

If you have questions about contributing:
- Open a GitHub issue with the "question" label
- Check existing issues for similar questions
- Review the documentation and examples

## License

By contributing to Stereopair, you agree that your contributions will be licensed under the MIT License.

## Attribution

Contributors will be recognized in:
- The project README
- Release notes
- Git commit history

Thank you for contributing to Stereopair!
