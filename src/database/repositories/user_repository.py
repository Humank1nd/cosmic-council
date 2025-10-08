"""
User repository for database operations.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc, func
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import SQLAlchemyError
import logging

from .base_repository import BaseRepository
from ..models.user import User, Stakeholder, Constraint, SuccessCriterion

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
    """Repository for User model"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            result = await self.session.execute(
                select(User)
                .where(User.username == username)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting user by username {username}: {e}")
            raise
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            result = await self.session.execute(
                select(User)
                .where(User.email == email)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting user by email {email}: {e}")
            raise
    
    async def get_by_role(self, role: str) -> List[User]:
        """Get users by role"""
        try:
            result = await self.session.execute(
                select(User)
                .where(User.role == role)
                .order_by(asc(User.username))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting users by role {role}: {e}")
            raise
    
    async def get_active_users(self) -> List[User]:
        """Get all active users"""
        try:
            result = await self.session.execute(
                select(User)
                .where(User.is_active == 'true')
                .order_by(asc(User.username))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting active users: {e}")
            raise
    
    async def get_inactive_users(self) -> List[User]:
        """Get all inactive users"""
        try:
            result = await self.session.execute(
                select(User)
                .where(User.is_active == 'false')
                .order_by(asc(User.username))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting inactive users: {e}")
            raise
    
    async def search_users(self, search_term: str) -> List[User]:
        """Search users by username, email, or full name"""
        try:
            result = await self.session.execute(
                select(User)
                .where(
                    or_(
                        User.username.ilike(f"%{search_term}%"),
                        User.email.ilike(f"%{search_term}%"),
                        User.full_name.ilike(f"%{search_term}%")
                    )
                )
                .order_by(asc(User.username))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error searching users with term {search_term}: {e}")
            raise
    
    async def update_last_login(self, user_id: str) -> Optional[User]:
        """Update user's last login timestamp"""
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return None
            
            from datetime import datetime, timezone
            user.last_login = datetime.now(timezone.utc)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error updating last login for user {user_id}: {e}")
            raise
    
    async def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            # Total users
            total_result = await self.session.execute(
                select(func.count(User.id))
            )
            total_users = total_result.scalar()
            
            # Users by role
            role_result = await self.session.execute(
                select(User.role, func.count(User.id))
                .group_by(User.role)
            )
            role_counts = dict(role_result.fetchall())
            
            # Active vs inactive users
            active_result = await self.session.execute(
                select(User.is_active, func.count(User.id))
                .group_by(User.is_active)
            )
            active_counts = dict(active_result.fetchall())
            
            return {
                'total_users': total_users,
                'by_role': role_counts,
                'by_status': active_counts
            }
        except SQLAlchemyError as e:
            logger.error(f"Error getting user statistics: {e}")
            raise


class StakeholderRepository(BaseRepository[Stakeholder]):
    """Repository for Stakeholder model"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Stakeholder)
    
    async def get_by_organization(self, organization: str) -> List[Stakeholder]:
        """Get stakeholders by organization"""
        try:
            result = await self.session.execute(
                select(Stakeholder)
                .where(Stakeholder.organization == organization)
                .order_by(asc(Stakeholder.name))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting stakeholders by organization {organization}: {e}")
            raise
    
    async def get_by_influence_level(self, influence_level: str) -> List[Stakeholder]:
        """Get stakeholders by influence level"""
        try:
            result = await self.session.execute(
                select(Stakeholder)
                .where(Stakeholder.influence_level == influence_level)
                .order_by(asc(Stakeholder.name))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting stakeholders by influence level {influence_level}: {e}")
            raise
    
    async def get_by_interest_level(self, interest_level: str) -> List[Stakeholder]:
        """Get stakeholders by interest level"""
        try:
            result = await self.session.execute(
                select(Stakeholder)
                .where(Stakeholder.interest_level == interest_level)
                .order_by(asc(Stakeholder.name))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting stakeholders by interest level {interest_level}: {e}")
            raise
    
    async def search_stakeholders(self, search_term: str) -> List[Stakeholder]:
        """Search stakeholders by name, email, or organization"""
        try:
            result = await self.session.execute(
                select(Stakeholder)
                .where(
                    or_(
                        Stakeholder.name.ilike(f"%{search_term}%"),
                        Stakeholder.email.ilike(f"%{search_term}%"),
                        Stakeholder.organization.ilike(f"%{search_term}%")
                    )
                )
                .order_by(asc(Stakeholder.name))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error searching stakeholders with term {search_term}: {e}")
            raise
    
    async def get_stakeholder_statistics(self) -> Dict[str, Any]:
        """Get stakeholder statistics"""
        try:
            # Total stakeholders
            total_result = await self.session.execute(
                select(func.count(Stakeholder.id))
            )
            total_stakeholders = total_result.scalar()
            
            # Stakeholders by influence level
            influence_result = await self.session.execute(
                select(Stakeholder.influence_level, func.count(Stakeholder.id))
                .group_by(Stakeholder.influence_level)
            )
            influence_counts = dict(influence_result.fetchall())
            
            # Stakeholders by interest level
            interest_result = await self.session.execute(
                select(Stakeholder.interest_level, func.count(Stakeholder.id))
                .group_by(Stakeholder.interest_level)
            )
            interest_counts = dict(interest_result.fetchall())
            
            # Stakeholders by organization
            org_result = await self.session.execute(
                select(Stakeholder.organization, func.count(Stakeholder.id))
                .group_by(Stakeholder.organization)
            )
            org_counts = dict(org_result.fetchall())
            
            return {
                'total_stakeholders': total_stakeholders,
                'by_influence_level': influence_counts,
                'by_interest_level': interest_counts,
                'by_organization': org_counts
            }
        except SQLAlchemyError as e:
            logger.error(f"Error getting stakeholder statistics: {e}")
            raise


class ConstraintRepository(BaseRepository[Constraint]):
    """Repository for Constraint model"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Constraint)
    
    async def get_by_type(self, constraint_type: str) -> List[Constraint]:
        """Get constraints by type"""
        try:
            result = await self.session.execute(
                select(Constraint)
                .where(Constraint.constraint_type == constraint_type)
                .order_by(asc(Constraint.name))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting constraints by type {constraint_type}: {e}")
            raise
    
    async def get_by_priority(self, priority: str) -> List[Constraint]:
        """Get constraints by priority"""
        try:
            result = await self.session.execute(
                select(Constraint)
                .where(Constraint.priority == priority)
                .order_by(asc(Constraint.name))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting constraints by priority {priority}: {e}")
            raise


class SuccessCriterionRepository(BaseRepository[SuccessCriterion]):
    """Repository for SuccessCriterion model"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, SuccessCriterion)
    
    async def get_by_measurement_type(self, measurement_type: str) -> List[SuccessCriterion]:
        """Get success criteria by measurement type"""
        try:
            result = await self.session.execute(
                select(SuccessCriterion)
                .where(SuccessCriterion.measurement_type == measurement_type)
                .order_by(asc(SuccessCriterion.name))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting success criteria by measurement type {measurement_type}: {e}")
            raise
