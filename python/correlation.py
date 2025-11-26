import pandas as pd
import logging
from data_fetcher import get_correlation_data

logger = logging.getLogger(__name__)

# Correlation thresholds
CORRELATION_THRESHOLD_POSITIVE = 0.5
CORRELATION_THRESHOLD_NEGATIVE = -0.5

def calculate_correlation(df1, df2, method='close'):#correlation calculating
  
    if len(df1) == 0 or len(df2) == 0:
        logger.error("Empty dataframes provided for correlation")
        raise ValueError("Cannot calculate correlation on empty data")
    
    df1_copy = df1.copy()# Align data by merging on time
    df2_copy = df2.copy()
    df1_copy = df1_copy.rename(columns={method: f'{method}_1'})
    df2_copy = df2_copy.rename(columns={method: f'{method}_2'})
    
    merged = pd.merge(df1_copy[['time', f'{method}_1']], 
                     df2_copy[['time', f'{method}_2']], 
                     on='time', 
                     how='inner')
    
    if len(merged) < 2:
        logger.error("Insufficient aligned data points for correlation")
        raise ValueError("Not enough aligned data points")
    
    
    correlation = merged[f'{method}_1'].corr(merged[f'{method}_2'])# Calculate correlation
    logger.info(f"Calculated correlation: {correlation:.4f} (using {len(merged)} aligned data points)")
    return correlation

def validate_signal(signal, symbol='EURUSD', dxy_symbol='DXY'):
   #Validate a trading signal using EURUSD-DXY correlation.

    logger.info(f"Validating {signal} signal for {symbol} vs {dxy_symbol}")
    try:
        
        logger.info("Fetching market data...")# Fetch data for both symbols
        df_eurusd, df_dxy = get_correlation_data(symbol, dxy_symbol, count=100)

        # Calculate correlation
        correlation = calculate_correlation(df_eurusd, df_dxy, method='close')
        # Validate signal based on correlation
        is_valid = False
        message = ""
        
        if signal == 'BUY':
            # BUY is valid when correlation is negative (EURUSD up, DXY down)
            if correlation < CORRELATION_THRESHOLD_NEGATIVE:
                is_valid = True
                message = f"Strong inverse correlation ({correlation:.4f}) confirms BUY signal"
            else:
                message = f"Correlation ({correlation:.4f}) does not support BUY signal (need < {CORRELATION_THRESHOLD_NEGATIVE})"
        
        elif signal == 'SELL':
            # SELL is valid when correlation is positive (EURUSD down, DXY up)
            if correlation > CORRELATION_THRESHOLD_POSITIVE:
                is_valid = True
                message = f"Strong positive correlation ({correlation:.4f}) confirms SELL signal"
            else:
                message = f"Correlation ({correlation:.4f}) does not support SELL signal (need > {CORRELATION_THRESHOLD_POSITIVE})"
        
        else:
            message = f"Invalid signal type: {signal}"
            logger.error(message)
        
        status = "VALID" if is_valid else "REJECT"
        logger.info(f"Validation result: {status} - {message}")
        
        return {
            "status": status,
            "correlation": round(correlation, 4),
            "message": message,
            "data_points": len(df_eurusd)}
        
    
    except Exception as e:
        error_message = f"Error during validation: {str(e)}"
        logger.error(error_message, exc_info=True)
        
        return {
            "status": "ERROR",
            "correlation": None,
            "message": error_message}
        

def get_correlation_matrix(symbols, count=100):
   # Calculate correlation matrix for multiple symbols.

    from data_fetcher import MT5DataFetcher
    fetcher = MT5DataFetcher()
    
    try:
        # Fetch data for all symbols
        data_dict = {}
        for symbol in symbols:
            try:
                df = fetcher.fetch_ohlc_data(symbol, count=count)
                data_dict[symbol] = df['close'].values
            except Exception as e:
                logger.error(f"Failed to fetch data for {symbol}: {e}")
                continue
        
        if len(data_dict) < 2:
            raise ValueError("Need at least 2 symbols with valid data")
        
        # Create DataFrame and calculate correlation
        df_combined = pd.DataFrame(data_dict)
        correlation_matrix = df_combined.corr()
        
        logger.info("Correlation matrix calculated successfully")
        return correlation_matrix
    
    finally:
        fetcher.disconnect()

if __name__ == '__main__':# Test the correlation calculator
    
    logging.basicConfig(level=logging.INFO)
    print("Testing Correlation Calculator...")
    print("=" * 60)
    print("\nTest 1: Validating BUY signal")# Testing BUY signal validation
    result = validate_signal('BUY', 'EURUSD', 'DXY')

    print(f"Status: {result['status']}")
    print(f"Correlation: {result.get('correlation', 'N/A')}")
    print(f"Message: {result['message']}")
    
    
    print("\nTest 2: Validating SELL signal")# Testing SELL signal validation
    result = validate_signal('SELL', 'EURUSD', 'DXY')
    print(f"Status: {result['status']}")
    print(f"Correlation: {result.get('correlation', 'N/A')}")
    print(f"Message: {result['message']}")
    print("\n" + "=" * 60)
    print("Test complete")