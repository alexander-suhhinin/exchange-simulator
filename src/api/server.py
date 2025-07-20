"""
FastAPI server for BingX Emulator
"""
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from datetime import timedelta
import uvicorn
import atexit

from src.data.manager import DataManager
from src.time.manager import TimeManager
from src.trading.balance_manager import BalanceManager
from src.trading.order_engine import OrderEngine
from src.trading.models import OrderStatus
from src.state.manager import StateManager
from src.utils.trade_logger import TradeLogger
from src.utils.logger import setup_logger
from src.config.settings import settings

logger = setup_logger(__name__)

class BingXEmulatorAPI:
    """
    BingX API emulator server
    """

    def __init__(self):
        self.app = FastAPI(title="BingX Emulator", version="1.0.0")
        self.data_manager = DataManager()

        # Initialize time manager with earliest available time
        earliest_time = self.data_manager.get_earliest_time("ADA-USDT")
        if earliest_time:
            # Start from a reasonable time (e.g., 1 hour after earliest data)
            start_time = earliest_time + timedelta(hours=1)
            self.time_manager = TimeManager(start_time)
            logger.info(f"Simulation started at: {start_time}")
        else:
            self.time_manager = TimeManager()
            logger.warning("Could not determine earliest time, using current time")

        self.balance_manager = BalanceManager()
        self.order_engine = OrderEngine(self.balance_manager)
        self.state_manager = StateManager()
        self.trade_logger = TradeLogger()

        # Load saved state
        self.state_manager.load_all_state(self.balance_manager, self.order_engine, self.time_manager)

        # Register cleanup on exit
        atexit.register(self._cleanup)

        # Setup routes
        self._setup_routes()

    def _cleanup(self):
        """Save state on exit"""
        try:
            self.state_manager.save_all_state(self.balance_manager, self.order_engine, self.time_manager)
            logger.info("State saved on exit")
        except Exception as e:
            logger.error(f"Error saving state on exit: {e}")

    def _setup_routes(self):
        """Setup API routes"""

        @self.app.get("/openApi/swap/v3/quote/klines")
        async def get_klines(
            symbol: str = Query(..., description="Trading pair symbol"),
            interval: str = Query("5m", description="Timeframe interval"),
            limit: int = Query(500, description="Number of candles"),
            startTime: Optional[int] = Query(None, description="Start time in milliseconds"),
            endTime: Optional[int] = Query(None, description="End time in milliseconds")
        ):
            """Get klines data in BingX format"""
            try:
                logger.info(f"Klines request: {symbol}, {interval}, limit={limit}")

                # Validate symbol
                if not self.data_manager.validate_symbol(symbol):
                    return JSONResponse(
                        status_code=404,
                        content={
                            "code": 404,
                            "msg": f"Symbol {symbol} not found or no data available",
                            "data": []
                        }
                    )

                klines = self.data_manager.get_klines(
                    symbol=symbol,
                    interval=interval,
                    limit=limit,
                    current_time=self.time_manager.current_time
                )

                return {
                    "code": 0,
                    "msg": "success",
                    "data": klines
                }

            except Exception as e:
                logger.error(f"Error in klines endpoint: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "code": 500,
                        "msg": f"Internal error: {str(e)}",
                        "data": []
                    }
                )

        @self.app.get("/openApi/swap/v2/quote/depth")
        async def get_depth(
            symbol: str = Query(..., description="Trading pair symbol"),
            limit: int = Query(50, description="Depth limit")
        ):
            """Get orderbook depth (mocked)"""
            try:
                logger.info(f"Depth request: {symbol}, limit={limit}")

                # Validate symbol
                if not self.data_manager.validate_symbol(symbol):
                    return JSONResponse(
                        status_code=404,
                        content={
                            "code": 404,
                            "msg": f"Symbol {symbol} not found or no data available",
                            "data": None
                        }
                    )

                # Mock depth data
                current_price = self.data_manager.get_current_price(
                    symbol, self.time_manager.current_time
                )

                if current_price is None:
                    return JSONResponse(
                        status_code=404,
                        content={
                            "code": 404,
                            "msg": "Symbol not found",
                            "data": None
                        }
                    )

                # Create mock orderbook
                depth_data = {
                    "symbol": symbol,
                    "bids": [
                        [str(current_price * 0.999), "1000"],
                        [str(current_price * 0.998), "2000"],
                        [str(current_price * 0.997), "3000"]
                    ],
                    "asks": [
                        [str(current_price * 1.001), "1000"],
                        [str(current_price * 1.002), "2000"],
                        [str(current_price * 1.003), "3000"]
                    ],
                    "timestamp": self.time_manager.get_timestamp_ms()
                }

                return {
                    "code": 0,
                    "msg": "success",
                    "data": depth_data
                }

            except Exception as e:
                logger.error(f"Error in depth endpoint: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "code": 500,
                        "msg": f"Internal error: {str(e)}",
                        "data": None
                    }
                )

        @self.app.post("/openApi/swap/v2/trade/order")
        async def create_order(
            symbol: str = Body(..., embed=True),
            side: str = Body(..., embed=True),
            positionSide: str = Body(..., embed=True),
            type: str = Body(..., embed=True),
            quantity: float = Body(..., embed=True),
            takeProfit: Optional[str] = Body(None, embed=True),
            stopLoss: Optional[str] = Body(None, embed=True),
            immediate: bool = Body(False, embed=True)
        ):
            """Create a new order"""
            try:
                logger.info(f"Order request: {symbol} {side} {quantity}")

                # Validate symbol
                if not self.data_manager.validate_symbol(symbol):
                    return JSONResponse(
                        status_code=404,
                        content={
                            "code": 404,
                            "msg": f"Symbol {symbol} not found or no data available",
                            "data": None
                        }
                    )

                # Parse TP/SL from JSON strings
                take_profit = None
                stop_loss = None

                if takeProfit:
                    import json
                    tp_data = json.loads(takeProfit)
                    take_profit = float(tp_data.get('stopPrice', 0))

                if stopLoss:
                    import json
                    sl_data = json.loads(stopLoss)
                    stop_loss = float(sl_data.get('stopPrice', 0))

                # Create order
                success, message, order = self.order_engine.create_order(
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    order_type=type,
                    take_profit=take_profit,
                    stop_loss=stop_loss
                )

                if not success:
                    self.trade_logger.log_error("order_creation_failed", message, {
                        "symbol": symbol, "side": side, "quantity": quantity
                    })
                    return JSONResponse(
                        status_code=400,
                        content={
                            "code": 400,
                            "msg": message,
                            "data": None
                        }
                    )

                # Log order creation
                self.trade_logger.log_order_created(order, self.time_manager.current_time)

                                # Execute market order immediately
                execution_result = None
                if type == "MARKET":
                    current_price = self.data_manager.get_current_price(
                        symbol, self.time_manager.current_time
                    )

                    if current_price:
                        # Get current candle data for TP/SL checking
                        base_df = self.data_manager.load_symbol_data(symbol)
                        filtered_df = base_df[base_df.index <= self.time_manager.current_time]

                        if not filtered_df.empty:
                            current_candle = filtered_df.iloc[-1]
                            success = self.order_engine.execute_market_order(
                                order, current_price,
                                current_candle['high'], current_candle['low']
                            )

                            if success:
                                # Log execution
                                self.trade_logger.log_order_executed(
                                    order, current_price, self.time_manager.current_time
                                )

                                # Save state after successful execution
                                self.state_manager.save_all_state(
                                    self.balance_manager, self.order_engine, self.time_manager
                                )

                # Handle immediate execution with TP/SL simulation
                if immediate and order.status == OrderStatus.FILLED:
                    execution_result = self._simulate_immediate_execution(order, symbol)

                response_data = {
                    "order": order.to_dict()
                }

                if execution_result:
                    response_data["execution"] = execution_result

                return {
                    "code": 0,
                    "msg": "success",
                    "data": response_data
                }

            except Exception as e:
                logger.error(f"Error in order endpoint: {e}")
                self.trade_logger.log_error("order_endpoint_error", str(e), {
                    "symbol": symbol, "side": side, "quantity": quantity
                })
                return JSONResponse(
                    status_code=500,
                    content={
                        "code": 500,
                        "msg": f"Internal error: {str(e)}",
                        "data": None
                    }
                )

        @self.app.get("/openApi/swap/v2/trade/openOrders")
        async def get_open_orders():
            """Get open orders"""
            try:
                open_orders = self.order_engine.get_open_orders()
                orders_data = [order.to_dict() for order in open_orders]

                return {
                    "code": 0,
                    "msg": "success",
                    "data": orders_data
                }

            except Exception as e:
                logger.error(f"Error in open orders endpoint: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "code": 500,
                        "msg": f"Internal error: {str(e)}",
                        "data": []
                    }
                )

        @self.app.get("/openApi/swap/v2/trade/order")
        async def get_order_details(
            orderId: str = Query(..., description="Order ID")
        ):
            """Get order details by ID"""
            try:
                order = self.order_engine.get_order(orderId)

                if not order:
                    return JSONResponse(
                        status_code=404,
                        content={
                            "code": 404,
                            "msg": "Order not found",
                            "data": None
                        }
                    )

                return {
                    "code": 0,
                    "msg": "success",
                    "data": order.to_dict()
                }

            except Exception as e:
                logger.error(f"Error in order details endpoint: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "code": 500,
                        "msg": f"Internal error: {str(e)}",
                        "data": None
                    }
                )

        @self.app.get("/openApi/swap/v2/trade/allOrders")
        async def get_all_orders(
            symbol: Optional[str] = Query(None, description="Trading pair symbol"),
            limit: int = Query(100, description="Number of orders to return")
        ):
            """Get all orders (open + history)"""
            try:
                # Get open orders
                open_orders = self.order_engine.get_open_orders(symbol)

                # Get order history
                history_orders = self.order_engine.get_order_history(symbol, limit)

                # Combine and sort by creation time
                all_orders = open_orders + history_orders
                all_orders.sort(key=lambda x: x.created_time, reverse=True)

                # Limit results
                all_orders = all_orders[:limit]

                orders_data = [order.to_dict() for order in all_orders]

                return {
                    "code": 0,
                    "msg": "success",
                    "data": orders_data
                }

            except Exception as e:
                logger.error(f"Error in all orders endpoint: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "code": 500,
                        "msg": f"Internal error: {str(e)}",
                        "data": []
                    }
                )

        @self.app.delete("/openApi/swap/v2/trade/order")
        async def cancel_order(
            orderId: str = Query(..., description="Order ID to cancel")
        ):
            """Cancel an order"""
            try:
                success, message = self.order_engine.cancel_order(orderId)

                if not success:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "code": 400,
                            "msg": message,
                            "data": None
                        }
                    )

                return {
                    "code": 0,
                    "msg": "Order cancelled successfully",
                    "data": None
                }

            except Exception as e:
                logger.error(f"Error in cancel order endpoint: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "code": 500,
                        "msg": f"Internal error: {str(e)}",
                        "data": None
                    }
                )

        @self.app.get("/openApi/swap/v2/user/positions")
        async def get_positions():
            """Get open positions"""
            try:
                positions = self.balance_manager.get_all_positions()
                positions_data = [pos.to_dict() for pos in positions]

                return {
                    "code": 0,
                    "msg": "success",
                    "data": positions_data
                }

            except Exception as e:
                logger.error(f"Error in positions endpoint: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "code": 500,
                        "msg": f"Internal error: {str(e)}",
                        "data": []
                    }
                )

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "current_time": self.time_manager.format_time_for_api(),
                "timestamp": self.time_manager.get_timestamp_ms(),
                "balance": self.balance_manager.get_account_summary()
            }

        @self.app.get("/api/v1/trading/summary")
        async def get_trading_summary():
            """Get trading summary"""
            try:
                summary = self.trade_logger.get_trade_summary()
                return {
                    "code": 0,
                    "msg": "success",
                    "data": summary
                }
            except Exception as e:
                logger.error(f"Error in trading summary endpoint: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "code": 500,
                        "msg": f"Internal error: {str(e)}",
                        "data": {}
                    }
                )

        @self.app.post("/api/v1/state/save")
        async def save_state():
            """Manually save state"""
            try:
                self.state_manager.save_all_state(
                    self.balance_manager, self.order_engine, self.time_manager
                )
                return {
                    "code": 0,
                    "msg": "State saved successfully",
                    "data": None
                }
            except Exception as e:
                logger.error(f"Error saving state: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "code": 500,
                        "msg": f"Error saving state: {str(e)}",
                        "data": None
                    }
                )

        @self.app.post("/api/v1/state/clear")
        async def clear_state():
            """Clear all saved state"""
            try:
                self.state_manager.clear_state()
                return {
                    "code": 0,
                    "msg": "State cleared successfully",
                    "data": None
                }
            except Exception as e:
                logger.error(f"Error clearing state: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "code": 500,
                        "msg": f"Error clearing state: {str(e)}",
                        "data": None
                    }
                )

        @self.app.get("/api/v1/time/current")
        async def get_current_time():
            """Get current simulation time"""
            try:
                return {
                    "code": 0,
                    "msg": "success",
                    "data": {
                        "current_time": self.time_manager.format_time_for_api(),
                        "timestamp": self.time_manager.get_timestamp_ms(),
                        "start_time": self.time_manager.start_time.isoformat()
                    }
                }
            except Exception as e:
                logger.error(f"Error in current time endpoint: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "code": 500,
                        "msg": f"Internal error: {str(e)}",
                        "data": None
                    }
                )

        @self.app.post("/api/v1/time/advance")
        async def advance_time(
            steps: int = Body(1, embed=True, description="Number of minutes to advance")
        ):
            """Advance simulation time"""
            try:
                self.time_manager.advance_time(steps)

                # Save state after time advance
                self.state_manager.save_all_state(
                    self.balance_manager, self.order_engine, self.time_manager
                )

                return {
                    "code": 0,
                    "msg": f"Time advanced by {steps} minutes",
                    "data": {
                        "current_time": self.time_manager.format_time_for_api(),
                        "timestamp": self.time_manager.get_timestamp_ms()
                    }
                }
            except Exception as e:
                logger.error(f"Error in advance time endpoint: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "code": 500,
                        "msg": f"Internal error: {str(e)}",
                        "data": None
                    }
                )

        @self.app.get("/api/v1/config")
        async def get_config():
            """Get current configuration"""
            try:
                from src.config.emulator_config import emulator_config
                return {
                    "code": 0,
                    "msg": "success",
                    "data": emulator_config.config
                }
            except Exception as e:
                logger.error(f"Error in config endpoint: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "code": 500,
                        "msg": f"Internal error: {str(e)}",
                        "data": None
                    }
                )

        @self.app.post("/api/v1/config/update")
        async def update_config(
            key_path: str = Body(..., embed=True, description="Configuration key path"),
            value: Any = Body(..., embed=True, description="New value")
        ):
            """Update configuration"""
            try:
                from src.config.emulator_config import emulator_config
                emulator_config.set(key_path, value)
                emulator_config.save()

                return {
                    "code": 0,
                    "msg": f"Configuration updated: {key_path} = {value}",
                    "data": None
                }
            except Exception as e:
                logger.error(f"Error in config update endpoint: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "code": 500,
                        "msg": f"Internal error: {str(e)}",
                        "data": None
                    }
                )

        @self.app.get("/api/v1/symbols")
        async def get_available_symbols():
            """Get list of available trading symbols"""
            try:
                symbols = self.data_manager.get_available_symbols()

                return {
                    "code": 0,
                    "msg": "success",
                    "data": {
                        "symbols": symbols,
                        "count": len(symbols)
                    }
                }
            except Exception as e:
                logger.error(f"Error in symbols endpoint: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "code": 500,
                        "msg": f"Internal error: {str(e)}",
                        "data": {"symbols": [], "count": 0}
                    }
                )

    def _simulate_immediate_execution(self, order, symbol: str) -> dict:
        """
        Simulate immediate execution with TP/SL checking

        Args:
            order: The executed order
            symbol: Trading pair symbol

        Returns:
            Execution result with TP/SL info
        """
        try:
            # Get position created by this order
            position_key = f"{symbol}_{order.position_side.value}"
            position = self.balance_manager.positions.get(position_key)

            if not position:
                return None

            # Simulate time progression to check TP/SL
            base_df = self.data_manager.load_symbol_data(symbol)
            current_time = self.time_manager.current_time

            # Look ahead for TP/SL triggers
            future_data = base_df[base_df.index > current_time]

            execution_result = {
                "triggered": False,
                "trigger_type": None,
                "trigger_price": None,
                "trigger_timestamp": None,
                "pnl": 0.0,
                "execution_time": current_time.isoformat()
            }

            # Check each future candle for TP/SL
            for timestamp, candle in future_data.iterrows():
                high = candle['high']
                low = candle['low']
                close = candle['close']

                # Check TP/SL conditions
                if position.take_profit_price:
                    if position.side.value == "LONG" and high >= position.take_profit_price:
                        # TP triggered for long position
                        execution_result.update({
                            "triggered": True,
                            "trigger_type": "TP",
                            "trigger_price": position.take_profit_price,
                            "trigger_timestamp": timestamp.isoformat(),
                            "pnl": (position.take_profit_price - position.entry_price) * position.quantity * position.leverage
                        })
                        break
                    elif position.side.value == "SHORT" and low <= position.take_profit_price:
                        # TP triggered for short position
                        execution_result.update({
                            "triggered": True,
                            "trigger_type": "TP",
                            "trigger_price": position.take_profit_price,
                            "trigger_timestamp": timestamp.isoformat(),
                            "pnl": (position.entry_price - position.take_profit_price) * position.quantity * position.leverage
                        })
                        break

                if position.stop_loss_price:
                    if position.side.value == "LONG" and low <= position.stop_loss_price:
                        # SL triggered for long position
                        execution_result.update({
                            "triggered": True,
                            "trigger_type": "SL",
                            "trigger_price": position.stop_loss_price,
                            "trigger_timestamp": timestamp.isoformat(),
                            "pnl": (position.stop_loss_price - position.entry_price) * position.quantity * position.leverage
                        })
                        break
                    elif position.side.value == "SHORT" and high >= position.stop_loss_price:
                        # SL triggered for short position
                        execution_result.update({
                            "triggered": True,
                            "trigger_type": "SL",
                            "trigger_price": position.stop_loss_price,
                            "trigger_timestamp": timestamp.isoformat(),
                            "pnl": (position.entry_price - position.stop_loss_price) * position.quantity * position.leverage
                        })
                        break

            # If no TP/SL triggered, calculate current PnL
            if not execution_result["triggered"]:
                current_price = self.data_manager.get_current_price(symbol, current_time)
                if current_price:
                    if position.side.value == "LONG":
                        pnl = (current_price - position.entry_price) * position.quantity * position.leverage
                    else:
                        pnl = (position.entry_price - current_price) * position.quantity * position.leverage

                    execution_result["pnl"] = pnl

            return execution_result

        except Exception as e:
            logger.error(f"Error in immediate execution simulation: {e}")
            return None

    def run(self, host: str = None, port: int = None):
        """Run the API server"""
        host = host or settings.API_HOST
        port = port or settings.API_PORT

        logger.info(f"Starting BingX Emulator API on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)

# Global API instance
api_server = BingXEmulatorAPI()