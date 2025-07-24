from modules.database import SessionLocal, User, create_tables
from modules.auth import get_password_hash

def setup_test_user():
    create_tables()
    
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.user_id == 'test_user').first()
        if not existing_user:
            hashed_password = get_password_hash('test_password')
            user = User(user_id='test_user', password_hash=hashed_password)
            db.add(user)
            db.commit()
            print('Test user created successfully')
        else:
            print('Test user already exists')
    finally:
        db.close()

if __name__ == "__main__":
    setup_test_user()
