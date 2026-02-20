from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime


class RequestHeader(BaseModel):
    requestId: str
    channelId: str
    clientCode: str
    requestTime: str
    msgType: str


class GMSRequest(BaseModel):
    header: RequestHeader
    body: Dict


class ManualRequestParams(BaseModel):
    msgType: str
    body: Dict


class ConfigUpdateParams(BaseModel):
    client_code: Optional[str] = None
    channel_id: Optional[str] = None
    auto_query: Optional[bool] = None
    interval_ms: Optional[int] = None
    auto_msg_types: Optional[str] = None


# --- Professional API Response Schema ---
class ApiResponse(BaseModel):
    success: bool
    code: int
    status: str
    message: str
    details: Optional[str] = None
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)
