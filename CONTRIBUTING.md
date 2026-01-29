# Contributing to Clawdbot SMTP Tool

Thanks for your interest in contributing!

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/clawdbot-smtp.git
cd clawdbot-smtp

# Install dependencies
pip install -r requirements.txt

# Run tests (add tests later)
python -m pytest tests/

# Run CLI
python -m email_cli --help
```

## Code Style

- Follow PEP 8
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small

## Feature Ideas

- Add OAuth2 authentication support
- Add more email templates
- Add email filtering and auto-forwarding
- Add calendar integration
- Add support for sending calendar invites
- Add email threading support
- Add support for flags (starred, important, etc.)
- Add email export to different formats

## Bug Reports

When reporting bugs, please include:
- Your Python version
- Your OS
- Steps to reproduce the issue
- Expected vs actual behavior
- Any error messages

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
