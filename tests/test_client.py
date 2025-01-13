import asyncio

import pytest

from diving_station_py.client import DivingStationClient
from diving_station_py.protocol.hand_bend import HandType


@pytest.fixture(scope="module")
def event_loop():
  """Test the event loop."""
  loop = asyncio.get_event_loop()
  yield loop
  loop.close()


@pytest.fixture(scope="function")
async def client(event_loop):
  """Test the DivingStationClient."""
  client = DivingStationClient()
  yield client
  if client.connected:
    await client.disconnect()


@pytest.mark.asyncio()
async def test_init_client(client):
  """Test the DivingStationClient."""
  assert client.receive_port == 25788
  assert client._connected is False


@pytest.mark.asyncio()
async def test_connect(client):
  """Test the connect method."""
  await client.connect()
  assert client.connected is True
  await client.disconnect()


@pytest.mark.asyncio()
async def test_disconnect(client):
  """Test the disconnect method."""
  await client.connect()
  await client.disconnect()
  assert client.connected is False


@pytest.mark.asyncio()
async def test_send_haptic(client):
  """Test the send_haptic method."""
  await client.connect()

  # device が見つかるまで待つ
  main_device = None
  while not main_device:
    await asyncio.sleep(0.1)
    main_device = client.devices[0] if client.devices else None

  # 右手を振動
  await client.send_haptic(main_device.id, HandType.RIGHT, 0.1, 1.0, 0.2)
  await asyncio.sleep(0.2)
  # 左手を振動
  await client.send_haptic(main_device.id, HandType.LEFT, 0.1, 1.0, 0.2)
  await client.disconnect()

  assert True
