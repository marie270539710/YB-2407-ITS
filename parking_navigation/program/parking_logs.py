import serial
import sqlite3
from datetime import datetime

# 🔹 Open Serial connection (Check COM port in Arduino IDE > Tools > Port)
ser = serial.Serial('/dev/cu.usbserial-1120', 9600)  # Change 'COM3' to your port on Windows, or '/dev/ttyUSB0' on Linux/Mac

# 🔹 Connect to SQLite database (creates file if not exists)
conn = sqlite3.connect('/Users/marie/AquilaDrive/Yoobee/MSE806/YB-2407-ITS/parking_navigation/db.sqlite3')
cursor = conn.cursor()

# 🔹 Create logs table (if not exists)
# tablename = "available_slots_"+datetime.now().strftime("%Y%m%d");
# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS """+tablename+""" (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         log_value INTEGER,
#         timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
#     )
# """)
# conn.commit()

tablename = "navigation_availableslot"

# 🔹 Read Serial and save to database
while True:
    try:
        data = ser.readline().decode('utf-8').strip()  # Read Serial data
        if data.startswith("AVAILABLE: "):
            value = data.split("AVAILABLE: ")[1]  # Extract numeric value
            
            # 🔹 Insert into SQLite database
            cursor.execute("INSERT INTO " + tablename + " (slots, timestamp) VALUES (?, CURRENT_TIMESTAMP)", (value,))
            conn.commit()
            
            print(f"Saved to SQLite: {value}")  # Debugging output
    except Exception as e:
        print("Error:", e)
