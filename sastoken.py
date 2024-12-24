import paho.mqtt.client as mqtt

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

# Start the loop
client.loop_start()

# Publish sample telemetry data
client.publish(mqtt_topic, '{"temperature": 25}')

# Stop the loop after use
client.loop_stop()
client.disconnect()
