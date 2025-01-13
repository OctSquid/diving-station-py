from dataclasses import dataclass

from .constants import HandType, __protocol_version__


@dataclass
class FingerBend:
  """指の曲げ具合"""

  mcp: float
  pip: float
  dip: float
  tilt: float


@dataclass
class HandBend:
  """手のデータ"""

  device_id: str
  hand_type: HandType
  thumb: FingerBend
  index: FingerBend
  middle: FingerBend
  ring: FingerBend
  little: FingerBend


def parse_hand_bend(args) -> HandBend:
  """手のデータをパースする"""
  version = args[0]
  if version != __protocol_version__:
    raise ValueError(f"Unsupported protocol version: {version}")

  return HandBend(
    device_id=args[1],
    hand_type=HandType(args[2]),
    thumb=FingerBend(args[3], args[4], args[5], args[6]),
    index=FingerBend(args[7], args[8], args[9], args[10]),
    middle=FingerBend(args[11], args[12], args[13], args[14]),
    ring=FingerBend(args[15], args[16], args[17], args[18]),
    little=FingerBend(args[19], args[20], args[21], args[22]),
  )
