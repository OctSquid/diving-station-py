from dataclasses import dataclass

from .constants import HandType, __protocol_version__


@dataclass
class Quaternion:
  """回転量(クォータニオン)"""

  w: float
  x: float
  y: float
  z: float


@dataclass
class ThumbQuaternion:
  """各親指関節の回転量"""

  cmc: Quaternion
  mcp: Quaternion
  ip: Quaternion


@dataclass
class FingerQuaternion:
  """各指関節の回転量"""

  mcp: Quaternion
  pip: Quaternion
  dip: Quaternion


@dataclass
class HandQuaternion:
  """手の回転量"""

  device_id: str
  hand_type: HandType
  thumb: ThumbQuaternion
  index: FingerQuaternion
  middle: FingerQuaternion
  ring: FingerQuaternion
  little: FingerQuaternion


def parse_hand_quat(args) -> HandQuaternion:
  """手の各関節の回転量をパースする"""
  if args[0] != __protocol_version__:
    raise ValueError(f"Unsupported protocol version: {args[0]}")

  device_id = args[1]
  hand_type = HandType(args[2])

  thumb = ThumbQuaternion(
    cmc=Quaternion(w=args[3], x=args[4], y=args[5], z=args[6]),
    mcp=Quaternion(w=args[7], x=args[8], y=args[9], z=args[10]),
    ip=Quaternion(w=args[11], x=args[12], y=args[13], z=args[14]),
  )

  index = FingerQuaternion(
    mcp=Quaternion(w=args[15], x=args[16], y=args[17], z=args[18]),
    pip=Quaternion(w=args[19], x=args[20], y=args[21], z=args[22]),
    dip=Quaternion(w=args[23], x=args[24], y=args[25], z=args[26]),
  )

  middle = FingerQuaternion(
    mcp=Quaternion(w=args[27], x=args[28], y=args[29], z=args[30]),
    pip=Quaternion(w=args[31], x=args[32], y=args[33], z=args[34]),
    dip=Quaternion(w=args[35], x=args[36], y=args[37], z=args[38]),
  )

  ring = FingerQuaternion(
    mcp=Quaternion(w=args[39], x=args[40], y=args[41], z=args[42]),
    pip=Quaternion(w=args[43], x=args[44], y=args[45], z=args[46]),
    dip=Quaternion(w=args[47], x=args[48], y=args[49], z=args[50]),
  )

  little = FingerQuaternion(
    mcp=Quaternion(w=args[51], x=args[52], y=args[53], z=args[54]),
    pip=Quaternion(w=args[55], x=args[56], y=args[57], z=args[58]),
    dip=Quaternion(w=args[59], x=args[60], y=args[61], z=args[62]),
  )

  return HandQuaternion(
    device_id=device_id,
    hand_type=hand_type,
    thumb=thumb,
    index=index,
    middle=middle,
    ring=ring,
    little=little,
  )
