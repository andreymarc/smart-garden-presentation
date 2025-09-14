import time
import json
import random
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from smbus2 import SMBus

print("Script started")

# Initialize sensors
sensors_available = {
    'bme280': False,
    'gas': False  # Gas sensor is disabled
}

# Mock data for testing
def get_mock_data():
    return {
        "temperature": round(random.uniform(20, 25), 1),
        "humidity": round(random.uniform(40, 60), 1),
        "pressure": round(random.uniform(1000, 1015), 1),
        "gas": round(random.uniform(100000, 500000), 1),
        "aqi": round(random.uniform(0, 100), 1)
}

# Try to initialize BME280 sensor
try:
    from pimoroni_bme280 import BME280
    bme280 = BME280(i2c_dev=SMBus(1))
    sensors_available['bme280'] = True
    print("BME280 sensor initialized")
except Exception as e:
    print(f"Warning: BME280 sensor not available. Error: {e}")
    print("Using mock data for BME280 sensor")

# Gas sensor is disabled
print("Gas sensor is disabled - using mock data")

print("Initializing MQTT Client")
# Initialize the MQTT Client
client = AWSIoTMQTTClient("RaspberryPiClient")
endpoint = "a1jdknvzevt8bn-ats.iot.us-east-1.amazonaws.com"
client.configureEndpoint(endpoint, 8883)
client.configureCredentials(
    "/home/pi/smart-garden-backend/awsIoT/root-ca.pem",
    "/home/pi/smart-garden-backend/awsIoT/private.pem.key",
    "/home/pi/smart-garden-backend/awsIoT/certificate.pem.crt"
)

print("MQTT Client configured")
print(f"MQTT Client details: {client}")

try:
    # Connect to AWS IoT Core
    print(f"Attempting to connect to AWS IoT Core at endpoint: {endpoint}")
    time.sleep(2)  # Small delay to ensure configurations are set
    client.connect()
    print("Connected to AWS IoT Core")

    # Publish sensor data
    while True:
        data = {"timestamp": time.time()}

        if sensors_available['bme280']:
            try:
                temperature = bme280.get_temperature()
                pressure = bme280.get_pressure()
                humidity = bme280.get_humidity()
                data.update({
                    "temperature": temperature,
                    "pressure": pressure,
                    "humidity": humidity
                })
            except Exception as e:
                print(f"Error reading BME280: {e}")
                # Use mock data if sensor fails
                mock_data = get_mock_data()
                data.update({
                    "temperature": mock_data["temperature"],
                    "pressure": mock_data["pressure"],
                    "humidity": mock_data["humidity"]
                })
        else:
            # Use mock data if sensor is not available
            mock_data = get_mock_data()
            data.update({
                "temperature": mock_data["temperature"],
                "pressure": mock_data["pressure"],
                "humidity": mock_data["humidity"]
            })

        # Always use mock data for gas sensor
        mock_data = get_mock_data()
        data.update({
            "gas": mock_data["gas"]
        })
        
        # Calculate AQI based on gas, temperature, and humidity
        # This is a simplified calculation
        gas_factor = 1 - (data["gas"] / 500000)  # Normalize gas to 0-1 range (lower is worse)
        temp_factor = 1 - abs(data["temperature"] - 22.5) / 10  # Optimal temperature is 22.5°C
        humidity_factor = 1 - abs(data["humidity"] - 50) / 50  # Optimal humidity is 50%
        
        # Combine factors (weighted average)
        aqi = 100 * (0.5 * gas_factor + 0.25 * temp_factor + 0.25 * humidity_factor)
        data["aqi"] = round(aqi, 1)

        print(f"Attempting to publish: {data}")
        client.publish("air/quality/sensor", json.dumps(data), 1)
        print(f"Published: {data}")
        time.sleep(5)

except KeyboardInterrupt:
    print("Script stopped by user")
except Exception as e:
    print(f"Error: {e}")
finally:
    client.disconnect()
    print("Disconnected from AWS IoT Core")

print("Script ended")