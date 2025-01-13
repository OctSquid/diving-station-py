import asyncio
import warnings
from logging import getLogger
from typing import (
  Any,
  Optional,
  cast,
)

from pythonosc import osc_server, udp_client
from pythonosc.dispatcher import Dispatcher

from .event import (
  AsyncEventHandler,
  ConnectEvent,
  ControllerInputReceivedEvent,
  DeviceInfoReceivedEvent,
  DisconnectEvent,
  HandBendReceivedEvent,
  Handlers,
  HandQuatReceivedEvent,
  HapticEvent,
  WristReceivedEvent,
  event_handler,
)
from .protocol import (
  DeviceInfo,
  controller,
  hand_bend,
  hand_quat,
  wrist,
)
from .protocol.connect import build_connect_message
from .protocol.constants import HandType
from .protocol.device_info import parse_device_info
from .protocol.disconnect import build_disconnect_message
from .protocol.haptic import build_haptic_message

# Suppress warnings about coroutines not being awaited
warnings.filterwarnings("ignore", category=RuntimeWarning, message="coroutine.*was never awaited")

logger = getLogger(__name__)


class DivingStationClient:
  """Diving Station Protocol を使用してデータを送受信するためのクラス
  プロトコルの詳細: https://docs.diver-x.jp/dsprotocol/about.html
  """

  def __init__(self, ip: str = "127.0.0.1", receive_port: int = 25788) -> None:
    self.receive_port = receive_port
    self.handlers: Handlers = {}
    self._osc_dispatcher = Dispatcher()
    self._setup_osc_handlers()
    self._client = udp_client.SimpleUDPClient(ip, 25790)
    self._server = osc_server.AsyncIOOSCUDPServer(
      ("127.0.0.1", self.receive_port),
      self._osc_dispatcher,
      cast(asyncio.BaseEventLoop, asyncio.get_event_loop()),
    )
    self._transport: Optional[asyncio.BaseTransport] = None
    self._devices: list[DeviceInfo] = []
    self._connected = False

  def _setup_osc_handlers(self) -> None:
    self._osc_dispatcher.map("/DS/HC/Device", self._handle_osc_device_info)
    self._osc_dispatcher.map("/DS/HC/Hand", self._handle_osc_hand_bend)
    self._osc_dispatcher.map("/DS/HC/HandQuat", self._handle_osc_hand_quat)
    self._osc_dispatcher.map("/DS/HC/Wrist", self._handle_osc_wrist_data)
    self._osc_dispatcher.map("/DS/HC/Controller", self._handle_osc_controller_data)

  def _handle_osc_device_info(self, address: str, *args) -> None:
    devices = parse_device_info(args)
    self._devices = devices
    logger.debug(f"Device info: {devices}")
    asyncio.create_task(self.dispatch(DeviceInfoReceivedEvent(devices)))

  def _handle_osc_hand_bend(self, address: str, *args) -> None:
    hand_bend_data = hand_bend.parse_hand_bend(args)
    logger.debug(f"Hand bend data: {hand_bend_data}")
    asyncio.create_task(self.dispatch(HandBendReceivedEvent(hand_bend_data)))

  def _handle_osc_hand_quat(self, address: str, *args) -> None:
    hand_quat_data = hand_quat.parse_hand_quat(args)
    logger.debug(f"Hand quaternion data: {hand_quat_data}")
    asyncio.create_task(self.dispatch(HandQuatReceivedEvent(hand_quat_data)))

  def _handle_osc_wrist_data(self, address: str, *args) -> None:
    wrist_data = wrist.parse_wrist(args)
    logger.debug(f"Wrist data: {wrist_data}")
    asyncio.create_task(self.dispatch(WristReceivedEvent(wrist_data)))

  def _handle_osc_controller_data(self, address: str, *args) -> None:
    controller_data = controller.parse_controller(args)
    logger.debug(f"Controller data: {controller_data}")
    asyncio.create_task(self.dispatch(ControllerInputReceivedEvent(controller_data)))

  async def dispatch(self, event_data: object) -> Any:
    """イベントを対応するハンドラーにディスパッチします。

    Args:
        event_data (EventType): ディスパッチするイベントデータ

    Returns:
        Any: ハンドラーの実行結果
    """
    handler = self.handlers.get(type(event_data))
    if handler:
      return await handler(event_data)  # 非同期ハンドラをawaitで呼び出す

  def on_connect(
    self,
    handler: AsyncEventHandler[ConnectEvent],
  ) -> AsyncEventHandler[ConnectEvent]:
    """接続イベントのハンドラーを登録します。

    Args:
        handler (AsyncEventHandler[ConnectEvent]): 接続イベントを処理する非同期ハンドラー

    Returns:
        AsyncEventHandler[ConnectEvent]: デコレートされたイベントハンドラー
    """
    decorated_handler = event_handler(ConnectEvent)(handler)
    self.handlers[ConnectEvent] = decorated_handler
    return decorated_handler

  def on_disconnect(
    self,
    handler: AsyncEventHandler[DisconnectEvent],
  ) -> AsyncEventHandler[DisconnectEvent]:
    """切断イベントのハンドラーを登録します。

    Args:
        handler (AsyncEventHandler[DisconnectEvent]): 切断イベントを処理する非同期ハンドラー

    Returns:
        AsyncEventHandler[DisconnectEvent]: デコレートされたイベントハンドラー
    """
    decorated_handler = event_handler(DisconnectEvent)(handler)
    self.handlers[DisconnectEvent] = decorated_handler
    return decorated_handler

  def on_device_info_received(self, handler: AsyncEventHandler[DeviceInfoReceivedEvent]) -> AsyncEventHandler[DeviceInfoReceivedEvent]:
    """デバイス情報受信イベントのハンドラーを登録します。

    Args:
        handler (AsyncEventHandler[DeviceInfoReceivedEvent]): デバイス情報イベントを処理する非同期ハンドラー

    Returns:
        AsyncEventHandler[DeviceInfoReceivedEvent]: デコレートされたイベントハンドラー
    """
    decorated_handler = event_handler(DeviceInfoReceivedEvent)(handler)
    self.handlers[DeviceInfoReceivedEvent] = decorated_handler
    return decorated_handler

  def on_hand_bend_received(self, handler: AsyncEventHandler[HandBendReceivedEvent]) -> AsyncEventHandler[HandBendReceivedEvent]:
    """ハンドの曲げデータ受信イベントのハンドラーを登録します。

    Args:
        handler (AsyncEventHandler[HandBendReceivedEvent]): ハンドの曲げデータイベントを処理する非同期ハンドラー

    Returns:
        AsyncEventHandler[HandBendReceivedEvent]: デコレートされたイベントハンドラー
    """
    decorated_handler = event_handler(HandBendReceivedEvent)(handler)
    self.handlers[HandBendReceivedEvent] = decorated_handler
    return decorated_handler

  def on_wrist_received(self, handler: AsyncEventHandler[WristReceivedEvent]) -> AsyncEventHandler[WristReceivedEvent]:
    """手首の回転データ受信イベントのハンドラーを登録します。

    Args:
        handler (AsyncEventHandler[WristReceivedEvent]): 手首の回転データイベントを処理する非同期ハンドラー

    Returns:
        AsyncEventHandler[WristReceivedEvent]: デコレートされたイベントハンドラー
    """
    decorated_handler = event_handler(WristReceivedEvent)(handler)
    self.handlers[WristReceivedEvent] = decorated_handler
    return decorated_handler

  def on_hand_quat_received(self, handler: AsyncEventHandler[HandQuatReceivedEvent]) -> AsyncEventHandler[HandQuatReceivedEvent]:
    """ハンドのクォータニオンデータ受信イベントのハンドラーを登録します。

    Args:
        handler (AsyncEventHandler[HandQuatReceivedEvent]): ハンドのクォータニオンデータイベントを処理する非同期ハンドラー

    Returns:
        AsyncEventHandler[HandQuatReceivedEvent]: デコレートされたイベントハンドラー
    """
    decorated_handler = event_handler(HandQuatReceivedEvent)(handler)
    self.handlers[HandQuatReceivedEvent] = decorated_handler
    return decorated_handler

  def on_controller_received(
    self, handler: AsyncEventHandler[ControllerInputReceivedEvent]
  ) -> AsyncEventHandler[ControllerInputReceivedEvent]:
    """コントローラー入力データ受信イベントのハンドラーを登録します。

    Args:
        handler (AsyncEventHandler[ControllerInputReceivedEvent]): コントローラー入力データイベントを処理する非同期ハンドラー

    Returns:
        AsyncEventHandler[ControllerInputReceivedEvent]: デコレートされたイベントハンドラー
    """
    decorated_handler = event_handler(ControllerInputReceivedEvent)(handler)
    self.handlers[ControllerInputReceivedEvent] = decorated_handler
    return decorated_handler

  def on_haptic_received(self, handler: AsyncEventHandler[HapticEvent]) -> AsyncEventHandler[HapticEvent]:
    """ハプティックフィードバックイベントのハンドラーを登録します。

    Args:
        handler (AsyncEventHandler[HapticEvent]): ハプティックフィードバックイベントを処理する非同期ハンドラー

    Returns:
        AsyncEventHandler[HapticEvent]: デコレートされたイベントハンドラー
    """
    decorated_handler = event_handler(HapticEvent)(handler)
    self.handlers[HapticEvent] = decorated_handler
    return decorated_handler

  @property
  def connected(self) -> bool:
    """接続状態を取得します。

    Returns:
        bool: Diving Stationに接続されている場合はTrue、それ以外はFalse
    """
    return self._connected

  @property
  def devices(self) -> list[DeviceInfo]:
    """接続されているデバイス情報のリストを取得します。

    Returns:
        list[DeviceInfo]: デバイス情報のリスト
    """
    return self._devices

  async def connect(self):
    """Diving Stationに接続します。

    Raises:
        RuntimeError: 既に接続されている場合に発生
    """
    if self._connected:
      raise RuntimeError("Already connected to Diving Station")

    self._transport, _ = await self._server.create_serve_endpoint()

    # Send connection request
    msg = build_connect_message(self.receive_port)
    self._client.send(msg)

    logger.info(f"Connected to Diving Station on port {self.receive_port}")
    self._connected = True
    await self.dispatch(ConnectEvent())
    await asyncio.sleep(0.01)  # Allow minimal time for event processing

  async def disconnect(self):
    """Diving Stationから切断します。

    Raises:
        RuntimeError: 接続されていない場合に発生
    """
    if not self._connected or not self._transport:
      raise RuntimeError("Not connected to Diving Station")

    msg = build_disconnect_message(self.receive_port)
    self._client.send(msg)

    self._connected = False
    self._transport.close()
    await self.dispatch(DisconnectEvent())

  async def send_haptic(
    self,
    device_id: str,
    hand_type: HandType,
    frequency: float = 200,
    amplitude: float = 1.0,
    duration: float = 1.0,
  ):
    """デバイスの振動要求を送信します。

    Args:
        device_id (str): デバイスID
        hand_type (HandType): 左右の手の種類
        frequency (float, optional): 振動周波数(Hz). デフォルト値は200。
        amplitude (float, optional): 振動の強さ(0-1). デフォルト値は1.0。
        duration (float, optional): 振動時間(秒). デフォルト値は1.0。
    """
    msg = build_haptic_message(device_id, hand_type, frequency, amplitude, duration)
    self._client.send(msg)
    await self.dispatch(HapticEvent(device_id, hand_type, frequency, amplitude, duration))
