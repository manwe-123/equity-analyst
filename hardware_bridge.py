import serial
import time

class ArduinoBridge:
    def __init__(self, port='/dev/tty.usbmodem14101', baudrate=9600):
        """
        Initialize the serial connection. 
        Note: '/dev/tty.usbmodem...' is the standard port format for Mac. 
        When you plug in your Arduino, you will find its exact port name in the Arduino IDE.
        """
        self.port = port
        self.baudrate = baudrate
        self.is_connected = False
        self.serial_connection = None

        self._try_connect()

    def _try_connect(self):
        """Attempt to connect to the Arduino. Fail gracefully if not found."""
        try:
            # Try to open the serial port
            self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=2)
            time.sleep(2) # Give the Arduino a second to reset
            self.is_connected = True
            print(f"🔌 Connected to Arduino on {self.port}")
        except serial.SerialException:
            # This is the graceful fallback!
            self.is_connected = False
            print("⚠️ Arduino not found. Running in MOCK mode (printing to console).")

    def send_to_lcd(self, sentiment, tickers_list):
        """
        Formats the data and sends it to the Arduino.
        """
        # Format the data into a simple string protocol. 
        # Example: "SENTIMENT:BULLISH|TICKERS:AAPL,NVDA,TSM\n"
        tickers_str = ",".join(tickers_list) if tickers_list else "NONE"
        payload = f"SENTIMENT:{sentiment.upper()}|TICKERS:{tickers_str}\n"

        if self.is_connected:
            # Send the actual bytes over the USB cable
            self.serial_connection.write(payload.encode('utf-8'))
            print(f"📡 Sent to Arduino LCD: {payload.strip()}")
        else:
            # Mock mode: Just print what WOULD have been sent
            print(f"🖥️ [MOCK LCD DISPLAY] -> Sentiment: {sentiment.upper()} | Top Tickers: {tickers_str}")

    def close(self):
        """Clean up the connection when we are done."""
        if self.is_connected and self.serial_connection.is_open:
            self.serial_connection.close()