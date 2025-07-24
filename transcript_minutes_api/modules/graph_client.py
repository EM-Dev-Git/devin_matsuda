import os
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from msgraph import GraphServiceClient
from azure.identity import ClientSecretCredential
from modules.logger import logger

load_dotenv()

GRAPH_CLIENT_ID = os.getenv("GRAPH_CLIENT_ID")
GRAPH_CLIENT_SECRET = os.getenv("GRAPH_CLIENT_SECRET")
GRAPH_TENANT_ID = os.getenv("GRAPH_TENANT_ID")

def get_graph_client():
    if not all([GRAPH_CLIENT_ID, GRAPH_CLIENT_SECRET, GRAPH_TENANT_ID]):
        return None
    
    if any(val in ["your-graph-client-id-here", "your-graph-client-secret-here", "your-tenant-id-here"] 
           for val in [GRAPH_CLIENT_ID, GRAPH_CLIENT_SECRET, GRAPH_TENANT_ID]):
        return None
    
    try:
        credential = ClientSecretCredential(
            tenant_id=GRAPH_TENANT_ID,
            client_id=GRAPH_CLIENT_ID,
            client_secret=GRAPH_CLIENT_SECRET
        )
        
        scopes = ['https://graph.microsoft.com/.default']
        client = GraphServiceClient(credentials=credential, scopes=scopes)
        return client
    except Exception as e:
        logger.error(f"Failed to create Graph client: {str(e)}")
        return None

async def list_meeting_transcripts(meeting_id: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    try:
        client = get_graph_client()
        if not client:
            logger.error("Microsoft Graph client not configured or credentials are placeholders")
            raise Exception("Microsoft Graph client not configured properly")
        
        if user_id:
            transcripts = await client.users.by_user_id(user_id).online_meetings.by_online_meeting_id(meeting_id).transcripts.get()
        else:
            transcripts = await client.me.online_meetings.by_online_meeting_id(meeting_id).transcripts.get()
        
        transcript_list = []
        if transcripts and transcripts.value:
            for transcript in transcripts.value:
                transcript_info = {
                    "id": transcript.id,
                    "created_date_time": transcript.created_date_time.isoformat() if transcript.created_date_time else None,
                    "meeting_id": transcript.meeting_id,
                    "transcript_content_url": transcript.transcript_content_url
                }
                transcript_list.append(transcript_info)
        
        logger.info(f"Retrieved {len(transcript_list)} transcripts for meeting {meeting_id}")
        return transcript_list
        
    except Exception as e:
        logger.error(f"Error listing meeting transcripts for meeting {meeting_id}: {str(e)}")
        raise Exception(f"会議のトランスクリプト一覧取得中にエラーが発生しました: {str(e)}")

async def get_transcript_content(meeting_id: str, transcript_id: str, user_id: Optional[str] = None) -> str:
    try:
        client = get_graph_client()
        if not client:
            logger.error("Microsoft Graph client not configured or credentials are placeholders")
            raise Exception("Microsoft Graph client not configured properly")
        
        if user_id:
            transcript = await client.users.by_user_id(user_id).online_meetings.by_online_meeting_id(meeting_id).transcripts.by_call_transcript_id(transcript_id).get()
        else:
            transcript = await client.me.online_meetings.by_online_meeting_id(meeting_id).transcripts.by_call_transcript_id(transcript_id).get()
        
        if not transcript:
            raise Exception(f"Transcript {transcript_id} not found for meeting {meeting_id}")
        
        content_url = transcript.transcript_content_url
        if not content_url:
            raise Exception("Transcript content URL not available")
        
        import httpx
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(content_url)
            response.raise_for_status()
            content = response.text
        
        logger.info(f"Retrieved transcript content for meeting {meeting_id}, transcript {transcript_id}. Length: {len(content)} characters")
        return content
        
    except Exception as e:
        logger.error(f"Error getting transcript content for meeting {meeting_id}, transcript {transcript_id}: {str(e)}")
        raise Exception(f"トランスクリプト内容取得中にエラーが発生しました: {str(e)}")

async def get_meeting_transcript_for_minutes(meeting_id: str, user_id: Optional[str] = None) -> str:
    try:
        transcripts = await list_meeting_transcripts(meeting_id, user_id)
        
        if not transcripts:
            raise Exception(f"No transcripts found for meeting {meeting_id}")
        
        latest_transcript = max(transcripts, key=lambda x: x.get('created_date_time', ''))
        transcript_content = await get_transcript_content(meeting_id, latest_transcript['id'], user_id)
        
        logger.info(f"Retrieved latest transcript for meeting minutes generation: meeting {meeting_id}")
        return transcript_content
        
    except Exception as e:
        logger.error(f"Error getting meeting transcript for minutes: {str(e)}")
        raise Exception(f"議事録生成用トランスクリプト取得中にエラーが発生しました: {str(e)}")
