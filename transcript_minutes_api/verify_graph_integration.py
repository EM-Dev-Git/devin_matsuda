#!/usr/bin/env python3
"""
Verification script to test Microsoft Graph SDK integration
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_graph_imports():
    """Test that Microsoft Graph components can be imported successfully"""
    try:
        print("Testing Microsoft Graph imports...")
        
        from app.modules.graph_client import MicrosoftGraphClient, graph_client
        print("✅ Microsoft Graph client imports successfully")
        
        from app.schemas.transcript import TranscriptFromGraph
        print("✅ Graph transcript schema imports successfully")
        
        from app.modules.transcript_processor import process_graph_transcript, get_available_graph_transcripts
        print("✅ Graph transcript processor functions import successfully")
        
        from app.config import settings
        print("✅ Configuration with Graph settings imports successfully")
        
        print("\n🎉 All Microsoft Graph components imported successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Graph import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_with_graph():
    """Test that the FastAPI app starts with Graph integration"""
    try:
        from app.main import app
        
        routes = [route.path for route in app.routes]
        graph_routes = ["/transcripts/from-graph", "/transcripts/graph/available"]
        
        for graph_route in graph_routes:
            if any(graph_route in route for route in routes):
                print(f"✅ Graph route {graph_route} is registered")
            else:
                print(f"❌ Graph route {graph_route} is missing")
                return False
        
        print("✅ All Graph routes are registered")
        return True
        
    except Exception as e:
        print(f"❌ App with Graph integration test failed: {e}")
        return False

def test_database_model():
    """Test that the database model includes Graph fields"""
    try:
        from app.models.transcript import Transcript
        
        graph_fields = ['source_type', 'graph_meeting_id', 'graph_transcript_id', 'graph_organizer_id']
        
        for field in graph_fields:
            if hasattr(Transcript, field):
                print(f"✅ Graph field {field} exists in Transcript model")
            else:
                print(f"❌ Graph field {field} is missing from Transcript model")
                return False
        
        print("✅ All Graph fields are present in database model")
        return True
        
    except Exception as e:
        print(f"❌ Database model test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Microsoft Graph SDK Integration Verification ===\n")
    
    success = True
    success &= test_graph_imports()
    success &= test_app_with_graph()
    success &= test_database_model()
    
    if success:
        print("\n✅ All Microsoft Graph integration tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some Microsoft Graph integration tests failed!")
        sys.exit(1)
