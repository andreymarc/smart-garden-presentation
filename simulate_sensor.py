#!/usr/bin/env python3
"""
Simulate Enviro sensor data and send to local server
This script simulates the Enviro sensor readings and sends them to the local server
"""

import time
import json
import random
import requests
from datetime import datetime

def simulate_enviro_data():
    """Simulate Enviro sensor readings"""
    
    # Simulate realistic sensor data
    base_temp = 22.0
    base_humidity = 45.0
    base_pressure = 1013.25
    base_gas = 250000  # ohms (lower = worse air quality)
    
    # Add some realistic variation
    temperature = base_temp + random.uniform(-2, 3)
    humidity = base_humidity + random.uniform(-10, 15)
    pressure = base_pressure + random.uniform(-10, 10)
    gas = base_gas + random.uniform(-50000, 50000)
    
    # Ensure gas resistance is positive
    gas = max(gas, 100000)
    
    # Simulate additional gas sensors
    reducing = gas * 0.6 + random.uniform(-10000, 10000)
    nh3 = gas * 0.3 + random.uniform(-5000, 5000)
    
    return {
        'temperature': round(temperature, 1),
        'humidity': round(humidity, 1),
        'pressure': round(pressure, 2),
        'gas': round(gas),
        'reducing': round(reducing),
        'nh3': round(nh3),
        'timestamp': datetime.now().isoformat()
    }

def send_to_server(data):
    """Send sensor data to the local server"""
    try:
        url = 'http://localhost:3000/api/sensors'
        response = requests.post(url, json=data, timeout=5)
        
        if response.status_code == 201:
            print(f"✅ Data sent successfully: {data}")
            return True
        else:
            print(f"❌ Failed to send data. Status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending data: {e}")
        return False

def main():
    """Main function to simulate sensor data"""
    print("🌱 Starting Enviro sensor simulation...")
    print("📡 Sending data to http://localhost:3000/api/sensors")
    print("⏰ Sending data every 30 seconds...")
    print("🛑 Press Ctrl+C to stop\n")
    
    try:
        while True:
            # Generate simulated sensor data
            sensor_data = simulate_enviro_data()
            
            # Send to server
            success = send_to_server(sensor_data)
            
            if success:
                # Calculate AQI (simplified)
                gas_concentration = (1000000 / sensor_data['gas']) * 100
                aqi = min(max(gas_concentration * 5, 0), 500)
                
                print(f"📊 AQI: {aqi:.0f} | "
                      f"🌡️ {sensor_data['temperature']}°C | "
                      f"💧 {sensor_data['humidity']}% | "
                      f"🌪️ {sensor_data['pressure']} hPa | "
                      f"💨 {sensor_data['gas']:,} Ω")
            
            # Wait 30 seconds before next reading
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n🛑 Sensor simulation stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main() 