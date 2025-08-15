"""
File: test_database_service.py

Overview:
Test suite for database service layer

Purpose:
Tests database operations and service methods with mocked database

Dependencies:
- pytest: Testing framework
- unittest.mock: Mocking framework

Last Modified: 2025-08-15
Author: Claude
"""

import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from backend.services.database_service import DatabaseService
from backend.models.user import User
from backend.models.dataset import Dataset
from backend.models.job import Job, JobType, JobStatus

@pytest.fixture
def db_service():
    """Database service fixture"""
    return DatabaseService()

@pytest.fixture
def mock_session():
    """Mock database session"""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.close = AsyncMock()
    return session

class TestDatabaseService:
    """Test cases for DatabaseService"""
    
    @pytest.mark.asyncio
    async def test_create_user(self, db_service):
        """Test user creation"""
        with patch('backend.services.database_service.AsyncSessionLocal') as mock_session_factory:
            mock_session = AsyncMock()
            mock_session_factory.return_value.__aenter__.return_value = mock_session
            
            # Mock user creation
            created_user = User(
                username="testuser",
                email="test@example.com",
                full_name="Test User"
            )
            mock_session.refresh = AsyncMock(side_effect=lambda user: setattr(user, 'id', uuid.uuid4()))
            
            result = await db_service.create_user(
                username="testuser",
                email="test@example.com",
                full_name="Test User"
            )
            
            # Verify session operations
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, db_service):
        """Test get user by ID"""
        with patch('backend.services.database_service.AsyncSessionLocal') as mock_session_factory:
            mock_session = AsyncMock()
            mock_session_factory.return_value.__aenter__.return_value = mock_session
            
            # Mock user retrieval
            user_id = str(uuid.uuid4())
            mock_user = User(
                id=user_id,
                username="testuser",
                email="test@example.com"
            )
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_user
            mock_session.execute.return_value = mock_result
            
            result = await db_service.get_user_by_id(user_id)
            
            # Verify session operations
            mock_session.execute.assert_called_once()
            mock_result.scalar_one_or_none.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_by_username(self, db_service):
        """Test get user by username"""
        with patch('backend.services.database_service.AsyncSessionLocal') as mock_session_factory:
            mock_session = AsyncMock()
            mock_session_factory.return_value.__aenter__.return_value = mock_session
            
            # Mock user retrieval
            mock_user = User(
                username="testuser",
                email="test@example.com"
            )
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_user
            mock_session.execute.return_value = mock_result
            
            result = await db_service.get_user_by_username("testuser")
            
            # Verify session operations
            mock_session.execute.assert_called_once()
            mock_result.scalar_one_or_none.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_dataset(self, db_service):
        """Test dataset creation"""
        with patch('backend.services.database_service.AsyncSessionLocal') as mock_session_factory:
            mock_session = AsyncMock()
            mock_session_factory.return_value.__aenter__.return_value = mock_session
            
            # Mock dataset creation
            owner_id = str(uuid.uuid4())
            mock_session.refresh = AsyncMock(side_effect=lambda dataset: setattr(dataset, 'id', uuid.uuid4()))
            
            result = await db_service.create_dataset(
                name="Test Dataset",
                file_path="/path/to/dataset.csv",
                owner_id=owner_id,
                description="Test description"
            )
            
            # Verify session operations
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_dataset_by_id(self, db_service):
        """Test get dataset by ID"""
        with patch('backend.services.database_service.AsyncSessionLocal') as mock_session_factory:
            mock_session = AsyncMock()
            mock_session_factory.return_value.__aenter__.return_value = mock_session
            
            # Mock dataset retrieval
            dataset_id = str(uuid.uuid4())
            mock_dataset = Dataset(
                id=dataset_id,
                name="Test Dataset",
                file_path="/path/to/dataset.csv",
                owner_id=uuid.uuid4()
            )
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_dataset
            mock_session.execute.return_value = mock_result
            
            result = await db_service.get_dataset_by_id(dataset_id)
            
            # Verify session operations
            mock_session.execute.assert_called_once()
            mock_result.scalar_one_or_none.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_job(self, db_service):
        """Test job creation"""
        with patch('backend.services.database_service.AsyncSessionLocal') as mock_session_factory:
            mock_session = AsyncMock()
            mock_session_factory.return_value.__aenter__.return_value = mock_session
            
            # Mock job creation
            user_id = str(uuid.uuid4())
            task_id = "celery-task-123"
            mock_session.refresh = AsyncMock(side_effect=lambda job: setattr(job, 'id', uuid.uuid4()))
            
            result = await db_service.create_job(
                task_id=task_id,
                job_type=JobType.DATASET_ANALYSIS,
                user_id=user_id
            )
            
            # Verify session operations
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_job_status(self, db_service):
        """Test job status update"""
        with patch('backend.services.database_service.AsyncSessionLocal') as mock_session_factory:
            mock_session = AsyncMock()
            mock_session_factory.return_value.__aenter__.return_value = mock_session
            
            # Mock job status update
            task_id = "celery-task-123"
            mock_result = MagicMock()
            mock_result.rowcount = 1
            mock_session.execute.return_value = mock_result
            
            result = await db_service.update_job_status(
                task_id=task_id,
                status=JobStatus.COMPLETED,
                progress=100.0
            )
            
            # Verify session operations
            mock_session.execute.assert_called_once()
            mock_session.commit.assert_called_once()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_get_user_jobs(self, db_service):
        """Test get user jobs"""
        with patch('backend.services.database_service.AsyncSessionLocal') as mock_session_factory:
            mock_session = AsyncMock()
            mock_session_factory.return_value.__aenter__.return_value = mock_session
            
            # Mock jobs retrieval
            user_id = str(uuid.uuid4())
            mock_jobs = [
                Job(
                    task_id="task-1",
                    job_type=JobType.DATASET_ANALYSIS,
                    user_id=user_id
                ),
                Job(
                    task_id="task-2",
                    job_type=JobType.DATA_IMPUTATION,
                    user_id=user_id
                )
            ]
            
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = mock_jobs
            mock_session.execute.return_value = mock_result
            
            result = await db_service.get_user_jobs(user_id)
            
            # Verify session operations
            mock_session.execute.assert_called_once()
            mock_result.scalars.assert_called_once()
            mock_result.scalars.return_value.all.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_dataset_metadata(self, db_service):
        """Test dataset metadata update"""
        with patch('backend.services.database_service.AsyncSessionLocal') as mock_session_factory:
            mock_session = AsyncMock()
            mock_session_factory.return_value.__aenter__.return_value = mock_session
            
            # Mock metadata update
            dataset_id = str(uuid.uuid4())
            metadata = {"analyzed": True, "version": "1.0"}
            mock_result = MagicMock()
            mock_result.rowcount = 1
            mock_session.execute.return_value = mock_result
            
            result = await db_service.update_dataset_metadata(dataset_id, metadata)
            
            # Verify session operations
            mock_session.execute.assert_called_once()
            mock_session.commit.assert_called_once()
            assert result is True