import serial
import pyodbc
import time

# Arduino Serial Port Configuration
SERIAL_PORT = 'COM3'  # Change this to your correct serial port (e.g., /dev/ttyUSB0 on Linux)
BAUD_RATE = 9600      # Ensure this matches your Arduino baud rate

# Azure SQL Database Configuration
SQL_SERVER = 'iotlora.database.windows.net'
SQL_DATABASE = 'iots'
SQL_USERNAME = 'iot'
SQL_PASSWORD = 'Laharinadh@2003'
SQL_DRIVER = '{ODBC Driver 17 for SQL Server}'  # Ensure the correct driver is installed

# Establish connection to Azure SQL Database
def connect_to_sql():
    try:
        connection = pyodbc.connect(
            f'DRIVER={SQL_DRIVER};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};UID={SQL_USERNAME};PWD={SQL_PASSWORD};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
        )
        print("Connected to Azure SQL Database")
        return connection
    except Exception as e:
        print(f"Error connecting to Azure SQL Database: {e}")
        return None

# Insert data into the Azure SQL Database
def insert_data(connection, data_value):
    try:
     cursor = connection.cursor()
     query = """INSERT INTO Data (data, Timestamp) VALUES (?, ?)"""
     data_value = "Your data here"  # Replace this with the actual data you want to insert
     timestamp = time.strftime('%Y-%m-%d %H:%M:%S')  # Current timestamp
     cursor.execute(query, (data_value, timestamp))
     connection.commit()
    print("Data inserted successfully")
    except Exception as e:
     print(f"Error inserting data: {e}")

# Main function to read Serial Monitor and send data to SQL
def read_serial_and_send_to_sql():
    try:
        # Initialize serial communication
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Listening to serial port: {SERIAL_PORT}")
        
        # Establish SQL connection
        sql_connection = connect_to_sql()
        
        if sql_connection is None:
            return
        
        while True:
            # Read data from Arduino's Serial Monitor
            if ser.in_waiting > 0:
                serial_data = ser.readline().decode('utf-8').strip()
                print(f"Received from Serial Monitor: {serial_data}")
                
                try:
                    # Assuming the serial data is a single float value representing "data"
                    data_value = float(serial_data)
                    
                    # Insert data into Azure SQL Database
                    insert_data(sql_connection, data_value)
                except Exception as parse_error:
                    print(f"Error parsing data: {parse_error}")
    except Exception as e:
        print(f"Error reading from Serial Monitor: {e}")
    finally:
        if sql_connection:
            sql_connection.close()
        ser.close()

if __name__ == "__main__":
    read_serial_and_send_to_sql()
