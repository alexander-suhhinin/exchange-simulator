# Tests

This directory contains all test files for the BingX Emulator project.

## Test Files

### `test_api.py`
- **Purpose**: Basic API functionality tests
- **Tests**: Health check, klines data, order creation, positions
- **Usage**: `python tests/test_api.py`

### `test_symbols.py`
- **Purpose**: Symbol discovery and validation tests
- **Tests**: Available symbols endpoint, symbol validation
- **Usage**: `python tests/test_symbols.py`

### `test_multiple_symbols.py`
- **Purpose**: Multi-symbol trading tests
- **Tests**: Trading on different pairs, symbol switching
- **Usage**: `python tests/test_multiple_symbols.py`

### `test_immediate_execution.py`
- **Purpose**: Immediate order execution with TP/SL simulation
- **Tests**: Order creation with immediate execution, TP/SL triggering
- **Usage**: `python tests/test_immediate_execution.py`

## Running Tests

### Run All Tests
```bash
# From project root
python -m pytest tests/

# Or run individual files
python tests/test_api.py
python tests/test_symbols.py
python tests/test_multiple_symbols.py
python tests/test_immediate_execution.py
```

### Prerequisites
1. Start the emulator server: `python main.py`
2. Ensure the server is running on `http://localhost:8000`
3. Make sure you have the required dependencies installed

### Test Environment
- **Server URL**: `http://localhost:8000`
- **Default Symbol**: `ADA-USDT`
- **Test Data**: Historical data from `klines_data/` folder

## Test Structure

Each test file follows a similar pattern:
1. **Setup**: Import required modules and define test data
2. **Execution**: Make API calls to the emulator
3. **Validation**: Check responses and verify expected behavior
4. **Cleanup**: Reset state if needed

## Adding New Tests

When adding new test files:
1. Follow the naming convention: `test_*.py`
2. Include proper error handling
3. Add descriptive comments
4. Update this README with test description

## Notes

- Tests require the emulator server to be running
- Some tests may modify the emulator state
- Consider clearing state between test runs if needed
- Tests use real historical data for realistic simulation