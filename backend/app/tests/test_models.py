"""
File: tests/test_models.py

Overview:
Tests for SQLAlchemy models and database operations.

Purpose:
Comprehensive tests for User, Dataset, and Job models including
relationships, validation, and database operations.

Dependencies:
- pytest: Testing framework
- app.models: Database models
- app.database: Database connections

Last Modified: 2025-08-15
Author: Claude
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os

from app.database import Base
from app.models import User, Dataset, Job, DatasetStatus, JobStatus, JobType


# Test database setup
@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_session(test_engine):
    """Create test database session."""
    Session = sessionmaker(bind=test_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_user(test_session):
    """Create a sample user for testing."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password_123",
        first_name="Test",
        last_name="User"
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    return user


@pytest.fixture
def sample_dataset(test_session, sample_user):
    """Create a sample dataset for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("col1,col2,col3\n1,2,3\n4,5,6\n")
        temp_path = f.name
    
    dataset = Dataset(
        name="Test Dataset",
        description="A test dataset",
        original_filename="test.csv",
        file_path=temp_path,
        file_size=1024,
        file_type="csv",
        owner_id=sample_user.id,
        row_count=2,
        column_count=3
    )
    test_session.add(dataset)
    test_session.commit()
    test_session.refresh(dataset)
    
    yield dataset
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


class TestUser:
    """Test User model."""
    
    def test_user_creation(self, test_session):
        """Test basic user creation."""
        user = User(
            email="new@example.com",
            username="newuser",
            hashed_password="hashed123"
        )
        test_session.add(user)
        test_session.commit()
        
        assert user.id is not None
        assert user.email == "new@example.com"
        assert user.username == "newuser"
        assert user.is_active is True
        assert user.is_verified is False
        assert user.is_superuser is False
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_user_full_name(self, sample_user):
        """Test user full name property."""
        assert sample_user.full_name == "Test User"
        
        # Test with only first name
        sample_user.last_name = None
        assert sample_user.full_name == "Test"
        
        # Test with only last name
        sample_user.first_name = None
        sample_user.last_name = "User"
        assert sample_user.full_name == "User"
        
        # Test with no names
        sample_user.first_name = None
        sample_user.last_name = None
        assert sample_user.full_name == "testuser"
    
    def test_user_display_name(self, sample_user):
        """Test user display name property."""
        assert sample_user.display_name == "Test User"
    
    def test_user_verify_email(self, sample_user):
        """Test email verification."""
        assert sample_user.is_verified is False
        assert sample_user.email_verified_at is None
        
        sample_user.verify_email()
        
        assert sample_user.is_verified is True
        assert sample_user.email_verified_at is not None
    
    def test_user_update_last_login(self, sample_user):
        """Test last login update."""
        assert sample_user.last_login is None
        
        sample_user.update_last_login()
        
        assert sample_user.last_login is not None
    
    def test_user_to_dict(self, sample_user):
        """Test user to dictionary conversion."""
        user_dict = sample_user.to_dict()
        
        assert "id" in user_dict
        assert "email" in user_dict
        assert "username" in user_dict
        assert "hashed_password" not in user_dict  # Should be excluded by default
        assert "full_name" in user_dict
        assert "display_name" in user_dict
        
        # Test with sensitive data included
        user_dict_sensitive = sample_user.to_dict(include_sensitive=True)
        assert "hashed_password" in user_dict_sensitive


class TestDataset:
    """Test Dataset model."""
    
    def test_dataset_creation(self, test_session, sample_user):
        """Test basic dataset creation."""
        dataset = Dataset(
            name="New Dataset",
            original_filename="new.csv",
            file_path="/path/to/new.csv",
            file_size=2048,
            file_type="csv",
            owner_id=sample_user.id
        )
        test_session.add(dataset)
        test_session.commit()
        
        assert dataset.id is not None
        assert dataset.name == "New Dataset"
        assert dataset.status == DatasetStatus.UPLOADED.value
        assert dataset.is_processed is False
        assert dataset.has_headers is True
        assert dataset.created_at is not None
    
    def test_dataset_column_info(self, sample_dataset):
        """Test column info management."""
        column_data = {
            "col1": {"type": "int", "missing": 0},
            "col2": {"type": "int", "missing": 1}
        }
        
        sample_dataset.set_column_info(column_data)
        assert sample_dataset.get_column_info() == column_data
    
    def test_dataset_analysis_results(self, sample_dataset):
        """Test analysis results management."""
        results = {
            "missing_data": {"total": 5, "percentage": 10.5},
            "recommendations": ["Use mean imputation for col1"]
        }
        
        sample_dataset.set_analysis_results(results)
        assert sample_dataset.get_analysis_results() == results
    
    def test_dataset_processing_config(self, sample_dataset):
        """Test processing config management."""
        config = {
            "columns": [
                {"name": "col1", "strategy": "mean"},
                {"name": "col2", "strategy": "drop"}
            ]
        }
        
        sample_dataset.set_processing_config(config)
        assert sample_dataset.get_processing_config() == config
    
    def test_dataset_update_status(self, sample_dataset):
        """Test status updates."""
        sample_dataset.update_status(DatasetStatus.ANALYZING)
        assert sample_dataset.status == DatasetStatus.ANALYZING.value
        assert sample_dataset.error_message is None
        
        # Test error status
        sample_dataset.update_status(DatasetStatus.ERROR, "Test error")
        assert sample_dataset.status == DatasetStatus.ERROR.value
        assert sample_dataset.error_message == "Test error"
        
        # Test clearing error when status changes
        sample_dataset.update_status(DatasetStatus.COMPLETED)
        assert sample_dataset.status == DatasetStatus.COMPLETED.value
        assert sample_dataset.error_message is None
    
    def test_dataset_mark_as_processed(self, sample_dataset):
        """Test marking as processed."""
        sample_dataset.mark_as_processed()
        assert sample_dataset.is_processed is True
        assert sample_dataset.status == DatasetStatus.COMPLETED.value
    
    def test_dataset_relationship_with_user(self, test_session, sample_dataset, sample_user):
        """Test dataset-user relationship."""
        assert sample_dataset.owner == sample_user
        assert sample_dataset in sample_user.datasets


class TestJob:
    """Test Job model."""
    
    def test_job_creation(self, test_session, sample_user, sample_dataset):
        """Test basic job creation."""
        job = Job(
            name="Test Job",
            description="A test job",
            job_type=JobType.ANALYSIS.value,
            user_id=sample_user.id,
            dataset_id=sample_dataset.id
        )
        test_session.add(job)
        test_session.commit()
        
        assert job.id is not None
        assert job.name == "Test Job"
        assert job.job_type == JobType.ANALYSIS.value
        assert job.status == JobStatus.PENDING.value
        assert job.progress_percentage == 0
        assert job.created_at is not None
    
    def test_job_parameters(self, test_session, sample_user):
        """Test job parameters management."""
        job = Job(
            name="Param Job",
            job_type=JobType.IMPUTATION.value,
            user_id=sample_user.id
        )
        test_session.add(job)
        test_session.commit()
        
        params = {"strategy": "mean", "columns": ["col1", "col2"]}
        job.set_parameters(params)
        assert job.get_parameters() == params
    
    def test_job_results(self, test_session, sample_user):
        """Test job results management."""
        job = Job(
            name="Result Job",
            job_type=JobType.ANALYSIS.value,
            user_id=sample_user.id
        )
        test_session.add(job)
        test_session.commit()
        
        results = {"missing_data": {"total": 10}, "success": True}
        job.set_results(results)
        assert job.get_results() == results
    
    def test_job_output_files(self, test_session, sample_user):
        """Test output files management."""
        job = Job(
            name="File Job",
            job_type=JobType.EXPORT.value,
            user_id=sample_user.id
        )
        test_session.add(job)
        test_session.commit()
        
        files = ["/path/to/output1.csv", "/path/to/output2.json"]
        job.set_output_files(files)
        assert job.get_output_files() == files
    
    def test_job_lifecycle(self, test_session, sample_user):
        """Test complete job lifecycle."""
        job = Job(
            name="Lifecycle Job",
            job_type=JobType.IMPUTATION.value,
            user_id=sample_user.id
        )
        test_session.add(job)
        test_session.commit()
        
        # Start job
        assert job.status == JobStatus.PENDING.value
        assert not job.is_running()
        
        job.start_job("celery_task_123")
        test_session.commit()
        
        assert job.status == JobStatus.RUNNING.value
        assert job.is_running()
        assert job.started_at is not None
        assert job.celery_task_id == "celery_task_123"
        
        # Update progress
        job.update_progress(50)
        assert job.progress_percentage == 50
        
        # Complete job
        results = {"success": True}
        job.complete_job(results)
        test_session.commit()
        
        assert job.status == JobStatus.COMPLETED.value
        assert job.is_completed()
        assert job.is_finished()
        assert job.completed_at is not None
        assert job.progress_percentage == 100
        assert job.actual_duration is not None
        assert job.get_results() == results
    
    def test_job_failure(self, test_session, sample_user):
        """Test job failure handling."""
        job = Job(
            name="Fail Job",
            job_type=JobType.ANALYSIS.value,
            user_id=sample_user.id
        )
        test_session.add(job)
        test_session.commit()
        
        job.start_job()
        job.fail_job("Test error message", {"details": "Error details"})
        test_session.commit()
        
        assert job.status == JobStatus.FAILED.value
        assert job.is_failed()
        assert job.is_finished()
        assert job.error_message == "Test error message"
        assert job.error_details == {"details": "Error details"}
    
    def test_job_cancellation(self, test_session, sample_user):
        """Test job cancellation."""
        job = Job(
            name="Cancel Job",
            job_type=JobType.CORRELATION.value,
            user_id=sample_user.id
        )
        test_session.add(job)
        test_session.commit()
        
        job.start_job()
        job.cancel_job()
        test_session.commit()
        
        assert job.status == JobStatus.CANCELLED.value
        assert job.is_finished()
    
    def test_job_relationships(self, test_session, sample_user, sample_dataset):
        """Test job relationships."""
        job = Job(
            name="Relationship Job",
            job_type=JobType.ANALYSIS.value,
            user_id=sample_user.id,
            dataset_id=sample_dataset.id
        )
        test_session.add(job)
        test_session.commit()
        
        assert job.user == sample_user
        assert job.dataset == sample_dataset
        assert job in sample_user.jobs
        assert job in sample_dataset.jobs