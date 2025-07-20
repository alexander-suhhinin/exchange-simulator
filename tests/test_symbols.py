"""
Test script for multiple symbols support
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_available_symbols():
    """Test getting available symbols"""
    print("Testing available symbols endpoint...")

    try:
        response = requests.get(f"{BASE_URL}/api/v1/symbols")
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Code: {data.get('code')}")
            symbols = data.get('data', {}).get('symbols', [])
            count = data.get('data', {}).get('count', 0)
            print(f"Available symbols ({count}): {symbols}")
        else:
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"Error: {e}")

def test_symbol_validation():
    """Test symbol validation"""
    print("\nTesting symbol validation...")

    # Test existing symbol
    try:
        response = requests.get(f"{BASE_URL}/openApi/swap/v3/quote/klines?symbol=ADA-USDT&limit=5")
        print(f"ADA-USDT klines - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"ADA-USDT klines - Code: {data.get('code')}")
            print(f"ADA-USDT klines - Count: {len(data.get('data', []))}")
    except Exception as e:
        print(f"Error testing ADA-USDT: {e}")

    # Test non-existing symbol
    try:
        response = requests.get(f"{BASE_URL}/openApi/swap/v3/quote/klines?symbol=BTC-USDT&limit=5")
        print(f"BTC-USDT klines - Status: {response.status_code}")
        if response.status_code == 404:
            data = response.json()
            print(f"BTC-USDT klines - Code: {data.get('code')}")
            print(f"BTC-USDT klines - Message: {data.get('msg')}")
    except Exception as e:
        print(f"Error testing BTC-USDT: {e}")

def test_health_with_symbols():
    """Test health endpoint"""
    print("\nTesting health endpoint...")

    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Health: {data.get('status')}")
            print(f"Current time: {data.get('current_time')}")
            print(f"Balance: {data.get('balance')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Multiple Symbols Support Test")
    print("=" * 50)

    try:
        test_available_symbols()
        test_symbol_validation()
        test_health_with_symbols()

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure the emulator is running on http://localhost:8000")
    except Exception as e:
        print(f"Error: {e}")