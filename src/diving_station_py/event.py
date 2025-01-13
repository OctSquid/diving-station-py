from typing import Any, Awaitable, Callable, Dict, Type, TypeVar

from diving_station_py.protocol.constants import HandType
from diving_station_py.protocol.controller import ControllerInput
from diving_station_py.protocol.device_info import DeviceInfo
from diving_station_py.protocol.hand_bend import HandBend
from diving_station_py.protocol.hand_quat import HandQuaternion
from diving_station_py.protocol.wrist import Wirst

EventType = TypeVar("EventType")

AsyncEventHandler = Callable[[EventType], Awaitable[Any]]


Handlers = Dict[Type[EventType], AsyncEventHandler[EventType]]


def event_handler(
  event_type: Type[EventType],
) -> Callable[
  [AsyncEventHandler],
  AsyncEventHandler,
]:
  """イベントハンドラ"""

  def decorator(
    handler: AsyncEventHandler,
  ) -> AsyncEventHandler:
    def wrapper(event_data: Any) -> Any:
      if not isinstance(event_data, event_type):
        raise TypeError(f"Invalid event data type: expected {event_type}, got {type(event_data)}")
      return handler(event_data)

    return wrapper

  return decorator


class ConnectEvent:
  """Diving Station に接続したときに発生するイベント"""

  pass


class DisconnectEvent:
  """Diving Station から切断したときに発生するイベント"""

  pass


class HapticEvent:
  """デバイスが振動した時に発生するイベント"""

  def __init__(
    self,
    device_id: str,
    hand_type: HandType,
    frequency: float,
    amplitude: float,
    duration: float,
  ) -> None:
    self.device_id = device_id
    self.hand_type = hand_type
    self.frequency = frequency
    self.amplitude = amplitude
    self.duration = duration


class DeviceInfoReceivedEvent:
  """デバイス情報を受信したときに発生するイベント"""

  def __init__(self, devices: list[DeviceInfo]) -> None:
    self.devices = devices


class HandBendReceivedEvent:
  """手の曲げ情報を受信したときに発生するイベント"""

  def __init__(self, hand_bend: HandBend) -> None:
    self.hand_bend = hand_bend
    self.device_id = hand_bend.device_id
    self.hand_type = hand_bend.hand_type


class HandQuatReceivedEvent:
  """手のクォータニオン情報を受信したときに発生するイベント"""

  def __init__(self, quaternion: HandQuaternion) -> None:
    self.quaternion = quaternion
    self.device_id = quaternion.device_id
    self.hand_type = quaternion.hand_type


class WristReceivedEvent:
  """手首のクォータニオンを受信したときに発生するイベント"""

  def __init__(self, wrist: Wirst) -> None:
    self.wrist = wrist


class ControllerInputReceivedEvent:
  """コントローラの入力情報を受信したときに発生するイベント"""

  def __init__(self, controller_input: ControllerInput) -> None:
    self.controller_input = controller_input
