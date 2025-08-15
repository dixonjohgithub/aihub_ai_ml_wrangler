"""
Tests for API endpoints
"""

import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestDataPreviewAPI:
    """Test cases for data preview API endpoints"""
    
    @pytest.fixture
    def sample_csv_content(self):
        """Sample CSV content for testing"""
        return """name,age,city,salary
John Doe,30,New York,50000
Jane Smith,25,Los Angeles,55000
Bob Johnson,35,Chicago,60000"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_data_health_check(self):
        """Test data service health check"""
        response = client.get("/api/data/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "cached_files" in data
    
    def test_upload_csv_file(self, sample_csv_content):
        """Test CSV file upload"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_csv_content)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                response = client.post(
                    "/api/data/upload",
                    files={"file": ("test.csv", f, "text/csv")}
                )
            
            assert response.status_code == 200
            data = response.json()
            assert data["upload_status"] == "success"
            assert "file_id" in data
            assert data["filename"] == "test.csv"
            
            return data["file_id"]
        finally:
            os.unlink(temp_path)
    
    def test_upload_invalid_file(self):
        """Test upload of invalid file type"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is not a CSV file")
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                response = client.post(
                    "/api/data/upload",
                    files={"file": ("test.txt", f, "text/plain")}
                )
            
            assert response.status_code == 400
        finally:
            os.unlink(temp_path)
    
    def test_data_preview(self, sample_csv_content):
        """Test data preview endpoint"""
        # First upload a file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_csv_content)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                upload_response = client.post(
                    "/api/data/upload",
                    files={"file": ("test.csv", f, "text/csv")}
                )
            
            file_id = upload_response.json()["file_id"]
            
            # Test preview
            preview_response = client.post(
                "/api/data/preview",
                json={
                    "file_id": file_id,
                    "start_row": 0,
                    "limit": 10
                }
            )
            
            assert preview_response.status_code == 200
            data = preview_response.json()
            assert data["file_id"] == file_id
            assert "preview_data" in data
            assert data["total_rows"] == 3
            assert data["total_columns"] == 4
            assert set(data["columns"]) == {"name", "age", "city", "salary"}
        finally:
            os.unlink(temp_path)
    
    def test_data_validation(self, sample_csv_content):
        """Test data validation endpoint"""
        # First upload a file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_csv_content)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                upload_response = client.post(
                    "/api/data/upload",
                    files={"file": ("test.csv", f, "text/csv")}
                )
            
            file_id = upload_response.json()["file_id"]
            
            # Test validation
            validation_response = client.post(
                "/api/data/validate",
                json={"file_id": file_id}
            )
            
            assert validation_response.status_code == 200
            data = validation_response.json()
            assert "dataset_info" in data
            assert "issues" in data
            assert "summary" in data
        finally:
            os.unlink(temp_path)
    
    def test_type_detection(self, sample_csv_content):
        """Test type detection endpoint"""
        # First upload a file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_csv_content)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                upload_response = client.post(
                    "/api/data/upload",
                    files={"file": ("test.csv", f, "text/csv")}
                )
            
            file_id = upload_response.json()["file_id"]
            
            # Test type detection
            type_response = client.post(
                "/api/data/detect-types",
                json={"file_id": file_id}
            )
            
            assert type_response.status_code == 200
            data = type_response.json()
            assert "detection_results" in data
            assert "type_report" in data
            assert file_id == data["file_id"]
        finally:
            os.unlink(temp_path)
    
    def test_missing_data_analysis(self, sample_csv_content):
        """Test missing data analysis endpoint"""
        # Create data with missing values
        csv_with_missing = """name,age,city,salary
John Doe,30,New York,50000
Jane Smith,,Los Angeles,
Bob Johnson,35,,60000"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_with_missing)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                upload_response = client.post(
                    "/api/data/upload",
                    files={"file": ("test.csv", f, "text/csv")}
                )
            
            file_id = upload_response.json()["file_id"]
            
            # Test missing data analysis
            missing_response = client.post(
                "/api/data/analyze-missing",
                json={"file_id": file_id}
            )
            
            assert missing_response.status_code == 200
            data = missing_response.json()
            assert "missing_analysis" in data
            assert file_id == data["file_id"]
        finally:
            os.unlink(temp_path)
    
    def test_get_file_info(self, sample_csv_content):
        """Test get file info endpoint"""
        # First upload a file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_csv_content)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                upload_response = client.post(
                    "/api/data/upload",
                    files={"file": ("test.csv", f, "text/csv")}
                )
            
            file_id = upload_response.json()["file_id"]
            
            # Test get file info
            info_response = client.get(f"/api/data/file-info/{file_id}")
            
            assert info_response.status_code == 200
            data = info_response.json()
            assert data["filename"] == "test.csv"
            assert "file_size" in data
        finally:
            os.unlink(temp_path)
    
    def test_get_column_info(self, sample_csv_content):
        """Test get column info endpoint"""
        # First upload a file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_csv_content)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                upload_response = client.post(
                    "/api/data/upload",
                    files={"file": ("test.csv", f, "text/csv")}
                )
            
            file_id = upload_response.json()["file_id"]
            
            # Test get column info
            column_response = client.get(f"/api/data/columns/{file_id}")
            
            assert column_response.status_code == 200
            data = column_response.json()
            assert data["file_id"] == file_id
            assert set(data["columns"]) == {"name", "age", "city", "salary"}
        finally:
            os.unlink(temp_path)
    
    def test_delete_file(self, sample_csv_content):
        """Test delete file endpoint"""
        # First upload a file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_csv_content)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                upload_response = client.post(
                    "/api/data/upload",
                    files={"file": ("test.csv", f, "text/csv")}
                )
            
            file_id = upload_response.json()["file_id"]
            
            # Test delete file
            delete_response = client.delete(f"/api/data/file/{file_id}")
            
            assert delete_response.status_code == 200
            data = delete_response.json()
            assert data["status"] == "deleted"
            
            # Verify file is deleted - should return 404
            info_response = client.get(f"/api/data/file-info/{file_id}")
            assert info_response.status_code == 404
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_nonexistent_file_operations(self):
        """Test operations on nonexistent files"""
        fake_file_id = "nonexistent-file-id"
        
        # Test preview
        preview_response = client.post(
            "/api/data/preview",
            json={"file_id": fake_file_id}
        )
        assert preview_response.status_code == 404
        
        # Test validation
        validation_response = client.post(
            "/api/data/validate",
            json={"file_id": fake_file_id}
        )
        assert validation_response.status_code == 404
        
        # Test file info
        info_response = client.get(f"/api/data/file-info/{fake_file_id}")
        assert info_response.status_code == 404