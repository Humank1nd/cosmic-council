"""
Analytics service for providing insights and metrics in the Cosmic Council system.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
import logging

from ..models.cycle import Cycle, CycleResult
from ..models.problem import Problem
from ..models.solution import Solution
from ..models.enterprise import EnterpriseResult

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analytics and insights"""
    
    def __init__(self, repository=None):
        self.repository = repository
        self.logger = logger
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get overall system metrics"""
        try:
            metrics = {
                'timestamp': datetime.now(timezone.utc),
                'total_problems': 0,
                'total_solutions': 0,
                'total_cycles': 0,
                'active_cycles': 0,
                'completed_cycles': 0,
                'failed_cycles': 0,
                'average_cycle_duration': 0.0,
                'success_rate': 0.0
            }
            
            if self.repository:
                # Get problem count
                problems = await self.repository.list_problems()
                metrics['total_problems'] = len(problems)
                
                # Get solution count
                solutions = await self.repository.list_solutions()
                metrics['total_solutions'] = len(solutions)
                
                # Get cycle metrics
                cycles = await self.repository.list_cycles()
                metrics['total_cycles'] = len(cycles)
                
                active_cycles = [c for c in cycles if c.status.value in ['running', 'paused']]
                completed_cycles = [c for c in cycles if c.status.value == 'completed']
                failed_cycles = [c for c in cycles if c.status.value == 'failed']
                
                metrics['active_cycles'] = len(active_cycles)
                metrics['completed_cycles'] = len(completed_cycles)
                metrics['failed_cycles'] = len(failed_cycles)
                
                # Calculate success rate
                if len(cycles) > 0:
                    metrics['success_rate'] = len(completed_cycles) / len(cycles)
                
                # Calculate average cycle duration
                if completed_cycles:
                    total_duration = 0
                    for cycle in completed_cycles:
                        if cycle.started_at and cycle.completed_at:
                            duration = (cycle.completed_at - cycle.started_at).total_seconds()
                            total_duration += duration
                    metrics['average_cycle_duration'] = total_duration / len(completed_cycles)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {e}")
            return {'error': str(e)}
    
    async def get_problem_analytics(self, problem_id: str) -> Dict[str, Any]:
        """Get analytics for a specific problem"""
        try:
            analytics = {
                'problem_id': problem_id,
                'timestamp': datetime.now(timezone.utc),
                'total_cycles': 0,
                'successful_cycles': 0,
                'average_cycle_duration': 0.0,
                'enterprise_performance': {},
                'solution_quality': 0.0
            }
            
            if self.repository:
                # Get cycles for this problem
                cycles = await self.repository.get_cycles_by_problem_id(problem_id)
                analytics['total_cycles'] = len(cycles)
                
                successful_cycles = [c for c in cycles if c.status.value == 'completed']
                analytics['successful_cycles'] = len(successful_cycles)
                
                # Calculate average duration
                if successful_cycles:
                    total_duration = 0
                    for cycle in successful_cycles:
                        if cycle.started_at and cycle.completed_at:
                            duration = (cycle.completed_at - cycle.started_at).total_seconds()
                            total_duration += duration
                    analytics['average_cycle_duration'] = total_duration / len(successful_cycles)
                
                # Get enterprise performance
                for cycle in cycles:
                    results = await self.repository.get_results_by_cycle_id(cycle.id)
                    for result in results:
                        enterprise_type = result.enterprise_type.value
                        if enterprise_type not in analytics['enterprise_performance']:
                            analytics['enterprise_performance'][enterprise_type] = {
                                'total_executions': 0,
                                'successful_executions': 0,
                                'average_execution_time': 0.0,
                                'average_quality_score': 0.0
                            }
                        
                        perf = analytics['enterprise_performance'][enterprise_type]
                        perf['total_executions'] += 1
                        if result.success:
                            perf['successful_executions'] += 1
                        perf['average_execution_time'] += result.execution_time
                        perf['average_quality_score'] += result.quality_score
                
                # Calculate averages
                for enterprise_type, perf in analytics['enterprise_performance'].items():
                    if perf['total_executions'] > 0:
                        perf['average_execution_time'] /= perf['total_executions']
                        perf['average_quality_score'] /= perf['total_executions']
                
                # Get solution quality
                solutions = await self.repository.get_solutions_by_problem_id(problem_id)
                if solutions:
                    total_confidence = sum(s.confidence_score for s in solutions)
                    analytics['solution_quality'] = total_confidence / len(solutions)
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error getting problem analytics: {e}")
            return {'error': str(e)}
    
    async def get_enterprise_performance(self, enterprise_type: str, days: int = 30) -> Dict[str, Any]:
        """Get performance metrics for a specific enterprise"""
        try:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)
            
            performance = {
                'enterprise_type': enterprise_type,
                'period': f"{start_date.date()} to {end_date.date()}",
                'total_executions': 0,
                'successful_executions': 0,
                'failed_executions': 0,
                'average_execution_time': 0.0,
                'average_quality_score': 0.0,
                'success_rate': 0.0,
                'performance_trend': []
            }
            
            if self.repository:
                # Get results for this enterprise in the time period
                results = await self.repository.get_enterprise_results_by_type_and_date(
                    enterprise_type, start_date, end_date
                )
                
                performance['total_executions'] = len(results)
                successful_results = [r for r in results if r.success]
                failed_results = [r for r in results if not r.success]
                
                performance['successful_executions'] = len(successful_results)
                performance['failed_executions'] = len(failed_results)
                
                if len(results) > 0:
                    performance['success_rate'] = len(successful_results) / len(results)
                    performance['average_execution_time'] = sum(r.execution_time for r in results) / len(results)
                    performance['average_quality_score'] = sum(r.quality_score for r in results) / len(results)
                
                # Calculate daily performance trend
                daily_performance = {}
                for result in results:
                    date_key = result.created_at.date()
                    if date_key not in daily_performance:
                        daily_performance[date_key] = {'total': 0, 'successful': 0}
                    daily_performance[date_key]['total'] += 1
                    if result.success:
                        daily_performance[date_key]['successful'] += 1
                
                for date, stats in sorted(daily_performance.items()):
                    performance['performance_trend'].append({
                        'date': date.isoformat(),
                        'total_executions': stats['total'],
                        'successful_executions': stats['successful'],
                        'success_rate': stats['successful'] / stats['total'] if stats['total'] > 0 else 0
                    })
            
            return performance
            
        except Exception as e:
            self.logger.error(f"Error getting enterprise performance: {e}")
            return {'error': str(e)}
    
    async def get_cycle_analytics(self, cycle_id: str) -> Dict[str, Any]:
        """Get detailed analytics for a specific cycle"""
        try:
            analytics = {
                'cycle_id': cycle_id,
                'timestamp': datetime.now(timezone.utc),
                'cycle_status': '',
                'total_enterprises': 0,
                'completed_enterprises': 0,
                'failed_enterprises': 0,
                'total_execution_time': 0.0,
                'enterprise_results': [],
                'overall_quality_score': 0.0
            }
            
            if self.repository:
                cycle = await self.repository.get_cycle_by_id(cycle_id)
                if cycle:
                    analytics['cycle_status'] = cycle.status.value
                    analytics['total_enterprises'] = len(cycle.enterprises)
                    
                    results = await self.repository.get_results_by_cycle_id(cycle_id)
                    analytics['completed_enterprises'] = len([r for r in results if r.success])
                    analytics['failed_enterprises'] = len([r for r in results if not r.success])
                    analytics['total_execution_time'] = sum(r.execution_time for r in results)
                    
                    if results:
                        analytics['overall_quality_score'] = sum(r.quality_score for r in results) / len(results)
                    
                    # Detailed enterprise results
                    for result in results:
                        analytics['enterprise_results'].append({
                            'enterprise_type': result.enterprise_type.value,
                            'success': result.success,
                            'execution_time': result.execution_time,
                            'quality_score': result.quality_score,
                            'error_message': result.error_message if not result.success else None
                        })
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error getting cycle analytics: {e}")
            return {'error': str(e)}
    
    async def get_performance_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get performance trends over time"""
        try:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)
            
            trends = {
                'period': f"{start_date.date()} to {end_date.date()}",
                'daily_metrics': [],
                'enterprise_trends': {},
                'overall_trends': {
                    'cycles_started': 0,
                    'cycles_completed': 0,
                    'cycles_failed': 0,
                    'average_cycle_duration': 0.0
                }
            }
            
            if self.repository:
                # Get daily metrics
                for i in range(days):
                    date = start_date + timedelta(days=i)
                    daily_cycles = await self.repository.get_cycles_by_date(date.date())
                    
                    daily_metric = {
                        'date': date.date().isoformat(),
                        'cycles_started': len(daily_cycles),
                        'cycles_completed': len([c for c in daily_cycles if c.status.value == 'completed']),
                        'cycles_failed': len([c for c in daily_cycles if c.status.value == 'failed']),
                        'average_duration': 0.0
                    }
                    
                    completed_cycles = [c for c in daily_cycles if c.status.value == 'completed']
                    if completed_cycles:
                        total_duration = 0
                        for cycle in completed_cycles:
                            if cycle.started_at and cycle.completed_at:
                                duration = (cycle.completed_at - cycle.started_at).total_seconds()
                                total_duration += duration
                        daily_metric['average_duration'] = total_duration / len(completed_cycles)
                    
                    trends['daily_metrics'].append(daily_metric)
                
                # Calculate overall trends
                all_cycles = await self.repository.get_cycles_by_date_range(start_date.date(), end_date.date())
                trends['overall_trends']['cycles_started'] = len(all_cycles)
                trends['overall_trends']['cycles_completed'] = len([c for c in all_cycles if c.status.value == 'completed'])
                trends['overall_trends']['cycles_failed'] = len([c for c in all_cycles if c.status.value == 'failed'])
                
                completed_cycles = [c for c in all_cycles if c.status.value == 'completed']
                if completed_cycles:
                    total_duration = 0
                    for cycle in completed_cycles:
                        if cycle.started_at and cycle.completed_at:
                            duration = (cycle.completed_at - cycle.started_at).total_seconds()
                            total_duration += duration
                    trends['overall_trends']['average_cycle_duration'] = total_duration / len(completed_cycles)
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Error getting performance trends: {e}")
            return {'error': str(e)}
