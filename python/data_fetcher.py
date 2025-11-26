import MetaTrader5 as mt5
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class MT5DataFetcher: #Fetches historical data from MetaTrader 5.
   
    
    def __init__(self):#Initialize MT5 connection.
        self.is_connected = False
        self._connect()
    

    def _connect(self):#Establish connection to MT5.
        if not mt5.initialize():
            logger.error("Failed to initialize MT5")
            return False
        
        self.is_connected = True
        logger.info("Successfully connected to MT5")
        
        
        terminal_info = mt5.terminal_info()# Log MT5 info
        if terminal_info:
            logger.info(f"MT5 Terminal: {terminal_info.company}, Build: {terminal_info.build}")
        
        return True
    

    def disconnect(self):#Disconnect from MT5.
        if self.is_connected:
            mt5.shutdown()
            self.is_connected = False
            logger.info("Disconnected from MT5")
    

    def fetch_ohlc_data(self, symbol, timeframe=mt5.TIMEFRAME_H1, count=100):
        # Fetch OHLC data for a symbol.
        if not self.is_connected:
            logger.warning("Not connected to MT5, attempting reconnection...")
            if not self._connect():
                raise ConnectionError("Failed to connect to MT5")
        
        logger.info(f"Fetching {count} candles for {symbol}...")
        
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)# Fetch rates
        
        if rates is None or len(rates) == 0:
            error = mt5.last_error()
            logger.error(f"Failed to fetch data for {symbol}. Error: {error}")
            
            # Try alternative symbol names
            alternative_symbols = self._get_alternative_symbols(symbol)
            for alt_symbol in alternative_symbols:
                logger.info(f"Trying alternative symbol: {alt_symbol}")
                rates = mt5.copy_rates_from_pos(alt_symbol, timeframe, 0, count)
                if rates is not None and len(rates) > 0:
                    logger.info(f"Successfully fetched data using {alt_symbol}")
                    symbol = alt_symbol
                    break
            
            if rates is None or len(rates) == 0:
                raise ValueError(f"Could not fetch data for {symbol} or alternatives")
        
        
        df = pd.DataFrame(rates)# Convert to DataFrame
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        logger.info(f"Successfully fetched {len(df)} candles for {symbol}")
        logger.debug(f"Date range: {df['time'].min()} to {df['time'].max()}")
        
        return df[['time', 'open', 'high', 'low', 'close']]
    

    def _get_alternative_symbols(self, symbol):
       #Get alternative symbol names for common forex pairs and indices.

        alternatives = {
            'DXY': ['USDX', 'DXY.f', 'USDOLLAR', 'US30.cash', 'DX-Y.NYB'],
            'EURUSD': ['EURUSDm', 'EURUSD.f', 'EUR/USD'],
            'GBPUSD': ['GBPUSDm', 'GBPUSD.f', 'GBP/USD'],
            'USDJPY': ['USDJPYm', 'USDJPY.f', 'USD/JPY']}
        
        return alternatives.get(symbol, [])
    

    def get_available_symbols(self):
        if not self.is_connected:
            if not self._connect():
                return []
        
        symbols = mt5.symbols_get()
        if symbols is None:
            logger.error("Failed to get symbols list")
            return []
        
        symbol_names = [s.name for s in symbols]
        logger.info(f"Found {len(symbol_names)} available symbols")
        return symbol_names
    

    def symbol_exists(self, symbol):#Checking if a symbol exists in MT5.
       
        symbol_info = mt5.symbol_info(symbol)
        return symbol_info is not None


def get_correlation_data(symbol1='EURUSD', symbol2='DXY', count=100):
    # Fetch data for two symbols for correlation analysis.
    fetcher = MT5DataFetcher()
    
    try:
        # Fetch data for both symbols
        df1 = fetcher.fetch_ohlc_data(symbol1, count=count)
        df2 = fetcher.fetch_ohlc_data(symbol2, count=count)
        
        logger.info(f"Data fetch complete - {symbol1}: {len(df1)} candles, {symbol2}: {len(df2)} candles")
        
        return df1, df2
    
    except Exception as e:
        logger.error(f"Error fetching correlation data: {str(e)}", exc_info=True)
        raise
    
    finally:
        fetcher.disconnect()

if __name__ == '__main__':# Test the data fetcher
    logging.basicConfig(level=logging.INFO)
    print("Testing MT5 Data Fetcher...")
    print("=" * 60)
    
    fetcher = MT5DataFetcher()
    print("\nChecking DXY availability...")# Test symbol availability
    if fetcher.symbol_exists('DXY'):
        print("✓ DXY found")
    else:
        print("✗ DXY not found, checking alternatives...")
        available = fetcher.get_available_symbols()
        dxy_alternatives = [s for s in available if 'DX' in s or 'USD' in s]
        print(f"Possible alternatives: {dxy_alternatives[:5]}")
    
    print("\nFetching EURUSD data...")# Test data fetch
    try:
        df = fetcher.fetch_ohlc_data('EURUSD', count=10)
        print("✓ EURUSD data:")
        print(df.head())
    except Exception as e:
        print(f"✗ Error: {e}")
        
    fetcher.disconnect()
    print("\n" + "=" * 60)
    print("Test complete")