# Contributing Guide

Thank you for your interest in contributing to the Medical PDF to Anki Converter! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Contribution Workflow](#contribution-workflow)
- [Types of Contributions](#types-of-contributions)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Guidelines](#documentation-guidelines)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and constructive in all interactions.

### Standards

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

### Reporting Issues

If you encounter any inappropriate behavior, please contact the project maintainers directly.

---

## Getting Started

### Prerequisites

Before contributing, ensure you have:

| Requirement | Version/Tool |
|-------------|--------------|
| Python | 3.11+ |
| Git | Latest stable |
| Docker (optional) | Latest stable |
| Text Editor/IDE | VS Code, PyCharm, or similar |

### First Time Setup

```bash
# 1. Fork the repository
# Click "Fork" on GitHub at https://github.com/thies2005/Anki-Ai

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/Anki-Ai.git
cd Anki-Ai

# 3. Add upstream remote
git remote add upstream https://github.com/thies2005/Anki-Ai.git

# 4. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Install development dependencies
pip install pytest pytest-cov black isort mypy

# 7. Create a branch for your work
git checkout -b feature/your-feature-name
```

### Development Environment

```bash
# Run the application
streamlit run app.py

# Run tests
pytest

# Run linting
black .
isort .
mypy .
```

---

## Contribution Workflow

### 1. Find an Issue

- Browse [open issues](https://github.com/thes2005/Anki-Ai/issues)
- Look for labels like `good first issue` or `help wanted`
- Comment on the issue to indicate you're working on it

### 2. Create a Branch

```bash
# Use descriptive branch names
git checkout -b feature/feature-name
git checkout -b fix/bug-description
git checkout -b docs/documentation-update
```

### 3. Make Your Changes

- Write clean, well-documented code
- Follow the coding standards outlined below
- Add tests for new functionality
- Update documentation as needed

### 4. Test Your Changes

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=utils --cov=components

# Run specific test file
pytest tests/test_auth.py

# Run linting
black --check .
isort --check-only .
```

### 5. Commit Your Changes

```bash
# Stage files
git add .

# Commit with descriptive message
git commit -m "feat: add support for new LLM provider

- Add provider configuration in llm_handler.py
- Update sidebar with new provider options
- Add tests for new provider integration

Closes #123"
```

### 6. Sync with Upstream

```bash
# Fetch latest changes
git fetch upstream

# Rebase your branch on latest main
git rebase upstream/main

# Resolve any conflicts if needed
git add .
git rebase --continue
```

### 7. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
# Link to any related issues
```

---

## Types of Contributions

### Bug Reports

When reporting a bug, include:

- **Clear title**: Descriptive summary of the bug
- **Steps to reproduce**: Exact steps to recreate the issue
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**:
  - OS and version
  - Python version
  - Browser (if applicable)
- **Screenshots**: If applicable
- **Logs**: Error messages or stack traces

**Bug Report Template:**

```markdown
### Bug Description
Brief description of the bug.

### Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

### Expected Behavior
A clear and concise description of what you expected to happen.

### Screenshots
If applicable, add screenshots to help explain your problem.

### Environment
- OS: [e.g. Ubuntu 22.04]
- Python Version: [e.g. 3.11.5]
- Browser: [e.g. Chrome 120]

### Logs
```
Paste error logs here
```
```

### Feature Requests

When requesting a feature:

- **Use a clear title**: Summarize the feature
- **Describe the use case**: Why would this be useful?
- **Proposed solution**: How do you envision it working?
- **Alternatives considered**: Other approaches you've thought of
- **Additional context**: Any other relevant information

**Feature Request Template:**

```markdown
### Feature Description
A clear and concise description of the feature.

### Use Case
Describe the use case for this feature. Why would it be useful?

### Proposed Solution
A detailed description of how you would like this feature to work.

### Alternatives Considered
Describe any alternative solutions or features you've considered.

### Additional Context
Any other context, screenshots, or examples about the feature request.
```

### Documentation Improvements

Documentation is crucial for the project. You can help by:

- Fixing typos and grammar
- Adding missing examples
- Improving explanations
- Adding new sections
- Translating documentation

---

## Pull Request Guidelines

### PR Title Format

Use conventional commits format:

| Type | Description |
|------|-------------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation changes |
| `style:` | Code style changes (formatting, etc.) |
| `refactor:` | Code refactoring |
| `test:` | Adding or updating tests |
| `chore:` | Maintenance tasks |

Examples:
- `feat: add support for OpenAI API`
- `fix: resolve memory leak in PDF processing`
- `docs: update installation instructions`

### PR Description Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Related Issue
Fixes #123
Related to #456

## Changes Made
- Added support for new LLM provider
- Updated sidebar with provider selection
- Added comprehensive tests
- Updated API documentation

## Testing
- [ ] Unit tests pass locally
- [ ] Integration tests pass locally
- [ ] Manual testing completed
- [ ] Added new tests for new functionality

## Screenshots (if applicable)
[Upload screenshots here]

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have tested my changes locally
- [ ] I have added tests that prove my fix is effective or that my feature works
```

### Review Process

1. **Automated Checks**: CI runs tests and linting
2. **Code Review**: Maintainers review your code
3. **Feedback**: Address any review comments
4. **Approval**: Once approved, your PR will be merged

### Addressing Review Feedback

- Be open to feedback and suggestions
- Ask for clarification if needed
- Make requested changes promptly
- Mark comments as resolved when addressed

---

## Coding Standards

### Python Style Guide

Follow PEP 8 with these specifics:

```python
# Import order: stdlib, third-party, local
import os
import sys

import requests
import streamlit as st

from utils.auth import authenticate_user
from utils.llm_handler import LLMHandler

# Use type hints
def process_data(input_data: str) -> dict[str, str]:
    """Process input data and return results.

    Args:
        input_data: The data to process

    Returns:
        Dictionary containing processed results
    """
    return {"result": input_data.upper()}

# Use constants at module level
MAX_CHUNK_SIZE = 20000
DEFAULT_TIMEOUT = 60

# Use descriptive variable names
user_authentication_token = "abc123"  # Good
uat = "abc123"  # Bad
```

### Docstrings

Use Google-style docstrings:

```python
def generate_cards(
    text: str,
    density: str = "normal",
    answer_length: str = "medium"
) -> list[dict]:
    """Generate flashcards from text.

    This function processes the input text and generates
    flashcards based on the specified density and answer length.

    Args:
        text: Source text for card generation
        density: Card density ("low", "normal", "high")
        answer_length: Answer detail ("short", "medium", "long")

    Returns:
        List of card dictionaries with 'front', 'back', 'tags' keys

    Raises:
        ValueError: If density or answer_length is invalid

    Example:
        >>> cards = generate_cards("The heart pumps blood...")
        >>> len(cards) > 0
        True
    """
    # Implementation here
    pass
```

### Error Handling

```python
# Always handle exceptions
try:
    result = api_call()
except APIRateLimitError as e:
    logger.warning(f"Rate limited: {e}")
    return fallback_result
except APIError as e:
    logger.error(f"API error: {e}")
    raise
except Exception as e:
    logger.critical(f"Unexpected error: {e}", exc_info=True)
    raise
```

### Security Best Practices

```python
# Never hardcode secrets
api_key = os.getenv("API_KEY")  # Good
api_key = "sk-1234567890"  # Bad - NEVER DO THIS

# Validate user input
if not validate_email(user_email):
    raise ValueError("Invalid email format")

# Use parameterized queries
cursor.execute("SELECT * FROM users WHERE email = ?", (email,))  # Good
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")  # Bad - SQL injection risk

# Sanitize output before displaying
st.markdown(sanitize_html(user_input))  # Good
st.markdown(user_input)  # Bad - XSS risk
```

---

## Testing Guidelines

### Writing Tests

```python
import pytest
from utils.auth import register_user, authenticate_user


class TestAuthentication:
    """Test authentication functions."""

    def test_register_user_success(self, tmp_path):
        """Test successful user registration."""
        # Arrange
        email = "test@example.com"
        password = "SecurePass123"

        # Act
        success, message = register_user(email, password)

        # Assert
        assert success is True
        assert "successfully" in message.lower()

    def test_register_user_weak_password(self):
        """Test registration with weak password."""
        success, message = register_user("test@example.com", "weak")
        assert success is False
        assert "8 characters" in message

    def test_authenticate_user_valid_credentials(self, registered_user):
        """Test authentication with valid credentials."""
        email, password = registered_user
        success, token = authenticate_user(email, password)
        assert success is True
        assert len(token) > 0
```

### Test Coverage

Maintain test coverage above 80%:

```bash
# Check coverage
pytest --cov=utils --cov=components --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Test Organization

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_auth.py             # Auth tests
├── test_llm_handler.py      # LLM handler tests
├── test_pdf_processor.py    # PDF processor tests
└── test_rag.py              # RAG tests
```

---

## Documentation Guidelines

### Code Comments

```python
# Good: Explains WHY, not WHAT
# Use bcrypt instead of SHA-256 for better security against rainbow tables
hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# Bad: Just repeats the code
# Hash the password
hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

### README Updates

When adding features:
- Update the features list
- Add new configuration options
- Include new environment variables
- Update usage examples

### API Documentation

When modifying APIs:
- Update the API.md documentation
- Add examples for new endpoints
- Document breaking changes
- Update type hints

---

## Recognition

Contributors will be recognized in the CONTRIBUTORS.md file. Your name and contribution will be listed based on your GitHub profile.

### Contributors List

We use the "all-contributors" specification:

```markdown
## Contributors

Thanks to all these wonderful people:

<!-- prettier-ignore -->
<a href="https://github.com/thies2005"><img src="https://avatars.githubusercontent.com/u/123456?v=4" width="50" /></a>
<a href="https://github.com/otheruser"><img src="https://avatars.githubusercontent.com/u/789012?v=4" width="50" /></a>
```

---

## Getting Help

If you need help contributing:

1. **Read the documentation**: Start with [DEVELOPER.md](DEVELOPER.md)
2. **Check existing issues**: See if your question has been answered
3. **Ask in discussions**: Start a GitHub discussion
4. **Contact maintainers**: Reach out directly for urgent matters

### Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Python Style Guide](https://pep8.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](../LICENSE).

---

Thank you for contributing to the Medical PDF to Anki Converter! Your contributions help make this project better for everyone.

---

*Last updated: 2025*
