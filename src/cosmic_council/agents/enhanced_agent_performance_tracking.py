"""
Enhanced Agent Performance Tracking System for Agent Orchestrator
Tracks and optimizes the performance of the 6-agent ROYGBV system
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import statistics

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Import the detailed database models
from ..core.models import (
    ResearchCoreProblem, ResearchFinding, ResearchPrioritizedQuestion,
    PlanningRelatedQuestion, PlanningActionPlan, PlanningDependency,
    DevelopmentPrototype, DevelopmentInternalTesting, DevelopmentCreativeNote,
    BudgetResourceInventory, BudgetAllocation, BudgetTimeCostAnalysis,
    MarketInsight, MarketCommunicationStrategy, MarketPerformanceMetric,
    SupportUserFeedback, SupportPerformanceAssessment, SupportContinuousImprovement
)

logger = logging.getLogger(__name__)

class AgentType(Enum):
    """The six Agent Orchestrator agents in ROYGBV order"""
    RED_OWL = "red_owl"           # Research & Inquiry
    ORANGE_ORANGUTAN = "orange_orangutan"  # Planning & Logistics
    YELLOW_HONEYBEE = "yellow_honeybee"    # Development & Creativity
    GREEN_TORTOISE = "green_tortoise"      # Budget & Resources
    BLUE_DOLPHIN = "blue_dolphin"          # Market & Communication
    PURPLE_ELEPHANT = "purple_elephant"    # Support & Feedback

class PerformanceMetricType(Enum):
    """Types of performance metrics"""
    CONFIDENCE_SCORE = "confidence_score"
    PROCESSING_TIME = "processing_time"
    SUCCESS_RATE = "success_rate"
    ERROR_RATE = "error_rate"
    DATA_QUALITY = "data_quality"
    USER_SATISFACTION = "user_satisfaction"
    RESOURCE_UTILIZATION = "resource_utilization"
    LEARNING_RATE = "learning_rate"

@dataclass
class AgentPerformanceMetric:
    """Individual agent performance metric"""
    agent_type: AgentType
    metric_type: PerformanceMetricType
    value: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentPerformanceReport:
    """Agent performance report"""
    agent_type: AgentType
    report_period: Tuple[datetime, datetime]
    metrics: Dict[PerformanceMetricType, List[AgentPerformanceMetric]]
    summary: Dict[str, Any]
    recommendations: List[str]
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class AgentLearningData:
    """Data for agent learning and improvement"""
    agent_type: AgentType
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    performance_feedback: Dict[str, Any]
    improvement_suggestions: List[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class EnhancedAgentPerformanceTracker:
    """
    Enhanced agent performance tracking system
    Monitors, analyzes, and optimizes agent performance
    """
    
    def __init__(self, 
                 database_url: str,
                 performance_config: Dict[str, Any] = None):
        """
        Initialize the performance tracker
        
        Args:
            database_url: Database connection string
            performance_config: Performance tracking configuration
        """
        self.database_url = database_url
        self.performance_config = performance_config or {}
        
        # Create database engine
        self.engine = create_async_engine(database_url)
        self.session_factory = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Performance tracking settings
        self.metric_retention_days = self.performance_config.get('metric_retention_days', 90)
        self.alert_thresholds = self.performance_config.get('alert_thresholds', {
            'confidence_score': 0.7,
            'processing_time': 30.0,  # seconds
            'success_rate': 0.8,
            'error_rate': 0.1
        })
        
        # In-memory performance cache
        self.performance_cache = {}
        self.learning_data = []
        
        logger.info("Enhanced Agent Performance Tracker initialized")

    async def record_agent_performance(self, 
                                     agent_type: AgentType,
                                     metric_type: PerformanceMetricType,
                                     value: float,
                                     context: Dict[str, Any] = None,
                                     metadata: Dict[str, Any] = None) -> str:
        """
        Record a performance metric for an agent
        
        Args:
            agent_type: Type of agent
            metric_type: Type of metric
            value: Metric value
            context: Context information
            metadata: Additional metadata
            
        Returns:
            Metric ID
        """
        try:
            metric_id = str(uuid.uuid4())
            
            # Create performance metric
            metric = AgentPerformanceMetric(
                agent_type=agent_type,
                metric_type=metric_type,
                value=value,
                context=context or {},
                metadata=metadata or {}
            )
            
            # Store in database
            async with self.session_factory() as session:
                await self._store_performance_metric(session, metric, metric_id)
                await session.commit()
            
            # Update cache
            self._update_performance_cache(metric)
            
            # Check for alerts
            await self._check_performance_alerts(metric)
            
            logger.info(f"Recorded {metric_type.value} metric for {agent_type.value}: {value}")
            return metric_id
            
        except Exception as e:
            logger.error(f"Failed to record performance metric: {e}")
            raise

    async def _store_performance_metric(self, session: AsyncSession, metric: AgentPerformanceMetric, metric_id: str):
        """Store performance metric in database"""
        try:
            # Insert into performance_metrics table
            query = text("""
                INSERT INTO agent_performance_metrics 
                (id, agent_type, metric_type, value, timestamp, context, metadata)
                VALUES (:id, :agent_type, :metric_type, :value, :timestamp, :context, :metadata)
            """)
            
            await session.execute(query, {
                'id': metric_id,
                'agent_type': metric.agent_type.value,
                'metric_type': metric.metric_type.value,
                'value': metric.value,
                'timestamp': metric.timestamp,
                'context': json.dumps(metric.context),
                'metadata': json.dumps(metric.metadata)
            })
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to store performance metric: {e}")
            raise

    def _update_performance_cache(self, metric: AgentPerformanceMetric):
        """Update in-memory performance cache"""
        cache_key = f"{metric.agent_type.value}_{metric.metric_type.value}"
        
        if cache_key not in self.performance_cache:
            self.performance_cache[cache_key] = []
        
        self.performance_cache[cache_key].append(metric)
        
        # Keep only recent metrics in cache
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
        self.performance_cache[cache_key] = [
            m for m in self.performance_cache[cache_key] 
            if m.timestamp > cutoff_time
        ]

    async def _check_performance_alerts(self, metric: AgentPerformanceMetric):
        """Check if metric triggers any performance alerts"""
        try:
            threshold = self.alert_thresholds.get(metric.metric_type.value)
            if not threshold:
                return
            
            # Check if metric exceeds threshold
            if metric.metric_type == PerformanceMetricType.CONFIDENCE_SCORE:
                if metric.value < threshold:
                    await self._create_performance_alert(metric, threshold, "low_confidence")
            elif metric.metric_type == PerformanceMetricType.PROCESSING_TIME:
                if metric.value > threshold:
                    await self._create_performance_alert(metric, threshold, "slow_processing")
            elif metric.metric_type == PerformanceMetricType.SUCCESS_RATE:
                if metric.value < threshold:
                    await self._create_performance_alert(metric, threshold, "low_success_rate")
            elif metric.metric_type == PerformanceMetricType.ERROR_RATE:
                if metric.value > threshold:
                    await self._create_performance_alert(metric, threshold, "high_error_rate")
                    
        except Exception as e:
            logger.error(f"Failed to check performance alerts: {e}")

    async def _create_performance_alert(self, metric: AgentPerformanceMetric, threshold: float, alert_type: str):
        """Create a performance alert"""
        try:
            alert_id = str(uuid.uuid4())
            
            async with self.session_factory() as session:
                query = text("""
                    INSERT INTO agent_performance_alerts
                    (id, agent_type, metric_type, alert_type, threshold, current_value, 
                     message, timestamp, resolved)
                    VALUES (:id, :agent_type, :metric_type, :alert_type, :threshold, 
                            :current_value, :message, :timestamp, :resolved)
                """)
                
                message = f"{metric.agent_type.value} {metric.metric_type.value} {alert_type}: {metric.value} (threshold: {threshold})"
                
                await session.execute(query, {
                    'id': alert_id,
                    'agent_type': metric.agent_type.value,
                    'metric_type': metric.metric_type.value,
                    'alert_type': alert_type,
                    'threshold': threshold,
                    'current_value': metric.value,
                    'message': message,
                    'timestamp': metric.timestamp,
                    'resolved': False
                })
                
                await session.commit()
                
            logger.warning(f"Created performance alert: {message}")
            
        except Exception as e:
            logger.error(f"Failed to create performance alert: {e}")

    async def get_agent_performance_report(self, 
                                         agent_type: AgentType,
                                         start_time: datetime,
                                         end_time: datetime) -> AgentPerformanceReport:
        """
        Generate a performance report for an agent
        
        Args:
            agent_type: Type of agent
            start_time: Report start time
            end_time: Report end time
            
        Returns:
            AgentPerformanceReport
        """
        try:
            async with self.session_factory() as session:
                # Get performance metrics
                metrics = await self._get_performance_metrics(session, agent_type, start_time, end_time)
                
                # Calculate summary statistics
                summary = self._calculate_performance_summary(metrics)
                
                # Generate recommendations
                recommendations = await self._generate_performance_recommendations(agent_type, metrics, summary)
                
                return AgentPerformanceReport(
                    agent_type=agent_type,
                    report_period=(start_time, end_time),
                    metrics=metrics,
                    summary=summary,
                    recommendations=recommendations
                )
                
        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            raise

    async def _get_performance_metrics(self, 
                                     session: AsyncSession, 
                                     agent_type: AgentType, 
                                     start_time: datetime, 
                                     end_time: datetime) -> Dict[PerformanceMetricType, List[AgentPerformanceMetric]]:
        """Get performance metrics for an agent"""
        try:
            query = text("""
                SELECT metric_type, value, timestamp, context, metadata
                FROM agent_performance_metrics
                WHERE agent_type = :agent_type
                AND timestamp BETWEEN :start_time AND :end_time
                ORDER BY timestamp
            """)
            
            result = await session.execute(query, {
                'agent_type': agent_type.value,
                'start_time': start_time,
                'end_time': end_time
            })
            
            rows = result.fetchall()
            
            # Group metrics by type
            metrics = {}
            for row in rows:
                metric_type = PerformanceMetricType(row.metric_type)
                if metric_type not in metrics:
                    metrics[metric_type] = []
                
                metric = AgentPerformanceMetric(
                    agent_type=agent_type,
                    metric_type=metric_type,
                    value=row.value,
                    timestamp=row.timestamp,
                    context=json.loads(row.context) if row.context else {},
                    metadata=json.loads(row.metadata) if row.metadata else {}
                )
                metrics[metric_type].append(metric)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            raise

    def _calculate_performance_summary(self, metrics: Dict[PerformanceMetricType, List[AgentPerformanceMetric]]) -> Dict[str, Any]:
        """Calculate performance summary statistics"""
        summary = {}
        
        for metric_type, metric_list in metrics.items():
            if not metric_list:
                continue
            
            values = [metric.value for metric in metric_list]
            
            summary[metric_type.value] = {
                'count': len(values),
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'min': min(values),
                'max': max(values),
                'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0,
                'latest': values[-1] if values else None,
                'trend': self._calculate_trend(values)
            }
        
        return summary

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for a series of values"""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple linear trend calculation
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        if second_avg > first_avg * 1.05:
            return "improving"
        elif second_avg < first_avg * 0.95:
            return "declining"
        else:
            return "stable"

    async def _generate_performance_recommendations(self, 
                                                  agent_type: AgentType, 
                                                  metrics: Dict[PerformanceMetricType, List[AgentPerformanceMetric]], 
                                                  summary: Dict[str, Any]) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        try:
            # Check confidence score
            if 'confidence_score' in summary:
                confidence_data = summary['confidence_score']
                if confidence_data['mean'] < 0.7:
                    recommendations.append(f"Consider improving {agent_type.value} agent prompts and training data to increase confidence scores")
                if confidence_data['trend'] == 'declining':
                    recommendations.append(f"{agent_type.value} agent confidence is declining - review recent changes and feedback")
            
            # Check processing time
            if 'processing_time' in summary:
                processing_data = summary['processing_time']
                if processing_data['mean'] > 30.0:
                    recommendations.append(f"{agent_type.value} agent processing time is high - consider optimizing prompts or reducing data complexity")
                if processing_data['trend'] == 'declining':
                    recommendations.append(f"{agent_type.value} agent processing time is increasing - investigate performance bottlenecks")
            
            # Check success rate
            if 'success_rate' in summary:
                success_data = summary['success_rate']
                if success_data['mean'] < 0.8:
                    recommendations.append(f"{agent_type.value} agent success rate is low - review error patterns and improve error handling")
                if success_data['trend'] == 'declining':
                    recommendations.append(f"{agent_type.value} agent success rate is declining - investigate recent failures")
            
            # Check error rate
            if 'error_rate' in summary:
                error_data = summary['error_rate']
                if error_data['mean'] > 0.1:
                    recommendations.append(f"{agent_type.value} agent error rate is high - improve input validation and error handling")
                if error_data['trend'] == 'declining':
                    recommendations.append(f"{agent_type.value} agent error rate is increasing - review recent changes")
            
            # Agent-specific recommendations
            if agent_type == AgentType.RED_OWL:
                recommendations.append("Consider expanding research data sources and improving question prioritization algorithms")
            elif agent_type == AgentType.ORANGE_ORANGUTAN:
                recommendations.append("Review action plan templates and dependency identification processes")
            elif agent_type == AgentType.YELLOW_HONEYBEE:
                recommendations.append("Enhance creative brainstorming techniques and prototype evaluation criteria")
            elif agent_type == AgentType.GREEN_TORTOISE:
                recommendations.append("Improve budget allocation algorithms and resource optimization strategies")
            elif agent_type == AgentType.BLUE_DOLPHIN:
                recommendations.append("Enhance market analysis capabilities and communication strategy effectiveness")
            elif agent_type == AgentType.PURPLE_ELEPHANT:
                recommendations.append("Improve feedback collection methods and continuous improvement processes")
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            recommendations.append("Unable to generate specific recommendations due to data analysis error")
        
        return recommendations

    async def record_agent_learning_data(self, 
                                       agent_type: AgentType,
                                       input_data: Dict[str, Any],
                                       output_data: Dict[str, Any],
                                       performance_feedback: Dict[str, Any],
                                       improvement_suggestions: List[str] = None) -> str:
        """
        Record learning data for an agent
        
        Args:
            agent_type: Type of agent
            input_data: Input data for the agent
            output_data: Output data from the agent
            performance_feedback: Performance feedback
            improvement_suggestions: Suggestions for improvement
            
        Returns:
            Learning data ID
        """
        try:
            learning_id = str(uuid.uuid4())
            
            learning_data = AgentLearningData(
                agent_type=agent_type,
                input_data=input_data,
                output_data=output_data,
                performance_feedback=performance_feedback,
                improvement_suggestions=improvement_suggestions or []
            )
            
            # Store in database
            async with self.session_factory() as session:
                await self._store_learning_data(session, learning_data, learning_id)
                await session.commit()
            
            # Add to in-memory cache
            self.learning_data.append(learning_data)
            
            logger.info(f"Recorded learning data for {agent_type.value}")
            return learning_id
            
        except Exception as e:
            logger.error(f"Failed to record learning data: {e}")
            raise

    async def _store_learning_data(self, session: AsyncSession, learning_data: AgentLearningData, learning_id: str):
        """Store learning data in database"""
        try:
            query = text("""
                INSERT INTO agent_learning_data
                (id, agent_type, input_data, output_data, performance_feedback, 
                 improvement_suggestions, timestamp)
                VALUES (:id, :agent_type, :input_data, :output_data, :performance_feedback,
                        :improvement_suggestions, :timestamp)
            """)
            
            await session.execute(query, {
                'id': learning_id,
                'agent_type': learning_data.agent_type.value,
                'input_data': json.dumps(learning_data.input_data),
                'output_data': json.dumps(learning_data.output_data),
                'performance_feedback': json.dumps(learning_data.performance_feedback),
                'improvement_suggestions': json.dumps(learning_data.improvement_suggestions),
                'timestamp': learning_data.timestamp
            })
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to store learning data: {e}")
            raise

    async def get_agent_learning_insights(self, 
                                        agent_type: AgentType,
                                        days_back: int = 30) -> Dict[str, Any]:
        """
        Get learning insights for an agent
        
        Args:
            agent_type: Type of agent
            days_back: Number of days to look back
            
        Returns:
            Learning insights
        """
        try:
            start_time = datetime.now(timezone.utc) - timedelta(days=days_back)
            
            async with self.session_factory() as session:
                query = text("""
                    SELECT input_data, output_data, performance_feedback, improvement_suggestions
                    FROM agent_learning_data
                    WHERE agent_type = :agent_type
                    AND timestamp >= :start_time
                    ORDER BY timestamp
                """)
                
                result = await session.execute(query, {
                    'agent_type': agent_type.value,
                    'start_time': start_time
                })
                
                rows = result.fetchall()
                
                # Analyze learning data
                insights = {
                    'total_learning_instances': len(rows),
                    'common_input_patterns': {},
                    'common_output_patterns': {},
                    'performance_trends': {},
                    'improvement_areas': [],
                    'success_factors': []
                }
                
                # Analyze patterns
                for row in rows:
                    input_data = json.loads(row.input_data) if row.input_data else {}
                    output_data = json.loads(row.output_data) if row.output_data else {}
                    performance_feedback = json.loads(row.performance_feedback) if row.performance_feedback else {}
                    improvement_suggestions = json.loads(row.improvement_suggestions) if row.improvement_suggestions else []
                    
                    # Track common patterns
                    for key, value in input_data.items():
                        if key not in insights['common_input_patterns']:
                            insights['common_input_patterns'][key] = []
                        insights['common_input_patterns'][key].append(value)
                    
                    for key, value in output_data.items():
                        if key not in insights['common_output_patterns']:
                            insights['common_output_patterns'][key] = []
                        insights['common_output_patterns'][key].append(value)
                    
                    # Track improvement areas
                    insights['improvement_areas'].extend(improvement_suggestions)
                
                # Calculate success factors
                if insights['common_output_patterns']:
                    for pattern, values in insights['common_output_patterns'].items():
                        if len(values) > 5:  # Only consider patterns with sufficient data
                            insights['success_factors'].append({
                                'pattern': pattern,
                                'frequency': len(values),
                                'sample_values': values[:3]
                            })
                
                return insights
                
        except Exception as e:
            logger.error(f"Failed to get learning insights: {e}")
            raise

    async def optimize_agent_performance(self, agent_type: AgentType) -> Dict[str, Any]:
        """
        Optimize agent performance based on historical data
        
        Args:
            agent_type: Type of agent to optimize
            
        Returns:
            Optimization results
        """
        try:
            # Get recent performance data
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(days=30)
            
            report = await self.get_agent_performance_report(agent_type, start_time, end_time)
            learning_insights = await self.get_agent_learning_insights(agent_type, 30)
            
            # Generate optimization recommendations
            optimization_plan = {
                'agent_type': agent_type.value,
                'current_performance': report.summary,
                'optimization_recommendations': report.recommendations,
                'learning_insights': learning_insights,
                'optimization_actions': [],
                'expected_improvements': {}
            }
            
            # Generate specific optimization actions
            if 'confidence_score' in report.summary and report.summary['confidence_score']['mean'] < 0.8:
                optimization_plan['optimization_actions'].append({
                    'action': 'improve_prompts',
                    'description': 'Enhance agent prompts based on learning insights',
                    'priority': 'high'
                })
                optimization_plan['expected_improvements']['confidence_score'] = 0.1
            
            if 'processing_time' in report.summary and report.summary['processing_time']['mean'] > 20.0:
                optimization_plan['optimization_actions'].append({
                    'action': 'optimize_processing',
                    'description': 'Optimize data processing and reduce complexity',
                    'priority': 'medium'
                })
                optimization_plan['expected_improvements']['processing_time'] = -5.0
            
            if 'success_rate' in report.summary and report.summary['success_rate']['mean'] < 0.9:
                optimization_plan['optimization_actions'].append({
                    'action': 'improve_error_handling',
                    'description': 'Enhance error handling and validation',
                    'priority': 'high'
                })
                optimization_plan['expected_improvements']['success_rate'] = 0.05
            
            return optimization_plan
            
        except Exception as e:
            logger.error(f"Failed to optimize agent performance: {e}")
            raise

    async def close(self):
        """Close database connections"""
        await self.engine.dispose()
        logger.info("Enhanced Agent Performance Tracker closed")

# Example usage
async def main():
    """Example usage of the enhanced agent performance tracking system"""
    
    tracker = EnhancedAgentPerformanceTracker(
        database_url="postgresql+asyncpg://user:password@localhost/dream_caesar",
        performance_config={
            'metric_retention_days': 90,
            'alert_thresholds': {
                'confidence_score': 0.7,
                'processing_time': 30.0,
                'success_rate': 0.8,
                'error_rate': 0.1
            }
        }
    )
    
    try:
        # Record performance metrics
        await tracker.record_agent_performance(
            AgentType.RED_OWL,
            PerformanceMetricType.CONFIDENCE_SCORE,
            0.85,
            context={"problem_type": "research", "complexity": "medium"},
            metadata={"model_version": "gpt-4", "temperature": 0.7}
        )
        
        # Generate performance report
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=7)
        
        report = await tracker.get_agent_performance_report(
            AgentType.RED_OWL,
            start_time,
            end_time
        )
        
        print(f"Performance Report for {report.agent_type.value}:")
        print(f"Summary: {json.dumps(report.summary, indent=2)}")
        print(f"Recommendations: {report.recommendations}")
        
        # Get learning insights
        insights = await tracker.get_agent_learning_insights(AgentType.RED_OWL, 30)
        print(f"Learning Insights: {json.dumps(insights, indent=2)}")
        
        # Optimize performance
        optimization = await tracker.optimize_agent_performance(AgentType.RED_OWL)
        print(f"Optimization Plan: {json.dumps(optimization, indent=2)}")
        
    finally:
        await tracker.close()

if __name__ == "__main__":
    asyncio.run(main())
