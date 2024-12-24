import serial
import time
from azure.iot.device import IoTHubDeviceClient, Message

# Replace with your IoT Hub device connection string
CONNECTION_STRING = "HostName=Loragateway.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=0+mcQcw+RGTTdyflm9bwhZSRgg40CeSz+AIoTAkz1o0="

# Set up the IoT Hub client
def create_client():
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    return client

# Function to send data to Azure IoT Hub
def send_to_azure(client, bpm):
    message = Message(f'{{"BPM": {bpm}}}')
    client.send_message(message)
    print(f"Sent message: {message}")

# Set up serial communication with Arduino
ser = serial.Serial('COM3', 9600)  # Change 'COM3' to the appropriate port

def main():
    client = create_client()
    print("Reading from Arduino and sending data to Azure IoT Hub...")
    
    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                if "BPM:" in line:
                    bpm_value = line.split(":")[1].strip()
                    print(f"Received BPM: {bpm_value}")
                    send_to_azure(client, bpm_value)
                    time.sleep(2)  # Pause before the next read

    except KeyboardInterrupt:
        print("Program stopped.")
    finally:
        client.shutdown()

if __name__ == '__main__':
    main()
