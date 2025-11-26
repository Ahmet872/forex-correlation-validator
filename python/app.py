from flask import Flask, request, jsonify
import logging
from correlation import validate_signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

@app.route('/validate', methods=['POST'])
def validate():

    try:
        # Parse request
        data = request.get_json()
        
        if not data:
            logger.error("No JSON data received")
            return jsonify({
                "status": "ERROR",
                "message": "No JSON data provided"
            }), 400
        
        signal = data.get('signal')
        symbol = data.get('symbol')
        
        logger.info(f"Received validation request - Signal: {signal}, Symbol: {symbol}")
        
        # Validate input
        if not signal or not symbol:
            logger.error("Missing signal or symbol in request")
            return jsonify({
                "status": "ERROR",
                "message": "Missing 'signal' or 'symbol' field"}), 400
            
        
        if signal not in ['BUY', 'SELL']:
            logger.error(f"Invalid signal: {signal}")
            return jsonify({
                "status": "ERROR",
                "message": "Signal must be 'BUY' or 'SELL'"}), 400
            
        
        # Validate signal using correlation
        result = validate_signal(signal, symbol)
        logger.info(f"Validation result: {result['status']}, Correlation: {result.get('correlation', 'N/A')}")
    
        return jsonify(result),200
    
    except Exception as e:
        logger.error(f"Error processing validation request: {str(e)}", exc_info=True)
        return jsonify({
            "status": "ERROR",
            "message": f"Internal server error: {str(e)}"}), 500
        

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "OK",
        "message": "Correlation validation server is running"}), 200
    

@app.route('/', methods=['GET'])
def home():
    """Root endpoint with API information."""
    return jsonify({
        "service": "Correlation-Based Signal Validator",
        "version": "1.0.0",
        "endpoints": {
            "/validate": "POST - Validate trading signals",
            "/health": "GET - Health check"}}), 200
        
def main():#Start the Flask server.
    logger.info("=" * 60)
    logger.info("Starting Correlation Validation Server")
    logger.info("=" * 60)
    logger.info("Server will listen on: http://127.0.0.1:5000")
    logger.info("Validation endpoint: http://127.0.0.1:5000/validate")
    logger.info("Health check: http://127.0.0.1:5000/health")
    logger.info("=" * 60)
    
    
    app.run(# Run Flask app
        host='127.0.0.1',
        port=5000,
        debug=False,
        use_reloader=False)
    
    
if __name__ == '__main__':
    main()