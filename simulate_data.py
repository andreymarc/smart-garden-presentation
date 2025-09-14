import json
import time
import random
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# Initialize the MQTT Client
client = AWSIoTMQTTClient("SimulatedPiClient")
client.configureEndpoint("a1jdknvzevt8bn-ats.iot.us-east-1.amazonaws.com", 8883)
client.configureCredentials(
    "/Users/andreymarchuk/Downloads/awsIoT/root-ca.pem",
    "/Users/andreymarchuk/Downloads/awsIoT/private.pem.key",
    "/Users/andreymarchuk/Downloads/awsIoT/certificate.pem.crt"
)

client.configureConnectDisconnectTimeout(10)  # 10 seconds
client.configureMQTTOperationTimeout(5)       # 5 seconds

# Connect to AWS IoT Core
try:
    client.connect()
    print("Connected to AWS IoT Core.")

    # Simulate and publish sensor data
    while True:
        data = {
            'light': round(random.uniform(0, 100), 2),
            'moisture': round(random.uniform(0, 100), 2),
            'temperature': round(random.uniform(15, 30), 2),
            'timestamp': time.time()
        }
        client.publish("smart/garden/sensor", json.dumps(data), 1)
        print(f"Published: {data}")
        time.sleep(5)  # Publish every 5 seconds

except Exception as e:
    print(f"Failed to connect or publish: {e}")
