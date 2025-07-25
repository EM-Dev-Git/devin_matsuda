from typing import List, Optional, Dict, Any
from msgraph import GraphServiceClient
from azure.identity import ClientSecretCredential
from ..config import settings
from .logger import get_logger

logger = get_logger(__name__)


class MicrosoftGraphClient:
    def __init__(self):
        self.credential = ClientSecretCredential(
            tenant_id=settings.microsoft_tenant_id,
            client_id=settings.microsoft_client_id,
            client_secret=settings.microsoft_client_secret
        )
        self.client = GraphServiceClient(
            credentials=self.credential,
            scopes=[settings.microsoft_graph_scopes]
        )

    async def get_user_meetings(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            logger.info("Fetching meetings for user", extra={"user_id": user_id, "limit": limit})
            
            meetings = await self.client.users.by_user_id(user_id).online_meetings.get(
                request_configuration={
                    "query_parameters": {
                        "$top": limit,
                        "$orderby": "creationDateTime desc"
                    }
                }
            )
            
            return meetings.value if meetings else []
            
        except Exception as e:
            logger.error("Failed to fetch user meetings", extra={"user_id": user_id, "error": str(e)})
            return []

    async def get_meeting_transcripts(self, meeting_id: str) -> List[Dict[str, Any]]:
        try:
            logger.info("Fetching transcripts for meeting", extra={"meeting_id": meeting_id})
            
            transcripts = await self.client.communications.online_meetings.by_online_meeting_id(meeting_id).transcripts.get()
            
            return transcripts.value if transcripts else []
            
        except Exception as e:
            logger.error("Failed to fetch meeting transcripts", extra={"meeting_id": meeting_id, "error": str(e)})
            return []

    async def get_transcript_content(self, meeting_id: str, transcript_id: str) -> Optional[str]:
        try:
            logger.info("Fetching transcript content", extra={"meeting_id": meeting_id, "transcript_id": transcript_id})
            
            transcript = await self.client.communications.online_meetings.by_online_meeting_id(meeting_id).transcripts.by_call_transcript_id(transcript_id).get()
            
            if transcript and transcript.transcript_content_url:
                content_response = await self.client.get(transcript.transcript_content_url)
                return content_response.text if content_response else None
            
            return None
            
        except Exception as e:
            logger.error("Failed to fetch transcript content", extra={"meeting_id": meeting_id, "transcript_id": transcript_id, "error": str(e)})
            return None

    async def search_transcripts_by_organizer(self, organizer_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            logger.info("Searching transcripts by organizer", extra={"organizer_id": organizer_id, "limit": limit})
            
            meetings = await self.get_user_meetings(organizer_id, limit)
            
            all_transcripts = []
            for meeting in meetings:
                meeting_transcripts = await self.get_meeting_transcripts(meeting.get("id", ""))
                for transcript in meeting_transcripts:
                    transcript["meeting_info"] = meeting
                    all_transcripts.append(transcript)
            
            return all_transcripts
            
        except Exception as e:
            logger.error("Failed to search transcripts by organizer", extra={"organizer_id": organizer_id, "error": str(e)})
            return []


graph_client = MicrosoftGraphClient()
