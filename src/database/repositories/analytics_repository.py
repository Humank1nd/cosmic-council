"""
Analytics Repository for Agent Orchestrator.

Provides database access for analytics data including cycle metrics,
enterprise performance, and historical trends.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


# ============== Time Range ==============

class TimeRange:
    """Time range for analytics queries."""

    def __init__(self, start: datetime, end: datetime):
        self.start = start
        self.end = end

    @classmethod
    def last_hour(cls) -> "TimeRange":
        end = datetime.utcnow()
        return cls(end - timedelta(hours=1), end)

    @classmethod
    def last_day(cls) -> "TimeRange":
        end = datetime.utcnow()
        return cls(end - timedelta(days=1), end)

    @classmethod
    def last_week(cls) -> "TimeRange":
        end = datetime.utcnow()
        return cls(end - timedelta(weeks=1), end)

    @classmethod
    def last_month(cls) -> "TimeRange":
        end = datetime.utcnow()
        return cls(end - timedelta(days=30), end)

    @classmethod
    def last_quarter(cls) -> "TimeRange":
        end = datetime.utcnow()
        return cls(end - timedelta(days=90), end)

    @classmethod
    def custom(cls, days: int) -> "TimeRange":
        end = datetime.utcnow()
        return cls(end - timedelta(days=days), end)


# ============== Analytics Repository ==============

class AnalyticsRepository:
    """
    Repository for analytics data queries.

    Provides aggregated metrics from cycle, problem, and solution data.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    # ============== Cycle Metrics ==============

    async def get_cycle_metrics(
        self,
        time_range: Optional[TimeRange] = None,
    ) -> Dict[str, Any]:
        """
        Get aggregated cycle metrics.

        Returns:
            Dict with total, completed, failed, in_progress counts
            and average duration, success rate.
        """
        try:
            # Build base query for cycles
            query = """
                SELECT
                    COUNT(*) as total_cycles,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                    SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) as in_progress,
                    AVG(CASE
                        WHEN completed_at IS NOT NULL
                        THEN CAST((julianday(completed_at) - julianday(started_at)) * 86400 AS REAL)
                        ELSE NULL
                    END) as avg_duration_seconds
                FROM cycles
            """

            if time_range:
                query += f" WHERE started_at >= '{time_range.start.isoformat()}'"
                query += f" AND started_at <= '{time_range.end.isoformat()}'"

            result = await self.session.execute(text(query))
            row = result.fetchone()

            if not row:
                return self._empty_cycle_metrics()

            total = row[0] or 0
            completed = row[1] or 0
            failed = row[2] or 0
            in_progress = row[3] or 0
            avg_duration = row[4] or 0

            success_rate = (completed / total * 100) if total > 0 else 0

            return {
                "total_cycles": total,
                "completed_cycles": completed,
                "failed_cycles": failed,
                "in_progress_cycles": in_progress,
                "avg_duration_seconds": round(avg_duration, 2),
                "success_rate": round(success_rate, 2),
            }

        except SQLAlchemyError as e:
            logger.error(f"Error getting cycle metrics: {e}")
            return self._empty_cycle_metrics()

    def _empty_cycle_metrics(self) -> Dict[str, Any]:
        """Return empty cycle metrics structure."""
        return {
            "total_cycles": 0,
            "completed_cycles": 0,
            "failed_cycles": 0,
            "in_progress_cycles": 0,
            "avg_duration_seconds": 0,
            "success_rate": 0,
        }

    # ============== Enterprise Performance ==============

    async def get_enterprise_performance(
        self,
        enterprise: Optional[str] = None,
        time_range: Optional[TimeRange] = None,
    ) -> Dict[str, Any]:
        """
        Get enterprise (agent) performance metrics.

        Args:
            enterprise: Specific enterprise to query (or all if None)
            time_range: Optional time range filter

        Returns:
            Dict with per-enterprise success rates, latencies, confidence.
        """
        try:
            query = """
                SELECT
                    enterprise_type,
                    COUNT(*) as total_executions,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                    AVG(execution_time) as avg_latency,
                    AVG(json_extract(metrics, '$.confidence')) as avg_confidence
                FROM cycle_results
            """

            conditions = []
            if enterprise:
                conditions.append(f"enterprise_type = '{enterprise}'")
            if time_range:
                conditions.append(f"created_at >= '{time_range.start.isoformat()}'")
                conditions.append(f"created_at <= '{time_range.end.isoformat()}'")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " GROUP BY enterprise_type"

            result = await self.session.execute(text(query))
            rows = result.fetchall()

            performance = {}
            for row in rows:
                ent_type = row[0]
                total = row[1] or 0
                successful = row[2] or 0
                avg_latency = row[3] or 0
                avg_confidence = row[4] or 0

                success_rate = (successful / total * 100) if total > 0 else 0

                performance[ent_type] = {
                    "total_executions": total,
                    "successful_executions": successful,
                    "success_rate": round(success_rate, 2),
                    "avg_latency_seconds": round(avg_latency, 3),
                    "avg_confidence": round(avg_confidence, 3),
                }

            return performance

        except SQLAlchemyError as e:
            logger.error(f"Error getting enterprise performance: {e}")
            return {}

    # ============== Problem Metrics ==============

    async def get_problem_metrics(
        self,
        time_range: Optional[TimeRange] = None,
    ) -> Dict[str, Any]:
        """
        Get problem-related metrics.

        Returns:
            Dict with problem counts by status, complexity distribution.
        """
        try:
            query = """
                SELECT
                    COUNT(*) as total_problems,
                    SUM(CASE WHEN status = 'solved' THEN 1 ELSE 0 END) as solved,
                    SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                    AVG(json_extract(metadata, '$.complexity')) as avg_complexity
                FROM problems
            """

            if time_range:
                query += f" WHERE created_at >= '{time_range.start.isoformat()}'"
                query += f" AND created_at <= '{time_range.end.isoformat()}'"

            result = await self.session.execute(text(query))
            row = result.fetchone()

            if not row:
                return self._empty_problem_metrics()

            return {
                "total_problems": row[0] or 0,
                "solved_problems": row[1] or 0,
                "in_progress_problems": row[2] or 0,
                "failed_problems": row[3] or 0,
                "avg_complexity": round(row[4] or 0, 2),
            }

        except SQLAlchemyError as e:
            logger.error(f"Error getting problem metrics: {e}")
            return self._empty_problem_metrics()

    def _empty_problem_metrics(self) -> Dict[str, Any]:
        """Return empty problem metrics structure."""
        return {
            "total_problems": 0,
            "solved_problems": 0,
            "in_progress_problems": 0,
            "failed_problems": 0,
            "avg_complexity": 0,
        }

    # ============== Solution Metrics ==============

    async def get_solution_metrics(
        self,
        time_range: Optional[TimeRange] = None,
    ) -> Dict[str, Any]:
        """
        Get solution-related metrics.

        Returns:
            Dict with solution quality scores, implementation rates.
        """
        try:
            query = """
                SELECT
                    COUNT(*) as total_solutions,
                    AVG(json_extract(metadata, '$.quality_score')) as avg_quality,
                    SUM(CASE WHEN status = 'implemented' THEN 1 ELSE 0 END) as implemented,
                    AVG(json_extract(metadata, '$.stakeholder_satisfaction')) as avg_satisfaction
                FROM solutions
            """

            if time_range:
                query += f" WHERE created_at >= '{time_range.start.isoformat()}'"
                query += f" AND created_at <= '{time_range.end.isoformat()}'"

            result = await self.session.execute(text(query))
            row = result.fetchone()

            if not row:
                return self._empty_solution_metrics()

            total = row[0] or 0
            implemented = row[2] or 0
            implementation_rate = (implemented / total * 100) if total > 0 else 0

            return {
                "total_solutions": total,
                "avg_quality_score": round(row[1] or 0, 2),
                "implemented_solutions": implemented,
                "implementation_rate": round(implementation_rate, 2),
                "avg_stakeholder_satisfaction": round(row[3] or 0, 2),
            }

        except SQLAlchemyError as e:
            logger.error(f"Error getting solution metrics: {e}")
            return self._empty_solution_metrics()

    def _empty_solution_metrics(self) -> Dict[str, Any]:
        """Return empty solution metrics structure."""
        return {
            "total_solutions": 0,
            "avg_quality_score": 0,
            "implemented_solutions": 0,
            "implementation_rate": 0,
            "avg_stakeholder_satisfaction": 0,
        }

    # ============== Recursion Metrics ==============

    async def get_recursion_metrics(
        self,
        time_range: Optional[TimeRange] = None,
    ) -> Dict[str, Any]:
        """
        Get recursion-related metrics for confidence calibration.

        Returns:
            Dict with recursion counts, reasons, success after recursion.
        """
        try:
            query = """
                SELECT
                    COUNT(*) as total_recursions,
                    AVG(recursion_depth) as avg_recursion_depth,
                    MAX(recursion_depth) as max_recursion_depth,
                    SUM(CASE WHEN final_status = 'solved' THEN 1 ELSE 0 END) as successful_after_recursion
                FROM cycles
                WHERE recursion_depth > 0
            """

            if time_range:
                query += f" AND started_at >= '{time_range.start.isoformat()}'"
                query += f" AND started_at <= '{time_range.end.isoformat()}'"

            result = await self.session.execute(text(query))
            row = result.fetchone()

            if not row or row[0] == 0:
                return {
                    "total_recursions": 0,
                    "avg_recursion_depth": 0,
                    "max_recursion_depth": 0,
                    "success_after_recursion_rate": 0,
                }

            total = row[0] or 0
            successful = row[3] or 0
            success_rate = (successful / total * 100) if total > 0 else 0

            return {
                "total_recursions": total,
                "avg_recursion_depth": round(row[1] or 0, 2),
                "max_recursion_depth": row[2] or 0,
                "success_after_recursion_rate": round(success_rate, 2),
            }

        except SQLAlchemyError as e:
            logger.error(f"Error getting recursion metrics: {e}")
            return {
                "total_recursions": 0,
                "avg_recursion_depth": 0,
                "max_recursion_depth": 0,
                "success_after_recursion_rate": 0,
            }

    # ============== Calibration Metrics ==============

    async def get_calibration_metrics(
        self,
        start_time: datetime,
        end_time: datetime,
    ) -> Dict[str, Any]:
        """
        Get metrics for confidence calibration.

        Used by ConfidenceCalibrator to adjust thresholds.

        Returns:
            Dict with historical success rates and confidence distributions.
        """
        try:
            # Overall metrics
            cycle_metrics = await self.get_cycle_metrics(
                TimeRange(start_time, end_time)
            )

            # Per-enterprise performance
            enterprise_perf = await self.get_enterprise_performance(
                time_range=TimeRange(start_time, end_time)
            )

            # Recursion metrics
            recursion_metrics = await self.get_recursion_metrics(
                TimeRange(start_time, end_time)
            )

            # Build calibration data
            avg_confidence_by_role = {}
            success_rate_by_role = {}

            for enterprise, perf in enterprise_perf.items():
                role = self._enterprise_to_role(enterprise)
                if role:
                    avg_confidence_by_role[role] = perf.get("avg_confidence", 0)
                    success_rate_by_role[role] = perf.get("success_rate", 0) / 100

            return {
                "total_cycles": cycle_metrics.get("total_cycles", 0),
                "successful_cycles": cycle_metrics.get("completed_cycles", 0),
                "recursion_count": recursion_metrics.get("total_recursions", 0),
                "human_review_count": 0,  # TODO: Track human reviews
                "avg_confidence_by_role": avg_confidence_by_role,
                "success_rate_by_role": success_rate_by_role,
            }

        except SQLAlchemyError as e:
            logger.error(f"Error getting calibration metrics: {e}")
            return {
                "total_cycles": 0,
                "successful_cycles": 0,
                "recursion_count": 0,
                "human_review_count": 0,
                "avg_confidence_by_role": {},
                "success_rate_by_role": {},
            }

    def _enterprise_to_role(self, enterprise: str) -> Optional[str]:
        """Map enterprise type to triangle role."""
        mapping = {
            "red_owl": "why",
            "orange_orangutan": "how",
            "yellow_honeybee": "what",
            "green_tortoise": "when",
            "blue_dolphin": "where",
            "purple_elephant": "who",
            "research": "why",
            "planning": "how",
            "development": "what",
            "budget": "when",
            "market": "where",
            "support": "who",
        }
        return mapping.get(enterprise.lower())

    # ============== Trend Data ==============

    async def get_trend_data(
        self,
        metric: str,
        time_range: TimeRange,
        granularity: str = "day",
    ) -> List[Dict[str, Any]]:
        """
        Get time-series trend data for a metric.

        Args:
            metric: Metric name (cycles, problems, solutions)
            time_range: Time range for data
            granularity: "hour", "day", "week", "month"

        Returns:
            List of {timestamp, value} dicts
        """
        try:
            # Determine date function based on granularity
            date_func_map = {
                "hour": "strftime('%Y-%m-%d %H:00', created_at)",
                "day": "date(created_at)",
                "week": "strftime('%Y-W%W', created_at)",
                "month": "strftime('%Y-%m', created_at)",
            }
            date_func = date_func_map.get(granularity, date_func_map["day"])

            # Map metric to table
            table_map = {
                "cycles": "cycles",
                "problems": "problems",
                "solutions": "solutions",
            }
            table = table_map.get(metric, "cycles")

            query = f"""
                SELECT
                    {date_func} as period,
                    COUNT(*) as count
                FROM {table}
                WHERE created_at >= '{time_range.start.isoformat()}'
                  AND created_at <= '{time_range.end.isoformat()}'
                GROUP BY period
                ORDER BY period
            """

            result = await self.session.execute(text(query))
            rows = result.fetchall()

            return [
                {"timestamp": row[0], "value": row[1]}
                for row in rows
            ]

        except SQLAlchemyError as e:
            logger.error(f"Error getting trend data for {metric}: {e}")
            return []

    # ============== KPI Calculations ==============

    async def get_kpis(
        self,
        time_range: Optional[TimeRange] = None,
    ) -> Dict[str, Any]:
        """
        Get key performance indicators.

        Returns:
            Dict with all major KPIs
        """
        cycle_metrics = await self.get_cycle_metrics(time_range)
        problem_metrics = await self.get_problem_metrics(time_range)
        solution_metrics = await self.get_solution_metrics(time_range)
        recursion_metrics = await self.get_recursion_metrics(time_range)

        return {
            "total_problems_solved": problem_metrics.get("solved_problems", 0),
            "cycle_success_rate": cycle_metrics.get("success_rate", 0),
            "avg_cycle_duration": cycle_metrics.get("avg_duration_seconds", 0),
            "solution_quality_score": solution_metrics.get("avg_quality_score", 0),
            "stakeholder_satisfaction": solution_metrics.get("avg_stakeholder_satisfaction", 0),
            "recursion_success_rate": recursion_metrics.get("success_after_recursion_rate", 0),
            "implementation_rate": solution_metrics.get("implementation_rate", 0),
            "active_cycles": cycle_metrics.get("in_progress_cycles", 0),
        }

    # ============== Recent Activity ==============

    async def get_recent_activity(
        self,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get recent activity across all entities.

        Returns:
            List of recent activity events
        """
        try:
            query = """
                SELECT 'cycle' as type, id, status, created_at
                FROM cycles
                ORDER BY created_at DESC
                LIMIT :limit
            """

            result = await self.session.execute(text(query), {"limit": limit})
            rows = result.fetchall()

            return [
                {
                    "type": row[0],
                    "id": row[1],
                    "status": row[2],
                    "timestamp": row[3],
                }
                for row in rows
            ]

        except SQLAlchemyError as e:
            logger.error(f"Error getting recent activity: {e}")
            return []
