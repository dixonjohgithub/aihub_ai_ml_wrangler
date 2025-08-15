"""
Simple test to verify FastAPI setup is working correctly
"""

import sys
from pathlib import Path

# Add app directory to Python path
app_path = Path(__file__).parent / "app"
sys.path.insert(0, str(app_path))

def test_imports():
    """Test that all modules can be imported correctly"""
    try:
        from main import app
        from core.config import settings
        from core.logging import setup_logging
        from api.router import api_router
        from api.endpoints.health import router
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_app_creation():
    """Test that the FastAPI app can be created"""
    try:
        from main import create_application
        app = create_application()
        print(f"✅ FastAPI app created successfully: {app.title}")
        return True
    except Exception as e:
        print(f"❌ App creation error: {e}")
        return False

def test_health_endpoint():
    """Test that the health endpoint is configured"""
    try:
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        response = client.get("/api/health/")
        print(f"✅ Health endpoint test: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Service: {data.get('service')}")
            print(f"   Status: {data.get('status')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing FastAPI Backend Setup...")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("App Creation Test", test_app_creation),
        ("Health Endpoint Test", test_health_endpoint)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        results.append(test_func())
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Backend setup is ready.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")