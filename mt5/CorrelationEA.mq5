#property copyright "Correlation Validator Bot"
#property version   "1.00"
#property strict

// Input parameters
input int    EMA_Period = 50;           // EMA period for trend
input int    RSI_Period = 14;           // RSI period
input int    RSI_Oversold = 30;         // RSI oversold level
input int    RSI_Overbought = 70;       // RSI overbought level
input double Lot_Size = 0.01;           // Position size
input int    Stop_Loss = 50;            // Stop loss in pips
input int    Take_Profit = 100;         // Take profit in pips
input string Python_URL = "http://localhost:5000/validate"; // Python server URL 

// Global variables 
int ema_handle;
int rsi_handle;
double ema_buffer[];
double rsi_buffer[];
datetime last_bar_time = 0;

int OnInit()

  {Print("Initializing Correlation EA...");
   
   // Create indicator handles
   ema_handle = iMA(_Symbol, PERIOD_CURRENT, EMA_Period, 0, MODE_EMA, PRICE_CLOSE);
   rsi_handle = iRSI(_Symbol, PERIOD_CURRENT, RSI_Period, PRICE_CLOSE);
   
   // Check if handles are valid
   if(ema_handle == INVALID_HANDLE || rsi_handle == INVALID_HANDLE)
   
     {Print("Error creating indicators: ", GetLastError());
      return(INIT_FAILED);}
   
   
   // Set array as series
   ArraySetAsSeries(ema_buffer, true);
   ArraySetAsSeries(rsi_buffer, true);
   
   Print("Correlation EA initialized successfully");
   Print("Monitoring ", _Symbol, " with EMA(", EMA_Period, ") and RSI(", RSI_Period, ")");
   Print("Python validation server: ", Python_URL);
   
   return(INIT_SUCCEEDED);}


void OnDeinit(const int reason)

  {Print("Correlation EA stopped. Reason: ", reason);
   
   // Release indicator handles
   if(ema_handle != INVALID_HANDLE)
      IndicatorRelease(ema_handle);
   if(rsi_handle != INVALID_HANDLE)
      IndicatorRelease(rsi_handle);}


void OnTick()

   // Check for new bar
  {datetime current_bar_time = iTime(_Symbol, PERIOD_CURRENT, 0);
   if(current_bar_time == last_bar_time)
      return;
   
   last_bar_time = current_bar_time;
   
   // Check if we already have an open position
   if(PositionSelect(_Symbol))
   
   {return;}
      
      
   // Copy indicator data
   if(CopyBuffer(ema_handle, 0, 0, 3, ema_buffer) < 3)
   
     {Print("Error copying EMA data: ", GetLastError());
      return;}
   
   
   if(CopyBuffer(rsi_handle, 0, 0, 3, rsi_buffer) < 3)
   
     {Print("Error copying RSI data: ", GetLastError());
      return;}
   
   
   // Generate signal
   string signal = GenerateSignal();
   
   if(signal != "NONE")
   
     {Print("Signal generated: ", signal);
      
      // Validate with Python
      bool is_valid = ValidateWithPython(signal);
      
      if(is_valid)
      
        {Print("Signal validated. Opening trade...");
         ExecuteTrade(signal);}
      
      else
      
        {Print("Signal rejected by correlation validator");}}}
      
   


string GenerateSignal()

  {double current_price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ema_current = ema_buffer[1];
   double rsi_current = rsi_buffer[1];
   
   // BUY Signal: Price above EMA and RSI oversold
   if(current_price > ema_current && rsi_current < RSI_Oversold)
   
     {return "BUY";}
   
   
   // SELL Signal: Price below EMA and RSI overbought
   if(current_price < ema_current && rsi_current > RSI_Overbought)
   
     {return "SELL";}
   
   
   return "NONE";}


bool ValidateWithPython(string signal)

  {char post_data[];
   char result_data[];
   string result_headers;
   
   // Prepare JSON request
   string json_request = StringFormat("{\"signal\":\"%s\",\"symbol\":\"%s\"}", signal, _Symbol);
   StringToCharArray(json_request, post_data, 0, WHOLE_ARRAY, CP_UTF8);
   ArrayResize(post_data, ArraySize(post_data) - 1); // Remove null terminator
   
   Print("Sending validation request to Python server...");
   Print("Request: ", json_request);
   
   // Send HTTP POST request
   int timeout = 5000; // 5 seconds timeout
   ResetLastError();
   
   int res = WebRequest(
      "POST",
      Python_URL,
      "Content-Type: application/json\r\n",
      timeout,
      post_data,
      result_data,
      result_headers);
   
   
   if(res == -1)
     {int error = GetLastError();
      Print("WebRequest failed. Error: ", error);
      
      if(error == 4060)
     
      {Print("URL not allowed. Add ", Python_URL, " to Tools->Options->Expert Advisors->Allow WebRequest");}
         
      return false;}
   
   
   // Parse response
   string result_string = CharArrayToString(result_data, 0, WHOLE_ARRAY, CP_UTF8);
   Print("Validation response: ", result_string);
   
   // Check if status is VALID
   if(StringFind(result_string, "\"status\":\"VALID\"") >= 0 || 
      StringFind(result_string, "\"status\": \"VALID\"") >= 0)
      
     {Print("Validation result: VALID");
      return true;}
      
   
   
   Print("Validation result: REJECT");
   return false;}


void ExecuteTrade(string signal)

  {MqlTradeRequest request;
   MqlTradeResult result;
   ZeroMemory(request);
   ZeroMemory(result);
   
   double price;
   double sl;
   double tp;
   ENUM_ORDER_TYPE order_type;
   
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   int digits = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);
   
   if(signal == "BUY")
   
     {price = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      sl = price - Stop_Loss * point * 10;
      tp = price + Take_Profit * point * 10;
      order_type = ORDER_TYPE_BUY;}
      
   
   else if(signal == "SELL")
     {price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      sl = price + Stop_Loss * point * 10;
      tp = price - Take_Profit * point * 10;
      order_type = ORDER_TYPE_SELL;}
      
   
   else
   
   {return;}

   
   price = NormalizeDouble(price, digits);
   sl = NormalizeDouble(sl, digits);
   tp = NormalizeDouble(tp, digits);
   
   // Fill request structure
   request.action = TRADE_ACTION_DEAL;
   request.symbol = _Symbol;
   request.volume = Lot_Size;
   request.type = order_type;
   request.price = price;
   request.sl = sl;
   request.tp = tp;
   request.deviation = 10;
   request.magic = 123456;
   request.comment = "Correlation EA";
   
   if(!OrderSend(request, result))
     {Print("OrderSend failed. Error: ", GetLastError());
      Print("Result code: ", result.retcode, ", Deal: ", result.deal, ", Order: ", result.order);}
   
   else
     {Print("Trade executed successfully!");
      Print("Order: ", result.order, ", Deal: ", result.deal);
      Print("Volume: ", result.volume, ", Price: ", result.price);}}

// Will be further developed.