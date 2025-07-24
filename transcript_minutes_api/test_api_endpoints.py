import requests
import json

BASE_URL = "http://localhost:8000"

def test_root_endpoint():
    print("Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_health_endpoint():
    print("\nTesting health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_user_registration():
    print("\nTesting user registration...")
    user_data = {
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "testpassword123"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_user_login():
    print("\nTesting user login...")
    login_data = {
        "username": "testuser2",
        "password": "testpassword123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        token_data = response.json()
        print(f"Response: {token_data}")
        return token_data.get("access_token")
    else:
        print(f"Response: {response.json()}")
        return None

def test_transcript_generation(token):
    print("\nTesting transcript generation...")
    headers = {"Authorization": f"Bearer {token}"}
    transcript_data = {
        "transcript": "会議を開始します。今日は新しいプロジェクトについて話し合います。田中さん、進捗はいかがですか？田中：はい、現在80%完了しています。来週には完成予定です。佐藤：素晴らしいですね。次のフェーズの準備も進めましょう。",
        "meeting_title": "プロジェクト進捗会議",
        "participants": ["田中", "佐藤", "鈴木"]
    }
    response = requests.post(f"{BASE_URL}/transcript/generate", json=transcript_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Generated minutes preview: {result['meeting_minutes'][:200]}...")
        print(f"Status: {result['status']}")
        return True
    else:
        print(f"Response: {response.json()}")
        return False

if __name__ == "__main__":
    print("=== API Endpoint Testing ===")
    
    success = True
    success &= test_root_endpoint()
    success &= test_health_endpoint()
    success &= test_user_registration()
    
    token = test_user_login()
    if token:
        success &= test_transcript_generation(token)
    else:
        success = False
        print("Failed to get authentication token")
    
    if success:
        print("\n✓ All API tests passed! The system is working correctly.")
    else:
        print("\n✗ Some API tests failed. Please check the errors above.")
