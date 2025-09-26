import httpx
import time
import uuid
from typing import Tuple, Dict, Any, List, Optional
from .settings import settings
from .schemas import PolicyDiff, SimulationResult

class PolicyEngine:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.OPA_URL
        self.policy_versions = {
            "guard/access": "1.0.0",
            "guard/brand": "1.0.0", 
            "guard/budget": "1.0.0"
        }

    async def evaluate(self, package: str, input_obj: dict) -> Tuple[bool, Dict[str, Any]]:
        # Example: call OPA data path: /v1/data/guard/access/allow and obligations
        t0 = time.time()
        async with httpx.AsyncClient(timeout=5.0) as client:
            allow_r = await client.post(f"{self.base_url}/{package}/allow", json={"input": input_obj})
            allow = allow_r.json().get("result", False)
            expl_r = await client.post(f"{self.base_url}/{package}/obligations", json={"input": input_obj})
            obligations = expl_r.json().get("result", [])
        return allow, {"obligations": obligations, "latency_ms": int((time.time()-t0)*1000)}

    async def simulate_with_diff(self, package: str, input_obj: dict, 
                               pretend_policy_version: Optional[str] = None,
                               pretend_context_overrides: Optional[Dict[str, Any]] = None,
                               perturbation: Optional[Dict[str, Any]] = None) -> SimulationResult:
        """
        Enhanced simulation with policy diff capabilities
        """
        simulation_id = str(uuid.uuid4())
        
        # Get current decision
        current_allow, current_meta = await self.evaluate(package, input_obj)
        current_result = {
            "allow": current_allow,
            "obligations": current_meta.get("obligations", []),
            "latency_ms": current_meta.get("latency_ms", 0)
        }
        
        # Prepare proposed input with modifications
        proposed_input = input_obj.copy()
        
        # Apply context overrides
        if pretend_context_overrides:
            proposed_input["context"] = {**proposed_input.get("context", {}), **pretend_context_overrides}
        
        # Apply perturbations
        if perturbation:
            context = proposed_input.get("context", {})
            for key, value in perturbation.items():
                if key in context and isinstance(context[key], (int, float)):
                    if isinstance(value, str) and value.startswith(('+', '-')):
                        # Handle relative changes like "+0.2" or "-0.1"
                        delta = float(value)
                        context[key] = context[key] + delta
                    else:
                        context[key] = value
                else:
                    context[key] = value
            proposed_input["context"] = context
        
        # Get proposed decision (simplified - in real implementation, would load different policy version)
        proposed_allow, proposed_meta = await self.evaluate(package, proposed_input)
        proposed_result = {
            "allow": proposed_allow,
            "obligations": proposed_meta.get("obligations", []),
            "latency_ms": proposed_meta.get("latency_ms", 0)
        }
        
        # Calculate diffs
        changed_policies = []
        if pretend_policy_version:
            current_version = self.policy_versions.get(package, "1.0.0")
            changed_policies.append(PolicyDiff(
                policy_name=package,
                current_version=current_version,
                proposed_version=pretend_policy_version,
                changes=[f"Policy version changed from {current_version} to {pretend_policy_version}"]
            ))
        
        # Calculate risk delta
        risk_delta = None
        if perturbation and "risk" in perturbation:
            risk_delta = float(perturbation["risk"].replace("+", "").replace("-", ""))
            if perturbation["risk"].startswith("-"):
                risk_delta = -risk_delta
        
        # Calculate obligations delta
        current_obligations = set(current_result.get("obligations", []))
        proposed_obligations = set(proposed_result.get("obligations", []))
        obligations_delta = list(proposed_obligations - current_obligations)
        
        return SimulationResult(
            current=current_result,
            proposed=proposed_result,
            changed_policies=changed_policies,
            risk_delta=risk_delta,
            obligations_delta=obligations_delta,
            simulation_id=simulation_id
        )

engine = PolicyEngine()
