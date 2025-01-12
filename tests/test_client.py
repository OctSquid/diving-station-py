import asyncio
import pytest

from diving_station_py.protocol.hand_bend import HandType
from diving_station_py.client import DivingStationClient


@pytest.fixture
def client():
    return DivingStationClient()


@pytest.mark.asyncio(loop_scope="module")
async def test_client(client):
    assert client.receive_port == 25788
    assert client.devices == []
    assert client._dispatcher is not None
    assert client._client is not None
    assert client._connected is False


@pytest.mark.asyncio(loop_scope="module")
async def test_connect(client):
    await client.connect()
    assert client.connected is True
    await client.disconnect()


@pytest.mark.asyncio(loop_scope="module")
async def test_disconnect(client):
    await client.connect()
    await client.disconnect()
    assert client.connected is False


@pytest.mark.asyncio(loop_scope="module")
async def test_send_haptic(client):
    await client.connect()

    # device が見つかるまで待つ
    main_device = None
    while not main_device:
        await asyncio.sleep(0.1)
        main_device = client.devices[0] if client.devices else None

    await client.send_haptic(main_device.id, HandType.RIGHT, 0.1, 1.0, 0.5)
    await client.disconnect()

    assert True
