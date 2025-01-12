from dataclasses import dataclass
from enum import Enum
from logging import getLogger
from .constants import __protocol_version__

logger = getLogger(__name__)


class DeviceType(Enum):
    """デバイス種別"""

    CONTACT_GLOVE = 0
    CONTACT_SHEET = 1
    CONTACT_GLOVE2 = 2


class DeviceColor(Enum):
    """デバイスカラー"""

    MAGENTA = 0
    RED = 1
    ORANGE = 2
    YELLOW = 3
    GREEN = 4
    CYAN = 5
    BLUE = 6
    GRAY = 7


@dataclass
class DeviceInfo:
    """デバイス情報"""

    id: str
    is_main: bool
    device_type: DeviceType
    name: str
    color: DeviceColor
    ping: float
    is_left_connected: bool
    left_battery: int
    left_ping: float
    is_right_connected: bool
    right_battery: int
    right_ping: float


def parse_device_info(args) -> list[DeviceInfo]:
    """デバイス情報をパースする"""
    version = args[0]
    if version != __protocol_version__:
        raise ValueError(f"Unsupported protocol version: {version}")

    devices: list[DeviceInfo] = []

    for i in range(1, len(args), 12):
        device = DeviceInfo(
            id=args[i],
            is_main=bool(args[i + 1]),
            device_type=DeviceType(args[i + 2]),
            name=args[i + 3],
            color=DeviceColor(args[i + 4]),
            ping=args[i + 5],
            is_left_connected=bool(args[i + 6]),
            left_battery=args[i + 7],
            left_ping=args[i + 8],
            is_right_connected=bool(args[i + 9]),
            right_battery=args[i + 10],
            right_ping=args[i + 11],
        )
        devices.append(device)

    return devices
