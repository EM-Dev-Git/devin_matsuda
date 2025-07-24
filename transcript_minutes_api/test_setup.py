import sys
sys.path.append('.')

from modules.database import create_tables
from modules.logger import logger
from modules.auth import get_password_hash
from modules.database import SessionLocal, User

def test_database_setup():
    print("Testing database setup...")
    try:
        create_tables()
        print("✓ Database tables created successfully")
    except Exception as e:
        print(f"✗ Database setup failed: {e}")
        return False
    return True

def test_user_creation():
    print("Testing user creation...")
    try:
        db = SessionLocal()
        
        existing_user = db.query(User).filter(User.username == "test_user").first()
        if existing_user:
            db.delete(existing_user)
            db.commit()
        
        hashed_password = get_password_hash("test_password")
        test_user = User(
            username="test_user",
            email="test@example.com",
            hashed_password=hashed_password
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f"✓ Test user created with ID: {test_user.id}")
        db.close()
        return True
    except Exception as e:
        print(f"✗ User creation failed: {e}")
        return False

def test_imports():
    print("Testing module imports...")
    try:
        from modules.auth import create_access_token, verify_password
        from modules.openai_client import generate_meeting_minutes
        from modules.logger import logger
        from routers.auth import router as auth_router
        from routers.transcript import router as transcript_router
        print("✓ All modules imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Transcript Minutes API Setup Test ===")
    
    success = True
    success &= test_imports()
    success &= test_database_setup()
    success &= test_user_creation()
    
    if success:
        print("\n✓ All tests passed! API setup is ready.")
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
