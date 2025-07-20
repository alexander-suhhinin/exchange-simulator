"""
Test script for BingX Emulator API
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_klines():
    """Test klines endpoint"""
    print("Testing klines endpoint...")

    response = requests.get(f"{BASE_URL}/openApi/swap/v3/quote/klines", params={
        "symbol": "ADA-USDT",
        "interval": "5m",
        "limit": 10
    })

    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Code: {data.get('code')}")
    print(f"Message: {data.get('msg')}")
    print(f"Data length: {len(data.get('data', []))}")

    if data.get('data'):
        print(f"First candle: {data['data'][0]}")
        print(f"Last candle: {data['data'][-1]}")

def test_depth():
    """Test depth endpoint"""
    print("\nTesting depth endpoint...")

    response = requests.get(f"{BASE_URL}/openApi/swap/v2/quote/depth", params={
        "symbol": "ADA-USDT",
        "limit": 10
    })

    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Code: {data.get('code')}")
    print(f"Data: {json.dumps(data.get('data'), indent=2)}")

def test_health():
    """Test health endpoint"""
    print("\nTesting health endpoint...")

    response = requests.get(f"{BASE_URL}/health")

    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Health data: {json.dumps(data, indent=2)}")

def test_order():
    """Test order creation"""
    print("\nTesting order creation...")

    order_data = {
        "symbol": "ADA-USDT",
        "side": "BUY",
        "positionSide": "LONG",
        "type": "MARKET",
        "quantity": 100.0,
        "takeProfit": '{"type": "TAKE_PROFIT_MARKET", "stopPrice": 0.6, "price": 0.6, "workingType": "MARK_PRICE"}',
        "stopLoss": '{"type": "STOP_MARKET", "stopPrice": 0.4, "price": 0.4, "workingType": "MARK_PRICE"}'
    }

    response = requests.post(f"{BASE_URL}/openApi/swap/v2/trade/order", json=order_data)

    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Code: {data.get('code')}")
    print(f"Message: {data.get('msg')}")
    print(f"Order data: {json.dumps(data.get('data'), indent=2)}")

def test_positions():
    """Test positions endpoint"""
    print("\nTesting positions endpoint...")

    response = requests.get(f"{BASE_URL}/openApi/swap/v2/user/positions")

    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Code: {data.get('code')}")
    print(f"Positions: {json.dumps(data.get('data'), indent=2)}")

def test_trading_summary():
    """Test trading summary endpoint"""
    print("\nTesting trading summary endpoint...")

    response = requests.get(f"{BASE_URL}/api/v1/trading/summary")

    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Code: {data.get('code')}")
    print(f"Trading Summary: {json.dumps(data.get('data'), indent=2)}")

def test_state_management():
    """Test state management endpoints"""
    print("\nTesting state management...")

    # Save state
    response = requests.post(f"{BASE_URL}/api/v1/state/save")
    print(f"Save state - Status: {response.status_code}")
    data = response.json()
    print(f"Save state - Code: {data.get('code')}")
    print(f"Save state - Message: {data.get('msg')}")

def test_order_management():
    """Test order management endpoints"""
    print("\nTesting order management...")

    # Get all orders
    response = requests.get(f"{BASE_URL}/openApi/swap/v2/trade/allOrders", params={"limit": 10})
    print(f"All orders - Status: {response.status_code}")
    data = response.json()
    print(f"All orders - Code: {data.get('code')}")
    print(f"All orders count: {len(data.get('data', []))}")

def test_time_management():
    """Test time management endpoints"""
    print("\nTesting time management...")

    # Get current time
    response = requests.get(f"{BASE_URL}/api/v1/time/current")
    print(f"Current time - Status: {response.status_code}")
    data = response.json()
    print(f"Current time - Code: {data.get('code')}")
    print(f"Current time: {data.get('data', {}).get('current_time')}")

    # Advance time
    response = requests.post(f"{BASE_URL}/api/v1/time/advance", json={"steps": 5})
    print(f"Advance time - Status: {response.status_code}")
    data = response.json()
    print(f"Advance time - Code: {data.get('code')}")
    print(f"New time: {data.get('data', {}).get('current_time')}")

def test_config_management():
    """Test configuration management endpoints"""
    print("\nTesting configuration management...")

    # Get config
    response = requests.get(f"{BASE_URL}/api/v1/config")
    print(f"Get config - Status: {response.status_code}")
    data = response.json()
    print(f"Get config - Code: {data.get('code')}")
    print(f"Config keys: {list(data.get('data', {}).keys())}")

if __name__ == "__main__":
    print("BingX Emulator API Test")
    print("=" * 50)

    try:
        test_health()
        test_klines()
        test_depth()
        test_order()
        test_positions()
        test_trading_summary()
        test_state_management()
        test_order_management()
        test_time_management()
        test_config_management()

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure the emulator is running on http://localhost:8000")
    except Exception as e:
        print(f"Error: {e}")