from pythonosc.osc_message_builder import OscMessageBuilder
from pythonosc.osc_message import OscMessage


def build_disconnect_message(receive_port: int) -> OscMessage:
    msg = OscMessageBuilder(address="/DS/HC/Disconnect")
    msg.add_arg(receive_port, arg_type=OscMessageBuilder.ARG_TYPE_INT)
    return msg.build()
