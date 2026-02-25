from fastapi import APIRouter, Depends, status
from typing import Dict
from app.models.schemas import ApiResponse, ManualRequestParams, ConfigUpdateParams
from datetime import datetime

router = APIRouter(prefix="/api/v1/socket/gms", tags=["GMS Console"])


# Dependency Injections (will be initialized in main.py)
def get_polling_manager():
    from main import polling_manager

    return polling_manager


def get_gms_client():
    from main import gms_client

    return gms_client


@router.post("/connect", response_model=ApiResponse)
async def start_gms_service(pm=Depends(get_polling_manager)):
    pm.start_service()
    return ApiResponse(
        success=True,
        code=status.HTTP_202_ACCEPTED,
        status="STARTING",
        message="GMS Service initialization requested.",
        details="The backend is now attempting to establish a socket connection with GMS.",
    )


@router.post("/disconnect", response_model=ApiResponse)
async def stop_gms_service(pm=Depends(get_polling_manager)):
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

    if gmsClient.send_request(
        params.msgType,
        pollingManager.client_code,
        pollingManager.channel_id,
        params.body,
    ):
        return ApiResponse(
            success=True,
            code=status.HTTP_202_ACCEPTED,
            status="QUEUED",
            message="Command accepted and queued for transmission.",
            data={"msgType": params.msgType},
        )
    else:
        return ApiResponse(
            success=False,
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            status="SEND_FAILED",
            message="Command failed to send to GMS.",
            details="The socket connection may have been closed or encountered an error.",
        )
