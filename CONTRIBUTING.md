# Contributing to AI Hub AI/ML Wrangler

Thank you for your interest in contributing to the AI Hub AI/ML Wrangler! We welcome contributions from the community and are grateful for any help you can provide.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Process](#development-process)
- [Style Guidelines](#style-guidelines)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)

## 📜 Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- **Be respectful**: Treat everyone with respect and consideration
- **Be collaborative**: Work together to resolve conflicts and find solutions
- **Be inclusive**: Welcome and support people of all backgrounds and identities
- **Be professional**: Maintain professionalism in all interactions

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/[your-username]/aihub_ai_ml_wrangler.git
   cd aihub_ai_ml_wrangler
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/[original-username]/aihub_ai_ml_wrangler.git
   ```
4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🤝 How to Contribute

### Types of Contributions

- **Bug Fixes**: Fix issues reported in GitHub Issues
- **Features**: Implement new features from the roadmap
- **Documentation**: Improve or add documentation
- **Tests**: Add missing tests or improve existing ones
- **Performance**: Optimize code for better performance
- **Refactoring**: Improve code quality and maintainability

### Before You Start

1. Check [existing issues](https://github.com/[username]/aihub_ai_ml_wrangler/issues) to avoid duplicates
2. For major changes, open an issue first to discuss the proposal
3. Ensure your idea aligns with the project's goals and roadmap

## 💻 Development Process

### Setting Up Development Environment

1. **Install dependencies**:
   ```bash
   npm install
   cd backend && pip install -r requirements.txt && cd ..
   ```

2. **Set up pre-commit hooks**:
   ```bash
   npm run setup:hooks
   ```

3. **Run tests** to ensure everything works:
   ```bash
   npm test
   ```

### Development Workflow

1. **Make your changes** in your feature branch
2. **Write/update tests** for your changes
3. **Run tests locally**:
   ```bash
   # Frontend tests
   cd frontend && npm test
   
   # Backend tests
   cd backend && pytest
   ```
4. **Lint your code**:
   ```bash
   npm run lint
   ```
5. **Update documentation** if needed

## 📝 Style Guidelines

### Frontend (TypeScript/React)

- Use TypeScript for all new code
- Follow the existing component structure
- Use functional components with hooks
- Maintain consistent naming conventions:
  - Components: PascalCase
  - Functions/variables: camelCase
  - Constants: UPPER_SNAKE_CASE
- Use Tailwind CSS for styling

### Backend (Python)

- Follow PEP 8 style guide
- Use type hints for function parameters and returns
- Write docstrings for all functions and classes
- Maintain consistent naming conventions:
  - Classes: PascalCase
  - Functions/variables: snake_case
  - Constants: UPPER_SNAKE_CASE

### General Guidelines

- Keep functions small and focused
- Write self-documenting code
- Add comments for complex logic
- Avoid code duplication
- Handle errors appropriately

## 💬 Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

### Examples

```bash
feat(imputation): add KNN imputation method

fix(api): handle null values in correlation endpoint

docs(readme): update installation instructions
```

## 🔄 Pull Request Process

1. **Update your branch** with the latest upstream changes:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push your changes** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request** on GitHub with:
   - Clear title describing the change
   - Description of what changed and why
   - Reference to any related issues
   - Screenshots for UI changes
   - Test results

4. **PR Requirements**:
   - All tests must pass
   - Code must be properly linted
   - Documentation must be updated
   - PR must be reviewed by at least one maintainer

5. **After Review**:
   - Address any feedback
   - Squash commits if requested
   - Ensure branch is up to date with main

## 🐛 Reporting Issues

### Bug Reports

When reporting bugs, include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Detailed steps to reproduce the issue
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**:
   - OS and version
   - Browser and version
   - Node.js version
   - Python version
6. **Screenshots/Logs**: If applicable
7. **Additional Context**: Any other relevant information

### Feature Requests

When requesting features, include:

1. **Problem Statement**: What problem does this solve?
2. **Proposed Solution**: How should it work?
3. **Alternatives Considered**: Other approaches you've thought about
4. **Additional Context**: Use cases, examples, mockups

## 🏗️ Project Structure

Understanding the project structure helps in making contributions:

```
aihub_ai_ml_wrangler/
├── frontend/          # React TypeScript application
├── backend/           # FastAPI Python application
├── docker/           # Docker configurations
├── docs/            # Documentation
├── tests/           # End-to-end tests
└── scripts/         # Utility scripts
```

## 🧪 Testing Guidelines

- Write tests for all new features
- Maintain test coverage above 80%
- Use meaningful test descriptions
- Test edge cases and error conditions
- Mock external dependencies

### Frontend Testing

```typescript
describe('ComponentName', () => {
  it('should render correctly', () => {
    // Test implementation
  });
  
  it('should handle user interaction', () => {
    // Test implementation
  });
});
```

### Backend Testing

```python
def test_function_name():
    """Test description"""
    # Test implementation
    assert expected == actual
```

## 📚 Resources

- [Project Documentation](docs/)
- [API Reference](docs/api-reference.md)
- [Development Guide](docs/development.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)

## 🙏 Recognition

Contributors will be recognized in:
- The project's README
- Release notes
- The contributors page

## 📧 Questions?

If you have questions, feel free to:
- Open a [discussion](https://github.com/[username]/aihub_ai_ml_wrangler/discussions)
- Ask in an [issue](https://github.com/[username]/aihub_ai_ml_wrangler/issues)
- Contact the maintainers

Thank you for contributing to AI Hub AI/ML Wrangler! 🎉