"""
Base repository class for database operations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import SQLAlchemyError
import logging

from ..models.base import BaseModel

T = TypeVar('T', bound=BaseModel)
logger = logging.getLogger(__name__)


class BaseRepository(Generic[T], ABC):
    """Base repository class for common database operations"""
    
    def __init__(self, session: AsyncSession, model_class: Type[T]):
        self.session = session
        self.model_class = model_class
    
    async def create(self, data: Dict[str, Any]) -> T:
        """Create a new record"""
        try:
            instance = self.model_class(**data)
            self.session.add(instance)
            await self.session.commit()
            await self.session.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error creating {self.model_class.__name__}: {e}")
            raise
    
    async def get_by_id(self, record_id: str) -> Optional[T]:
        """Get a record by ID"""
        try:
            result = await self.session.execute(
                select(self.model_class).where(self.model_class.id == record_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model_class.__name__} by ID {record_id}: {e}")
            raise
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """Get all records with pagination"""
        try:
            result = await self.session.execute(
                select(self.model_class)
                .limit(limit)
                .offset(offset)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting all {self.model_class.__name__}: {e}")
            raise
    
    async def update(self, record_id: str, data: Dict[str, Any]) -> Optional[T]:
        """Update a record"""
        try:
            # Get the record first
            record = await self.get_by_id(record_id)
            if not record:
                return None
            
            # Update fields
            for key, value in data.items():
                if hasattr(record, key):
                    setattr(record, key, value)
            
            await self.session.commit()
            await self.session.refresh(record)
            return record
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error updating {self.model_class.__name__} {record_id}: {e}")
            raise
    
    async def delete(self, record_id: str) -> bool:
        """Delete a record"""
        try:
            result = await self.session.execute(
                delete(self.model_class).where(self.model_class.id == record_id)
            )
            await self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error deleting {self.model_class.__name__} {record_id}: {e}")
            raise
    
    async def count(self) -> int:
        """Count total records"""
        try:
            result = await self.session.execute(
                select(func.count(self.model_class.id))
            )
            return result.scalar()
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model_class.__name__}: {e}")
            raise
    
    async def exists(self, record_id: str) -> bool:
        """Check if record exists"""
        try:
            result = await self.session.execute(
                select(func.count(self.model_class.id))
                .where(self.model_class.id == record_id)
            )
            return result.scalar() > 0
        except SQLAlchemyError as e:
            logger.error(f"Error checking existence of {self.model_class.__name__} {record_id}: {e}")
            raise
    
    async def find_by(self, **filters) -> List[T]:
        """Find records by filters"""
        try:
            query = select(self.model_class)
            for key, value in filters.items():
                if hasattr(self.model_class, key):
                    query = query.where(getattr(self.model_class, key) == value)
            
            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error finding {self.model_class.__name__} by filters {filters}: {e}")
            raise
    
    async def find_one_by(self, **filters) -> Optional[T]:
        """Find one record by filters"""
        try:
            query = select(self.model_class)
            for key, value in filters.items():
                if hasattr(self.model_class, key):
                    query = query.where(getattr(self.model_class, key) == value)
            
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error finding one {self.model_class.__name__} by filters {filters}: {e}")
            raise
    
    async def bulk_create(self, data_list: List[Dict[str, Any]]) -> List[T]:
        """Create multiple records"""
        try:
            instances = [self.model_class(**data) for data in data_list]
            self.session.add_all(instances)
            await self.session.commit()
            
            # Refresh all instances
            for instance in instances:
                await self.session.refresh(instance)
            
            return instances
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error bulk creating {self.model_class.__name__}: {e}")
            raise
    
    async def bulk_update(self, updates: List[Dict[str, Any]]) -> int:
        """Bulk update records"""
        try:
            updated_count = 0
            for update_data in updates:
                record_id = update_data.pop('id')
                if await self.update(record_id, update_data):
                    updated_count += 1
            
            return updated_count
        except SQLAlchemyError as e:
            logger.error(f"Error bulk updating {self.model_class.__name__}: {e}")
            raise
    
    async def search(self, search_term: str, search_fields: List[str]) -> List[T]:
        """Search records by term in specified fields"""
        try:
            query = select(self.model_class)
            conditions = []
            
            for field in search_fields:
                if hasattr(self.model_class, field):
                    field_attr = getattr(self.model_class, field)
                    conditions.append(field_attr.ilike(f"%{search_term}%"))
            
            if conditions:
                from sqlalchemy import or_
                query = query.where(or_(*conditions))
            
            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error searching {self.model_class.__name__}: {e}")
            raise
