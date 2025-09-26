"""
Cosmic Council Code Review Rules
Automated enforcement of repository rules and governance
"""

import ast
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ViolationType(Enum):
    """Types of rule violations"""
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"

class StageType(Enum):
    """Cosmic Council stages"""
    RESEARCH = "research"
    PLANNING = "planning"
    DEVELOPMENT = "development"
    BUDGET = "budget"
    MARKET = "market"
    SUPPORT = "support"
    SHARED = "shared"

@dataclass
class Violation:
    """Represents a rule violation"""
    violation_type: ViolationType
    rule_name: str
    description: str
    file_path: str
    line_number: int
    suggested_fix: str
    severity_score: int

class CosmicCouncilCodeReviewer:
    """
    Automated code reviewer that enforces Cosmic Council rules
    """
    
    def __init__(self):
        self.violations: List[Violation] = []
        self.stage_patterns = {
            StageType.RESEARCH: r"research|red_owl|inquiry",
            StageType.PLANNING: r"planning|orange_orangutan|logistics",
            StageType.DEVELOPMENT: r"development|yellow_honeybee|creativity",
            StageType.BUDGET: r"budget|green_tortoise|resources",
            StageType.MARKET: r"market|blue_dolphin|communication",
            StageType.SUPPORT: r"support|violet_elephant|feedback",
            StageType.SHARED: r"shared|common|utils"
        }
        
        # ROYGBV sequence enforcement
        self.roygbv_sequence = [
            StageType.RESEARCH,
            StageType.PLANNING,
            StageType.DEVELOPMENT,
            StageType.BUDGET,
            StageType.MARKET,
            StageType.SUPPORT
        ]

    def review_file(self, file_path: str, content: str) -> List[Violation]:
        """
        Review a single file for rule violations
        
        Args:
            file_path: Path to the file
            content: File content
            
        Returns:
            List of violations found
        """
        self.violations = []
        
        # Check file naming conventions
        self._check_file_naming(file_path)
        
        # Check directory structure
        self._check_directory_structure(file_path)
        
        # Parse Python files for additional checks
        if file_path.endswith('.py'):
            try:
                tree = ast.parse(content)
                self._check_python_code(file_path, tree, content)
            except SyntaxError as e:
                self.violations.append(Violation(
                    violation_type=ViolationType.CRITICAL,
                    rule_name="syntax_error",
                    description=f"Syntax error in Python file: {e}",
                    file_path=file_path,
                    line_number=e.lineno or 0,
                    suggested_fix="Fix syntax errors before submission",
                    severity_score=10
                ))
        
        # Check SQL files
        elif file_path.endswith('.sql'):
            self._check_sql_code(file_path, content)
        
        return self.violations

    def _check_file_naming(self, file_path: str):
        """Check file naming conventions"""
        filename = file_path.split('/')[-1]
        
        # Check for proper stage prefix
        stage_found = False
        for stage, pattern in self.stage_patterns.items():
            if re.search(pattern, filename, re.IGNORECASE):
                stage_found = True
                break
        
        if not stage_found and not filename.startswith(('test_', 'conftest', 'README', 'CHANGELOG')):
            self.violations.append(Violation(
                violation_type=ViolationType.MINOR,
                rule_name="file_naming_convention",
                description=f"File '{filename}' does not follow Cosmic Council naming conventions",
                file_path=file_path,
                line_number=0,
                suggested_fix="Rename file to include stage prefix (e.g., research_, planning_, etc.)",
                severity_score=2
            ))

    def _check_directory_structure(self, file_path: str):
        """Check directory structure compliance"""
        path_parts = file_path.split('/')
        
        # Check if file is in correct stage directory
        if len(path_parts) > 1:
            directory = path_parts[0]
            filename = path_parts[-1]
            
            # Determine expected stage from filename
            expected_stage = None
            for stage, pattern in self.stage_patterns.items():
                if re.search(pattern, filename, re.IGNORECASE):
                    expected_stage = stage
                    break
            
            # Check if file is in correct directory
            if expected_stage and expected_stage != StageType.SHARED:
                expected_dir = expected_stage.value
                if directory != expected_dir and not filename.startswith(('test_', 'conftest')):
                    self.violations.append(Violation(
                        violation_type=ViolationType.MINOR,
                        rule_name="directory_structure",
                        description=f"File '{filename}' should be in '{expected_dir}/' directory",
                        file_path=file_path,
                        line_number=0,
                        suggested_fix=f"Move file to {expected_dir}/ directory",
                        severity_score=2
                    ))

    def _check_python_code(self, file_path: str, tree: ast.AST, content: str):
        """Check Python code for rule violations"""
        
        # Check for proper imports
        self._check_imports(file_path, tree)
        
        # Check for docstrings
        self._check_docstrings(file_path, tree)
        
        # Check for type hints
        self._check_type_hints(file_path, tree)
        
        # Check for stage-specific patterns
        self._check_stage_patterns(file_path, content)
        
        # Check for ROYGBV sequence violations
        self._check_roygbv_sequence(file_path, content)

    def _check_imports(self, file_path: str, tree: ast.AST):
        """Check import statements for compliance"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self._validate_import(file_path, alias.name, node.lineno)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self._validate_import(file_path, node.module, node.lineno)

    def _validate_import(self, file_path: str, import_name: str, line_number: int):
        """Validate individual import"""
        # Check for cross-stage imports
        path_parts = file_path.split('/')
        if len(path_parts) > 1:
            current_stage = path_parts[0]
            
            # Check if importing from another stage (not allowed)
            for stage in self.stage_patterns:
                if stage.value != current_stage and stage != StageType.SHARED:
                    if re.search(stage.value, import_name, re.IGNORECASE):
                        self.violations.append(Violation(
                            violation_type=ViolationType.MAJOR,
                            rule_name="cross_stage_import",
                            description=f"Import from {stage.value} stage not allowed from {current_stage}",
                            file_path=file_path,
                            line_number=line_number,
                            suggested_fix=f"Use shared/ utilities or refactor to avoid cross-stage dependency",
                            severity_score=5
                        ))

    def _check_docstrings(self, file_path: str, tree: ast.AST):
        """Check for required docstrings"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    self.violations.append(Violation(
                        violation_type=ViolationType.MINOR,
                        rule_name="missing_docstring",
                        description=f"{type(node).__name__} '{node.name}' missing docstring",
                        file_path=file_path,
                        line_number=node.lineno,
                        suggested_fix="Add comprehensive docstring with type hints",
                        severity_score=2
                    ))

    def _check_type_hints(self, file_path: str, tree: ast.AST):
        """Check for type hints in function signatures"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Check return type annotation
                if not node.returns:
                    self.violations.append(Violation(
                        violation_type=ViolationType.MINOR,
                        rule_name="missing_return_type",
                        description=f"Function '{node.name}' missing return type annotation",
                        file_path=file_path,
                        line_number=node.lineno,
                        suggested_fix="Add return type annotation",
                        severity_score=2
                    ))
                
                # Check parameter type annotations
                for arg in node.args.args:
                    if arg.arg != 'self' and not arg.annotation:
                        self.violations.append(Violation(
                            violation_type=ViolationType.MINOR,
                            rule_name="missing_parameter_type",
                            description=f"Parameter '{arg.arg}' in function '{node.name}' missing type annotation",
                            file_path=file_path,
                            line_number=node.lineno,
                            suggested_fix="Add type annotation for parameter",
                            severity_score=2
                        ))

    def _check_stage_patterns(self, file_path: str, content: str):
        """Check for stage-specific pattern compliance"""
        # Check for proper stage identification in comments
        if not re.search(r'# (Red Owl|Orange Orangutan|Yellow Honeybee|Green Tortoise|Blue Dolphin|Violet Elephant)', content):
            self.violations.append(Violation(
                violation_type=ViolationType.MINOR,
                rule_name="missing_stage_identification",
                description="File missing stage identification comment",
                file_path=file_path,
                line_number=1,
                suggested_fix="Add stage identification comment at top of file",
                severity_score=1
            ))

    def _check_roygbv_sequence(self, file_path: str, content: str):
        """Check for ROYGBV sequence violations"""
        # Look for direct stage transitions that bypass the sequence
        stage_transitions = re.findall(r'(research|planning|development|budget|market|support)_to_(research|planning|development|budget|market|support)', content, re.IGNORECASE)
        
        for from_stage, to_stage in stage_transitions:
            from_index = self._get_stage_index(from_stage)
            to_index = self._get_stage_index(to_stage)
            
            # Check if transition follows ROYGBV sequence
            if to_index != (from_index + 1) % len(self.roygbv_sequence):
                self.violations.append(Violation(
                    violation_type=ViolationType.MAJOR,
                    rule_name="roygbv_sequence_violation",
                    description=f"Direct transition from {from_stage} to {to_stage} violates ROYGBV sequence",
                    file_path=file_path,
                    line_number=0,
                    suggested_fix="Use proper ROYGBV sequence: Research → Planning → Development → Budget → Market → Support",
                    severity_score=7
                ))
        
        # Check for stage skipping violations
        if re.search(r'skip.*stage|bypass.*stage|jump.*stage', content, re.IGNORECASE):
            self.violations.append(Violation(
                violation_type=ViolationType.CRITICAL,
                rule_name="stage_skipping_violation",
                description="Code suggests skipping stages, which violates mandatory linear flow",
                file_path=file_path,
                line_number=0,
                suggested_fix="All problems must flow through complete ROYGBV sequence - no stage skipping allowed",
                severity_score=10
            ))
        
        # Check for proper turn-based progression
        if re.search(r'parallel.*stage|concurrent.*stage|simultaneous.*stage', content, re.IGNORECASE):
            self.violations.append(Violation(
                violation_type=ViolationType.MAJOR,
                rule_name="parallel_processing_violation",
                description="Code suggests parallel stage processing, which violates turn-based progression",
                file_path=file_path,
                line_number=0,
                suggested_fix="Each enterprise agent acts only during its stage - no parallel processing allowed",
                severity_score=8
            ))
        
        # Check for fractal recursion compliance
        if re.search(r'sub.council|fractal|recursive', content, re.IGNORECASE):
            if not re.search(r'roygbv.*sequence|linear.*flow|turn.based', content, re.IGNORECASE):
                self.violations.append(Violation(
                    violation_type=ViolationType.MINOR,
                    rule_name="fractal_compliance_warning",
                    description="Fractal/recursive code should explicitly maintain ROYGBV sequence compliance",
                    file_path=file_path,
                    line_number=0,
                    suggested_fix="Ensure sub-councils and fractal structures follow the same ROYGBV rules",
                    severity_score=3
                ))

    def _get_stage_index(self, stage_name: str) -> int:
        """Get index of stage in ROYGBV sequence"""
        stage_mapping = {
            'research': StageType.RESEARCH,
            'planning': StageType.PLANNING,
            'development': StageType.DEVELOPMENT,
            'budget': StageType.BUDGET,
            'market': StageType.MARKET,
            'support': StageType.SUPPORT
        }
        
        stage = stage_mapping.get(stage_name.lower())
        if stage:
            return self.roygbv_sequence.index(stage)
        return -1

    def _check_sql_code(self, file_path: str, content: str):
        """Check SQL code for compliance"""
        # Check for proper table naming
        table_matches = re.findall(r'CREATE TABLE\s+(\w+)', content, re.IGNORECASE)
        for table_name in table_matches:
            if not re.search(r'_(research|planning|development|budget|market|support|core|shared)_', table_name, re.IGNORECASE):
                self.violations.append(Violation(
                    violation_type=ViolationType.MINOR,
                    rule_name="sql_table_naming",
                    description=f"Table '{table_name}' does not follow Cosmic Council naming conventions",
                    file_path=file_path,
                    line_number=0,
                    suggested_fix="Rename table to include stage prefix",
                    severity_score=2
                ))
        
        # Check for required audit fields
        if 'CREATE TABLE' in content.upper():
            if not re.search(r'(created_at|updated_at)', content, re.IGNORECASE):
                self.violations.append(Violation(
                    violation_type=ViolationType.MINOR,
                    rule_name="missing_audit_fields",
                    description="Table missing required audit fields (created_at, updated_at)",
                    file_path=file_path,
                    line_number=0,
                    suggested_fix="Add created_at and updated_at timestamp fields",
                    severity_score=3
                ))

    def generate_report(self) -> str:
        """Generate a comprehensive violation report"""
        if not self.violations:
            return "✅ No violations found. Code complies with Cosmic Council rules."
        
        report = "🚨 Cosmic Council Code Review Report\n"
        report += "=" * 50 + "\n\n"
        
        # Group violations by type
        violations_by_type = {}
        for violation in self.violations:
            if violation.violation_type not in violations_by_type:
                violations_by_type[violation.violation_type] = []
            violations_by_type[violation.violation_type].append(violation)
        
        # Report critical violations first
        for violation_type in [ViolationType.CRITICAL, ViolationType.MAJOR, ViolationType.MINOR]:
            if violation_type in violations_by_type:
                violations = violations_by_type[violation_type]
                report += f"\n🔴 {violation_type.value.upper()} VIOLATIONS ({len(violations)})\n"
                report += "-" * 30 + "\n"
                
                for violation in violations:
                    report += f"📁 {violation.file_path}:{violation.line_number}\n"
                    report += f"   Rule: {violation.rule_name}\n"
                    report += f"   Issue: {violation.description}\n"
                    report += f"   Fix: {violation.suggested_fix}\n"
                    report += f"   Severity: {violation.severity_score}/10\n\n"
        
        # Calculate overall score
        total_severity = sum(v.severity_score for v in self.violations)
        max_severity = len(self.violations) * 10
        compliance_score = max(0, 100 - (total_severity / max_severity * 100))
        
        report += f"\n📊 Overall Compliance Score: {compliance_score:.1f}%\n"
        
        if compliance_score >= 90:
            report += "🌟 Excellent compliance with Cosmic Council rules!"
        elif compliance_score >= 70:
            report += "✅ Good compliance, minor improvements needed."
        elif compliance_score >= 50:
            report += "⚠️ Moderate compliance, several issues to address."
        else:
            report += "🚨 Poor compliance, major issues must be resolved."
        
        return report

# Example usage
if __name__ == "__main__":
    reviewer = CosmicCouncilCodeReviewer()
    
    # Example file content
    sample_code = '''
# Red Owl - Research & Inquiry
import pandas as pd
from typing import List, Dict

def analyze_research_findings(data: List[Dict]) -> Dict[str, Any]:
    """Analyze research findings for relevance and credibility"""
    return {"analysis": "complete"}

class ResearchAnalyzer:
    """Analyzes research data for the Red Owl stage"""
    pass
'''
    
    violations = reviewer.review_file("research/analysis.py", sample_code)
    report = reviewer.generate_report()
    print(report)
