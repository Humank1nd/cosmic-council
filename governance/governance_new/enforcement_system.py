"""
Cosmic Council Enforcement System
Automated enforcement of repository rules and governance
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import aiohttp

from code_review_rules import CosmicCouncilCodeReviewer, Violation, ViolationType

logger = logging.getLogger(__name__)

class EnforcementAction(Enum):
    """Types of enforcement actions"""
    WARNING = "warning"
    BLOCK = "block"
    SUSPEND = "suspend"
    BAN = "ban"

class AgentLevel(Enum):
    """Agent experience levels"""
    NOVICE = "novice"
    APPRENTICE = "apprentice"
    JOURNEYMAN = "journeyman"
    MASTER = "master"
    GRANDMASTER = "grandmaster"

@dataclass
class AgentProfile:
    """Agent profile and performance tracking"""
    agent_id: str
    name: str
    stage: str
    level: AgentLevel
    cycles_completed: int
    violations_count: Dict[str, int]
    last_violation: Optional[datetime]
    suspension_count: int
    achievements: List[str]
    performance_score: float
    created_at: datetime
    updated_at: datetime

@dataclass
class EnforcementRecord:
    """Record of enforcement action taken"""
    record_id: str
    agent_id: str
    violation_type: ViolationType
    action_taken: EnforcementAction
    reason: str
    timestamp: datetime
    duration: Optional[int]  # Duration in hours for suspensions
    resolved: bool
    notes: str

class CosmicCouncilEnforcementSystem:
    """
    Automated enforcement system for Cosmic Council repository rules
    """
    
    def __init__(self, 
                 database_url: str,
                 n8n_webhook_url: Optional[str] = None,
                 slack_webhook_url: Optional[str] = None):
        """
        Initialize the enforcement system
        
        Args:
            database_url: Database connection for storing enforcement records
            n8n_webhook_url: N8N webhook for automated workflows
            slack_webhook_url: Slack webhook for notifications
        """
        self.database_url = database_url
        self.n8n_webhook_url = n8n_webhook_url
        self.slack_webhook_url = slack_webhook_url
        
        self.code_reviewer = CosmicCouncilCodeReviewer()
        self.agent_profiles: Dict[str, AgentProfile] = {}
        self.enforcement_records: List[EnforcementRecord] = []
        
        # Enforcement thresholds
        self.thresholds = {
            AgentLevel.NOVICE: {
                'minor_violations': 10,
                'major_violations': 3,
                'critical_violations': 1
            },
            AgentLevel.APPRENTICE: {
                'minor_violations': 8,
                'major_violations': 2,
                'critical_violations': 1
            },
            AgentLevel.JOURNEYMAN: {
                'minor_violations': 6,
                'major_violations': 2,
                'critical_violations': 1
            },
            AgentLevel.MASTER: {
                'minor_violations': 4,
                'major_violations': 1,
                'critical_violations': 1
            },
            AgentLevel.GRANDMASTER: {
                'minor_violations': 2,
                'major_violations': 1,
                'critical_violations': 1
            }
        }
        
        logger.info("Cosmic Council Enforcement System initialized")

    async def review_pull_request(self, 
                                pr_data: Dict[str, Any],
                                agent_id: str) -> Dict[str, Any]:
        """
        Review a pull request for rule violations
        
        Args:
            pr_data: Pull request data including files and changes
            agent_id: ID of the agent submitting the PR
            
        Returns:
            Review result with violations and enforcement actions
        """
        try:
            # Get agent profile
            agent_profile = await self._get_agent_profile(agent_id)
            
            # Review all changed files
            all_violations = []
            for file_data in pr_data.get('files', []):
                violations = self.code_reviewer.review_file(
                    file_data['path'], 
                    file_data['content']
                )
                all_violations.extend(violations)
            
            # Determine enforcement action
            action = await self._determine_enforcement_action(agent_profile, all_violations)
            
            # Create enforcement record
            if action != EnforcementAction.WARNING:
                await self._create_enforcement_record(
                    agent_id, 
                    all_violations, 
                    action
                )
            
            # Update agent profile
            await self._update_agent_profile(agent_profile, all_violations, action)
            
            # Send notifications
            await self._send_notifications(agent_id, all_violations, action)
            
            # Generate review report
            report = self.code_reviewer.generate_report()
            
            return {
                'approved': action == EnforcementAction.WARNING,
                'action_taken': action.value,
                'violations_count': len(all_violations),
                'violations_by_type': self._count_violations_by_type(all_violations),
                'report': report,
                'agent_level': agent_profile.level.value,
                'performance_score': agent_profile.performance_score
            }
            
        except Exception as e:
            logger.error(f"Error reviewing pull request: {e}")
            return {
                'approved': False,
                'action_taken': 'error',
                'error': str(e)
            }

    async def _get_agent_profile(self, agent_id: str) -> AgentProfile:
        """Get or create agent profile"""
        if agent_id not in self.agent_profiles:
            # Create new agent profile
            self.agent_profiles[agent_id] = AgentProfile(
                agent_id=agent_id,
                name=f"Agent_{agent_id}",
                stage="unknown",
                level=AgentLevel.NOVICE,
                cycles_completed=0,
                violations_count={'minor': 0, 'major': 0, 'critical': 0},
                last_violation=None,
                suspension_count=0,
                achievements=[],
                performance_score=100.0,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
        
        return self.agent_profiles[agent_id]

    async def _determine_enforcement_action(self, 
                                          agent_profile: AgentProfile,
                                          violations: List[Violation]) -> EnforcementAction:
        """Determine appropriate enforcement action based on violations and agent level"""
        
        # Count violations by type
        violation_counts = self._count_violations_by_type(violations)
        
        # Get thresholds for agent level
        thresholds = self.thresholds[agent_profile.level]
        
        # Check for critical violations (immediate action)
        if violation_counts['critical'] > 0:
            return EnforcementAction.BAN
        
        # Check for major violations
        if violation_counts['major'] >= thresholds['major_violations']:
            if agent_profile.suspension_count >= 2:
                return EnforcementAction.BAN
            return EnforcementAction.SUSPEND
        
        # Check for minor violations
        if violation_counts['minor'] >= thresholds['minor_violations']:
            return EnforcementAction.BLOCK
        
        # Check cumulative violations
        total_violations = sum(violation_counts.values())
        if total_violations >= thresholds['minor_violations']:
            return EnforcementAction.BLOCK
        
        return EnforcementAction.WARNING

    def _count_violations_by_type(self, violations: List[Violation]) -> Dict[str, int]:
        """Count violations by type"""
        counts = {'minor': 0, 'major': 0, 'critical': 0}
        for violation in violations:
            counts[violation.violation_type.value] += 1
        return counts

    async def _create_enforcement_record(self, 
                                       agent_id: str,
                                       violations: List[Violation],
                                       action: EnforcementAction):
        """Create enforcement record"""
        record = EnforcementRecord(
            record_id=f"enforcement_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{agent_id}",
            agent_id=agent_id,
            violation_type=ViolationType.CRITICAL if violations else ViolationType.MINOR,
            action_taken=action,
            reason=f"Rule violations: {len(violations)} violations found",
            timestamp=datetime.now(timezone.utc),
            duration=24 if action == EnforcementAction.SUSPEND else None,
            resolved=False,
            notes=f"Violations: {[v.rule_name for v in violations]}"
        )
        
        self.enforcement_records.append(record)
        
        # Store in database (would implement actual database storage)
        logger.info(f"Created enforcement record: {record.record_id}")

    async def _update_agent_profile(self, 
                                  agent_profile: AgentProfile,
                                  violations: List[Violation],
                                  action: EnforcementAction):
        """Update agent profile based on violations and action"""
        
        # Update violation counts
        violation_counts = self._count_violations_by_type(violations)
        for violation_type, count in violation_counts.items():
            agent_profile.violations_count[violation_type] += count
        
        # Update last violation timestamp
        if violations:
            agent_profile.last_violation = datetime.now(timezone.utc)
        
        # Update suspension count
        if action == EnforcementAction.SUSPEND:
            agent_profile.suspension_count += 1
        
        # Update performance score
        agent_profile.performance_score = self._calculate_performance_score(agent_profile)
        
        # Update agent level based on performance
        agent_profile.level = self._calculate_agent_level(agent_profile)
        
        # Update timestamp
        agent_profile.updated_at = datetime.now(timezone.utc)
        
        # Store updated profile
        self.agent_profiles[agent_profile.agent_id] = agent_profile

    def _calculate_performance_score(self, agent_profile: AgentProfile) -> float:
        """Calculate agent performance score"""
        base_score = 100.0
        
        # Deduct points for violations
        base_score -= agent_profile.violations_count['minor'] * 2
        base_score -= agent_profile.violations_count['major'] * 10
        base_score -= agent_profile.violations_count['critical'] * 25
        
        # Deduct points for suspensions
        base_score -= agent_profile.suspension_count * 15
        
        # Bonus points for cycles completed
        base_score += min(agent_profile.cycles_completed * 0.5, 20)
        
        return max(0.0, min(100.0, base_score))

    def _calculate_agent_level(self, agent_profile: AgentProfile) -> AgentLevel:
        """Calculate agent level based on performance and experience"""
        if agent_profile.performance_score >= 95 and agent_profile.cycles_completed >= 51:
            return AgentLevel.GRANDMASTER
        elif agent_profile.performance_score >= 90 and agent_profile.cycles_completed >= 31:
            return AgentLevel.MASTER
        elif agent_profile.performance_score >= 80 and agent_profile.cycles_completed >= 16:
            return AgentLevel.JOURNEYMAN
        elif agent_profile.performance_score >= 70 and agent_profile.cycles_completed >= 6:
            return AgentLevel.APPRENTICE
        else:
            return AgentLevel.NOVICE

    async def _send_notifications(self, 
                                agent_id: str,
                                violations: List[Violation],
                                action: EnforcementAction):
        """Send notifications about enforcement actions"""
        
        # Send to N8N workflow
        if self.n8n_webhook_url:
            await self._send_n8n_notification(agent_id, violations, action)
        
        # Send to Slack
        if self.slack_webhook_url:
            await self._send_slack_notification(agent_id, violations, action)

    async def _send_n8n_notification(self, 
                                   agent_id: str,
                                   violations: List[Violation],
                                   action: EnforcementAction):
        """Send notification to N8N workflow"""
        try:
            payload = {
                'event_type': 'enforcement_action',
                'agent_id': agent_id,
                'action': action.value,
                'violations_count': len(violations),
                'violations': [asdict(v) for v in violations],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.n8n_webhook_url,
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status == 200:
                        logger.info(f"Sent N8N notification for enforcement action: {action.value}")
                    else:
                        logger.warning(f"N8N notification failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send N8N notification: {e}")

    async def _send_slack_notification(self, 
                                     agent_id: str,
                                     violations: List[Violation],
                                     action: EnforcementAction):
        """Send notification to Slack"""
        try:
            # Create Slack message
            if action == EnforcementAction.BAN:
                color = "danger"
                emoji = "🚨"
                message = f"{emoji} *CRITICAL VIOLATION* - Agent {agent_id} has been BANNED"
            elif action == EnforcementAction.SUSPEND:
                color = "warning"
                emoji = "⚠️"
                message = f"{emoji} *MAJOR VIOLATION* - Agent {agent_id} has been SUSPENDED"
            elif action == EnforcementAction.BLOCK:
                color = "warning"
                emoji = "🛑"
                message = f"{emoji} *RULE VIOLATION* - Agent {agent_id} PR BLOCKED"
            else:
                color = "good"
                emoji = "✅"
                message = f"{emoji} *WARNING* - Agent {agent_id} has minor violations"
            
            # Add violation details
            violation_text = "\n".join([f"• {v.rule_name}: {v.description}" for v in violations[:5]])
            if len(violations) > 5:
                violation_text += f"\n• ... and {len(violations) - 5} more violations"
            
            slack_payload = {
                "attachments": [
                    {
                        "color": color,
                        "title": "Cosmic Council Enforcement Action",
                        "text": message,
                        "fields": [
                            {
                                "title": "Agent ID",
                                "value": agent_id,
                                "short": True
                            },
                            {
                                "title": "Action Taken",
                                "value": action.value.upper(),
                                "short": True
                            },
                            {
                                "title": "Violations",
                                "value": violation_text,
                                "short": False
                            }
                        ],
                        "footer": "Cosmic Council Enforcement System",
                        "ts": int(datetime.now().timestamp())
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.slack_webhook_url,
                    json=slack_payload,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status == 200:
                        logger.info(f"Sent Slack notification for enforcement action: {action.value}")
                    else:
                        logger.warning(f"Slack notification failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")

    async def get_agent_statistics(self) -> Dict[str, Any]:
        """Get overall agent statistics"""
        total_agents = len(self.agent_profiles)
        level_counts = {}
        for level in AgentLevel:
            level_counts[level.value] = sum(1 for profile in self.agent_profiles.values() if profile.level == level)
        
        total_violations = sum(
            sum(profile.violations_count.values()) 
            for profile in self.agent_profiles.values()
        )
        
        total_enforcements = len(self.enforcement_records)
        
        return {
            'total_agents': total_agents,
            'level_distribution': level_counts,
            'total_violations': total_violations,
            'total_enforcements': total_enforcements,
            'average_performance_score': sum(p.performance_score for p in self.agent_profiles.values()) / max(total_agents, 1)
        }

    async def get_agent_profile(self, agent_id: str) -> Optional[AgentProfile]:
        """Get agent profile by ID"""
        return self.agent_profiles.get(agent_id)

    async def resolve_enforcement_record(self, record_id: str, notes: str = ""):
        """Resolve an enforcement record"""
        for record in self.enforcement_records:
            if record.record_id == record_id:
                record.resolved = True
                record.notes += f"\nResolved: {notes}"
                logger.info(f"Resolved enforcement record: {record_id}")
                break

# Example usage
async def main():
    """Example usage of the enforcement system"""
    
    enforcement_system = CosmicCouncilEnforcementSystem(
        database_url="postgresql://localhost/dream_caesar",
        n8n_webhook_url="https://your-n8n-instance.com/webhook/enforcement",
        slack_webhook_url="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
    )
    
    # Example PR data
    pr_data = {
        'files': [
            {
                'path': 'research/analysis.py',
                'content': '''
# Red Owl - Research & Inquiry
import pandas as pd
from typing import List, Dict

def analyze_research_findings(data: List[Dict]) -> Dict[str, Any]:
    """Analyze research findings for relevance and credibility"""
    return {"analysis": "complete"}
'''
            }
        ]
    }
    
    # Review PR
    result = await enforcement_system.review_pull_request(pr_data, "agent_001")
    print(f"PR Review Result: {result}")
    
    # Get agent statistics
    stats = await enforcement_system.get_agent_statistics()
    print(f"Agent Statistics: {stats}")

if __name__ == "__main__":
    asyncio.run(main())
