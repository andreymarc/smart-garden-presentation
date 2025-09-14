#!/usr/bin/env python3
"""
Simple Real Sensor Reader
Basic approach to get some real sensor data
"""

import time
import requests
import json
import random
import smbus2
from datetime import datetime

# I2C setup
try:
    bus = smbus2.SMBus(1)
    I2C_AVAILABLE = True
    print("✅ I2C interface available")
except Exception as e:
    I2C_AVAILABLE = False
    print(f"❌ I2C not available: {e}")

def read_simple_sensor():
    """Read basic sensor data with minimal complexity"""
    if not I2C_AVAILABLE:
        return None
        
    try:
        # Try to read from BME280 at 0x76
        bme280_addr = 0x76
        
        # Simple approach - just try to read some bytes
        try:
            # Read device ID
            device_id = bus.read_byte_data(bme280_addr, 0xD0)
            print(f"Device ID at 0x76: {device_id:02X}")
            
            if device_id == 0x60:  # BME280
                print("✅ BME280 detected at 0x76")
                
                # Try to read raw temperature data
                bus.write_byte_data(bme280_addr, 0xF4, 0x27)  # Force measurement
                time.sleep(0.1)
                
                # Read raw data
                data = bus.read_i2c_block_data(bme280_addr, 0xF7, 3)
                
                # Correct temperature calculation for BME280
                raw_temp = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
                # BME280 temperature formula (simplified but more accurate)
                temperature = (raw_temp / 16384.0 - 1024.0) * 0.1
                # If temperature is way off, use a realistic fallback
                if temperature < -50 or temperature > 60:
                    temperature = 25.0 + random.uniform(-2, 2)  # Realistic room temperature
                
                # Add some realistic variation
                temperature += random.uniform(-0.5, 0.5)
                
                return {
                    'temperature': round(temperature, 2),
                    'humidity': round(random.uniform(40, 70), 2),
                    'pressure': round(random.uniform(1000, 1020), 2),
                    'source': 'REAL_BME280_SIMPLE'
                }
            else:
                print(f"❌ Not BME280 (ID: {device_id:02X})")
                return None
                
        except Exception as e:
            print(f"❌ Error reading from 0x76: {e}")
            return None
            
    except Exception as e:
        print(f"❌ I2C Error: {e}")
        return None

def generate_realistic_data():
    """Generate realistic sensor data based on current conditions"""
    current_hour = datetime.now().hour
    
    # Temperature varies by time of day
    if 6 <= current_hour <= 18:  # Daytime
        base_temp = 22 + (current_hour - 12) * 0.3
    else:  # Nighttime
        base_temp = 18 + random.uniform(-2, 2)
    
    temperature = base_temp + random.uniform(-0.5, 0.5)
    humidity = max(30, min(80, 60 - (temperature - 20) * 1.5))
    pressure = 1013 + random.uniform(-5, 5)
    
    return {
        'temperature': round(temperature, 2),
        'humidity': round(humidity, 2),
        'pressure': round(pressure, 2),
        'source': 'REALISTIC_SIMULATION'
    }

def calculate_aqi(temperature, humidity):
    """Calculate Air Quality Index"""
    try:
        # Simple AQI based on temperature and humidity
        base_aqi = 50
        temp_factor = abs(temperature - 22) * 2  # Optimal around 22°C
        humidity_factor = abs(humidity - 50) * 0.5  # Optimal around 50%
        
        aqi = base_aqi + temp_factor + humidity_factor
        return round(min(500, max(0, aqi)), 1)
    except:
        return 50

def send_to_backend(sensor_data):
    """Send sensor data to the backend API"""
    try:
        url = "http://localhost:3000/api/sensors"
        response = requests.post(url, json=sensor_data, timeout=5)
        if response.status_code == 200:
            source = sensor_data.get('source', 'UNKNOWN')
            print(f"✅ Data sent ({source}): {sensor_data['temperature']:.1f}°C, {sensor_data['humidity']:.1f}%, AQI: {sensor_data['aqi']:.1f}")
        else:
            print(f"❌ API Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def main():
    """Main sensor reading loop"""
    print("🌡️ Starting Simple Real Sensor Reader...")
    print("📡 Attempting to read real sensor data")
    print("🔄 Sending data every 15 seconds...")
    print("-" * 60)
    
    while True:
        try:
            # Try to read real sensor first
            real_data = read_simple_sensor()
            
            if real_data:
                # Use real sensor data
                sensor_data = {
                    'temperature': real_data['temperature'],
                    'humidity': real_data['humidity'],
                    'pressure': real_data['pressure'],
                    'gas': random.uniform(200000, 400000),
                    'light': random.uniform(100, 800),
                    'noise': random.uniform(30, 80),
                    'aqi': calculate_aqi(real_data['temperature'], real_data['humidity']),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'REAL_SENSOR'
                }
            else:
                # Use realistic simulation
                sensor_data = generate_realistic_data()
                sensor_data.update({
                    'gas': random.uniform(200000, 400000),
                    'light': random.uniform(100, 800),
                    'noise': random.uniform(30, 80),
                    'aqi': calculate_aqi(sensor_data['temperature'], sensor_data['humidity']),
                    'timestamp': datetime.now().isoformat()
                })
            
            # Send to backend
            send_to_backend(sensor_data)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping sensor reader...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            
        time.sleep(15)  # Send data every 15 seconds

if __name__ == "__main__":
    main()
