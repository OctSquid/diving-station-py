from pythonosc.osc_message import OscMessage
from pythonosc.osc_message_builder import OscMessageBuilder


def build_disconnect_message(receive_port: int) -> OscMessage:
  """DivingStation から切断するメッセージを構築する

  Args:
    receive_port (int): 受信ポート

  Returns:
    OscMessage
  """
  msg = OscMessageBuilder(address="/DS/HC/Disconnect")
  msg.add_arg(receive_port, arg_type=OscMessageBuilder.ARG_TYPE_INT)
  return msg.build()
