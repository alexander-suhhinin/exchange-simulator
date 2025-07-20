"""
Test script for immediate order execution with TP/SL simulation
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_immediate_execution_no_tp_sl():
    """Test immediate execution without TP/SL"""
    print("Testing immediate execution without TP/SL...")

    order_data = {
        "symbol": "ADA-USDT",
        "side": "BUY",
        "positionSide": "LONG",
        "type": "MARKET",
        "quantity": 50.0,
        "immediate": True
    }

    try:
        response = requests.post(f"{BASE_URL}/openApi/swap/v2/trade/order", json=order_data)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Code: {data.get('code')}")

            order = data.get('data', {}).get('order', {})
            print(f"Order ID: {order.get('orderId')}")
            print(f"Executed Price: {order.get('executedPrice')}")
            print(f"Status: {order.get('status')}")

            execution = data.get('data', {}).get('execution', {})
            if execution:
                print(f"Execution triggered: {execution.get('triggered')}")
                print(f"Trigger type: {execution.get('trigger_type')}")
                print(f"Trigger price: {execution.get('trigger_price')}")
                print(f"Trigger timestamp: {execution.get('trigger_timestamp')}")
                print(f"PnL: {execution.get('pnl')}")
                print(f"Execution time: {execution.get('execution_time')}")
            else:
                print("No execution data")
        else:
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"Error: {e}")

def test_immediate_execution_with_tp():
    """Test immediate execution with Take Profit"""
    print("\nTesting immediate execution with Take Profit...")

    order_data = {
        "symbol": "ADA-USDT",
        "side": "BUY",
        "positionSide": "LONG",
        "type": "MARKET",
        "quantity": 30.0,
        "takeProfit": "{\"stopPrice\": \"0.65\"}",
        "immediate": True
    }

    try:
        response = requests.post(f"{BASE_URL}/openApi/swap/v2/trade/order", json=order_data)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Code: {data.get('code')}")

            order = data.get('data', {}).get('order', {})
            print(f"Order ID: {order.get('orderId')}")
            print(f"Executed Price: {order.get('executedPrice')}")
            print(f"Take Profit: {order.get('takeProfit')}")

            execution = data.get('data', {}).get('execution', {})
            if execution:
                print(f"Execution triggered: {execution.get('triggered')}")
                print(f"Trigger type: {execution.get('trigger_type')}")
                print(f"Trigger price: {execution.get('trigger_price')}")
                print(f"Trigger timestamp: {execution.get('trigger_timestamp')}")
                print(f"PnL: {execution.get('pnl')}")
                print(f"Execution time: {execution.get('execution_time')}")
            else:
                print("No execution data")
        else:
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"Error: {e}")

def test_immediate_execution_with_sl():
    """Test immediate execution with Stop Loss"""
    print("\nTesting immediate execution with Stop Loss...")

    order_data = {
        "symbol": "ADA-USDT",
        "side": "BUY",
        "positionSide": "LONG",
        "type": "MARKET",
        "quantity": 20.0,
        "stopLoss": "{\"stopPrice\": \"0.55\"}",
        "immediate": True
    }

    try:
        response = requests.post(f"{BASE_URL}/openApi/swap/v2/trade/order", json=order_data)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Code: {data.get('code')}")

            order = data.get('data', {}).get('order', {})
            print(f"Order ID: {order.get('orderId')}")
            print(f"Executed Price: {order.get('executedPrice')}")
            print(f"Stop Loss: {order.get('stopLoss')}")

            execution = data.get('data', {}).get('execution', {})
            if execution:
                print(f"Execution triggered: {execution.get('triggered')}")
                print(f"Trigger type: {execution.get('trigger_type')}")
                print(f"Trigger price: {execution.get('trigger_price')}")
                print(f"Trigger timestamp: {execution.get('trigger_timestamp')}")
                print(f"PnL: {execution.get('pnl')}")
                print(f"Execution time: {execution.get('execution_time')}")
            else:
                print("No execution data")
        else:
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"Error: {e}")

def test_immediate_execution_with_tp_sl():
    """Test immediate execution with both TP and SL"""
    print("\nTesting immediate execution with both TP and SL...")

    order_data = {
        "symbol": "ADA-USDT",
        "side": "BUY",
        "positionSide": "LONG",
        "type": "MARKET",
        "quantity": 25.0,
        "takeProfit": "{\"stopPrice\": \"0.70\"}",
        "stopLoss": "{\"stopPrice\": \"0.50\"}",
        "immediate": True
    }

    try:
        response = requests.post(f"{BASE_URL}/openApi/swap/v2/trade/order", json=order_data)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Code: {data.get('code')}")

            order = data.get('data', {}).get('order', {})
            print(f"Order ID: {order.get('orderId')}")
            print(f"Executed Price: {order.get('executedPrice')}")
            print(f"Take Profit: {order.get('takeProfit')}")
            print(f"Stop Loss: {order.get('stopLoss')}")

            execution = data.get('data', {}).get('execution', {})
            if execution:
                print(f"Execution triggered: {execution.get('triggered')}")
                print(f"Trigger type: {execution.get('trigger_type')}")
                print(f"Trigger price: {execution.get('trigger_price')}")
                print(f"Trigger timestamp: {execution.get('trigger_timestamp')}")
                print(f"PnL: {execution.get('pnl')}")
                print(f"Execution time: {execution.get('execution_time')}")
            else:
                print("No execution data")
        else:
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"Error: {e}")

def test_short_position_immediate():
    """Test immediate execution for short position"""
    print("\nTesting immediate execution for short position...")

    order_data = {
        "symbol": "ADA-USDT",
        "side": "SELL",
        "positionSide": "SHORT",
        "type": "MARKET",
        "quantity": 15.0,
        "takeProfit": "{\"stopPrice\": \"0.55\"}",
        "stopLoss": "{\"stopPrice\": \"0.70\"}",
        "immediate": True
    }

    try:
        response = requests.post(f"{BASE_URL}/openApi/swap/v2/trade/order", json=order_data)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Code: {data.get('code')}")

            order = data.get('data', {}).get('order', {})
            print(f"Order ID: {order.get('orderId')}")
            print(f"Executed Price: {order.get('executedPrice')}")
            print(f"Position Side: {order.get('positionSide')}")

            execution = data.get('data', {}).get('execution', {})
            if execution:
                print(f"Execution triggered: {execution.get('triggered')}")
                print(f"Trigger type: {execution.get('trigger_type')}")
                print(f"Trigger price: {execution.get('trigger_price')}")
                print(f"Trigger timestamp: {execution.get('trigger_timestamp')}")
                print(f"PnL: {execution.get('pnl')}")
                print(f"Execution time: {execution.get('execution_time')}")
            else:
                print("No execution data")
        else:
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"Error: {e}")

def test_positions_after_immediate():
    """Test positions after immediate execution"""
    print("\nTesting positions after immediate execution...")

    try:
        response = requests.get(f"{BASE_URL}/openApi/swap/v2/user/positions")
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            positions = data.get('data', [])
            print(f"Positions count: {len(positions)}")

            for pos in positions:
                print(f"  {pos.get('symbol')}: {pos.get('side')} {pos.get('quantity')} @ {pos.get('entryPrice')}")
                print(f"    TP: {pos.get('takeProfit')}, SL: {pos.get('stopLoss')}")
                print(f"    PnL: {pos.get('unrealizedPnl')}")
        else:
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Immediate Execution Test")
    print("=" * 50)

    try:
        test_immediate_execution_no_tp_sl()
        test_immediate_execution_with_tp()
        test_immediate_execution_with_sl()
        test_immediate_execution_with_tp_sl()
        test_short_position_immediate()
        test_positions_after_immediate()

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure the emulator is running on http://localhost:8000")
    except Exception as e:
        print(f"Error: {e}")