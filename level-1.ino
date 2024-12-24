#include <LoRa.h>                                // LoRa library
#include <PulseSensorPlayground.h>                // Pulse Sensor library
#include <TinyGPS++.h>   
#include <SoftwareSerial.h>                         // GPS library

/* VARIABLES */
char buf[70];

/* LM35_Temperature_sensor */
const int LM35_sensor_output = A0;                // assigning analog pin A0 to variable 'LM35_sensor_output'
float temp;                                       // variable for temperature in Celsius
float vout;                                       // temporary variable to hold sensor digital reading
int contor_apelare = 0;

/* Pulse_sensor_Variables */
int Beat_per_minutes = 0;                         // variable for pulse
const int OUTPUT_TYPE = SERIAL_PLOTTER;           // the format of our pulse sensor output (serial monitor output)

const int Pulse_sensor_output = A1;               // analog Input for pulse sensor
const int treshhold = 550;                        // threshold for detecting pulse

byte samplesUntilReport;                          // number of samples until reporting
const byte MY_SAMPLES_PER_SERIAL_SAMPLE = 10;        // after 10 samples, calculate pulse

/* GPS_Variables */
double latitude = 0;                              // variable for latitude
double longitude = 0;                             // variable for longitude
int years, month, days;                           // variables for date
int hours, minutes, seconds;                      // variables for time
static const uint32_t GPSBaud = 9600;             // GPS baudrate
static const int RXPin = 4, TXPin = 3;            // pins for software serial communication with GPS
SoftwareSerial gps_bus(RXPin, TXPin);             // software serial connection to GPS

/* FUNCTION OBJECT FOR DEDICATED LIBRARY */
PulseSensorPlayground pulseSensor;                // Pulse sensor object
TinyGPSPlus GPS;                                  // GPS object

/* COMMUNICATION SETUP AND OTHERS SETUP */
void setup() {
  pinMode(LM35_sensor_output, INPUT);             // configure pin A0 as input
  Serial.begin(9600);                             // initialize serial monitor communication

  // Initialize LoRa communication at a specified frequency (e.g., 433E6 or 915E6 based on your region)
  if (!LoRa.begin(465E6)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }
  LoRa.setSpreadingFactor(12);                    // Optional: change spreading factor for better range

  gps_bus.begin(GPSBaud);                         // start software serial communication with GPS
  
  // Configure the PulseSensor manager.
  pulseSensor.analogInput(Pulse_sensor_output);   // assign pulse sensor to analog pin (A1)
  pulseSensor.setSerial(Serial);                  // set serial monitor output
  pulseSensor.setOutputType(OUTPUT_TYPE);         // set output type
  pulseSensor.setThreshold(treshhold);            // set threshold for pulse

  samplesUntilReport = SAMPLES_PER_SERIAL_SAMPLE; // skip the first SAMPLES_PER_SERIAL_SAMPLE in the loop
  
  if (!pulseSensor.begin()) {                     // start reading pulse sensor signal
    Serial.print("Pulse sensor failed to start");
  }
}

/* MAIN FUNCTION */
void loop() {
  if (contor_apelare == 25) {
    vout = analogRead(LM35_sensor_output);
    vout = analogRead(LM35_sensor_output);
    vout = vout * 5 / 1023;
    temp = vout / 0.01;
    contor_apelare = 0;
  }

  if (pulseSensor.sawNewSample()) {
    contor_apelare++;
    if (--samplesUntilReport == (byte)0) {
      samplesUntilReport = SAMPLES_PER_SERIAL_SAMPLE;

      if (pulseSensor.sawStartOfBeat()) {
        Beat_per_minutes = pulseSensor.getBeatsPerMinute();
      }
    }

    if (gps_bus.available() > 0) {
      GPS.encode(gps_bus.read());                 // encode GPS data
      if (GPS.location.isUpdated()) {

        /* LOCATION */
        latitude = GPS.location.lat();
        longitude = GPS.location.lng();
        
        String dataPacket = "Latitude: " + String(latitude, 6) + 
                            " Longitude: " + String(longitude, 6) + "\n";
        
        /* DATE */
        years = GPS.date.year();
        month = GPS.date.month();
        days = GPS.date.day();
        
        dataPacket += "Date: " + String(years) + "-" + String(month) + "-" + String(days) + "\n";
        
        /* TIME */
        hours = GPS.time.hour() + 5; // Time adjustment (if necessary)
        minutes = GPS.time.minute();
        
        dataPacket += "Time: " + String(hours) + ":" + String(minutes) + "\n";

        /* PULSE */
        dataPacket += "BPM: " + String(Beat_per_minutes) + "\n";

        /* TEMPERATURE */
        dataPacket += "Temperature: " + String(temp, 2) + " °C\n";

        // Send data using LoRa
        LoRa.beginPacket();
        LoRa.print(dataPacket);
        LoRa.endPacket();

        Serial.println("Sent Soldier's Data.");
      }
    }
  }
}
