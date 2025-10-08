#!/usr/bin/env python3
"""
Codex MCP Server for Cosmic Council Framework
Provides Codex capabilities as an MCP server for multi-agent integration
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodexMCPServer:
    """MCP Server that provides Codex capabilities to other agents."""
    
    def __init__(self):
        self.server = Server("codex-cosmic-council")
        self.setup_handlers()
        self.codex_config = self._load_codex_config()
    
    def _load_codex_config(self) -> Dict[str, Any]:
        """Load Codex configuration from environment or defaults."""
        return {
            "approval_policy": os.getenv("CODEX_APPROVAL_POLICY", "on-failure"),
            "sandbox": os.getenv("CODEX_SANDBOX", "workspace-write"),
            "model": os.getenv("CODEX_MODEL", "o1-preview"),
            "base_instructions": self._get_base_instructions(),
        }
    
    def _get_base_instructions(self) -> str:
        """Get base instructions for Codex based on Cosmic Council standards."""
        return """
        You are working with the Cosmic Council AI-Powered Problem Solving System.
        
        Follow these guidelines:
        - Use feature-based directory structure
        - Keep files under 300 lines
        - One class per file (except for related classes)
        - Use snake_case for functions and variables
        - Use PascalCase for classes
        - Add type hints for all functions and methods
        - Add docstrings for all public methods and classes
        - Follow the established directory structure in src/
        - Use async/await for I/O operations
        - Implement proper error handling with specific exception types
        - Add comprehensive tests for new functionality
        
        Current project structure:
        - src/api/ - API layer (routes, middleware, schemas)
        - src/core/ - Core business logic (models, services, workflows)
        - src/agents/ - AI agent system
        - src/database/ - Database layer (models, repositories, migrations)
        - src/integrations/ - External system integrations
        - src/utils/ - Utility functions
        - src/web/ - Web interface components
        """
    
    def setup_handlers(self):
        """Set up MCP server handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available Codex tools."""
            return [
                Tool(
                    name="codex_execute",
                    description="Execute Codex with a specific prompt and configuration",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "The prompt to send to Codex"
                            },
                            "approval_policy": {
                                "type": "string",
                                "enum": ["untrusted", "on-failure", "never"],
                                "description": "Approval policy for shell commands"
                            },
                            "sandbox": {
                                "type": "string",
                                "enum": ["read-only", "workspace-write", "danger-full-access"],
                                "description": "Sandbox mode for Codex"
                            },
                            "model": {
                                "type": "string",
                                "description": "Model to use (e.g., o1-preview, o1-mini)"
                            },
                            "cwd": {
                                "type": "string",
                                "description": "Working directory for the session"
                            }
                        },
                        "required": ["prompt"]
                    }
                ),
                Tool(
                    name="codex_resume",
                    description="Resume a previous Codex session",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "conversation_id": {
                                "type": "string",
                                "description": "The conversation ID to resume"
                            },
                            "prompt": {
                                "type": "string",
                                "description": "Additional prompt to continue the conversation"
                            }
                        },
                        "required": ["conversation_id", "prompt"]
                    }
                ),
                Tool(
                    name="codex_analyze_codebase",
                    description="Analyze the codebase and provide improvement suggestions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "focus_area": {
                                "type": "string",
                                "description": "Specific area to focus on (e.g., 'performance', 'security', 'testing')"
                            },
                            "file_pattern": {
                                "type": "string",
                                "description": "File pattern to analyze (e.g., 'src/api/*.py')"
                            }
                        }
                    }
                ),
                Tool(
                    name="codex_generate_tests",
                    description="Generate comprehensive tests for specific files or modules",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "target_files": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of files to generate tests for"
                            },
                            "test_type": {
                                "type": "string",
                                "enum": ["unit", "integration", "e2e"],
                                "description": "Type of tests to generate"
                            }
                        },
                        "required": ["target_files"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            try:
                if name == "codex_execute":
                    return await self._execute_codex(arguments)
                elif name == "codex_resume":
                    return await self._resume_codex(arguments)
                elif name == "codex_analyze_codebase":
                    return await self._analyze_codebase(arguments)
                elif name == "codex_generate_tests":
                    return await self._generate_tests(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _execute_codex(self, args: Dict[str, Any]) -> List[TextContent]:
        """Execute Codex with the given arguments."""
        prompt = args["prompt"]
        approval_policy = args.get("approval_policy", self.codex_config["approval_policy"])
        sandbox = args.get("sandbox", self.codex_config["sandbox"])
        model = args.get("model", self.codex_config["model"])
        cwd = args.get("cwd", os.getcwd())
        
        # Build Codex command
        cmd = [
            "codex", "exec",
            "--approval-policy", approval_policy,
            "--sandbox", sandbox,
            "--model", model,
            "--cwd", cwd,
            prompt
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=600  # 10 minute timeout
            )
            
            output = {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "command": " ".join(cmd)
            }
            
            return [TextContent(type="text", text=json.dumps(output, indent=2))]
            
        except subprocess.TimeoutExpired:
            return [TextContent(type="text", text="Codex execution timed out after 10 minutes")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error executing Codex: {str(e)}")]
    
    async def _resume_codex(self, args: Dict[str, Any]) -> List[TextContent]:
        """Resume a previous Codex session."""
        conversation_id = args["conversation_id"]
        prompt = args["prompt"]
        
        cmd = [
            "codex", "exec", "resume", conversation_id,
            prompt
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            output = {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "conversation_id": conversation_id
            }
            
            return [TextContent(type="text", text=json.dumps(output, indent=2))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error resuming Codex session: {str(e)}")]
    
    async def _analyze_codebase(self, args: Dict[str, Any]) -> List[TextContent]:
        """Analyze the codebase and provide improvement suggestions."""
        focus_area = args.get("focus_area", "general")
        file_pattern = args.get("file_pattern", "src/**/*.py")
        
        prompt = f"""
        Analyze the Cosmic Council codebase with focus on {focus_area}.
        Look at files matching pattern: {file_pattern}
        
        Provide:
        1. Code quality assessment
        2. Performance optimization opportunities
        3. Security improvements
        4. Test coverage gaps
        5. Documentation improvements
        6. Specific actionable recommendations
        
        Focus on the Cosmic Council coding standards and architecture.
        """
        
        return await self._execute_codex({"prompt": prompt})
    
    async def _generate_tests(self, args: Dict[str, Any]) -> List[TextContent]:
        """Generate comprehensive tests for specific files."""
        target_files = args["target_files"]
        test_type = args.get("test_type", "unit")
        
        files_str = ", ".join(target_files)
        prompt = f"""
        Generate comprehensive {test_type} tests for the following files: {files_str}
        
        Requirements:
        - Follow the existing test patterns in tests/ directory
        - Use pytest framework
        - Include edge cases and error conditions
        - Add proper fixtures and mocks
        - Ensure good test coverage
        - Follow Cosmic Council testing standards
        - Add docstrings to test functions
        - Use descriptive test names
        
        Create test files in the appropriate tests/ subdirectory.
        """
        
        return await self._execute_codex({"prompt": prompt})
    
    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="codex-cosmic-council",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )

async def main():
    """Main entry point."""
    server = CodexMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
