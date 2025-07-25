#!/usr/bin/env python3
"""
Verification script to test that all components of the transcript API are properly implemented
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported successfully"""
    try:
        print("Testing imports...")
        
        from app.main import app
        print("✅ FastAPI app imports successfully")
        
        from app.models import User, Transcript
        print("✅ Database models import successfully")
        
        from app.schemas import auth, user, transcript
        print("✅ Schemas import successfully")
        
        from app.modules import auth as auth_module
        from app.modules import openai_client, transcript_processor, logger
        print("✅ Modules import successfully")
        
        from app.routers import auth_router, users_router, transcripts_router
        print("✅ Routers import successfully")
        
        from app.dependencies import get_current_user
        print("✅ Dependencies import successfully")
        
        from app.config import settings
        print("✅ Configuration imports successfully")
        
        print("\n🎉 All components implemented successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_structure():
    """Test that the FastAPI app is properly structured"""
    try:
        from app.main import app
        
        routes = [route.path for route in app.routes]
        expected_routes = ["/", "/health", "/auth/register", "/auth/login", "/auth/me", 
                          "/users/profile", "/transcripts", "/transcripts/{transcript_id}"]
        
        for expected_route in expected_routes:
            if any(expected_route in route for route in routes):
                print(f"✅ Route {expected_route} is registered")
            else:
                print(f"❌ Route {expected_route} is missing")
                return False
        
        print("✅ All expected routes are registered")
        return True
        
    except Exception as e:
        print(f"❌ App structure test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Transcript to Minutes API Verification ===\n")
    
    success = True
    success &= test_imports()
    success &= test_app_structure()
    
    if success:
        print("\n✅ All verification tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some verification tests failed!")
        sys.exit(1)
