from enum import Enum


class AppStatus(str, Enum):
    IDLE = "IDLE"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    ERROR = "ERROR"


class AppErrorCode(str, Enum):
    NONE = "NONE"
    CONNECTION_LOST = "CONNECTION_LOST"
    SEND_FAILED = "SEND_FAILED"
    SOCKET_ERROR = "SOCKET_ERROR"
    INVALID_JSON = "INVALID_JSON"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    AUTH_FAILED = "AUTH_FAILED"


class GMSMessageType(str, Enum):
    HEARTBEAT = "HeartbeatMsg"
    ROBOT_INFO = "RobotInfoMsg"
    LOCATION_LIST = "LocationListMsg"
    STATION_LIST = "StationListMsg"
    CONTAINER_LIST = "ContainerListMsg"
    AREA_LIST = "AreaListMsg"
    WORKFLOW_LIST = "WorkflowListMsg"
