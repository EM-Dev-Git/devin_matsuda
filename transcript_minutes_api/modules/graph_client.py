from typing import List, Optional, Dict, Any
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.models.o_data_errors.o_data_error import ODataError
import os
from dotenv import load_dotenv
from .logger import logger

load_dotenv()

class GraphTranscriptClient:
    def __init__(self):
        self.client_id = os.getenv("MICROSOFT_CLIENT_ID")
        self.client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")
        self.tenant_id = os.getenv("MICROSOFT_TENANT_ID")
        
        if not all([self.client_id, self.client_secret, self.tenant_id]):
            raise ValueError("Microsoft Graph credentials not properly configured")
        
        self.credential = ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        
        self.client = GraphServiceClient(
            credentials=self.credential,
            scopes=['https://graph.microsoft.com/.default']
        )
    
    async def get_user_meetings(self, user_id: str) -> List[Dict[str, Any]]:
        try:
            logger.info(f"Fetching meetings for user: {user_id}")
            
            meetings = await self.client.users.by_user_id(user_id).online_meetings.get()
            
            meeting_list = []
            if meetings and meetings.value:
                for meeting in meetings.value:
                    meeting_data = {
                        "id": meeting.id,
                        "subject": meeting.subject,
                        "start_time": meeting.start_date_time.isoformat() if meeting.start_date_time else None,
                        "end_time": meeting.end_date_time.isoformat() if meeting.end_date_time else None,
                        "join_url": meeting.join_web_url,
                        "organizer": meeting.participants.organizer.identity.user.display_name if meeting.participants and meeting.participants.organizer else None
                    }
                    meeting_list.append(meeting_data)
            
            logger.info(f"Found {len(meeting_list)} meetings for user {user_id}")
            return meeting_list
            
        except ODataError as e:
            logger.error(f"Graph API error getting meetings: {e.error.message if e.error else str(e)}")
            raise Exception(f"Failed to fetch meetings: {e.error.message if e.error else str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting meetings: {str(e)}")
            raise Exception(f"Failed to fetch meetings: {str(e)}")
    
    async def get_meeting_transcripts(self, user_id: str, meeting_id: str) -> List[Dict[str, Any]]:
        try:
            logger.info(f"Fetching transcripts for meeting: {meeting_id}")
            
            transcripts = await self.client.users.by_user_id(user_id).online_meetings.by_online_meeting_id(meeting_id).transcripts.get()
            
            transcript_list = []
            if transcripts and transcripts.value:
                for transcript in transcripts.value:
                    transcript_data = {
                        "id": transcript.id,
                        "meeting_id": transcript.meeting_id,
                        "created_date_time": transcript.created_date_time.isoformat() if transcript.created_date_time else None,
                        "content_url": transcript.transcript_content_url
                    }
                    transcript_list.append(transcript_data)
            
            logger.info(f"Found {len(transcript_list)} transcripts for meeting {meeting_id}")
            return transcript_list
            
        except ODataError as e:
            logger.error(f"Graph API error getting transcripts: {e.error.message if e.error else str(e)}")
            raise Exception(f"Failed to fetch transcripts: {e.error.message if e.error else str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting transcripts: {str(e)}")
            raise Exception(f"Failed to fetch transcripts: {str(e)}")
    
    async def get_transcript_content(self, user_id: str, meeting_id: str, transcript_id: str) -> str:
        try:
            logger.info(f"Fetching transcript content: {transcript_id}")
            
            transcript = await self.client.users.by_user_id(user_id).online_meetings.by_online_meeting_id(meeting_id).transcripts.by_call_transcript_id(transcript_id).get()
            
            if transcript and transcript.transcript_content_url:
                content_response = await self.client.users.by_user_id(user_id).online_meetings.by_online_meeting_id(meeting_id).transcripts.by_call_transcript_id(transcript_id).content.get()
                
                if content_response:
                    content = content_response.decode('utf-8') if isinstance(content_response, bytes) else str(content_response)
                    logger.info(f"Successfully retrieved transcript content for {transcript_id}")
                    return content
            
            raise Exception("Transcript content not available")
            
        except ODataError as e:
            logger.error(f"Graph API error getting transcript content: {e.error.message if e.error else str(e)}")
            raise Exception(f"Failed to fetch transcript content: {e.error.message if e.error else str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting transcript content: {str(e)}")
            raise Exception(f"Failed to fetch transcript content: {str(e)}")

graph_client = GraphTranscriptClient()
