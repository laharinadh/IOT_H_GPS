#include <SPI.h>
#include <LoRa.h>

// Define the LoRa pins
#define CS_PIN 10     // Chip select pin
#define RESET_PIN 9   // Reset pin
#define IRQ_PIN 2     // IRQ pin (DIO0)

void setup() {
  Serial.begin(9600);          // Start serial communication for debugging

  // Setup LoRa transceiver module
  Serial.println("LoRa Receiver");
  if (!LoRa.begin(465E6)) {    // Initialize LoRa on 865 MHz for India
    Serial.println("Starting LoRa failed!");
    while (1);
  }
  LoRa.setPins(CS_PIN, RESET_PIN, IRQ_PIN); // Set the pins for LoRa
}

void loop() {
  // Try to parse packet
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    // Received a packet
    Serial.print("Received packet: ");
    
    // Read the packet
    while (LoRa.available()) {
      String receivedData = LoRa.readString();
      Serial.print(receivedData); // Print received data
    }

    // Print RSSI (Received Signal Strength Indicator)
    Serial.print(" with RSSI ");
    Serial.println(LoRa.packetRssi());
  }
}
