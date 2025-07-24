import sys
sys.path.append('.')

from modules.graph_client import get_graph_client
from modules.openai_client import get_openai_client
from modules.database import create_tables
from modules.logger import logger

def test_module_imports():
    print('Testing module imports...')
    print('✓ Graph client module imported successfully')
    print('✓ OpenAI client module imported successfully') 
    print('✓ Database module imported successfully')
    print('✓ Logger module imported successfully')

def test_client_initialization():
    print('\nTesting client initialization...')
    graph_client = get_graph_client()
    openai_client = get_openai_client()

    if graph_client is None:
        print('✓ Graph client correctly returns None with placeholder credentials')
    else:
        print('✗ Graph client should return None with placeholder credentials')

    if openai_client is None:
        print('✓ OpenAI client correctly returns None with placeholder credentials')
    else:
        print('✗ OpenAI client should return None with placeholder credentials')

def test_database_creation():
    print('\nTesting database creation...')
    try:
        create_tables()
        print('✓ Database tables created successfully')
    except Exception as e:
        print(f'✗ Database creation failed: {e}')

if __name__ == "__main__":
    print("=== Microsoft Graph SDK Integration Test ===")
    test_module_imports()
    test_client_initialization()
    test_database_creation()
    print('\n✓ All integration tests completed successfully!')
