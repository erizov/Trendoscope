# 🤝 Contributing to Trendoscope

Thank you for your interest in contributing to Trendoscope!

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)

---

## 📜 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Respect different viewpoints

---

## 🚀 Getting Started

### 1. Fork the Repository

```bash
# Fork on GitHub, then clone
git clone https://github.com/your-username/Trendoscope.git
cd Trendoscope
```

### 2. Create Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes

- Follow coding standards
- Write tests
- Update documentation

### 4. Commit

```bash
git commit -m "feat: Add your feature"
```

### 5. Push & PR

```bash
git push origin feature/your-feature-name
# Create PR on GitHub
```

---

## 💻 Development Setup

### Prerequisites

- Python 3.11+
- pip
- Git

### Setup

```bash
# Clone repository
git clone https://github.com/erizov/Trendoscope.git
cd Trendoscope/trendascope

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install pytest pytest-cov black flake8 mypy

# Run tests
pytest tests/ -v
```

---

## 📝 Coding Standards

### Python Style

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use Black for formatting

```bash
# Format code
black src/

# Check style
flake8 src/
```

### Code Organization

- **Services**: Business logic
- **API**: HTTP endpoints
- **Utils**: Helper functions
- **Tests**: Test files

### Naming Conventions

- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore`

---

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src/trendascope --cov-report=html

# Specific test
pytest tests/test_services.py -v
```

### Write Tests

- Unit tests for services
- Integration tests for API
- Test edge cases
- Aim for 80%+ coverage

---

## 📚 Documentation

### Code Documentation

- Docstrings for all functions
- Type hints for parameters
- Examples for complex functions

### Markdown Files

- Follow markdownlint rules
- Use proper headings
- Include code examples
- Keep it concise

---

## 🔀 Commit Guidelines

### Format

```
type(scope): subject

body (optional)

footer (optional)
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Tests
- `chore`: Maintenance

### Examples

```bash
feat(api): Add post management endpoints
fix(gen): Fix balance checking logic
docs(readme): Update installation instructions
```

---

## 🔍 Pull Request Process

### Before Submitting

1. ✅ Tests pass
2. ✅ Code formatted
3. ✅ Documentation updated
4. ✅ No lint errors
5. ✅ Commit messages clear

### PR Description

- What changed
- Why changed
- How to test
- Screenshots (if UI)

### Review Process

- Maintainers review
- Address feedback
- Update if needed
- Merge when approved

---

## 🐛 Reporting Bugs

### Bug Report Template

```markdown
**Description**
Clear description of the bug

**Steps to Reproduce**
1. Step one
2. Step two
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: Windows 10
- Python: 3.11
- Version: 2.2.0

**Additional Context**
Any other relevant information
```

---

## 💡 Feature Requests

### Feature Request Template

```markdown
**Feature Description**
Clear description of the feature

**Use Case**
Why is this needed?

**Proposed Solution**
How should it work?

**Alternatives**
Other solutions considered

**Additional Context**
Any other relevant information
```

---

## 📖 Documentation Contributions

### Areas Needing Documentation

- API endpoints
- Configuration options
- Deployment guides
- Troubleshooting
- Examples

### Documentation Standards

- Clear and concise
- Code examples
- Screenshots when helpful
- Keep updated

---

## 🎯 Areas for Contribution

### High Priority

- Test coverage improvements
- Documentation enhancements
- Performance optimizations
- Security improvements

### Medium Priority

- New features
- UI/UX improvements
- Integration examples
- Tutorial videos

### Low Priority

- Code cleanup
- Refactoring
- Style improvements
- Minor bug fixes

---

## ❓ Questions?

- **GitHub Issues**: For bugs and features
- **Discussions**: For questions
- **Email**: For direct contact

---

**Thank you for contributing!** 🎉

