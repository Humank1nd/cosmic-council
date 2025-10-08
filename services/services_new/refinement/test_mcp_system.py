"""
Test Model Context Protocols (MCP) System
Tests the MCP system for context isolation and recursion efficiency.
"""

import asyncio
import json
from datetime import datetime
from unittest.mock import Mock, AsyncMock

# Import MCP system components
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_system import MCPManager, SectorType, LayerType, MCPDefinition


class TestMCPSystem:
    """Test the MCP system functionality."""
    
    def __init__(self):
        self.mcp_manager = MCPManager()
    
    def test_mcp_definitions_initialization(self):
        """Test that MCP definitions are properly initialized."""
        print("🧪 Testing MCP Definitions Initialization...")
        
        # Test that we have definitions for all sector/layer combinations
        total_combinations = len(SectorType) * len(LayerType)
        assert len(self.mcp_manager.mcp_definitions) == total_combinations
        
        # Test specific combinations
        red_deci = self.mcp_manager.get_mcp_definition(SectorType.RED, LayerType.DECI)
        assert red_deci is not None
        assert red_deci.sector == SectorType.RED
        assert red_deci.layer == LayerType.DECI
        
        purple_quecto = self.mcp_manager.get_mcp_definition(SectorType.PURPLE, LayerType.QUECTO)
        assert purple_quecto is not None
        assert purple_quecto.sector == SectorType.PURPLE
        assert purple_quecto.layer == LayerType.QUECTO
        
        print("✅ MCP Definitions Initialization Test PASSED")
        return True
    
    def test_layer_granularity_application(self):
        """Test that layer granularity is properly applied to schemas."""
        print("🧪 Testing Layer Granularity Application...")
        
        # Test Deci layer (broad, high-level)
        red_deci = self.mcp_manager.get_mcp_definition(SectorType.RED, LayerType.DECI)
        deci_schema = red_deci.input_schema
        
        # Deci should have larger limits
        assert deci_schema["_granularity"]["granularity"] == "broad"
        assert deci_schema["_granularity"]["context_size"] == "large"
        
        # Test Nano layer (atomic, individual elements)
        red_nano = self.mcp_manager.get_mcp_definition(SectorType.RED, LayerType.NANO)
        nano_schema = red_nano.input_schema
        
        # Nano should have smaller limits
        assert nano_schema["_granularity"]["granularity"] == "atomic"
        assert nano_schema["_granularity"]["context_size"] == "small"
        
        print("✅ Layer Granularity Application Test PASSED")
        return True
    
    def test_context_creation_and_validation(self):
        """Test MCP context creation and validation."""
        print("🧪 Testing Context Creation and Validation...")
        
        # Test valid context creation
        valid_inputs = {
            "problem_statement": "Test problem",
            "hypotheses": ["hypothesis1", "hypothesis2"],
            "relevant_sources": [{"source": "test", "relevance": 0.8}],
            "knowledge_gaps": ["gap1", "gap2"]
        }
        
        context = self.mcp_manager.create_context(SectorType.RED, LayerType.DECI, valid_inputs)
        assert context is not None
        assert context.sector == SectorType.RED
        assert context.layer == LayerType.DECI
        assert context.inputs == valid_inputs
        
        # Test invalid context creation (missing required field)
        invalid_inputs = {
            "hypotheses": ["hypothesis1"],
            # Missing required "problem_statement"
        }
        
        try:
            self.mcp_manager.create_context(SectorType.RED, LayerType.DECI, invalid_inputs)
            assert False, "Should have raised validation error"
        except ValueError as e:
            assert "Required input 'problem_statement' missing" in str(e)
        
        print("✅ Context Creation and Validation Test PASSED")
        return True
    
    def test_context_transformation_between_sectors(self):
        """Test context transformation between different sectors."""
        print("🧪 Testing Context Transformation Between Sectors...")
        
        # Create Red Owl context
        red_inputs = {
            "problem_statement": "Design sustainable housing",
            "hypotheses": ["modular design", "sustainable materials"],
            "relevant_sources": [{"source": "research_paper", "relevance": 0.9}],
            "knowledge_gaps": ["cost_analysis"]
        }
        
        red_context = self.mcp_manager.create_context(SectorType.RED, LayerType.DECI, red_inputs)
        
        # Simulate Red Owl outputs
        red_outputs = {
            "evidence_blocks": [{"evidence": "modular design reduces costs", "confidence": 0.8}],
            "knowledge_summary": {"key_findings": ["modularity", "sustainability"]},
            "research_quality_score": 0.85,
            "gaps_identified": ["cost_analysis"]
        }
        
        # Update context with outputs
        updated_red_context = self.mcp_manager.update_context_outputs(red_context.context_id, red_outputs)
        assert updated_red_context.outputs == red_outputs
        
        # Transform to Orange Orangutan context
        orange_context = self.mcp_manager.transition_context(
            updated_red_context, SectorType.ORANGE, LayerType.DECI
        )
        
        assert orange_context.sector == SectorType.ORANGE
        assert orange_context.layer == LayerType.DECI
        
        # Check that transformation occurred
        orange_inputs = orange_context.inputs
        assert "research_summary" in orange_inputs
        assert "constraints" in orange_inputs
        assert "dependencies" in orange_inputs
        assert "timeline" in orange_inputs
        
        # Verify research summary was passed through
        assert orange_inputs["research_summary"] == red_outputs["knowledge_summary"]
        
        print("✅ Context Transformation Between Sectors Test PASSED")
        return True
    
    def test_layer_transformation_granularity(self):
        """Test context transformation between different layers."""
        print("🧪 Testing Layer Transformation Granularity...")
        
        # Create context at Deci layer
        deci_inputs = {
            "problem_statement": "Design sustainable housing",
            "hypotheses": ["modular design", "sustainable materials"],
            "relevant_sources": [{"source": "research_paper", "relevance": 0.9}],
            "knowledge_gaps": ["cost_analysis"]
        }
        
        deci_context = self.mcp_manager.create_context(SectorType.RED, LayerType.DECI, deci_inputs)
        
        # Simulate outputs
        deci_outputs = {
            "evidence_blocks": [{"evidence": "modular design reduces costs", "confidence": 0.8}],
            "knowledge_summary": {"key_findings": ["modularity", "sustainability"]},
            "research_quality_score": 0.85,
            "gaps_identified": ["cost_analysis"]
        }
        
        updated_deci_context = self.mcp_manager.update_context_outputs(deci_context.context_id, deci_outputs)
        
        # Transform to Milli layer (deeper)
        milli_context = self.mcp_manager.transition_context(
            updated_deci_context, SectorType.RED, LayerType.MILLI
        )
        
        assert milli_context.layer == LayerType.MILLI
        
        # Check that granularity increased
        milli_inputs = milli_context.inputs
        assert "problem_statement" in milli_inputs
        
        # Transform to Yocto layer (much deeper)
        yocto_context = self.mcp_manager.transition_context(
            updated_deci_context, SectorType.RED, LayerType.YOCTO
        )
        
        assert yocto_context.layer == LayerType.YOCTO
        
        print("✅ Layer Transformation Granularity Test PASSED")
        return True
    
    def test_constraints_and_limits(self):
        """Test MCP constraints and limits."""
        print("🧪 Testing Constraints and Limits...")
        
        # Test Deci layer constraints
        deci_mcp = self.mcp_manager.get_mcp_definition(SectorType.RED, LayerType.DECI)
        deci_constraints = deci_mcp.constraints
        
        assert deci_constraints["max_context_size"] == 10000
        assert deci_constraints["processing_time_limit"] == 300  # 5 minutes
        assert deci_constraints["quality_thresholds"]["min_confidence"] == 0.4
        
        # Test Quecto layer constraints (much stricter)
        quecto_mcp = self.mcp_manager.get_mcp_definition(SectorType.RED, LayerType.QUECTO)
        quecto_constraints = quecto_mcp.constraints
        
        assert quecto_constraints["max_context_size"] == 10
        assert quecto_constraints["processing_time_limit"] == 5  # 5 seconds
        assert quecto_constraints["quality_thresholds"]["min_confidence"] == 0.8
        
        print("✅ Constraints and Limits Test PASSED")
        return True
    
    def test_transition_history_tracking(self):
        """Test that transitions are properly tracked."""
        print("🧪 Testing Transition History Tracking...")
        
        # Clear transition history for clean test
        self.mcp_manager.transition_history.clear()
        
        # Create and transition contexts
        red_context = self.mcp_manager.create_context(SectorType.RED, LayerType.DECI, {
            "problem_statement": "Test",
            "hypotheses": [],
            "relevant_sources": [],
            "knowledge_gaps": []
        })
        
        red_outputs = {
            "evidence_blocks": [],
            "knowledge_summary": {},
            "research_quality_score": 0.8,
            "gaps_identified": []
        }
        
        updated_red = self.mcp_manager.update_context_outputs(red_context.context_id, red_outputs)
        
        # Transition to Orange
        orange_context = self.mcp_manager.transition_context(
            updated_red, SectorType.ORANGE, LayerType.DECI
        )
        
        # Check transition history
        assert len(self.mcp_manager.transition_history) == 1
        
        transition = self.mcp_manager.transition_history[0]
        assert transition.from_sector == SectorType.RED
        assert transition.to_sector == SectorType.ORANGE
        assert transition.from_layer == LayerType.DECI
        assert transition.to_layer == LayerType.DECI
        assert transition.transition_type == "sector"
        
        print("✅ Transition History Tracking Test PASSED")
        return True
    
    def test_context_compression(self):
        """Test context compression for size limits."""
        print("🧪 Testing Context Compression...")
        
        # Create large context that exceeds limits
        large_inputs = {
            "problem_statement": "Test problem " * 1000,  # Very large string
            "hypotheses": ["hypothesis"] * 100,
            "relevant_sources": [{"source": "test", "relevance": 0.8}] * 100,
            "knowledge_gaps": ["gap"] * 100
        }
        
        # This should be compressed automatically
        context = self.mcp_manager.create_context(SectorType.RED, LayerType.DECI, large_inputs)
        
        # Check that context was compressed
        context_size = len(json.dumps(context.inputs))
        max_size = self.mcp_manager.get_mcp_definition(SectorType.RED, LayerType.DECI).constraints["max_context_size"]
        
        assert context_size <= max_size, f"Context size {context_size} exceeds limit {max_size}"
        
        print("✅ Context Compression Test PASSED")
        return True
    
    def test_mcp_statistics(self):
        """Test MCP system statistics."""
        print("🧪 Testing MCP Statistics...")
        
        # Clear contexts and transitions for clean test
        self.mcp_manager.active_contexts.clear()
        self.mcp_manager.transition_history.clear()
        
        # Create some contexts and transitions
        red_context = self.mcp_manager.create_context(SectorType.RED, LayerType.DECI, {
            "problem_statement": "Test",
            "hypotheses": [],
            "relevant_sources": [],
            "knowledge_gaps": []
        })
        
        orange_context = self.mcp_manager.create_context(SectorType.ORANGE, LayerType.DECI, {
            "research_summary": {},
            "constraints": {},
            "dependencies": [],
            "timeline": {}
        })
        
        # Get statistics
        stats = self.mcp_manager.get_context_statistics()
        
        assert stats["active_contexts"] == 2
        assert stats["mcp_definitions"] == len(SectorType) * len(LayerType)
        
        print("✅ MCP Statistics Test PASSED")
        return True
    
    def run_all_tests(self):
        """Run all MCP system tests."""
        print("🧪 Testing Model Context Protocols (MCP) System")
        print("=" * 60)
        
        tests = [
            self.test_mcp_definitions_initialization,
            self.test_layer_granularity_application,
            self.test_context_creation_and_validation,
            self.test_context_transformation_between_sectors,
            self.test_layer_transformation_granularity,
            self.test_constraints_and_limits,
            self.test_transition_history_tracking,
            self.test_context_compression,
            self.test_mcp_statistics
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                result = test()
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ {test.__name__} FAILED: {e}")
        
        print("=" * 60)
        print(f"📊 MCP System Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL MCP TESTS PASSED! The MCP system is working correctly!")
        else:
            print("⚠️  Some MCP tests failed. The system needs more work.")
        
        return passed == total


def main():
    """Run MCP system tests."""
    test_suite = TestMCPSystem()
    return test_suite.run_all_tests()


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
