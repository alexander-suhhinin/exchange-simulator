# 🎯 Multiple Symbols Support Extension

## ✅ What's Implemented

### 1. **Automatic Symbol Discovery**
- Dynamic detection of available trading pairs from `klines_data/` folder
- Validation of data availability for each symbol
- Support for 38 trading pairs including major cryptocurrencies and memecoins

### 2. **Extended Configuration**
- Updated `emulator_config.py` with comprehensive symbol list
- Automatic symbol validation in API endpoints
- Error handling for unsupported symbols

### 3. **API Improvements**
- New `/api/v1/symbols` endpoint for getting available symbols
- Enhanced error responses for invalid symbols
- Improved symbol validation in all trading endpoints

## 📊 Results

### Available Trading Pairs: **38 Symbols**

**Major Cryptocurrencies:**
- BTC-USDT, ETH-USDT, BNB-USDT, XRP-USDT, ADA-USDT
- SOL-USDT, AVAX-USDT, LTC-USDT, ATOM-USDT, UNI-USDT
- LINK-USDT, TRX-USDT, NEAR-USDT, FTM-USDT, APT-USDT

**DeFi & Layer 2:**
- OP-USDT, ARB-USDT, SNX-USDT, AAVE-USDT, SUI-USDT
- STRK-USDT, TIA-USDT, SEI-USDT, JTO-USDT, MANTA-USDT

**Gaming & Metaverse:**
- GALA-USDT, SAND-USDT, PEOPLE-USDT, WLD-USDT

**Memecoins:**
- DOGE-USDT, SHIB-USDT, 1000PEPE-USDT, FLOKI-USDT
- 1000BONK-USDT, WIF-USDT, TURBO-USDT, MEME-USDT
- 1000CHEEMS-USDT, 1000CAT-USDT

**Other:**
- INJ-USDT

### Symbol Discovery Process:
1. **Scan Directory**: Check `klines_data/{symbol}/` folders
2. **Validate Data**: Ensure `{date}/1m_data.csv` files exist
3. **Date Check**: Verify data for 2023-12-19 or 2023-12-20
4. **API Integration**: Add to available symbols list

### API Response Example:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "symbols": [
      "ADA-USDT", "BTC-USDT", "ETH-USDT", "SOL-USDT",
      "DOGE-USDT", "1000PEPE-USDT", "FLOKI-USDT"
    ],
    "count": 38
  }
}
```

## 🧪 Testing

### Successfully Tested:
- ✅ Symbol discovery and validation
- ✅ Trading on multiple pairs
- ✅ Error handling for invalid symbols
- ✅ API endpoint responses
- ✅ Data loading for different symbols

### Test Examples:

```python
# Get available symbols
response = requests.get("http://localhost:8000/api/v1/symbols")
symbols = response.json()["data"]["symbols"]

# Get candles for BTC
klines = requests.get("http://localhost:8000/openApi/swap/v3/quote/klines?symbol=BTC-USDT&interval=5m&limit=100")

# Create order on ETH
order_data = {
    "symbol": "ETH-USDT",
    "side": "BUY",
    "positionSide": "LONG",
    "type": "MARKET",
    "quantity": 0.1
}
response = requests.post("http://localhost:8000/openApi/swap/v2/trade/order", json=order_data)
```

## 📁 Data Structure

```
klines_data/
├── ADA-USDT/
│   ├── 2023-12-19/
│   │   └── 1m_data.csv
│   └── 2023-12-20/
│       └── 1m_data.csv
├── BTC-USDT/
│   ├── 2023-12-19/
│   │   └── 1m_data.csv
│   └── 2023-12-20/
│       └── 1m_data.csv
├── ETH-USDT/
│   ├── 2023-12-19/
│   │   └── 1m_data.csv
│   └── 2023-12-20/
│       └── 1m_data.csv
└── ... (35 more pairs)
```

### CSV Data Format:
```csv
time,open,high,low,close,volume
1703001600000,0.59885988,0.59945994,0.59874012,0.59945994,1234567.89
1703001660000,0.59945994,0.60005988,0.59945994,0.60005988,2345678.90
```

## 🔧 Technical Details

### Symbol Validation
```python
def validate_symbol(self, symbol: str) -> bool:
    """
    Validate if symbol has available data

    Args:
        symbol: Trading pair symbol (e.g., 'BTC-USDT')

    Returns:
        bool: True if symbol has data, False otherwise
    """
    # Check data in 2023-12-19 or 2023-12-20
    for date in ['2023-12-19', '2023-12-20']:
        data_path = self.data_path / symbol / date / '1m_data.csv'
        if data_path.exists():
            return True
    return False
```

### Automatic Discovery
```python
def get_available_symbols(self) -> List[str]:
    """
    Get list of all available trading symbols

    Returns:
        List[str]: List of available symbol names
    """
    symbols = []
    for symbol_dir in self.data_path.iterdir():
        if symbol_dir.is_dir():
            symbol = symbol_dir.name
            if self.validate_symbol(symbol):
                symbols.append(symbol)
    return sorted(symbols)
```

### API Integration
- **Endpoint**: `GET /api/v1/symbols`
- **Validation**: All trading endpoints validate symbol before processing
- **Error Response**: 404 for invalid symbols with descriptive message

## 🚀 Ready to Use!

### To Add New Pair:
1. Create folder: `klines_data/NEW-SYMBOL/`
2. Add date folders: `2023-12-19/` and `2023-12-20/`
3. Place `1m_data.csv` files with OHLCV data
4. Restart emulator - symbol will be automatically detected

### To Use:
1. Get available symbols: `GET /api/v1/symbols`
2. Trade on any supported pair
3. All existing functionality works with new symbols
4. Automatic validation prevents errors

**The emulator now supports 38 trading pairs with full functionality!** 🎉