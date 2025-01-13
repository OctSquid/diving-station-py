from dataclasses import dataclass

from .constants import ButtonState, HandType, __protocol_version__


@dataclass
class Joystick:
  """ジョイスティックの入力"""

  x: float
  y: float


@dataclass
class Trackpad:
  """トラックパッドの入力"""

  x: float
  y: float


@dataclass
class ControllerAnalog:
  """コントローラのアナログ入力"""

  trigger: float
  grip_value: float
  grip_force: float
  joystick: Joystick
  trackpad: Trackpad


@dataclass
class ControllerButtons:
  """コントローラのボタン入力"""

  a: ButtonState
  b: ButtonState
  sys: ButtonState
  trigger: ButtonState
  joystick: ButtonState
  trackpad: ButtonState


@dataclass
class ControllerInput:
  """コントローラの入力"""

  device_id: str
  hand_type: HandType
  buttons: ControllerButtons
  analog: ControllerAnalog


def parse_controller(args) -> ControllerInput:
  """コントローラの入力をパースする"""
  version = args[0]
  if version != __protocol_version__:
    raise ValueError(f"Unsupported protocol version: {version}")

  return ControllerInput(
    device_id=args[1],
    hand_type=HandType(args[2]),
    buttons=ControllerButtons(
      a=ButtonState(args[3]),
      b=ButtonState(args[4]),
      sys=ButtonState(args[5]),
      trigger=ButtonState(args[6]),
      joystick=ButtonState(args[7]),
      trackpad=ButtonState(args[8]),
    ),
    analog=ControllerAnalog(
      trigger=args[9],
      grip_value=args[10],
      grip_force=args[11],
      joystick=Joystick(x=args[12], y=args[13]),
      trackpad=Trackpad(x=args[14], y=args[15]),
    ),
  )
