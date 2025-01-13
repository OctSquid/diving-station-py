from dataclasses import dataclass

from .constants import HandType, __protocol_version__


@dataclass
class Wirst:
  """手首の回転量"""

  device_id: str
  hand_type: HandType
  w: float
  x: float
  y: float
  z: float


def parse_wrist(args) -> Wirst:
  """手首の回転量をパースする"""
  version = args[0]
  if version != __protocol_version__:
    raise ValueError(f"Unsupported protocol version: {version}")

  return Wirst(
    device_id=args[1],
    hand_type=HandType(args[2]),
    w=args[3],
    x=args[4],
    y=args[5],
    z=args[6],
  )
