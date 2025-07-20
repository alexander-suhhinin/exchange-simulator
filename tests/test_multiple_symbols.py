"""
Test script for multiple symbols trading
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_multiple_symbols_klines():
    """Test klines for multiple symbols"""
    print("Testing klines for multiple symbols...")

    symbols = ["ADA-USDT", "BTC-USDT", "BNB-USDT", "AVAX-USDT", "ATOM-USDT"]

    for symbol in symbols:
        try:
            response = requests.get(f"{BASE_URL}/openApi/swap/v3/quote/klines?symbol={symbol}&limit=3")
            print(f"\n{symbol}:")
            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                klines = data.get('data', [])
                print(f"  Code: {data.get('code')}")
                print(f"  Klines count: {len(klines)}")
                if klines:
                    last_candle = klines[-1]
                    print(f"  Last close: {last_candle.get('close')}")
            else:
                print(f"  Error: {response.text}")

        except Exception as e:
            print(f"  Error: {e}")

def test_multiple_symbols_depth():
    """Test depth for multiple symbols"""
    print("\nTesting depth for multiple symbols...")

    symbols = ["ADA-USDT", "BTC-USDT", "BNB-USDT"]

    for symbol in symbols:
        try:
            response = requests.get(f"{BASE_URL}/openApi/swap/v2/quote/depth?symbol={symbol}&limit=3")
            print(f"\n{symbol}:")
            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                depth = data.get('data', {})
                print(f"  Code: {data.get('code')}")
                print(f"  Bids: {len(depth.get('bids', []))}")
                print(f"  Asks: {len(depth.get('asks', []))}")
            else:
                print(f"  Error: {response.text}")

        except Exception as e:
            print(f"  Error: {e}")

def test_trading_multiple_symbols():
    """Test trading on multiple symbols"""
    print("\nTesting trading on multiple symbols...")

    symbols = ["ADA-USDT", "BTC-USDT", "BNB-USDT"]

    for symbol in symbols:
        try:
            # Create a small order
            order_data = {
                "symbol": symbol,
                "side": "BUY",
                "positionSide": "LONG",
                "type": "MARKET",
                "quantity": 10.0
            }

            response = requests.post(f"{BASE_URL}/openApi/swap/v2/trade/order", json=order_data)
            print(f"\n{symbol} order:")
            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                order = data.get('data', {}).get('order', {})
                print(f"  Code: {data.get('code')}")
                print(f"  Order ID: {order.get('orderId')}")
                print(f"  Executed Price: {order.get('executedPrice')}")
                print(f"  Status: {order.get('status')}")
            else:
                print(f"  Error: {response.text}")

        except Exception as e:
            print(f"  Error: {e}")

def test_positions_multiple_symbols():
    """Test positions for multiple symbols"""
    print("\nTesting positions...")

    try:
        response = requests.get(f"{BASE_URL}/openApi/swap/v2/user/positions")
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            positions = data.get('data', [])
            print(f"Code: {data.get('code')}")
            print(f"Positions count: {len(positions)}")

            for pos in positions:
                print(f"  {pos.get('symbol')}: {pos.get('side')} {pos.get('quantity')} @ {pos.get('entryPrice')}")
        else:
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Multiple Symbols Trading Test")
    print("=" * 50)

    try:
        test_multiple_symbols_klines()
        test_multiple_symbols_depth()
        test_trading_multiple_symbols()
        test_positions_multiple_symbols()

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure the emulator is running on http://localhost:8000")
    except Exception as e:
        print(f"Error: {e}")