import paho.mqtt.client as mqtt
import serial  # Import serial library for reading from Serial Monitor
import json

# Setup Serial port for Arduino (replace COM3 with your port, e.g., /dev/ttyUSB0 for Linux)
ser = serial.Serial('COM3', 9600, timeout=1)  # Adjust port and baud rate as needed

# MQTT and Azure IoT Hub details
broker_address = "Loragateway.azure-devices.net"
mqtt_port = 8883
mqtt_topic = "devices/ra-02/messages/events/"
mqtt_username = "Loragateway.azure-devices.net/ra-02/?api-version=2018-06-30"
sas_token = "SharedAccessSignature sr=Loragateway.azure-devices.net%2Fdevices%2Fra-02&sig=bZap2B60bW9FzXQYVC6ItwSFDa2%2FwKlhUFPjDDjTe1M%3D&se=1730270358"

# Setup MQTT client
client = mqtt.Client("ra-02")
client.username_pw_set(mqtt_username, password=sas_token)
client.tls_set()  # Enable secure connection

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to Azure IoT Hub")
    else:
        print(f"Failed to connect, return code {rc}")

# Connect to Azure IoT Hub
client.on_connect = on_connect
client.connect(broker_address, mqtt_port)

# Start the MQTT loop
client.loop_start()

try:
    while True:
        # Read data from the serial monitor (Arduino)
        if ser.in_waiting > 0:
            serial_data = ser.readline().decode('utf-8').strip()  # Read and decode serial data
            print(f"Data from serial: {serial_data}")

            # Example: Assume serial data is in the format: "temperature:25,pulse:60,latitude:17.729972,longitude:83.318333"
            data_dict = {}
            try:
                # Parse the incoming data
                for item in serial_data.split(","):
                    key, value = item.split(":")
                    data_dict[key] = float(value) if key in ['temperature', 'pulse'] else value  # Keep latitude/longitude as string

                # Convert telemetry data to JSON format
                json_data = json.dumps(data_dict)

                # Publish the data to Azure IoT Hub
                client.publish(mqtt_topic, json_data)
                print(f"Published: {json_data}")

            except ValueError:
                print("Error parsing serial data.")

except KeyboardInterrupt:
    print("Interrupted")

finally:
    # Close the serial connection and stop MQTT loop
    ser.close()
    client.loop_stop()
    client.disconnect()
