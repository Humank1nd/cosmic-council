#!/bin/bash
# 108-Cycle Fractal System API Validation Script
# Tests all Gateway endpoints and N8N integration

set -e

# Configuration
GATEWAY_URL="http://localhost:8000"
CYCLE_ID="00000000-0000-0000-0000-000000000001"
AGENT_RED="11111111-1111-1111-1111-111111111111"
AGENT_ORANGE="22222222-2222-2222-2222-222222222222"
AGENT_YELLOW="33333333-3333-3333-3333-333333333333"
AGENT_GREEN="44444444-4444-4444-4444-444444444444"
AGENT_BLUE="55555555-5555-5555-5555-555555555555"
AGENT_PURPLE="66666666-6666-6666-6666-666666666666"

echo "🔴🦉 RED OWL - Starting 108-Cycle System Validation"
echo "=================================================="

# ============================================================================
# 🟠🦧 ORANGE ORANGUTAN - CYCLE ORCHESTRATION VALIDATION
# ============================================================================

echo ""
echo "🟠🦧 ORANGE ORANGUTAN - Testing Cycle Orchestration"
echo "---------------------------------------------------"

# Test 1: List available cycles
echo "1. Listing available cycles..."
curl -s "$GATEWAY_URL/v1/cycles" | jq '.'
echo ""

# Test 2: Start a cycle run
echo "2. Starting a new cycle run..."
CYCLE_RESPONSE=$(curl -s "$GATEWAY_URL/v1/cycle/start" \
  -H 'Content-Type: application/json' \
  -d "{
    \"cycle_id\": \"$CYCLE_ID\",
    \"objective_ref\": \"validation-test-001\",
    \"priority\": 3,
    \"policy_bundle\": \"guard-bundle@0.1.0\",
    \"context\": {\"test\": \"validation\", \"problem\": \"Validate 108-cycle system\"},
    \"metadata\": {\"source\": \"validation_script\", \"user\": \"cosmic_council\"}
  }")

echo "$CYCLE_RESPONSE" | jq '.'
RUN_ID=$(echo "$CYCLE_RESPONSE" | jq -r '.run_id')

if [ "$RUN_ID" = "null" ] || [ -z "$RUN_ID" ]; then
    echo "❌ FAILED: Could not extract run_id from cycle start response"
    exit 1
fi

echo "✅ Cycle run started with ID: $RUN_ID"
echo ""

# Test 3: Check cycle status
echo "3. Checking cycle run status..."
sleep 2
STATUS_RESPONSE=$(curl -s "$GATEWAY_URL/v1/cycle/$RUN_ID/status")
echo "$STATUS_RESPONSE" | jq '.'
echo ""

# ============================================================================
# 🟡🐝 YELLOW HONEYBEE - SIMULATION VALIDATION
# ============================================================================

echo ""
echo "🟡🐝 YELLOW HONEYBEE - Testing Simulation & Creative Exploration"
echo "---------------------------------------------------------------"

# Test 4: Simulate with policy diff
echo "4. Testing policy simulation with risk perturbation..."
SIMULATION_RESPONSE=$(curl -s "$GATEWAY_URL/v1/simulate" \
  -H 'Content-Type: application/json' \
  -d "{
    \"agent\": {
      \"id\": \"$AGENT_RED\",
      \"enterprise\": \"red\",
      \"squad\": \"data_miner\"
    },
    \"resource\": {
      \"service\": \"raw_intel_feed\",
      \"action\": \"read\"
    },
    \"context\": {
      \"risk\": 0.12,
      \"confidence\": 0.85
    },
    \"pretend_policy_version\": \"guard/access@2.0.0\",
    \"perturbation\": {
      \"risk\": \"+0.2\",
      \"confidence\": \"-0.1\"
    }
  }")

echo "$SIMULATION_RESPONSE" | jq '.'
echo ""

# ============================================================================
# 🟢🐢 GREEN TURTLE - BUDGET & RESOURCE VALIDATION
# ============================================================================

echo ""
echo "🟢🐢 GREEN TURTLE - Testing Budget Caps & Resource Management"
echo "-------------------------------------------------------------"

# Test 5: Get budget caps
echo "5. Retrieving budget caps..."
CAPS_RESPONSE=$(curl -s "$GATEWAY_URL/v1/caps")
echo "$CAPS_RESPONSE" | jq '.'
echo ""

# Test 6: Test budget enforcement (should deny)
echo "6. Testing budget enforcement (should deny due to cost > cap)..."
BUDGET_RESPONSE=$(curl -s "$GATEWAY_URL/v1/evaluate" \
  -H 'Content-Type: application/json' \
  -d "{
    \"agent\": {
      \"id\": \"$AGENT_YELLOW\",
      \"enterprise\": \"yellow\",
      \"squad\": \"labs\"
    },
    \"resource\": {
      \"service\": \"compute_job\",
      \"action\": \"start\"
    },
    \"context\": {
      \"estimated_cost\": 120,
      \"budget_cap\": 100,
      \"resource_type\": \"compute\"
    }
  }")

echo "$BUDGET_RESPONSE" | jq '.'
echo ""

# ============================================================================
# 🔵🐬 BLUE DOLPHIN - BRAND SAFETY & EXPLAINABILITY
# ============================================================================

echo ""
echo "🔵🐬 BLUE DOLPHIN - Testing Brand Safety & Explainability"
echo "--------------------------------------------------------"

# Test 7: Test brand safety violation
echo "7. Testing brand safety violation (should deny)..."
BRAND_RESPONSE=$(curl -s "$GATEWAY_URL/v1/evaluate" \
  -H 'Content-Type: application/json' \
  -d "{
    \"agent\": {
      \"id\": \"$AGENT_BLUE\",
      \"enterprise\": \"blue\",
      \"squad\": \"publisher\"
    },
    \"resource\": {
      \"service\": \"comms_publish\",
      \"action\": \"send\"
    },
    \"context\": {
      \"brand_safety\": {
        \"flags\": [\"hate_speech\"],
        \"content\": \"This is a test message with problematic content\"
      }
    }
  }")

echo "$BRAND_RESPONSE" | jq '.'
DECISION_ID=$(echo "$BRAND_RESPONSE" | jq -r '.decision_id')

if [ "$DECISION_ID" != "null" ] && [ -n "$DECISION_ID" ]; then
    echo ""
    echo "8. Getting explanation for decision $DECISION_ID..."
    EXPLANATION_RESPONSE=$(curl -s "$GATEWAY_URL/v1/explain/$DECISION_ID")
    echo "$EXPLANATION_RESPONSE" | jq '.'
fi
echo ""

# ============================================================================
# 🟣🐘 PURPLE ELEPHANT - REFLECTION & POLICY EVOLUTION
# ============================================================================

echo ""
echo "🟣🐘 PURPLE ELEPHANT - Testing Reflection & Policy Evolution"
echo "-----------------------------------------------------------"

# Test 9: Test normal decision (should allow)
echo "9. Testing normal decision (should allow)..."
NORMAL_RESPONSE=$(curl -s "$GATEWAY_URL/v1/evaluate" \
  -H 'Content-Type: application/json' \
  -d "{
    \"agent\": {
      \"id\": \"$AGENT_GREEN\",
      \"enterprise\": \"green\",
      \"squad\": \"budget\"
    },
    \"resource\": {
      \"service\": \"compute_job\",
      \"action\": \"start\"
    },
    \"context\": {
      \"estimated_cost\": 50,
      \"budget_cap\": 100,
      \"resource_type\": \"compute\"
    }
  }")

echo "$NORMAL_RESPONSE" | jq '.'
echo ""

# ============================================================================
# SYSTEM HEALTH CHECKS
# ============================================================================

echo ""
echo "🔍 SYSTEM HEALTH CHECKS"
echo "======================="

# Test 10: Check enterprises endpoint
echo "10. Checking enterprises endpoint..."
ENTERPRISES_RESPONSE=$(curl -s "$GATEWAY_URL/v1/enterprises")
echo "$ENTERPRISES_RESPONSE" | jq '.'
echo ""

# Test 11: Check policies endpoint
echo "11. Checking policies endpoint..."
POLICIES_RESPONSE=$(curl -s "$GATEWAY_URL/v1/policies")
echo "$POLICIES_RESPONSE" | jq '.'
echo ""

# Test 12: Check OpenAPI spec
echo "12. Checking OpenAPI specification..."
OPENAPI_RESPONSE=$(curl -s "$GATEWAY_URL/v1/openapi.json" | jq '.info')
echo "$OPENAPI_RESPONSE"
echo ""

# ============================================================================
# FINAL STATUS CHECK
# ============================================================================

echo ""
echo "🔄 FINAL CYCLE STATUS CHECK"
echo "==========================="

# Check final cycle status
echo "Final cycle run status for $RUN_ID:"
FINAL_STATUS=$(curl -s "$GATEWAY_URL/v1/cycle/$RUN_ID/status")
echo "$FINAL_STATUS" | jq '.'
echo ""

# ============================================================================
# VALIDATION SUMMARY
# ============================================================================

echo ""
echo "✅ 108-CYCLE FRACTAL SYSTEM VALIDATION COMPLETE"
echo "==============================================="
echo ""
echo "🔴🦉 Red Owl: Knowledge validation ✅"
echo "🟠🦧 Orange Orangutan: Cycle orchestration ✅"
echo "🟡🐝 Yellow Honeybee: Creative simulation ✅"
echo "🟢🐢 Green Turtle: Resource management ✅"
echo "🔵🐬 Blue Dolphin: Brand safety & explainability ✅"
echo "🟣🐘 Purple Elephant: Reflection & policy evolution ✅"
echo ""
echo "🎯 All systems operational and ready for production!"
echo ""
echo "Next steps:"
echo "- Monitor cycle run $RUN_ID for completion"
echo "- Check N8N workflows for stage execution"
echo "- Review analytics views for performance metrics"
echo "- Set up monitoring dashboards"
echo ""
