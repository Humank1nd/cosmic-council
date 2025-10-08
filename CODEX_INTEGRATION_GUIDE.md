# Codex Integration Guide for Cosmic Council Framework

This guide provides comprehensive instructions for integrating and using Codex with your Cosmic Council AI-Powered Problem Solving System.

## 🚀 Quick Start

### 1. Install Codex CLI

```bash
# Install globally via npm
npm install -g @openai/codex

# Verify installation
codex --version
```

### 2. Authenticate with OpenAI

```bash
# Login with your API key
codex login --api-key YOUR_OPENAI_API_KEY

# Or set environment variable
export OPENAI_API_KEY=your-api-key-here
```

### 3. Configure Codex for Cosmic Council

The project includes a pre-configured `.codex/config.toml` file optimized for your codebase. Key features:

- **Approval Policy**: `on-failure` (safe for development)
- **Sandbox Mode**: `workspace-write` (allows file modifications)
- **Model**: `o1-preview` (latest reasoning model)
- **Base Instructions**: Tailored for Cosmic Council coding standards

## 🔧 Integration Options

### Option 1: CI/CD Pipeline Integration (Recommended)

The project includes a comprehensive GitHub Actions workflow (`.github/workflows/codex-automation.yml`) that:

- **Automated Code Improvements**: Runs weekly to improve code quality
- **Test Generation**: Generates tests for changed files in PRs
- **Documentation Updates**: Keeps docs current with code changes
- **Changelog Generation**: Automatically updates CHANGELOG.md

**Setup:**
1. Add `OPENAI_API_KEY` to your GitHub repository secrets
2. The workflow will automatically run on pushes and PRs
3. Weekly improvements run every Monday at 2 AM

### Option 2: MCP Server Integration

For multi-agent systems, Codex can run as an MCP server:

```bash
# Start the MCP server
python -m src.cosmic_council.mcp_server

# Use with MCP Inspector
npx @modelcontextprotocol/inspector codex mcp
```

**Available Tools:**
- `codex_execute`: Run Codex with custom prompts
- `codex_resume`: Continue previous sessions
- `codex_analyze_codebase`: Analyze code quality
- `codex_generate_tests`: Generate comprehensive tests

### Option 3: Local Development Integration

Use the enhanced deployment and testing scripts:

```bash
# Enhanced deployment with Codex analysis
./scripts/codex_deploy.sh development deploy

# Intelligent test generation and optimization
python scripts/codex_test_runner.py --action full

# Codex-powered health checks
./scripts/codex_deploy.sh production health
```

## 📋 Usage Examples

### 1. Automated Code Improvements

```bash
# Run Codex to improve code quality
codex exec --full-auto "Review and improve code quality, add missing tests, and optimize performance across the entire codebase"

# Focus on specific areas
codex exec --full-auto "Improve error handling and add comprehensive logging to the API layer"
```

### 2. Test Generation

```bash
# Generate tests for specific files
codex exec --full-auto "Generate comprehensive unit tests for src/api/routes.py and src/core/services.py"

# Generate integration tests
codex exec --full-auto "Create integration tests for the database layer and API endpoints"
```

### 3. Documentation Updates

```bash
# Update API documentation
codex exec --full-auto "Update API documentation in docs/ to reflect current code changes"

# Improve README files
codex exec --full-auto "Update all README files with current usage examples and setup instructions"
```

### 4. Deployment Optimization

```bash
# Analyze deployment readiness
codex exec --approval-policy on-failure --sandbox read-only "Analyze the codebase for deployment readiness and provide recommendations"

# Optimize Docker configuration
codex exec --approval-policy on-failure --sandbox workspace-write "Review and optimize Docker configuration for better performance and security"
```

## 🛠️ Advanced Configuration

### Environment-Specific Profiles

The `.codex/config.toml` includes profiles for different environments:

```toml
[profiles.development]
approval_policy = "on-failure"
sandbox = "workspace-write"
model = "o1-mini"

[profiles.production]
approval_policy = "untrusted"
sandbox = "read-only"
model = "o1-preview"
```

Use profiles with:
```bash
codex exec --profile production "Analyze production readiness"
```

### Custom Base Instructions

Modify the base instructions in `.codex/config.toml` to include project-specific guidelines:

```toml
base_instructions = """
Your custom instructions here...
Focus on specific patterns, libraries, or architectural decisions.
"""
```

### MCP Server Configuration

Configure additional MCP servers in `.codex/config.toml`:

```toml
[mcp_servers.custom-tool]
command = "python"
args = ["-m", "your.custom.mcp_server"]
env = { "API_KEY" = "your-api-key" }
```

## 🔍 Monitoring and Logging

### Enable Verbose Logging

```bash
# Set environment variable for detailed logs
export RUST_LOG=codex_core=debug,codex_tui=debug

# Monitor logs in real-time
tail -F ~/.codex/log/codex-tui.log
```

### CI/CD Monitoring

The GitHub Actions workflow includes comprehensive logging and reporting:

- **Test Results**: Detailed test execution reports
- **Code Quality**: Coverage and quality metrics
- **Performance**: Build and deployment timing
- **Security**: Vulnerability scanning results

## 🚨 Safety and Security

### Approval Policies

- **`untrusted`**: Require approval for all commands (production)
- **`on-failure`**: Require approval only on failures (development)
- **`never`**: No approval required (testing only)

### Sandbox Modes

- **`read-only`**: No file modifications (analysis only)
- **`workspace-write`**: Allow file modifications (development)
- **`danger-full-access`**: Full system access (use with caution)

### Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for sensitive data
3. **Review all changes** before applying to production
4. **Use read-only mode** for production analysis
5. **Enable approval policies** for critical environments

## 📊 Performance Optimization

### Parallel Execution

Enable parallel execution in `.codex/config.toml`:

```toml
[performance]
parallel_execution = true
max_parallel_tasks = 3
max_execution_time = 600
```

### Caching

Codex automatically caches results. Clear cache when needed:

```bash
# Clear Codex cache
rm -rf ~/.codex/cache/*
```

## 🔄 Session Management

### Resume Previous Sessions

```bash
# Resume the most recent session
codex resume --last

# Resume specific session
codex resume <SESSION_ID>

# Continue with new prompt
codex exec "continue the previous task" resume --last
```

### Session History

View session history:
```bash
# List recent sessions
ls ~/.codex/sessions/

# View session details
cat ~/.codex/sessions/<SESSION_ID>.json
```

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```bash
   # Re-authenticate
   codex login --api-key YOUR_API_KEY
   ```

2. **Permission Errors**
   ```bash
   # Check file permissions
   ls -la scripts/
   chmod +x scripts/codex_deploy.sh
   ```

3. **Timeout Issues**
   ```bash
   # Increase timeout in config
   # Edit .codex/config.toml
   max_execution_time = 1200  # 20 minutes
   ```

4. **Memory Issues**
   ```bash
   # Reduce parallel tasks
   # Edit .codex/config.toml
   max_parallel_tasks = 1
   ```

### Debug Mode

Enable debug logging:
```bash
export RUST_LOG=codex_core=debug
codex exec "your prompt here"
```

## 📈 Best Practices

### 1. Start Small
- Begin with read-only analysis
- Gradually increase permissions
- Test in development first

### 2. Be Specific
- Use detailed prompts
- Specify file patterns
- Include context and requirements

### 3. Review Changes
- Always review generated code
- Test changes thoroughly
- Use version control

### 4. Monitor Performance
- Track execution times
- Monitor resource usage
- Optimize configurations

### 5. Security First
- Use appropriate approval policies
- Limit sandbox permissions
- Audit all changes

## 🎯 Use Cases for Cosmic Council

### 1. Code Quality Improvement
- Automated refactoring
- Performance optimization
- Security enhancement
- Documentation updates

### 2. Test Generation
- Unit test creation
- Integration test development
- E2E test automation
- Test data generation

### 3. Deployment Automation
- Pre-deployment analysis
- Configuration optimization
- Health check enhancement
- Rollback procedures

### 4. Documentation
- API documentation updates
- README improvements
- Code comments enhancement
- Architecture documentation

### 5. Multi-Agent Integration
- MCP server deployment
- Agent communication
- Workflow automation
- Task coordination

## 📚 Additional Resources

- [Codex CLI Documentation](https://github.com/openai/codex-cli)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Cosmic Council Project Structure](README.md)

## 🤝 Support

For issues specific to Cosmic Council integration:
1. Check the troubleshooting section
2. Review the configuration files
3. Enable debug logging
4. Create an issue in the project repository

For Codex CLI issues:
1. Check the [Codex CLI repository](https://github.com/openai/codex-cli)
2. Review the official documentation
3. Check OpenAI API status
