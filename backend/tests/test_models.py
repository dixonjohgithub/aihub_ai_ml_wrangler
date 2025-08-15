"""
File: test_models.py

Overview:
Test suite for database models

Purpose:
Tests the User, Dataset, and Job models for correct functionality

Dependencies:
- pytest: Testing framework
- sqlalchemy: ORM testing

Last Modified: 2025-08-15
Author: Claude
"""

import pytest
import uuid
from datetime import datetime
from backend.models.user import User
from backend.models.dataset import Dataset
from backend.models.job import Job, JobStatus, JobType

class TestUserModel:
    """Test cases for User model"""
    
    def test_user_creation(self):
        """Test user model creation"""
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User"
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.is_admin is False
        assert isinstance(user.id, uuid.UUID)
        assert isinstance(user.created_at, datetime)
    
    def test_user_repr(self):
        """Test user string representation"""
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            username="testuser",
            email="test@example.com"
        )
        
        expected = f"<User(id={user_id}, username=testuser)>"
        assert repr(user) == expected

class TestDatasetModel:
    """Test cases for Dataset model"""
    
    def test_dataset_creation(self):
        """Test dataset model creation"""
        owner_id = uuid.uuid4()
        dataset = Dataset(
            name="Test Dataset",
            description="A test dataset",
            file_path="/path/to/dataset.csv",
            file_size=1024,
            mime_type="text/csv",
            rows_count=100,
            columns_count=5,
            owner_id=owner_id
        )
        
        assert dataset.name == "Test Dataset"
        assert dataset.description == "A test dataset"
        assert dataset.file_path == "/path/to/dataset.csv"
        assert dataset.file_size == 1024
        assert dataset.mime_type == "text/csv"
        assert dataset.rows_count == 100
        assert dataset.columns_count == 5
        assert dataset.owner_id == owner_id
        assert isinstance(dataset.id, uuid.UUID)
        assert isinstance(dataset.created_at, datetime)
    
    def test_dataset_with_metadata(self):
        """Test dataset with JSON metadata"""
        owner_id = uuid.uuid4()
        metadata = {
            "source": "manual_upload",
            "format": "csv",
            "encoding": "utf-8"
        }
        
        dataset = Dataset(
            name="Test Dataset",
            file_path="/path/to/dataset.csv",
            owner_id=owner_id,
            metadata=metadata
        )
        
        assert dataset.metadata == metadata
    
    def test_dataset_repr(self):
        """Test dataset string representation"""
        dataset_id = uuid.uuid4()
        dataset = Dataset(
            id=dataset_id,
            name="Test Dataset",
            file_path="/path/to/dataset.csv",
            owner_id=uuid.uuid4()
        )
        
        expected = f"<Dataset(id={dataset_id}, name=Test Dataset)>"
        assert repr(dataset) == expected

class TestJobModel:
    """Test cases for Job model"""
    
    def test_job_creation(self):
        """Test job model creation"""
        user_id = uuid.uuid4()
        dataset_id = uuid.uuid4()
        
        job = Job(
            task_id="celery-task-123",
            job_type=JobType.DATASET_ANALYSIS,
            status=JobStatus.PENDING,
            progress=0.0,
            user_id=user_id,
            dataset_id=dataset_id
        )
        
        assert job.task_id == "celery-task-123"
        assert job.job_type == JobType.DATASET_ANALYSIS
        assert job.status == JobStatus.PENDING
        assert job.progress == 0.0
        assert job.user_id == user_id
        assert job.dataset_id == dataset_id
        assert isinstance(job.id, uuid.UUID)
        assert isinstance(job.created_at, datetime)
    
    def test_job_with_parameters_and_results(self):
        """Test job with JSON parameters and results"""
        user_id = uuid.uuid4()
        parameters = {
            "method": "statistical_analysis",
            "include_correlations": True
        }
        results = {
            "total_rows": 1000,
            "missing_values": 50,
            "analysis_complete": True
        }
        
        job = Job(
            task_id="celery-task-456",
            job_type=JobType.DATA_IMPUTATION,
            user_id=user_id,
            parameters=parameters,
            results=results
        )
        
        assert job.parameters == parameters
        assert job.results == results
    
    def test_job_status_enum_values(self):
        """Test job status enum values"""
        assert JobStatus.PENDING.value == "pending"
        assert JobStatus.RUNNING.value == "running"
        assert JobStatus.COMPLETED.value == "completed"
        assert JobStatus.FAILED.value == "failed"
        assert JobStatus.CANCELLED.value == "cancelled"
    
    def test_job_type_enum_values(self):
        """Test job type enum values"""
        assert JobType.DATASET_ANALYSIS.value == "dataset_analysis"
        assert JobType.DATA_IMPUTATION.value == "data_imputation"
        assert JobType.CORRELATION_ANALYSIS.value == "correlation_analysis"
        assert JobType.MODEL_TRAINING.value == "model_training"
    
    def test_job_repr(self):
        """Test job string representation"""
        job_id = uuid.uuid4()
        job = Job(
            id=job_id,
            task_id="celery-task-789",
            job_type=JobType.CORRELATION_ANALYSIS,
            status=JobStatus.RUNNING,
            user_id=uuid.uuid4()
        )
        
        expected = f"<Job(id={job_id}, type=JobType.CORRELATION_ANALYSIS, status=JobStatus.RUNNING)>"
        assert repr(job) == expected