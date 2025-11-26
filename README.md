# Forex Signal Validation System

A professional forex trading system that combines MetaTrader 5 with Python to validate trading signals using correlation analysis between EURUSD and the US Dollar Index (DXY).

## What Does This Do?

Most forex trading bots rely solely on technical indicators like moving averages and RSI, which often generate false signals. This system adds a validation layer by analyzing the correlation between EURUSD and DXY before executing trades.

The MetaTrader 5 Expert Advisor identifies potential trades using EMA and RSI indicators, then sends the signal to a Python server. The server analyzes the correlation between EURUSD and DXY over the last 100 candles. Only when this correlation confirms the signal direction does the system actually place the trade.

## Why This Approach Works

The relationship between EURUSD and the US Dollar Index is fundamental to forex trading. When DXY strengthens, EURUSD typically weakens, and vice versa. By measuring this correlation in real-time, we filter out technical signals that don't align with the broader market structure.

## Technical Overview

### Signal Generation (MT5)

The Expert Advisor monitors EURUSD using:
* EMA(50) for trend direction
* RSI(14) for overbought/oversold conditions

### Validation Logic (Python)

The Python server calculates the Pearson correlation coefficient between EURUSD and DXY:
* **BUY Signal**: Validated if correlation < -0.5 (strong inverse relationship)
* **SELL Signal**: Validated if correlation > 0.5 (strong positive relationship)
* **Rejection**: Any correlation between -0.5 and 0.5 results in signal rejection

### Trade Execution

Only validated signals result in actual trades.

## Project Structure

```
forex-correlation-validator/
│
├── mt5/
│   └── CorrelationEA.mq5        # Expert Advisor for signal generation
│
├── python/
│   ├── app.py                   # Flask server handling validation requests
│   ├── data_fetcher.py          # Fetches historical data from MT5
│   ├── correlation.py           # Calculates and validates correlations
│   └── requirements.txt         # Python package dependencies
│
└── README.md
```

## Installation

### Step 1: Create Project Structure

```bash
mkdir forex-correlation-validator
cd forex-correlation-validator
mkdir mt5 python
```

### Step 2: Set Up Python Environment

```bash
cd python
pip install -r requirements.txt
```

### Step 3: Configure MetaTrader 5

1. Open MetaEditor in MT5 (press F4)
2. Open the provided `CorrelationEA.mq5`
3. Compile the EA (press F7)
4. Ensure there are no compilation errors

### Step 4: Verify DXY Symbol

Different brokers provide DXY under different symbol names (DXY, USDX, DX, GDXY). Check available symbols:

```bash
python data_fetcher.py
```

This shows which DXY symbols are available and how many candles align with EURUSD data. Use the symbol with the highest alignment.

## Usage

### Starting the System

1. **Start the Python server:**

```bash
cd python
python app.py
```

Server will start on `http://127.0.0.1:5000`

2. **Load the EA in MT5:**
   * Open MT5 platform
   * Navigate to Navigator panel
   * Drag CorrelationEA onto an EURUSD chart
   * Enable AutoTrading

### Signal Flow Example

**MT5 generates signal:**
```
Signal generated: BUY
Sending to Python for validation...
```

**Python validates:**
```
Received signal: BUY for EURUSD
Correlation: -0.68
Status: VALID - Strong inverse correlation confirms BUY signal
```

**MT5 executes:**
```
Validation received: VALID
Executing BUY trade on EURUSD...
```

## API Reference

### Endpoint: POST /validate

**Request:**
```json
{
  "signal": "BUY",
  "symbol": "EURUSD"
}
```

**Response (Valid):**
```json
{
  "status": "VALID",
  "correlation": -0.68,
  "message": "Strong inverse correlation confirms BUY signal"
}
```

**Response (Rejected):**
```json
{
  "status": "REJECT",
  "correlation": -0.23,
  "message": "Correlation too weak to validate signal"
}
```

## Testing

Before running with real money:

1. Start `app.py` and verify it's listening on port 5000
2. Load the EA on a demo account
3. Monitor Python logs for correlation calculations
4. Confirm rejected signals don't result in trades
5. Paper trade for at least a week before going live

## Important Notes

### DXY Symbol Availability

Not all forex brokers provide the US Dollar Index symbol. Some offer it under alternative names (USDX, DX, GDXY), while others don't offer it at all. Run `data_fetcher.py` to check your broker's available symbols and their data quality.

### Data Alignment

The correlation calculation only works when both EURUSD and DXY have data for the same time periods. If your DXY symbol has gaps or different trading hours, the aligned candle count will be low, resulting in unreliable correlations.

### Broker Considerations

Different brokers have different data sources, liquidity providers, time zones, and execution speeds. All of these can affect correlation accuracy. What works on one broker might need adjustment on another.

### Risk Management

This system improves signal quality but doesn't eliminate risk. Always use appropriate position sizing, stop losses, maximum loss limits, and proper testing before live trading.

## Technologies Used

* **MetaTrader 5**: Trading platform and Expert Advisor development
* **MQL5**: Programming language for MT5 automation
* **Python 3.8+**: Core validation logic and server
* **Flask**: Web framework for API endpoints
* **MetaTrader5 Python Package**: Bridge between Python and MT5
* **NumPy**: Numerical computations and correlation calculations
* **Pandas**: Data manipulation and time series analysis
* **Visual Studio Code**: Code editor with Python and MQL5 extensions
* **Claude (Anthropic)**: AI assistance for code review and documentation
* **Git**: Version control

## Additional Resources

### Recommended Reading

* MetaTrader 5 Python Integration Guide
* Pearson Correlation Coefficient in Financial Markets
* Flask API Best Practices
* MQL5 HTTP Request Documentation

### Troubleshooting

If you encounter issues:
1. Check Python logs for detailed validation information
2. Verify your DXY symbol is available and has sufficient data
3. Ensure both MT5 and Python are running simultaneously
4. Always test with a demo account first

## Disclaimer

This system is provided for educational purposes. Forex trading carries substantial risk of loss. Past performance doesn't guarantee future results. Always test thoroughly on a demo account before risking real capital.

## License

This project is open source and available for personal and educational use. Commercial use requires explicit permission.

## Contributing

Contributions are welcome! If you've found a bug, have a feature suggestion, or want to improve the documentation, feel free to open an issue or submit a pull request.

---

**Built with a focus on reliability, transparency, and real market relationships.**