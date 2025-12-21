#!/usr/bin/env python3
"""
108-Cycle Fractal System Stage Generator
Generates all 108 stages and transitions with proper codes and metadata
"""

import json
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any

# Enterprise definitions
ENTERPRISES = [
    {"id": 1, "code": "red", "name": "Red Owl", "description": "Library of Origins - Knowledge and inquiry foundation"},
    {"id": 2, "code": "orange", "name": "Orange Orangutan", "description": "Logistics of Progress - Planning and coordination"},
    {"id": 3, "code": "yellow", "name": "Yellow Honeybee", "description": "Superposition Lab - Creative experimentation"},
    {"id": 4, "code": "green", "name": "Green Turtle", "description": "Vault of Prosperity - Resource stewardship"},
    {"id": 5, "code": "blue", "name": "Blue Dolphin", "description": "Ocean of Exchange - Communication and influence"},
    {"id": 6, "code": "purple", "name": "Purple Elephant", "description": "Sanctuary of Empathy - Reflection and ethics"}
]

# Squad definitions (fractal structure)
SQUADS = [
    {"id": 1, "code": "red", "name": "Inquiry/Root", "description": "Deep questioning and foundational analysis"},
    {"id": 2, "code": "orange", "name": "Logistics/Routing", "description": "Process optimization and flow management"},
    {"id": 3, "code": "yellow", "name": "Creative/Labs", "description": "Innovation and experimental development"},
    {"id": 4, "code": "green", "name": "Stewardship/Core", "description": "Resource management and sustainability"},
    {"id": 5, "code": "blue", "name": "Exchange/Comms", "description": "Communication and relationship building"},
    {"id": 6, "code": "purple", "name": "Reflection/Ethics", "description": "Ethical review and continuous improvement"}
]

# Redundancy passes
REDUNDANCY_PASSES = [
    {"id": 1, "code": "decide", "description": "Primary decision pass - Initial reasoning and action"},
    {"id": 2, "code": "validate", "description": "Independent validation pass - Cross-checking and verification"},
    {"id": 3, "code": "reflect", "description": "Retrospective reflection pass - Learning and improvement"}
]

def generate_stages() -> List[Dict[str, Any]]:
    """Generate all 108 stages (6 enterprises × 6 squads × 3 passes)"""
    stages = []
    stage_id = 1
    
    for enterprise in ENTERPRISES:
        for squad in SQUADS:
            for pass_type in REDUNDANCY_PASSES:
                # Generate stage code: enterprise:squad:pass:ordinal
                code = f"{enterprise['code']}:{squad['code']}:{pass_type['code']}:{stage_id:03d}"
                
                # Generate human-friendly name
                name = f"{enterprise['name']} — {squad['name']} — {pass_type['code'].title()} #{stage_id}"
                
                # Generate description
                description = f"Stage {stage_id}: {enterprise['name']} {squad['name']} {pass_type['description']}"
                
                # Set expected duration based on pass type
                duration_map = {
                    "decide": 3000,   # Primary decisions are faster
                    "validate": 4000, # Validation takes more time
                    "reflect": 5000   # Reflection takes the most time
                }
                
                stage = {
                    "stage_id": stage_id,
                    "enterprise_id": enterprise["id"],
                    "squad_id": squad["id"],
                    "pass_id": pass_type["id"],
                    "ordinal": stage_id,
                    "code": code,
                    "name": name,
                    "description": description,
                    "expected_duration_ms": duration_map[pass_type["code"]],
                    "policy_pin": None  # Can be set per stage if needed
                }
                
                stages.append(stage)
                stage_id += 1
    
    return stages

def generate_transitions(stages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate stage transitions (clockwise, redundancy, fallback, error)"""
    transitions = []
    transition_id = 1
    
    # Create a lookup for stage_id by ordinal
    stage_by_ordinal = {stage["ordinal"]: stage for stage in stages}
    
    for stage in stages:
        # 1. Clockwise transitions (normal flow)
        if stage["ordinal"] < 108:
            next_stage = stage_by_ordinal[stage["ordinal"] + 1]
            transitions.append({
                "transition_id": str(uuid.uuid4()),
                "from_stage_id": stage["stage_id"],
                "to_stage_id": next_stage["stage_id"],
                "kind": "clockwise",
                "priority": 1,
                "condition": {"type": "normal_flow"}
            })
        
        # 2. Redundancy transitions (decide -> validate -> reflect)
        if stage["pass_id"] in [1, 2]:  # From decide or validate
            # Find the next pass for same enterprise/squad
            next_pass_id = stage["pass_id"] + 1
            next_stage = next(
                (s for s in stages 
                 if s["enterprise_id"] == stage["enterprise_id"] 
                 and s["squad_id"] == stage["squad_id"] 
                 and s["pass_id"] == next_pass_id), 
                None
            )
            if next_stage:
                transitions.append({
                    "transition_id": str(uuid.uuid4()),
                    "from_stage_id": stage["stage_id"],
                    "to_stage_id": next_stage["stage_id"],
                    "kind": "redundancy",
                    "priority": 2,
                    "condition": {"type": "redundancy_check"}
                })
        
        # 3. Fallback transitions (reflect -> decide for same enterprise/squad)
        if stage["pass_id"] == 3:  # From reflect
            fallback_stage = next(
                (s for s in stages 
                 if s["enterprise_id"] == stage["enterprise_id"] 
                 and s["squad_id"] == stage["squad_id"] 
                 and s["pass_id"] == 1),  # Back to decide
                None
            )
            if fallback_stage:
                transitions.append({
                    "transition_id": str(uuid.uuid4()),
                    "from_stage_id": stage["stage_id"],
                    "to_stage_id": fallback_stage["stage_id"],
                    "kind": "fallback",
                    "priority": 3,
                    "condition": {"type": "error_recovery"}
                })
        
        # 4. Error transitions (self-loop for error handling)
        transitions.append({
            "transition_id": str(uuid.uuid4()),
            "from_stage_id": stage["stage_id"],
            "to_stage_id": stage["stage_id"],  # Self-loop
            "kind": "error",
            "priority": 10,
            "condition": {"type": "error_handling"}
        })
    
    return transitions

def generate_sql_inserts(stages: List[Dict[str, Any]], transitions: List[Dict[str, Any]]) -> str:
    """Generate SQL INSERT statements for stages and transitions"""
    sql_parts = []
    
    # Insert stages
    sql_parts.append("-- Insert all 108 stages")
    sql_parts.append("INSERT INTO cycle_stages (stage_id, enterprise_id, squad_id, pass_id, ordinal, code, name, description, expected_duration_ms) VALUES")
    
    stage_values = []
    for stage in stages:
        values = f"({stage['stage_id']}, {stage['enterprise_id']}, {stage['squad_id']}, {stage['pass_id']}, {stage['ordinal']}, '{stage['code']}', '{stage['name']}', '{stage['description']}', {stage['expected_duration_ms']})"
        stage_values.append(values)
    
    sql_parts.append(",\n".join(stage_values) + ";")
    sql_parts.append("")
    
    # Insert transitions
    sql_parts.append("-- Insert stage transitions")
    sql_parts.append("INSERT INTO cycle_stage_transitions (transition_id, from_stage_id, to_stage_id, kind, priority, condition) VALUES")
    
    transition_values = []
    for transition in transitions:
        condition_json = json.dumps(transition["condition"]).replace("'", "''")
        values = f"('{transition['transition_id']}', {transition['from_stage_id']}, {transition['to_stage_id']}, '{transition['kind']}', {transition['priority']}, '{condition_json}'::jsonb)"
        transition_values.append(values)
    
    sql_parts.append(",\n".join(transition_values) + ";")
    
    return "\n".join(sql_parts)

def generate_cycle_template() -> Dict[str, Any]:
    """Generate the default cycle template"""
    return {
        "cycle_id": "00000000-0000-0000-0000-000000000001",
        "title": "Default 108-Stage Fractal Cycle",
        "description": "The complete Cosmic Council fractal cycle with 6 enterprises × 6 squads × 3 redundancy passes",
        "version": "1.0.0",
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

def generate_n8n_templates() -> List[Dict[str, Any]]:
    """Generate N8N workflow templates"""
    templates = [
        {
            "template_id": "00000000-0000-0000-0000-000000000001",
            "name": "Cycle Run Starter",
            "description": "Initiates a new 108-stage cycle run",
            "workflow_json": {
                "name": "Cycle Run Starter",
                "nodes": [
                    {
                        "id": "webhook",
                        "name": "HTTP Trigger",
                        "type": "n8n-nodes-base.webhook",
                        "parameters": {
                            "httpMethod": "POST",
                            "path": "run-cycle"
                        }
                    }
                ],
                "connections": {}
            },
            "version": "1.0.0",
            "active": True
        },
        {
            "template_id": "00000000-0000-0000-0000-000000000002",
            "name": "Stage Runner",
            "description": "Executes individual cycle stages with Guardrail Gateway integration",
            "workflow_json": {
                "name": "Stage Runner",
                "nodes": [
                    {
                        "id": "cron",
                        "name": "Cron Trigger",
                        "type": "n8n-nodes-base.cron",
                        "parameters": {
                            "rule": {"interval": [{"field": "seconds", "secondsInterval": 5}]}
                        }
                    }
                ],
                "connections": {}
            },
            "version": "1.0.0",
            "active": True
        },
        {
            "template_id": "00000000-0000-0000-0000-000000000003",
            "name": "Reflection & Policy Evolution",
            "description": "Purple Elephant reflection and policy improvement workflows",
            "workflow_json": {
                "name": "Reflection & Policy Evolution",
                "nodes": [
                    {
                        "id": "hourly-cron",
                        "name": "Hourly Cron",
                        "type": "n8n-nodes-base.cron",
                        "parameters": {
                            "rule": {"interval": [{"field": "hours", "hoursInterval": 1}]}
                        }
                    }
                ],
                "connections": {}
            },
            "version": "1.0.0",
            "active": True
        },
        {
            "template_id": "00000000-0000-0000-0000-000000000004",
            "name": "Run Completer",
            "description": "Completes cycle runs and calculates final metrics",
            "workflow_json": {
                "name": "Run Completer",
                "nodes": [
                    {
                        "id": "trigger",
                        "name": "Trigger",
                        "type": "n8n-nodes-base.trigger"
                    }
                ],
                "connections": {}
            },
            "version": "1.0.0",
            "active": True
        }
    ]
    return templates

def main():
    """Main function to generate all 108-cycle data"""
    print("🔴🦉 Generating 108-Cycle Fractal System Data...")
    print("=" * 50)
    
    # Generate stages
    print("Generating 108 stages...")
    stages = generate_stages()
    print(f"✅ Generated {len(stages)} stages")
    
    # Generate transitions
    print("Generating stage transitions...")
    transitions = generate_transitions(stages)
    print(f"✅ Generated {len(transitions)} transitions")
    
    # Generate SQL
    print("Generating SQL INSERT statements...")
    sql_content = generate_sql_inserts(stages, transitions)
    
    # Write SQL file
    with open("generated_108_stages.sql", "w") as f:
        f.write(sql_content)
    print("✅ Written to generated_108_stages.sql")
    
    # Generate JSON exports
    print("Generating JSON exports...")
    
    # Stages JSON
    with open("stages_108.json", "w") as f:
        json.dump(stages, f, indent=2)
    print("✅ Written to stages_108.json")
    
    # Transitions JSON
    with open("transitions_108.json", "w") as f:
        json.dump(transitions, f, indent=2)
    print("✅ Written to transitions_108.json")
    
    # Cycle template JSON
    cycle_template = generate_cycle_template()
    with open("cycle_template.json", "w") as f:
        json.dump(cycle_template, f, indent=2)
    print("✅ Written to cycle_template.json")
    
    # N8N templates JSON
    n8n_templates = generate_n8n_templates()
    with open("n8n_templates.json", "w") as f:
        json.dump(n8n_templates, f, indent=2)
    print("✅ Written to n8n_templates.json")
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 108-CYCLE FRACTAL SYSTEM GENERATION COMPLETE")
    print("=" * 50)
    print(f"🔴🦉 Red Owl: {len([s for s in stages if s['enterprise_id'] == 1])} stages")
    print(f"🟠🦧 Orange Orangutan: {len([s for s in stages if s['enterprise_id'] == 2])} stages")
    print(f"🟡🐝 Yellow Honeybee: {len([s for s in stages if s['enterprise_id'] == 3])} stages")
    print(f"🟢🐢 Green Turtle: {len([s for s in stages if s['enterprise_id'] == 4])} stages")
    print(f"🔵🐬 Blue Dolphin: {len([s for s in stages if s['enterprise_id'] == 5])} stages")
    print(f"🟣🐘 Purple Elephant: {len([s for s in stages if s['enterprise_id'] == 6])} stages")
    print(f"📊 Total: {len(stages)} stages, {len(transitions)} transitions")
    print(f"🔄 Transition types: {len(set(t['kind'] for t in transitions))} different kinds")
    print("\nFiles generated:")
    print("- generated_108_stages.sql (SQL INSERT statements)")
    print("- stages_108.json (Stage definitions)")
    print("- transitions_108.json (Transition definitions)")
    print("- cycle_template.json (Default cycle template)")
    print("- n8n_templates.json (N8N workflow templates)")
    print("\n🚀 Ready for deployment!")

if __name__ == "__main__":
    main()
