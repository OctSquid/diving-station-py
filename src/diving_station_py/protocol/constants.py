from enum import Enum

__protocol_version__ = 1
"""サポートしているプロトコルバージョン"""


class DeviceType(Enum):
  """デバイス種別"""

  CONTACT_GLOVE = 0
  CONTACT_SHEET = 1
  CONTACT_GLOVE2 = 2


class HandType(Enum):
  """手の種別"""

  RIGHT = 0
  LEFT = 1


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


class ButtonState(Enum):
  """ボタンの状態"""

  RELEASED = 0
  TOUCHED = 1
  PRESSED = 2
