from pythonosc.osc_message import OscMessage
from pythonosc.osc_message_builder import OscMessageBuilder

from .constants import HandType, __protocol_version__


def build_haptic_message(
  device_id: str,
  hand_type: HandType,
  frequency: float,
  amplitude: float,
  duration: float,
) -> OscMessage:
  """デバイスを振動させるメッセージを構築する

  Args:
      device_id (int): デバイスID
      hand_type (HandType): 手の種類
      frequency (float): 振動の周波数
      amplitude (float): 振動の振幅(0.0 ~ 1.0)
      duration (float): 振動の持続時間(秒)

  Returns:
      OscMessage
  """
  msg = OscMessageBuilder(address=f"/DS/HC/{device_id}/Haptics/Body")
  msg.add_arg(__protocol_version__, arg_type=OscMessageBuilder.ARG_TYPE_INT)
  msg.add_arg(hand_type.value, arg_type=OscMessageBuilder.ARG_TYPE_INT)
  msg.add_arg(frequency, arg_type=OscMessageBuilder.ARG_TYPE_FLOAT)
  msg.add_arg(amplitude, arg_type=OscMessageBuilder.ARG_TYPE_FLOAT)
  msg.add_arg(duration, arg_type=OscMessageBuilder.ARG_TYPE_FLOAT)
  return msg.build()
