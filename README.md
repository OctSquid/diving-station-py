# Diving Station Python SDK

Diving Stationデバイスと通信するためのPython SDKです。
v1.5.6以降のDiving Stationに対応しています。

## 特徴

- Diving Stationデバイスとの接続管理
- デバイス情報の取得
- ハンドジェスチャー（手の曲げ、クォータニオン）データの受信
- 触覚フィードバックの制御
- 手首の動きデータの受信

## インストール

- pip

```bash
pip install diving-station
```

- rye

```bash
rye add diving-station
```

## 使用方法

```python
import asyncio
from diving_station_py.client import DivingStationClient
from diving_station_py.constants import HandType

async def main():
    client = DivingStationClient()
    
    # デバイスに接続
    await client.connect()
    
    # メインデバイスが見つかるまで待機
    main_device = None
    while not main_device:
        await asyncio.sleep(0.1)
        main_device = client.devices[0] if client.devices else None
    
    if main_device:
        # 右手に触覚フィードバックを送信
        await client.send_haptic(
            device_id=main_device.id,
            hand_type=HandType.RIGHT,
            frequency=0.1,
            intensity=1.0,
            duration=0.2
        )
    
    # 切断
    await client.disconnect()

# 非同期実行
asyncio.run(main())
```

## 開発

### 依存関係のインストール

```bash
rye sync
```

### テストの実行

テストの実行はDiving Stationを起動し, デバイスを接続してから行ってください。

```bash
rye pytest
```

## ライセンス

[MIT](LICENSE)
