"""
File: database_service.py

Overview:
Database service layer for managing database operations

Purpose:
Provides high-level database operations and transaction management

Dependencies:
- sqlalchemy: ORM framework
- backend.config.database: Database configuration

Last Modified: 2025-08-15
Author: Claude
"""

from typing import Optional, List, Type, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from backend.config.database import AsyncSessionLocal
from backend.models.user import User
from backend.models.dataset import Dataset
from backend.models.job import Job

T = TypeVar('T')

class DatabaseService:
    """Database service for managing database operations"""

    async def create_user(self, username: str, email: str, full_name: Optional[str] = None) -> User:
        """Create a new user"""
        async with AsyncSessionLocal() as session:
            user = User(username=username, email=email, full_name=full_name)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.username == username)
            )
            return result.scalar_one_or_none()

    async def get_user_datasets(self, user_id: str) -> List[Dataset]:
        """Get all datasets for a user"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Dataset).where(Dataset.owner_id == user_id).options(selectinload(Dataset.owner))
            )
            return result.scalars().all()

    async def create_dataset(self, name: str, file_path: str, owner_id: str, **kwargs) -> Dataset:
        """Create a new dataset"""
        async with AsyncSessionLocal() as session:
            dataset = Dataset(
                name=name,
                file_path=file_path,
                owner_id=owner_id,
                **kwargs
            )
            session.add(dataset)
            await session.commit()
            await session.refresh(dataset)
            return dataset

    async def get_dataset_by_id(self, dataset_id: str) -> Optional[Dataset]:
        """Get dataset by ID"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Dataset)
                .where(Dataset.id == dataset_id)
                .options(selectinload(Dataset.owner))
            )
            return result.scalar_one_or_none()

    async def update_dataset_metadata(self, dataset_id: str, metadata: dict) -> bool:
        """Update dataset metadata"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                update(Dataset)
                .where(Dataset.id == dataset_id)
                .values(metadata=metadata)
            )
            await session.commit()
            return result.rowcount > 0

    async def create_job(self, task_id: str, job_type, user_id: str, **kwargs) -> Job:
        """Create a new job"""
        async with AsyncSessionLocal() as session:
            job = Job(
                task_id=task_id,
                job_type=job_type,
                user_id=user_id,
                **kwargs
            )
            session.add(job)
            await session.commit()
            await session.refresh(job)
            return job

    async def get_job_by_task_id(self, task_id: str) -> Optional[Job]:
        """Get job by task ID"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Job)
                .where(Job.task_id == task_id)
                .options(selectinload(Job.user), selectinload(Job.dataset))
            )
            return result.scalar_one_or_none()

    async def update_job_status(self, task_id: str, status, progress: Optional[float] = None, **kwargs) -> bool:
        """Update job status and progress"""
        async with AsyncSessionLocal() as session:
            update_values = {"status": status}
            if progress is not None:
                update_values["progress"] = progress
            update_values.update(kwargs)
            
            result = await session.execute(
                update(Job)
                .where(Job.task_id == task_id)
                .values(**update_values)
            )
            await session.commit()
            return result.rowcount > 0

    async def get_user_jobs(self, user_id: str, limit: int = 50) -> List[Job]:
        """Get user jobs"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Job)
                .where(Job.user_id == user_id)
                .options(selectinload(Job.dataset))
                .order_by(Job.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()