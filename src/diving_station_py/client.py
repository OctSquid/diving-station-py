import asyncio
from enum import Enum
from dataclasses import dataclass
from typing import Optional
from pythonosc import udp_client, osc_server
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_message_builder import OscMessageBuilder
from logging import getLogger

from diving_station_py.protocol import (
    DeviceInfo,
    controller,
    hand_bend,
    hand_quat,
    wrist,
)
from diving_station_py.protocol.connect import build_connect_message
from diving_station_py.protocol.device_info import parse_device_info
from diving_station_py.protocol.disconnect import build_disconnect_message
from diving_station_py.protocol.haptic import build_haptic_message

logger = getLogger(__name__)


class DivingStationClient:
    """
    Diving Station Protocol を使用してデータを送受信するためのクラス
    プロトコルの詳細: diving_station_protocol.md
    """

    def __init__(self, ip: str = "127.0.0.1", receive_port: int = 25788) -> None:
        self.receive_port = receive_port
        self._dispatcher = Dispatcher()
        self._setup_handlers()
        self._client = udp_client.SimpleUDPClient(ip, 25790)
        self._server = osc_server.AsyncIOOSCUDPServer(
            ("127.0.0.1", self.receive_port), self._dispatcher, asyncio.get_event_loop()
        )
        self._transport: Optional[asyncio.DatagramTransport] = None
        self._devices: list[DeviceInfo] = []
        self._connected = False
        self._server_task: Optional[asyncio.Task] = None

    def _setup_handlers(self) -> None:
        self._dispatcher.map("/DS/HC/Device", self._handle_device_info)
        self._dispatcher.map("/DS/HC/Hand", self._handle_hand_bend)
        self._dispatcher.map("/DS/HC/HandQuat", self._handle_hand_quat)
        self._dispatcher.map("/DS/HC/Wrist", self._handle_wrist_data)
        self._dispatcher.map("/DS/HC/Controller", self._handle_controller_data)

    def _handle_device_info(self, address: str, *args) -> None:
        """Handle device info messages"""
        devices = parse_device_info(args)
        self._devices = devices

        logger.debug(f"Device info: {devices}")

    def _handle_hand_bend(self, address: str, *args) -> None:
        """Handle hand data messages"""
        hand_bend_data = hand_bend.parse_hand_bend(args)

        logger.debug(f"Hand bend data: {hand_bend_data}")

    def _handle_hand_quat(self, address: str, *args) -> None:
        """Handle hand quaternion messages"""
        hand_quat_data = hand_quat.parse_hand_quat(args)

        logger.debug(f"Hand quaternion data: {hand_quat_data}")

    def _handle_wrist_data(self, address: str, *args) -> None:
        """Handle wrist rotation messages"""
        wrist_data = wrist.parse_wrist(args)

        logger.debug(f"Wrist data: {wrist_data}")

    def _handle_controller_data(self, address: str, *args) -> None:
        """Handle controller input messages"""
        controller_data = controller.parse_controller(args)

        logger.debug(f"Controller data: {controller_data}")

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def devices(self) -> list[DeviceInfo]:
        return self._devices

    def serve(self):
        self._server.serve()

    async def connect(self):
        if self._connected:
            raise RuntimeError("Already connected to Diving Station")

        # 別スレッドで OSC サーバーを起動
        # self._server_task = asyncio.create_task(
        #     asyncio.get_event_loop().run_in_executor(None, self.serve)
        # )
        self._transport, _ = await self._server.create_serve_endpoint()

        # Send connection request
        msg = build_connect_message(self.receive_port)
        self._client.send(msg)

        logger.info(f"Connected to Diving Station on port {self.receive_port}")

        self._connected = True

    async def disconnect(self):
        if not self._connected:
            raise RuntimeError("Not connected to Diving Station")

        msg = build_disconnect_message(self.receive_port)
        self._client.send(msg)

        self._connected = False
        self._transport.close()

    async def send_haptic(
        self,
        device_id: int,
        hand_type: hand_bend.HandType,
        frequency: float = 200,
        amplitude: float = 1.0,
        duration: float = 1.0,
    ):
        msg = build_haptic_message(device_id, hand_type, frequency, amplitude, duration)
        self._client.send(msg)
