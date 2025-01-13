import asyncio

import pytest

from diving_station_py.client import DivingStationClient
from diving_station_py.event import (
  ConnectEvent,
  ControllerInputReceivedEvent,
  DeviceInfoReceivedEvent,
  DisconnectEvent,
  HandBendReceivedEvent,
  HandQuatReceivedEvent,
  WristReceivedEvent,
)
from diving_station_py.protocol import controller, hand_bend, hand_quat, wrist
from diving_station_py.protocol.device_info import DeviceInfo


@pytest.fixture(scope="module")
def event_loop():
  """Create an instance of the default event loop for each test case."""
  loop = asyncio.new_event_loop()
  yield loop
  loop.close()


@pytest.fixture(scope="function")
async def client(event_loop: asyncio.AbstractEventLoop):
  """Create an instance of the DivingStationClient for each test case."""
  client = DivingStationClient()
  yield client
  if client.connected:
    await client.disconnect()


@pytest.mark.asyncio()
async def test_handler_on_connect(client: DivingStationClient):
  """Test the on_connect handler."""
  called = False

  @client.on_connect
  async def on_connect(event: ConnectEvent) -> None:
    nonlocal called
    called = True

  await client.connect()
  await asyncio.sleep(0)
  assert called


@pytest.mark.asyncio()
async def test_handler_on_disconnect(client: DivingStationClient):
  """Test the on_disconnect handler."""
  called = False

  @client.on_disconnect
  async def on_disconnect(event: DisconnectEvent) -> None:
    nonlocal called
    called = True

  await client.connect()
  await client.disconnect()
  await asyncio.sleep(0)
  assert called


@pytest.mark.asyncio()
async def test_handler_on_device_info(client: DivingStationClient):
  """Test the on_device_info_received handler."""
  called = False

  @client.on_device_info_received
  async def on_device_info(event: DeviceInfoReceivedEvent) -> None:
    nonlocal called
    called = True

  await client.connect()
  await asyncio.sleep(0.2)
  assert called
  devices = client.devices

  for device in devices:
    assert isinstance(device, DeviceInfo)


@pytest.mark.asyncio()
async def test_handler_on_wrist_data(client: DivingStationClient):
  """Test the on_wrist_received handler."""
  called = False
  wrist_qt = None

  @client.on_wrist_received
  async def on_wrist(event: WristReceivedEvent):
    nonlocal called
    nonlocal wrist_qt
    called = True
    wrist_qt = event.wrist

  await client.connect()
  await asyncio.sleep(0.2)
  assert called
  assert isinstance(wrist_qt, wrist.Wirst)


@pytest.mark.asyncio()
async def test_handler_on_controller_input(client: DivingStationClient):
  """Test the on_controller_received handler"""
  called = False
  data: controller.ControllerInput | None = None

  @client.on_controller_received
  async def on_controller_input(event: ControllerInputReceivedEvent):
    nonlocal called
    nonlocal data
    called = True
    data = event.controller_input

  await client.connect()
  await asyncio.sleep(0.2)
  assert called
  assert isinstance(data, controller.ControllerInput)


@pytest.mark.asyncio()
async def test_handler_on_hand_bend(client: DivingStationClient):
  """Test the on_hand_bend_received handler."""
  called = False
  data: hand_bend.HandBend | None = None

  @client.on_hand_bend_received
  async def on_hand_bend(event: HandBendReceivedEvent):
    nonlocal called
    nonlocal data
    called = True
    data = event.hand_bend

  await client.connect()
  await asyncio.sleep(0.2)
  assert called
  assert isinstance(data, hand_bend.HandBend)


@pytest.mark.asyncio()
async def test_handler_on_hand_quat(client: DivingStationClient):
  """Test the on_hand_quat_received handler."""
  called = False
  data: hand_quat.HandQuaternion | None = None

  @client.on_hand_quat_received
  async def on_hand_quat(event: HandQuatReceivedEvent):
    nonlocal called
    nonlocal data
    called = True
    data = event.quaternion

  await client.connect()
  await asyncio.sleep(0.2)
  assert called
  assert isinstance(data, hand_quat.HandQuaternion)
