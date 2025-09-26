"""
Cosmic Council Achievement System
Gamification and recognition system for repository contributors
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)

class AchievementType(Enum):
    """Types of achievements"""
    CYCLE_COMPLETION = "cycle_completion"
    CODE_QUALITY = "code_quality"
    INNOVATION = "innovation"
    COLLABORATION = "collaboration"
    LEADERSHIP = "leadership"
    SPECIAL = "special"

class AchievementRarity(Enum):
    """Achievement rarity levels"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

@dataclass
class Achievement:
    """Represents an achievement"""
    achievement_id: str
    name: str
    description: str
    achievement_type: AchievementType
    rarity: AchievementRarity
    icon: str
    points: int
    requirements: Dict[str, Any]
    unlocked_by: Set[str]  # Agent IDs who have unlocked this
    created_at: datetime
    updated_at: datetime

@dataclass
class AgentAchievement:
    """Agent's achievement record"""
    agent_id: str
    achievement_id: str
    unlocked_at: datetime
    progress: Dict[str, Any]
    is_completed: bool

@dataclass
class AgentStats:
    """Agent statistics for achievement tracking"""
    agent_id: str
    cycles_completed: int
    code_quality_score: float
    innovations_contributed: int
    collaborations_count: int
    leadership_actions: int
    special_contributions: int
    total_points: int
    last_updated: datetime

class CosmicCouncilAchievementSystem:
    """
    Achievement system for the Cosmic Council repository
    Tracks and rewards agent contributions and milestones
    """
    
    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self.agent_achievements: Dict[str, List[AgentAchievement]] = {}
        self.agent_stats: Dict[str, AgentStats] = {}
        
        # Initialize default achievements
        self._initialize_default_achievements()
        
        logger.info("Cosmic Council Achievement System initialized")

    def _initialize_default_achievements(self):
        """Initialize default achievements"""
        
        # Cycle Completion Achievements
        self._add_achievement(Achievement(
            achievement_id="first_cycle",
            name="First Steps",
            description="Complete your first Cosmic Council cycle",
            achievement_type=AchievementType.CYCLE_COMPLETION,
            rarity=AchievementRarity.COMMON,
            icon="🌱",
            points=10,
            requirements={"cycles_completed": 1},
            unlocked_by=set(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ))
        
        self._add_achievement(Achievement(
            achievement_id="cycle_master",
            name="Cycle Master",
            description="Complete 10 Cosmic Council cycles",
            achievement_type=AchievementType.CYCLE_COMPLETION,
            rarity=AchievementRarity.UNCOMMON,
            icon="🔄",
            points=50,
            requirements={"cycles_completed": 10},
            unlocked_by=set(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ))
        
        self._add_achievement(Achievement(
            achievement_id="perfect_cycle",
            name="Perfect Cycle",
            description="Complete a cycle with 100% confidence score",
            achievement_type=AchievementType.CYCLE_COMPLETION,
            rarity=AchievementRarity.RARE,
            icon="⭐",
            points=100,
            requirements={"perfect_cycles": 1},
            unlocked_by=set(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ))
        
        # Code Quality Achievements
        self._add_achievement(Achievement(
            achievement_id="code_quality_expert",
            name="Code Quality Expert",
            description="Maintain 95%+ code quality score for 5 consecutive cycles",
            achievement_type=AchievementType.CODE_QUALITY,
            rarity=AchievementRarity.UNCOMMON,
            icon="💎",
            points=75,
            requirements={"consecutive_high_quality_cycles": 5},
            unlocked_by=set(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ))
        
        self._add_achievement(Achievement(
            achievement_id="zero_violations",
            name="Rule Follower",
            description="Complete 3 cycles with zero rule violations",
            achievement_type=AchievementType.CODE_QUALITY,
            rarity=AchievementRarity.RARE,
            icon="📜",
            points=100,
            requirements={"zero_violation_cycles": 3},
            unlocked_by=set(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ))
        
        # Innovation Achievements
        self._add_achievement(Achievement(
            achievement_id="innovation_pioneer",
            name="Innovation Pioneer",
            description="Contribute 5 innovative solutions",
            achievement_type=AchievementType.INNOVATION,
            rarity=AchievementRarity.UNCOMMON,
            icon="💡",
            points=60,
            requirements={"innovations_contributed": 5},
            unlocked_by=set(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ))
        
        self._add_achievement(Achievement(
            achievement_id="breakthrough_moment",
            name="Breakthrough Moment",
            description="Create a solution that achieves 200% of target metrics",
            achievement_type=AchievementType.INNOVATION,
            rarity=AchievementRarity.EPIC,
            icon="🚀",
            points=200,
            requirements={"breakthrough_solutions": 1},
            unlocked_by=set(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ))
        
        # Collaboration Achievements
        self._add_achievement(Achievement(
            achievement_id="team_player",
            name="Team Player",
            description="Collaborate with agents from all 6 stages",
            achievement_type=AchievementType.COLLABORATION,
            rarity=AchievementRarity.UNCOMMON,
            icon="🤝",
            points=80,
            requirements={"collaborated_stages": 6},
            unlocked_by=set(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ))
        
        self._add_achievement(Achievement(
            achievement_id="mentor",
            name="Mentor",
            description="Help 3 novice agents complete their first cycle",
            achievement_type=AchievementType.COLLABORATION,
            rarity=AchievementRarity.RARE,
            icon="👨‍🏫",
            points=150,
            requirements={"mentored_agents": 3},
            unlocked_by=set(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ))
        
        # Leadership Achievements
        self._add_achievement(Achievement(
            achievement_id="stage_leader",
            name="Stage Leader",
            description="Lead 5 successful stage transitions",
            achievement_type=AchievementType.LEADERSHIP,
            rarity=AchievementRarity.UNCOMMON,
            icon="👑",
            points=100,
            requirements={"successful_leadership_actions": 5},
            unlocked_by=set(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ))
        
        self._add_achievement(Achievement(
            achievement_id="cosmic_guide",
            name="Cosmic Guide",
            description="Guide a complete cycle from start to finish",
            achievement_type=AchievementType.LEADERSHIP,
            rarity=AchievementRarity.EPIC,
            icon="🌟",
            points=250,
            requirements={"complete_cycle_leadership": 1},
            unlocked_by=set(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ))
        
        # Special Achievements
        self._add_achievement(Achievement(
            achievement_id="early_adopter",
            name="Early Adopter",
            description="Be among the first 10 agents to join the Cosmic Council",
            achievement_type=AchievementType.SPECIAL,
            rarity=AchievementRarity.LEGENDARY,
            icon="🏆",
            points=500,
            requirements={"early_member": True},
            unlocked_by=set(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ))
        
        self._add_achievement(Achievement(
            achievement_id="sacred_geometry",
            name="Sacred Geometry Master",
            description="Complete 108 cycles (sacred number)",
            achievement_type=AchievementType.SPECIAL,
            rarity=AchievementRarity.LEGENDARY,
            icon="🔮",
            points=1000,
            requirements={"cycles_completed": 108},
            unlocked_by=set(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ))
        
        # Processing Rules Achievements
        self._add_achievement(Achievement(
            achievement_id="linear_flow_master",
            name="Linear Flow Master",
            description="Complete 10 cycles without any stage skipping violations",
            achievement_type=AchievementType.CODE_QUALITY,
            rarity=AchievementRarity.RARE,
            icon="➡️",
            points=150,
            requirements={"linear_flow_cycles": 10},
            unlocked_by=set(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ))
        
        self._add_achievement(Achievement(
            achievement_id="turn_based_expert",
            name="Turn-Based Expert",
            description="Maintain perfect turn-based progression for 5 consecutive cycles",
            achievement_type=AchievementType.CODE_QUALITY,
            rarity=AchievementRarity.UNCOMMON,
            icon="🎯",
            points=100,
            requirements={"perfect_turn_based_cycles": 5},
            unlocked_by=set(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ))
        
        self._add_achievement(Achievement(
            achievement_id="fractal_architect",
            name="Fractal Architect",
            description="Successfully create and manage 3 sub-councils",
            achievement_type=AchievementType.LEADERSHIP,
            rarity=AchievementRarity.EPIC,
            icon="🌀",
            points=300,
            requirements={"sub_councils_created": 3},
            unlocked_by=set(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ))
        
        self._add_achievement(Achievement(
            achievement_id="escalation_master",
            name="Escalation Master",
            description="Successfully escalate 2 problems to higher-order councils",
            achievement_type=AchievementType.LEADERSHIP,
            rarity=AchievementRarity.RARE,
            icon="⬆️",
            points=200,
            requirements={"successful_escalations": 2},
            unlocked_by=set(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ))
        
        self._add_achievement(Achievement(
            achievement_id="action_point_efficiency",
            name="Action Point Efficiency",
            description="Complete a cycle using minimal action points across all stages",
            achievement_type=AchievementType.INNOVATION,
            rarity=AchievementRarity.UNCOMMON,
            icon="⚡",
            points=120,
            requirements={"efficient_cycle_completion": 1},
            unlocked_by=set(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ))
        
        self._add_achievement(Achievement(
            achievement_id="victory_condition_solver",
            name="Victory Condition Solver",
            description="Achieve victory condition (solve, evolve, or escalate) in 5 different ways",
            achievement_type=AchievementType.SPECIAL,
            rarity=AchievementRarity.EPIC,
            icon="🏆",
            points=400,
            requirements={"victory_conditions_achieved": 5},
            unlocked_by=set(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ))
        
        self._add_achievement(Achievement(
            achievement_id="feedback_loop_master",
            name="Feedback Loop Master",
            description="Receive perfect feedback scores from Purple Elephant for 3 consecutive cycles",
            achievement_type=AchievementType.COLLABORATION,
            rarity=AchievementRarity.RARE,
            icon="🔄",
            points=180,
            requirements={"perfect_feedback_cycles": 3},
            unlocked_by=set(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ))

    def _add_achievement(self, achievement: Achievement):
        """Add an achievement to the system"""
        self.achievements[achievement.achievement_id] = achievement

    async def update_agent_stats(self, 
                               agent_id: str,
                               stats_update: Dict[str, Any]):
        """Update agent statistics and check for new achievements"""
        
        # Get or create agent stats
        if agent_id not in self.agent_stats:
            self.agent_stats[agent_id] = AgentStats(
                agent_id=agent_id,
                cycles_completed=0,
                code_quality_score=0.0,
                innovations_contributed=0,
                collaborations_count=0,
                leadership_actions=0,
                special_contributions=0,
                total_points=0,
                last_updated=datetime.now(timezone.utc)
            )
        
        agent_stats = self.agent_stats[agent_id]
        
        # Update stats
        for key, value in stats_update.items():
            if hasattr(agent_stats, key):
                setattr(agent_stats, key, value)
        
        agent_stats.last_updated = datetime.now(timezone.utc)
        
        # Check for new achievements
        new_achievements = await self._check_achievements(agent_id, agent_stats)
        
        # Update total points
        agent_stats.total_points = sum(
            achievement.points for achievement in self.achievements.values()
            if agent_id in achievement.unlocked_by
        )
        
        return new_achievements

    async def _check_achievements(self, agent_id: str, agent_stats: AgentStats) -> List[Achievement]:
        """Check if agent has unlocked any new achievements"""
        new_achievements = []
        
        for achievement in self.achievements.values():
            # Skip if already unlocked
            if agent_id in achievement.unlocked_by:
                continue
            
            # Check if requirements are met
            if self._check_achievement_requirements(achievement, agent_stats):
                # Unlock achievement
                achievement.unlocked_by.add(agent_id)
                new_achievements.append(achievement)
                
                # Create agent achievement record
                if agent_id not in self.agent_achievements:
                    self.agent_achievements[agent_id] = []
                
                self.agent_achievements[agent_id].append(AgentAchievement(
                    agent_id=agent_id,
                    achievement_id=achievement.achievement_id,
                    unlocked_at=datetime.now(timezone.utc),
                    progress={},
                    is_completed=True
                ))
                
                logger.info(f"Agent {agent_id} unlocked achievement: {achievement.name}")
        
        return new_achievements

    def _check_achievement_requirements(self, achievement: Achievement, agent_stats: AgentStats) -> bool:
        """Check if achievement requirements are met"""
        requirements = achievement.requirements
        
        for requirement, target_value in requirements.items():
            if requirement == "cycles_completed":
                if agent_stats.cycles_completed < target_value:
                    return False
            elif requirement == "perfect_cycles":
                # This would need to be tracked separately
                return False
            elif requirement == "consecutive_high_quality_cycles":
                # This would need to be tracked separately
                return False
            elif requirement == "zero_violation_cycles":
                # This would need to be tracked separately
                return False
            elif requirement == "innovations_contributed":
                if agent_stats.innovations_contributed < target_value:
                    return False
            elif requirement == "breakthrough_solutions":
                # This would need to be tracked separately
                return False
            elif requirement == "collaborated_stages":
                # This would need to be tracked separately
                return False
            elif requirement == "mentored_agents":
                # This would need to be tracked separately
                return False
            elif requirement == "successful_leadership_actions":
                if agent_stats.leadership_actions < target_value:
                    return False
            elif requirement == "complete_cycle_leadership":
                # This would need to be tracked separately
                return False
            elif requirement == "early_member":
                # This would need to be tracked separately
                return False
        
        return True

    async def get_agent_achievements(self, agent_id: str) -> List[Achievement]:
        """Get all achievements unlocked by an agent"""
        if agent_id not in self.agent_achievements:
            return []
        
        unlocked_achievement_ids = {
            achievement.achievement_id 
            for achievement in self.agent_achievements[agent_id]
        }
        
        return [
            achievement for achievement in self.achievements.values()
            if achievement.achievement_id in unlocked_achievement_ids
        ]

    async def get_agent_progress(self, agent_id: str) -> Dict[str, Any]:
        """Get agent's progress towards all achievements"""
        if agent_id not in self.agent_stats:
            return {}
        
        agent_stats = self.agent_stats[agent_id]
        progress = {}
        
        for achievement in self.achievements.values():
            if agent_id in achievement.unlocked_by:
                progress[achievement.achievement_id] = {
                    'unlocked': True,
                    'progress': 100,
                    'achievement': asdict(achievement)
                }
            else:
                # Calculate progress percentage
                progress_percentage = self._calculate_progress_percentage(achievement, agent_stats)
                progress[achievement.achievement_id] = {
                    'unlocked': False,
                    'progress': progress_percentage,
                    'achievement': asdict(achievement)
                }
        
        return progress

    def _calculate_progress_percentage(self, achievement: Achievement, agent_stats: AgentStats) -> int:
        """Calculate progress percentage towards an achievement"""
        requirements = achievement.requirements
        
        for requirement, target_value in requirements.items():
            if requirement == "cycles_completed":
                return min(100, int((agent_stats.cycles_completed / target_value) * 100))
            elif requirement == "innovations_contributed":
                return min(100, int((agent_stats.innovations_contributed / target_value) * 100))
            elif requirement == "leadership_actions":
                return min(100, int((agent_stats.leadership_actions / target_value) * 100))
        
        return 0

    async def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get leaderboard of top agents by points"""
        leaderboard = []
        
        for agent_id, stats in self.agent_stats.items():
            achievements = await self.get_agent_achievements(agent_id)
            total_points = sum(achievement.points for achievement in achievements)
            
            leaderboard.append({
                'agent_id': agent_id,
                'total_points': total_points,
                'cycles_completed': stats.cycles_completed,
                'achievements_count': len(achievements),
                'code_quality_score': stats.code_quality_score
            })
        
        # Sort by total points
        leaderboard.sort(key=lambda x: x['total_points'], reverse=True)
        
        return leaderboard[:limit]

    async def get_achievement_statistics(self) -> Dict[str, Any]:
        """Get overall achievement statistics"""
        total_achievements = len(self.achievements)
        total_agents = len(self.agent_stats)
        
        # Count achievements by type
        achievements_by_type = {}
        for achievement_type in AchievementType:
            achievements_by_type[achievement_type.value] = sum(
                1 for achievement in self.achievements.values()
                if achievement.achievement_type == achievement_type
            )
        
        # Count achievements by rarity
        achievements_by_rarity = {}
        for rarity in AchievementRarity:
            achievements_by_rarity[rarity.value] = sum(
                1 for achievement in self.achievements.values()
                if achievement.rarity == rarity
            )
        
        # Calculate unlock rates
        unlock_rates = {}
        for achievement_id, achievement in self.achievements.items():
            unlock_rate = len(achievement.unlocked_by) / max(total_agents, 1) * 100
            unlock_rates[achievement_id] = {
                'name': achievement.name,
                'unlock_rate': unlock_rate,
                'unlocked_count': len(achievement.unlocked_by)
            }
        
        return {
            'total_achievements': total_achievements,
            'total_agents': total_agents,
            'achievements_by_type': achievements_by_type,
            'achievements_by_rarity': achievements_by_rarity,
            'unlock_rates': unlock_rates
        }

    async def create_custom_achievement(self, 
                                      achievement_id: str,
                                      name: str,
                                      description: str,
                                      achievement_type: AchievementType,
                                      rarity: AchievementRarity,
                                      icon: str,
                                      points: int,
                                      requirements: Dict[str, Any]) -> Achievement:
        """Create a custom achievement"""
        
        achievement = Achievement(
            achievement_id=achievement_id,
            name=name,
            description=description,
            achievement_type=achievement_type,
            rarity=rarity,
            icon=icon,
            points=points,
            requirements=requirements,
            unlocked_by=set(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        self._add_achievement(achievement)
        logger.info(f"Created custom achievement: {name}")
        
        return achievement

# Example usage
async def main():
    """Example usage of the achievement system"""
    
    achievement_system = CosmicCouncilAchievementSystem()
    
    # Update agent stats
    new_achievements = await achievement_system.update_agent_stats("agent_001", {
        'cycles_completed': 1,
        'code_quality_score': 95.0,
        'innovations_contributed': 2
    })
    
    print(f"New achievements unlocked: {[a.name for a in new_achievements]}")
    
    # Get agent progress
    progress = await achievement_system.get_agent_progress("agent_001")
    print(f"Agent progress: {len(progress)} achievements tracked")
    
    # Get leaderboard
    leaderboard = await achievement_system.get_leaderboard(5)
    print(f"Top 5 agents: {leaderboard}")
    
    # Get statistics
    stats = await achievement_system.get_achievement_statistics()
    print(f"Achievement statistics: {stats}")

if __name__ == "__main__":
    asyncio.run(main())
