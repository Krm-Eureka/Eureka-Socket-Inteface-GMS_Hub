from fastapi import APIRouter, Depends, status, Header
from typing import Dict
from app.models.schemas import ApiResponse, ManualRequestParams, ConfigUpdateParams
from datetime import datetime
from app.api.v1.ui_router import _check_password
import httpx
import uuid
from app.core.config import settings

router = APIRouter(prefix="/api/v1/socket/gms", tags=["GMS Console"])


# Dependency Injections (will be initialized in main.py)
def get_polling_manager():
    from main import polling_manager

    return polling_manager


def get_gms_client():
    from main import gms_client

    return gms_client


@router.post("/connect", response_model=ApiResponse)
async def start_gms_service(
    pm=Depends(get_polling_manager), x_admin_password: str | None = Header(default=None)
):
    _check_password(x_admin_password)
    pm.start_service()
    return ApiResponse(
        success=True,
        code=status.HTTP_202_ACCEPTED,
        status="STARTING",
        message="GMS Service initialization requested.",
        details="The backend is now attempting to establish a socket connection with GMS.",
    )


@router.post("/disconnect", response_model=ApiResponse)
async def stop_gms_service(
    pm=Depends(get_polling_manager), x_admin_password: str | None = Header(default=None)
):
    _check_password(x_admin_password)
    pm.stop_service()
    return ApiResponse(
        success=True,
        code=status.HTTP_200_OK,
        status="STOPPING",
        message="GMS Service shutdown requested.",
        details="The backend is closing the socket connection and stopping background workers.",
    )


@router.get("/config", response_model=ApiResponse)
async def get_gms_config(pm=Depends(get_polling_manager)):
    return ApiResponse(
        success=True,
        code=status.HTTP_200_OK,
        status="CONFIG_LOADED",
        message="Current operational settings retrieved.",
        data={"config": pm.get_config()},
    )


@router.patch("/config", response_model=ApiResponse)
async def update_gms_config(params: Dict, pm=Depends(get_polling_manager)):
    pm.update_behavior(params)
    return ApiResponse(
        success=True,
        code=status.HTTP_200_OK,
        status="CONFIG_UPDATED",
        message="Operational settings updated successfully.",
        data=params,
    )


@router.post("/send", response_model=ApiResponse)
async def send_gms_command(
    params: ManualRequestParams,
    pollingManager=Depends(get_polling_manager),
    gmsClient=Depends(get_gms_client),
):
    if not gmsClient.is_connected():
        return ApiResponse(
            success=False,
            code=status.HTTP_503_SERVICE_UNAVAILABLE,
            status="NOT_CONNECTED",
            message="Command failed: GMS is not connected.",
            details="Please start the GMS service before sending manual commands.",
        )

    msg_type = params.body.get("msgType", "UnknownMsg")
    if gmsClient.send_request(
        msg_type,
        pollingManager.client_code,
        pollingManager.channel_id,
        params.body,
    ):
        return ApiResponse(
            success=True,
            code=status.HTTP_202_ACCEPTED,
            status="QUEUED",
            message="Command accepted and queued for transmission.",
            data={"msgType": msg_type},
        )
    else:
        return ApiResponse(
            success=False,
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            status="SEND_FAILED",
            message="Command failed to send to GMS.",
            details="The socket connection may have been closed or encountered an error.",
        )


@router.post("/send_http", response_model=ApiResponse)
async def send_gms_http_command(params: ManualRequestParams):
    url = settings.GMS_HTTP_URL

    msg_type = params.body.get("msgType", "UnknownMsg")
    payload = {
        "header": {
            "clientCode": settings.GMS_CLIENT_CODE,
            "channelId": settings.GMS_CHANNEL_ID,
            "requestId": str(uuid.uuid4()),
            "requestTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "language": "en_us",
        },
        "body": params.body,
    }

    async with httpx.AsyncClient() as client:
        try:
            print(payload)
            response = await client.post(url, json=payload, timeout=10.0)
            result = response.json()

            # Robust GMS Header Detection (DOC_REF Compliance)
            # Try finding the header in various common names: header, reqHeader, rspHeader, resHeader
            gms_header = (
                result.get("header")
                or result.get("reqHeader")
                or result.get("rspHeader")
                or result.get("resHeader")
                or {}
            )

            # Use 'code' from header. Success is usually "0".
            gms_code = str(gms_header.get("code", gms_header.get("logicalCode", "1")))

            if gms_code == "0":
                return ApiResponse(
                    success=True,
                    code=status.HTTP_200_OK,
                    status="SUCCESS",
                    message="HTTP Command executed successfully.",
                    data={"request_payload": payload, "gms_response": result},
                )
            else:
                return ApiResponse(
                    success=False,
                    code=status.HTTP_400_BAD_REQUEST,
                    status="GMS_ERROR",
                    message=gms_header.get(
                        "msg", gms_header.get("message", "GMS returned an error.")
                    ),
                    details=f"Logical Code: {gms_code}",
                    data=result,
                )
        except Exception as e:
            return ApiResponse(
                success=False,
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                status="HTTP_FAILED",
                message=f"Failed to communicate with GMS API: {str(e)}",
            )
