#!/usr/bin/env python3
"""
Codex Setup Script for Cosmic Council Framework
Automates the setup and configuration of Codex integration
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

def run_command(command: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        return result
    except subprocess.TimeoutExpired:
        print(f"Command timed out: {' '.join(command)}")
        return subprocess.CompletedProcess(command, 1, "", "Command timed out")
    except Exception as e:
        print(f"Error running command: {e}")
        return subprocess.CompletedProcess(command, 1, "", str(e))

def check_dependencies() -> bool:
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    # Check Node.js
    result = run_command(["node", "--version"])
    if result.returncode != 0:
        print("❌ Node.js is not installed. Please install Node.js first.")
        return False
    print(f"✅ Node.js version: {result.stdout.strip()}")
    
    # Check npm
    result = run_command(["npm", "--version"])
    if result.returncode != 0:
        print("❌ npm is not installed. Please install npm first.")
        return False
    print(f"✅ npm version: {result.stdout.strip()}")
    
    # Check Python
    result = run_command([sys.executable, "--version"])
    if result.returncode != 0:
        print("❌ Python is not available.")
        return False
    print(f"✅ Python version: {result.stdout.strip()}")
    
    return True

def install_codex_cli() -> bool:
    """Install Codex CLI globally."""
    print("📦 Installing Codex CLI...")
    
    result = run_command(["npm", "install", "-g", "@openai/codex"])
    if result.returncode != 0:
        print(f"❌ Failed to install Codex CLI: {result.stderr}")
        return False
    
    print("✅ Codex CLI installed successfully")
    return True

def verify_codex_installation() -> bool:
    """Verify Codex CLI installation."""
    print("🔍 Verifying Codex CLI installation...")
    
    result = run_command(["codex", "--version"])
    if result.returncode != 0:
        print(f"❌ Codex CLI not found: {result.stderr}")
        return False
    
    print(f"✅ Codex CLI version: {result.stdout.strip()}")
    return True

def setup_codex_config() -> bool:
    """Set up Codex configuration."""
    print("⚙️ Setting up Codex configuration...")
    
    project_root = Path(__file__).parent
    codex_dir = project_root / ".codex"
    config_file = codex_dir / "config.toml"
    
    # Create .codex directory if it doesn't exist
    codex_dir.mkdir(exist_ok=True)
    
    # Check if config already exists
    if config_file.exists():
        print("✅ Codex configuration already exists")
        return True
    
    # Copy the template config
    template_config = project_root / ".codex" / "config.toml"
    if template_config.exists():
        print("✅ Using existing Codex configuration template")
        return True
    
    print("❌ Codex configuration template not found")
    return False

def setup_environment_variables() -> bool:
    """Set up environment variables."""
    print("🔧 Setting up environment variables...")
    
    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("  Windows: set OPENAI_API_KEY=your-api-key-here")
        print("  Linux/Mac: export OPENAI_API_KEY=your-api-key-here")
        return False
    
    print("✅ OPENAI_API_KEY is set")
    return True

def authenticate_codex() -> bool:
    """Authenticate with Codex."""
    print("🔐 Authenticating with Codex...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No API key available for authentication")
        return False
    
    result = run_command(["codex", "login", "--api-key", api_key])
    if result.returncode != 0:
        print(f"❌ Failed to authenticate with Codex: {result.stderr}")
        return False
    
    print("✅ Successfully authenticated with Codex")
    return True

def test_codex_integration() -> bool:
    """Test Codex integration."""
    print("🧪 Testing Codex integration...")
    
    # Test basic Codex functionality
    result = run_command([
        "codex", "exec", 
        "--approval-policy", "never",
        "--sandbox", "read-only",
        "echo 'Codex integration test successful'"
    ])
    
    if result.returncode != 0:
        print(f"❌ Codex integration test failed: {result.stderr}")
        return False
    
    print("✅ Codex integration test successful")
    return True

def setup_git_hooks() -> bool:
    """Set up Git hooks for Codex integration."""
    print("🪝 Setting up Git hooks...")
    
    project_root = Path(__file__).parent
    git_hooks_dir = project_root / ".git" / "hooks"
    
    if not git_hooks_dir.exists():
        print("⚠️ Git repository not found, skipping Git hooks setup")
        return True
    
    # Pre-commit hook
    pre_commit_hook = git_hooks_dir / "pre-commit"
    if not pre_commit_hook.exists():
        pre_commit_content = """#!/bin/bash
# Codex pre-commit hook
echo "Running Codex pre-commit analysis..."
codex exec --approval-policy never --sandbox read-only "Analyze the staged changes for code quality issues, security vulnerabilities, and potential improvements. Provide a brief summary of findings."
"""
        try:
            with open(pre_commit_hook, 'w') as f:
                f.write(pre_commit_content)
            pre_commit_hook.chmod(0o755)
            print("✅ Pre-commit hook installed")
        except Exception as e:
            print(f"⚠️ Failed to install pre-commit hook: {e}")
    
    return True

def create_sample_scripts() -> bool:
    """Create sample scripts for common Codex operations."""
    print("📝 Creating sample scripts...")
    
    project_root = Path(__file__).parent
    scripts_dir = project_root / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    
    # Sample Codex commands script
    sample_script = scripts_dir / "codex_samples.py"
    if not sample_script.exists():
        sample_content = '''#!/usr/bin/env python3
"""
Sample Codex Commands for Cosmic Council Framework
Common Codex operations and examples
"""

import subprocess
import sys
from pathlib import Path

def run_codex_command(prompt: str, **kwargs):
    """Run a Codex command with the given prompt and options."""
    cmd = ["codex", "exec"]
    
    # Add options
    if kwargs.get("approval_policy"):
        cmd.extend(["--approval-policy", kwargs["approval_policy"]])
    if kwargs.get("sandbox"):
        cmd.extend(["--sandbox", kwargs["sandbox"]])
    if kwargs.get("model"):
        cmd.extend(["--model", kwargs["model"]])
    
    cmd.append(prompt)
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode == 0

def main():
    """Run sample Codex commands."""
    print("🚀 Cosmic Council Codex Sample Commands")
    print("=" * 50)
    
    # Example 1: Code quality analysis
    print("\\n1. Analyzing code quality...")
    run_codex_command(
        "Analyze the codebase for code quality issues, performance bottlenecks, and security vulnerabilities. Provide specific recommendations.",
        approval_policy="never",
        sandbox="read-only"
    )
    
    # Example 2: Test generation
    print("\\n2. Generating tests...")
    run_codex_command(
        "Generate comprehensive unit tests for the API layer. Focus on edge cases and error conditions.",
        approval_policy="on-failure",
        sandbox="workspace-write"
    )
    
    # Example 3: Documentation update
    print("\\n3. Updating documentation...")
    run_codex_command(
        "Update the README files with current usage examples and setup instructions.",
        approval_policy="on-failure",
        sandbox="workspace-write"
    )

if __name__ == "__main__":
    main()
'''
        try:
            with open(sample_script, 'w') as f:
                f.write(sample_content)
            print("✅ Sample scripts created")
        except Exception as e:
            print(f"⚠️ Failed to create sample scripts: {e}")
    
    return True

def main():
    """Main setup function."""
    print("🚀 Cosmic Council Codex Setup")
    print("=" * 40)
    
    steps = [
        ("Checking dependencies", check_dependencies),
        ("Installing Codex CLI", install_codex_cli),
        ("Verifying installation", verify_codex_installation),
        ("Setting up configuration", setup_codex_config),
        ("Setting up environment", setup_environment_variables),
        ("Authenticating with Codex", authenticate_codex),
        ("Testing integration", test_codex_integration),
        ("Setting up Git hooks", setup_git_hooks),
        ("Creating sample scripts", create_sample_scripts),
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        print(f"\\n📋 {step_name}...")
        try:
            if not step_func():
                failed_steps.append(step_name)
                print(f"❌ {step_name} failed")
            else:
                print(f"✅ {step_name} completed")
        except Exception as e:
            print(f"❌ {step_name} failed with error: {e}")
            failed_steps.append(step_name)
    
    print("\\n" + "=" * 40)
    if failed_steps:
        print(f"⚠️ Setup completed with {len(failed_steps)} failed steps:")
        for step in failed_steps:
            print(f"  - {step}")
        print("\\nPlease address the failed steps before using Codex.")
        return 1
    else:
        print("🎉 Codex setup completed successfully!")
        print("\\nNext steps:")
        print("1. Review the CODEX_INTEGRATION_GUIDE.md for usage instructions")
        print("2. Try running: python scripts/codex_samples.py")
        print("3. Use the enhanced deployment scripts: scripts/codex_deploy.sh")
        print("4. Set up CI/CD integration with the GitHub Actions workflow")
        return 0

if __name__ == "__main__":
    sys.exit(main())
