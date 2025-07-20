# BingX Emulator

Full-featured BingX cryptocurrency exchange emulator for testing trading bots on historical data.

## 🎯 Features

- ✅ **BingX API Compatibility** - all major endpoints
- ✅ **Historical Data** - OHLCV 1-minute candles for 1.5 years
- ✅ **Realistic Trading** - commissions, slippage, leverage
- ✅ **TP/SL Support** - automatic Take Profit and Stop Loss execution
- ✅ **Persistence** - state saving between runs
- ✅ **Detailed Logging** - all trading operations
- ✅ **Time Management** - step-by-step simulation
- ✅ **Configuration** - flexible settings via files

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install fastapi uvicorn pandas numpy
```

### 2. Start Emulator

```bash
python -m src.api.server
```

Server will start on `http://localhost:8000`

### 3. Test API

```bash
python test_api.py
```

## 📊 Project Structure

```
exch-emu/
├── src/
│   ├── api/
│   │   └── server.py              # FastAPI server
│   ├── config/
│   │   ├── settings.py            # Main settings
│   │   └── emulator_config.py     # Emulator configuration
│   ├── data/
│   │   └── manager.py             # Historical data management
│   ├── state/
│   │   └── manager.py             # State persistence
│   ├── time/
│   │   └── manager.py             # Simulation time management
│   ├── trading/
│   │   ├── models.py              # Data models
│   │   ├── balance_manager.py     # Balance management
│   │   └── order_engine.py        # Order execution engine
│   └── utils/
│       ├── logger.py              # Logging
│       └── trade_logger.py        # Trading logging
├── klines_data/                   # Historical data
│   ├── ADA-USDT/                  # Trading pair
│   │   ├── 2023-12-19/            # Date
│   │   │   └── 1m_data.csv        # 1-minute candles
│   │   └── 2023-12-20/            # Another date
│   │       └── 1m_data.csv
│   ├── BTC-USDT/
│   └── ...                        # Other pairs
├── data/                          # Saved state
├── config/                        # Configuration files
├── test_api.py                    # API tests
├── test_symbols.py                # Symbol tests
└── README.md                      # Documentation
```

## 🔌 API Endpoints

### Main BingX Endpoints

#### Get Available Symbols
```http
GET /api/v1/symbols
```

#### Get Candles
```http
GET /openApi/swap/v3/quote/klines?symbol=ADA-USDT&interval=5m&limit=100
```

#### Create Order
```http
POST /openApi/swap/v2/trade/order
Content-Type: application/json

{
    "symbol": "ADA-USDT",
    "side": "BUY",
    "positionSide": "LONG",
    "type": "MARKET",
    "quantity": 100,
    "takeProfit": "{\"stopPrice\": \"0.6\"}",
    "stopLoss": "{\"stopPrice\": \"0.4\"}"
}
```

#### Get Positions
```http
GET /openApi/swap/v2/user/positions
```

#### Get Orders
```http
GET /openApi/swap/v2/trade/openOrders
GET /openApi/swap/v2/trade/allOrders?symbol=ADA-USDT&limit=100
GET /openApi/swap/v2/trade/order?orderId=123
```

#### Cancel Order
```http
DELETE /openApi/swap/v2/trade/order?orderId=123
```

### Additional Endpoints

#### Time Management
```http
GET /api/v1/time/current                    # Current simulation time
POST /api/v1/time/advance                   # Advance time
```

#### State Management
```http
POST /api/v1/state/save                     # Save state
POST /api/v1/state/clear                    # Clear state
```

#### Statistics and Configuration
```http
GET /api/v1/trading/summary                 # Trading statistics
GET /api/v1/config                          # Configuration
POST /api/v1/config/update                  # Update configuration
```

#### Health Check
```http
GET /health                                 # Server status
```

## ⚙️ Configuration

### Main Settings (`src/config/settings.py`)

```python
# Commissions
COMMISSION_RATE = 0.0007  # 0.07%
MIN_COMMISSION = 0.04     # Minimum commission

# Slippage
SLIPPAGE_TIERS = {
    0: 0.0001,      # Up to $100
    100: 0.0005,    # $100-$1000
    1000: 0.001,    # $1000-$10000
    10000: 0.002    # More than $10000
}

# Leverage
DEFAULT_LEVERAGE = 10
MAX_LEVERAGE = 100

# Balance
INITIAL_BALANCE = 1000.0  # USDT
```

### Emulator Configuration (`config/emulator_config.json`)

```json
{
  "simulation": {
    "time_step_minutes": 1,
    "auto_save_interval": 60,
    "enable_logging": true
  },
  "trading": {
    "default_leverage": 10,
    "commission_rate": 0.0007,
    "enable_slippage": true
  },
  "risk_management": {
    "max_position_size": 10000,
    "max_daily_loss": 1000
  }
}
```

## 📈 Trading Features

### Order Types
- **MARKET** - market orders (executed instantly)
- **LIMIT** - limit orders (in development)

### Take Profit / Stop Loss
- Automatic execution when price levels are reached
- Support for LONG and SHORT positions
- Execution at exact trigger price

### Leverage
- Adjustable leverage (default x10)
- Maximum leverage x100
- Automatic margin calculation

### Commissions and Slippage
- Commission 0.07% of volume
- Minimum commission $0.04
- Slippage depends on order volume

## 💾 Persistence

Emulator automatically saves:
- Account balances
- Open positions
- Active orders
- Order history
- Simulation time

Data is saved in the `data/` folder in JSON format.

## 📝 Logging

### Trading Logs (`data/logs/`)
- `trades.jsonl` - order creation, positions
- `executions.jsonl` - order execution
- `errors.jsonl` - trading operation errors

### Example Log
```json
{
  "timestamp": "2023-12-18T23:00:00",
  "type": "order_created",
  "order_id": "123",
  "symbol": "ADA-USDT",
  "side": "BUY",
  "quantity": 100,
  "price": 0.596
}
```

## 🔧 Development

### Adding New Endpoint

1. Add method to `src/api/server.py`
2. Update tests in `test_api.py`
3. Update documentation

### Extending Functionality

- **New Order Types**: modify `src/trading/order_engine.py`
- **Additional Indicators**: add to `src/data/manager.py`
- **New Settings**: update `src/config/settings.py`

## 🧪 Testing

### Running Tests
```bash
python test_api.py
```

### Checking Endpoints
```bash
curl http://localhost:8000/health
curl http://localhost:8000/openApi/swap/v3/quote/klines?symbol=ADA-USDT
```

## 📊 Monitoring

### Trading Statistics
```bash
curl http://localhost:8000/api/v1/trading/summary
```

### Current State
```bash
curl http://localhost:8000/health
```

## 🚨 Limitations

- Only market orders (MARKET)
- Simulation without real market data
- No WebSocket support
- Some trading pairs may have no data

## 📈 Supported Trading Pairs

Emulator automatically discovers available trading pairs in the `klines_data/` folder.
Supported pairs include:

- **ADA-USDT** - Cardano
- **BTC-USDT** - Bitcoin
- **BNB-USDT** - Binance Coin
- **AVAX-USDT** - Avalanche
- **ATOM-USDT** - Cosmos
- **AAVE-USDT** - Aave
- **APT-USDT** - Aptos
- **ARB-USDT** - Arbitrum
- **DOGE-USDT** - Dogecoin
- **1000CAT-USDT** - 1000 Cats
- **1000CHEEMS-USDT** - 1000 Cheems
- **1000PEPE-USDT** - 1000 Pepe

### Adding New Pairs

To add a new trading pair:

1. Create a folder `klines_data/{SYMBOL}/`
2. Add subfolders with dates: `2023-12-19/`, `2023-12-20/`
3. Place the `1m_data.csv` file with OHLCV data
4. Restart the emulator

CSV file format:
```csv
time,open,high,low,close,volume
2023-12-19 00:00:00,0.5994,0.5997,0.5969,0.598,839861.7
2023-12-19 00:01:00,0.598,0.5985,0.5975,0.5982,123456.8
```

## 🔮 Future Plans

- [ ] Support for limit orders
- [ ] WebSocket API
- [ ] More trading pairs
- [ ] Graphical interface
- [ ] Backtesting strategies
- [ ] Export results

## 📞 Support

If you encounter issues:
1. Check logs in `data/logs/`
2. Ensure configuration is correct
3. Check historical data availability

## 📄 License

MIT License - free for any purpose.