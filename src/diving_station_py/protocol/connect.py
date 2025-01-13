from pythonosc.osc_message import OscMessage
from pythonosc.osc_message_builder import OscMessageBuilder


def build_connect_message(receive_port: int) -> OscMessage:
  """DivingStation に接続するメッセージを構築する

  Args:
      receive_port (int): 受信ポート

  Returns:
      OscMessage
  """
  msg = OscMessageBuilder(address="/DS/HC/Connect")
  msg.add_arg(receive_port, arg_type=OscMessageBuilder.ARG_TYPE_INT)
  return msg.build()
