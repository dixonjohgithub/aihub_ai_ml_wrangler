"""
File: test_celery_tasks.py

Overview:
Test suite for Celery background tasks

Purpose:
Tests ML tasks and background processing functionality

Dependencies:
- pytest: Testing framework
- unittest.mock: Mocking framework
- celery: Task testing

Last Modified: 2025-08-15
Author: Claude
"""

import pytest
import uuid
from unittest.mock import MagicMock, patch
from backend.tasks.ml_tasks import analyze_dataset, impute_missing_data, calculate_correlations

class TestMLTasks:
    """Test cases for ML background tasks"""
    
    def test_analyze_dataset_task_success(self):
        """Test successful dataset analysis task"""
        # Create mock task
        mock_task = MagicMock()
        mock_task.request.id = "test-task-123"
        mock_task.update_state = MagicMock()
        
        with patch('backend.tasks.ml_tasks.current_task', mock_task):
            with patch('backend.tasks.ml_tasks.time.sleep'):  # Skip actual sleep
                # Execute task
                dataset_id = str(uuid.uuid4())
                user_id = str(uuid.uuid4())
                
                result = analyze_dataset.apply(
                    args=[dataset_id, user_id], 
                    kwargs={}
                ).get()
                
                # Verify result structure
                assert result['status'] == 'completed'
                assert 'results' in result
                assert 'message' in result
                
                # Verify results content
                results = result['results']
                assert 'total_rows' in results
                assert 'total_columns' in results
                assert 'missing_values_count' in results
                assert 'numeric_columns' in results
                assert 'categorical_columns' in results
                assert 'data_types' in results
                assert 'summary_statistics' in results
    
    def test_analyze_dataset_with_parameters(self):
        """Test dataset analysis with custom parameters"""
        mock_task = MagicMock()
        mock_task.request.id = "test-task-456"
        mock_task.update_state = MagicMock()
        
        with patch('backend.tasks.ml_tasks.current_task', mock_task):
            with patch('backend.tasks.ml_tasks.time.sleep'):
                dataset_id = str(uuid.uuid4())
                user_id = str(uuid.uuid4())
                parameters = {
                    "include_correlations": True,
                    "max_categories": 50
                }
                
                result = analyze_dataset.apply(
                    args=[dataset_id, user_id, parameters], 
                    kwargs={}
                ).get()
                
                assert result['status'] == 'completed'
                assert 'results' in result
    
    def test_impute_missing_data_task_success(self):
        """Test successful data imputation task"""
        mock_task = MagicMock()
        mock_task.request.id = "test-task-789"
        mock_task.update_state = MagicMock()
        
        with patch('backend.tasks.ml_tasks.current_task', mock_task):
            with patch('backend.tasks.ml_tasks.time.sleep'):
                dataset_id = str(uuid.uuid4())
                user_id = str(uuid.uuid4())
                
                result = impute_missing_data.apply(
                    args=[dataset_id, user_id], 
                    kwargs={}
                ).get()
                
                # Verify result structure
                assert result['status'] == 'completed'
                assert 'results' in result
                assert 'message' in result
                
                # Verify results content
                results = result['results']
                assert 'imputation_method' in results
                assert 'columns_imputed' in results
                assert 'values_imputed' in results
                assert 'imputation_summary' in results
    
    def test_impute_missing_data_with_method(self):
        """Test data imputation with specific method"""
        mock_task = MagicMock()
        mock_task.request.id = "test-task-101"
        mock_task.update_state = MagicMock()
        
        with patch('backend.tasks.ml_tasks.current_task', mock_task):
            with patch('backend.tasks.ml_tasks.time.sleep'):
                dataset_id = str(uuid.uuid4())
                user_id = str(uuid.uuid4())
                parameters = {"method": "median"}
                
                result = impute_missing_data.apply(
                    args=[dataset_id, user_id, parameters], 
                    kwargs={}
                ).get()
                
                assert result['status'] == 'completed'
                assert result['results']['imputation_method'] == 'median'
    
    def test_calculate_correlations_task_success(self):
        """Test successful correlation analysis task"""
        mock_task = MagicMock()
        mock_task.request.id = "test-task-202"
        mock_task.update_state = MagicMock()
        
        with patch('backend.tasks.ml_tasks.current_task', mock_task):
            with patch('backend.tasks.ml_tasks.time.sleep'):
                dataset_id = str(uuid.uuid4())
                user_id = str(uuid.uuid4())
                
                result = calculate_correlations.apply(
                    args=[dataset_id, user_id], 
                    kwargs={}
                ).get()
                
                # Verify result structure
                assert result['status'] == 'completed'
                assert 'results' in result
                assert 'message' in result
                
                # Verify results content
                results = result['results']
                assert 'correlation_method' in results
                assert 'correlation_matrix' in results
                assert 'strong_correlations' in results
                assert 'numeric_columns_analyzed' in results
    
    def test_calculate_correlations_with_method(self):
        """Test correlation analysis with specific method"""
        mock_task = MagicMock()
        mock_task.request.id = "test-task-303"
        mock_task.update_state = MagicMock()
        
        with patch('backend.tasks.ml_tasks.current_task', mock_task):
            with patch('backend.tasks.ml_tasks.time.sleep'):
                dataset_id = str(uuid.uuid4())
                user_id = str(uuid.uuid4())
                parameters = {"method": "spearman"}
                
                result = calculate_correlations.apply(
                    args=[dataset_id, user_id, parameters], 
                    kwargs={}
                ).get()
                
                assert result['status'] == 'completed'
                assert result['results']['correlation_method'] == 'spearman'
    
    def test_task_progress_updates(self):
        """Test that tasks update progress correctly"""
        mock_task = MagicMock()
        mock_task.request.id = "test-task-404"
        mock_task.update_state = MagicMock()
        
        with patch('backend.tasks.ml_tasks.current_task', mock_task):
            with patch('backend.tasks.ml_tasks.time.sleep'):
                dataset_id = str(uuid.uuid4())
                user_id = str(uuid.uuid4())
                
                # Execute task
                analyze_dataset.apply(args=[dataset_id, user_id], kwargs={}).get()
                
                # Verify progress updates were called
                assert mock_task.update_state.call_count >= 3  # At least 3 progress updates
                
                # Check that progress updates include expected meta data
                call_args_list = mock_task.update_state.call_args_list
                for call in call_args_list[:-1]:  # Exclude final call
                    args, kwargs = call
                    assert 'state' in kwargs
                    assert kwargs['state'] == 'PROGRESS'
                    assert 'meta' in kwargs
                    assert 'current' in kwargs['meta']
                    assert 'total' in kwargs['meta']
                    assert 'status' in kwargs['meta']
    
    def test_task_error_handling(self):
        """Test task error handling"""
        mock_task = MagicMock()
        mock_task.request.id = "test-task-500"
        mock_task.update_state = MagicMock()
        
        with patch('backend.tasks.ml_tasks.current_task', mock_task):
            with patch('backend.tasks.ml_tasks.time.sleep', side_effect=Exception("Simulated error")):
                dataset_id = str(uuid.uuid4())
                user_id = str(uuid.uuid4())
                
                # Task should raise exception
                with pytest.raises(Exception, match="Simulated error"):
                    analyze_dataset.apply(args=[dataset_id, user_id], kwargs={}).get()
                
                # Verify error state was set
                error_calls = [call for call in mock_task.update_state.call_args_list 
                              if call[1].get('state') == 'FAILURE']
                assert len(error_calls) > 0
    
    def test_task_logging(self):
        """Test that tasks log appropriately"""
        mock_task = MagicMock()
        mock_task.request.id = "test-task-600"
        mock_task.update_state = MagicMock()
        
        with patch('backend.tasks.ml_tasks.current_task', mock_task):
            with patch('backend.tasks.ml_tasks.time.sleep'):
                with patch('backend.tasks.ml_tasks.logger') as mock_logger:
                    dataset_id = str(uuid.uuid4())
                    user_id = str(uuid.uuid4())
                    
                    # Execute task
                    analyze_dataset.apply(args=[dataset_id, user_id], kwargs={}).get()
                    
                    # Verify logging calls
                    assert mock_logger.info.call_count >= 2  # Start and completion logs
                    
                    # Check log messages
                    log_calls = [str(call) for call in mock_logger.info.call_args_list]
                    start_log = any("Starting dataset analysis" in call for call in log_calls)
                    complete_log = any("completed successfully" in call for call in log_calls)
                    
                    assert start_log, "Should log task start"
                    assert complete_log, "Should log task completion"