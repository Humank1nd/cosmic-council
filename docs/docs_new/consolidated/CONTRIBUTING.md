# Contributing to the Cosmic Council Framework

## Welcome Contributors! 🐘

Thank you for your interest in contributing to the Cosmic Council Framework! This guide will help you get started with contributing to our open-source project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Documentation](#documentation)
- [Testing](#testing)
- [Code Style](#code-style)
- [Release Process](#release-process)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to conduct@cosmic-council.org.

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

Examples of behavior that contributes to creating a positive environment include:

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- PostgreSQL 13 or higher
- Redis 6.0 or higher
- Node.js 16 or higher (for frontend development)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/your-username/framework.git
cd framework
```

3. Add the upstream repository:

```bash
git remote add upstream https://github.com/cosmic-council/framework.git
```

## Development Setup

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install the package in development mode
pip install -e .
```

### 3. Set Up Database

```bash
# Start PostgreSQL and Redis services
# On macOS with Homebrew:
brew services start postgresql
brew services start redis

# On Ubuntu/Debian:
sudo systemctl start postgresql
sudo systemctl start redis-server

# Create database
createdb cosmic_council_dev

# Run migrations
python -m database_migrations run_migrations
```

### 4. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

### 5. Run Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m e2e

# Run with coverage
pytest --cov=src --cov-report=html
```

### 6. Start Development Server

```bash
# Start the web interface
python web_interface.py

# Start the API server
python cosmic_council_api.py
```

## Contributing Guidelines

### Types of Contributions

We welcome several types of contributions:

- **Bug Fixes**: Fix issues in existing code
- **Feature Development**: Add new functionality
- **Documentation**: Improve or add documentation
- **Testing**: Add or improve tests
- **Performance**: Optimize existing code
- **Security**: Improve security measures

### Development Workflow

1. **Create a Branch**: Create a feature branch from `main`
2. **Make Changes**: Implement your changes
3. **Test**: Ensure all tests pass
4. **Document**: Update documentation if needed
5. **Commit**: Make clear, descriptive commits
6. **Push**: Push your branch to your fork
7. **Pull Request**: Create a pull request

### Branch Naming

Use descriptive branch names:

- `feature/add-new-enterprise-agent`
- `fix/database-connection-issue`
- `docs/update-api-documentation`
- `test/add-integration-tests`

## Pull Request Process

### Before Submitting

1. **Update Documentation**: Update relevant documentation
2. **Add Tests**: Add tests for new functionality
3. **Run Tests**: Ensure all tests pass
4. **Check Code Style**: Follow the project's code style
5. **Update CHANGELOG**: Add entry to CHANGELOG.md

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] CHANGELOG updated
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs automatically
2. **Code Review**: Maintainers review the code
3. **Testing**: Manual testing may be required
4. **Approval**: At least one maintainer approval required
5. **Merge**: Maintainer merges the PR

## Issue Reporting

### Bug Reports

When reporting bugs, please include:

- **Description**: Clear description of the bug
- **Steps to Reproduce**: Detailed steps to reproduce
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**: OS, Python version, etc.
- **Screenshots**: If applicable

### Feature Requests

When requesting features, please include:

- **Description**: Clear description of the feature
- **Use Case**: Why this feature is needed
- **Proposed Solution**: How you think it should work
- **Alternatives**: Other solutions you've considered

### Issue Templates

Use the provided issue templates:

- Bug Report: `.github/ISSUE_TEMPLATE/bug_report.md`
- Feature Request: `.github/ISSUE_TEMPLATE/feature_request.md`

## Documentation

### Documentation Standards

- **Clear and Concise**: Write clear, easy-to-understand documentation
- **Examples**: Include code examples where helpful
- **Up-to-Date**: Keep documentation current with code changes
- **Formatting**: Use consistent formatting and structure

### Documentation Types

- **API Documentation**: Document all API endpoints
- **User Guides**: Step-by-step user instructions
- **Developer Guides**: Technical implementation details
- **Admin Guides**: System administration information

### Documentation Structure

```
docs/
├── user-guides/
│   ├── getting-started.md
│   ├── problem-types.md
│   └── best-practices.md
├── developer-guides/
│   ├── api-integration.md
│   ├── custom-agents.md
│   └── plugin-development.md
├── admin-guides/
│   ├── system-admin.md
│   ├── user-management.md
│   └── monitoring.md
└── api-documentation.md
```

## Testing

### Test Categories

- **Unit Tests**: Test individual components
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Performance Tests**: Test system performance
- **Security Tests**: Test security measures

### Writing Tests

```python
import pytest
from cosmic_council_core import CosmicCouncil, ProblemStatement

class TestCosmicCouncil:
    def test_initialization(self):
        """Test Cosmic Council initialization"""
        council = CosmicCouncil()
        assert council is not None
        assert len(council.enterprises) == 6
    
    @pytest.mark.asyncio
    async def test_solve_problem(self):
        """Test problem solving"""
        council = CosmicCouncil()
        problem = ProblemStatement(
            title="Test Problem",
            description="Test description",
            complexity="simple",
            domain="Test"
        )
        
        result = await council.solve_problem(problem)
        assert result.status == "completed"
        assert result.overall_confidence > 0.0
```

### Test Guidelines

- **Test Coverage**: Aim for high test coverage
- **Test Names**: Use descriptive test names
- **Test Isolation**: Tests should be independent
- **Mocking**: Mock external dependencies
- **Fixtures**: Use pytest fixtures for common setup

## Code Style

### Python Style Guide

We follow PEP 8 with some modifications:

```python
# Use type hints
def solve_problem(self, problem: ProblemStatement) -> ProblemResult:
    """Solve a problem using the Cosmic Council framework.
    
    Args:
        problem: The problem to solve
        
    Returns:
        The solution result
        
    Raises:
        ValueError: If problem is invalid
    """
    if not problem:
        raise ValueError("Problem cannot be None")
    
    # Implementation here
    return result
```

### Code Formatting

We use Black for code formatting:

```bash
# Format code
black src/

# Check formatting
black --check src/
```

### Linting

We use flake8 for linting:

```bash
# Run linter
flake8 src/

# Run with configuration
flake8 --config=setup.cfg src/
```

### Import Organization

```python
# Standard library imports
import os
import sys
from typing import Dict, List, Optional

# Third-party imports
import asyncio
import pytest
from fastapi import FastAPI

# Local imports
from cosmic_council_core import CosmicCouncil
from database_models import Problem
```

## Release Process

### Version Numbering

We use Semantic Versioning (SemVer):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Steps

1. **Update Version**: Update version in `__init__.py`
2. **Update CHANGELOG**: Add release notes
3. **Create Tag**: Create git tag for version
4. **Build Package**: Build distribution packages
5. **Upload**: Upload to PyPI
6. **Release Notes**: Create GitHub release

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Version bumped
- [ ] Tag created
- [ ] Package built
- [ ] Package uploaded
- [ ] Release notes created

## Community

### Getting Help

- **Documentation**: Check the documentation first
- **Issues**: Search existing issues
- **Discussions**: Use GitHub Discussions
- **Discord**: Join our Discord server
- **Email**: Contact us at support@cosmic-council.org

### Contributing to Discussions

- **Be Respectful**: Treat everyone with respect
- **Stay On Topic**: Keep discussions relevant
- **Provide Context**: Give enough context for others to understand
- **Search First**: Check if your question has been asked before

### Recognition

Contributors are recognized in:

- **CONTRIBUTORS.md**: List of all contributors
- **Release Notes**: Mentioned in release notes
- **GitHub**: Listed as contributors
- **Website**: Featured on our website

## Development Tools

### Recommended IDE

- **VS Code**: With Python extension
- **PyCharm**: Professional or Community edition
- **Vim/Neovim**: With Python plugins

### Useful Extensions

- **Python**: Python language support
- **Pylance**: Python language server
- **Black**: Code formatter
- **Flake8**: Linter
- **GitLens**: Git integration

### Development Scripts

```bash
# Run all checks
./scripts/check.sh

# Format code
./scripts/format.sh

# Run tests
./scripts/test.sh

# Build package
./scripts/build.sh
```

## License

By contributing to the Cosmic Council Framework, you agree that your contributions will be licensed under the MIT License.

## Questions?

If you have any questions about contributing, please:

1. Check the documentation
2. Search existing issues
3. Start a discussion
4. Contact us at contribute@cosmic-council.org

Thank you for contributing to the Cosmic Council Framework! 🚀
